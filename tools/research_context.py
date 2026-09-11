"""Bounded non-job evidence over the Phase 2 policy/receipt/lifecycle contracts.

No discovery crawler, repository execution, model-driven URLs or Radar runtime.
Only explicitly reviewed URLs, pinned Git objects or selected report files enter.
"""
from copy import deepcopy
from datetime import datetime, timezone
import ipaddress
import json
from pathlib import Path
import re
import socket
import subprocess
from urllib.parse import urlparse
from urllib.request import Request, ProxyHandler, build_opener

from tools.research_evidence import (EvidenceError, digest, fields, require, strings, text,
                                     timestamp, validate_policy, validate_receipt)
from tools.research_sources import NoRedirect, html_text

TYPES = ('repository', 'product', 'problem', 'discussion', 'trend', 'experiment-result', 'imported-assessment', 'learning-resource')


def content_fingerprints(row):
    if row['content'] is None:
        return []
    fingerprints = [digest(['withdrawn-context', row['content']])]
    if row['evidence_type'] == 'imported-assessment':
        try:
            payload = json.loads(row['content'])
            for quote in payload.get('evidence_quotes') or []:
                fields(quote, ['quote', 'source_url'])
                text(quote['quote'], 6000); text(quote['source_url'])
                fingerprints.append(digest(['withdrawn-imported-quote', quote['source_url'], quote['quote']]))
        except (ValueError, TypeError, AttributeError):
            raise EvidenceError('imported assessment needs bounded original quote lineage') from None
    return sorted(set(fingerprints))


def validate_request(request, policy, now):
    fields(request, ['schema_version', 'problem', 'category', 'locators', 'query', 'period', 'max_items'])
    require(request['schema_version'] == 1 and request['category'] in TYPES, 'unsupported context request')
    text(request['problem']); text(request['query'])
    strings(request['locators'], 10)
    require(request['locators'] and type(request['max_items']) is int and
            1 <= request['max_items'] <= 10, 'context request needs bounded explicit locators')
    fields(request['period'], ['from', 'to'])
    for date in request['period'].values():
        if date is not None:
            timestamp(date)
    if all(request['period'].values()):
        require(timestamp(request['period']['from']) <= timestamp(request['period']['to']), 'invalid context period')
    validate_policy(policy, now)
    require(policy['method'] == 'reviewed-context', 'context permission must cover this method and locators')


def validate_context(row, request, now):
    fields(row, ['schema_version', 'source', 'evidence_type', 'original_date', 'date_precision',
                 'revision', 'captured_at', 'content', 'locator', 'inspector', 'inspection_depth',
                 'observation_basis', 'conditions', 'lineage', 'limitations'])
    require(row['schema_version'] == 1 and row['evidence_type'] in TYPES, 'unsupported context schema/type')
    require(row['evidence_type'] == request['category'], 'context category mismatch')
    for k in ('source', 'locator', 'inspector', 'inspection_depth'):
        text(row[k])
    require(row['locator'] in request['locators'], 'unrequested context locator')
    require(timestamp(row['captured_at']) <= now, 'future context capture')
    require(row['date_precision'] in ('unknown', 'day', 'instant'), 'invalid date precision')
    if row['original_date'] is None:
        require(row['date_precision'] == 'unknown', 'missing date cannot imply freshness')
    else:
        if row['date_precision'] == 'day':
            require(bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', row['original_date'])), 'invalid day date')
            date = datetime.fromisoformat(row['original_date']).replace(tzinfo=timezone.utc)
        else:
            require(row['date_precision'] == 'instant', 'date needs precision')
            date = timestamp(row['original_date'])
        require(date <= now, 'future source date')
    if row['revision'] is not None:
        text(row['revision'])
    if row['content'] is not None:
        text(row['content'], 60_000)
    require(row['observation_basis'] in ('inspected', 'self-reported', 'reproduced', 'imported-assessment'),
            'unknown observation basis')
    strings(row['conditions']); strings(row['lineage']); strings(row['limitations'])
    require(row['lineage'], 'original lineage required')
    if row['observation_basis'] == 'reproduced':
        require(row['evidence_type'] == 'experiment-result' and row['conditions'] and row['content'],
                'reproduced capability needs inspected results and conditions')
    if row['evidence_type'] == 'repository':
        require(row['revision'] and re.fullmatch(r'[0-9a-f]{40,64}', row['revision']), 'repository must be pinned')
    if row['evidence_type'] == 'imported-assessment':
        require(row['observation_basis'] == 'imported-assessment', 'imported assessment is not primary evidence')


def import_context(store, bundle):
    fields(bundle, ['schema_version', 'policy', 'request', 'receipt', 'records'])
    require(bundle['schema_version'] == 1, 'unsupported context bundle')
    now = store.clock()
    policy, request, receipt, rows = [bundle[k] for k in ('policy', 'request', 'receipt', 'records')]
    validate_request(request, policy, now)
    validate_receipt(receipt, policy['source'], now)
    require(receipt['kind'] == 'context', 'context requires context receipt')
    require(isinstance(rows, list) and len(rows) <= request['max_items'], 'context item budget exceeded')
    require(sum(p['returned'] for p in receipt['pages']) == len(rows), 'context receipt count mismatch')
    require(receipt['query'] == request['query'], 'context receipt query mismatch')
    require(receipt['completeness'] not in ('failed', 'blocked') or not rows, 'failed acquisition cannot carry evidence')
    for row in rows:
        validate_context(row, request, now)
        require(timestamp(receipt['started_at']) <= timestamp(row['captured_at']) <= timestamp(receipt['finished_at']),
                'context capture outside receipt')
    with store.transaction() as state:
        policy_id = store.put(state, 'policy', policy, use_until=policy.get('use_until'))
        request_id = store.put(state, 'context-request', request, [policy_id])
        receipt_id = store.put(state, 'context-receipt', receipt, [request_id, policy_id])
        ids = []
        for row in rows:
            fingerprints = content_fingerprints(row)
            require(not set(fingerprints).intersection(state['withdrawn']), 'withdrawn context cannot be reimported')
            # Same original source content is one corroborating item, even across Radar scans.
            identity = digest([row['source'], row['revision'], row['content']])
            ids.append(store.put(state, 'context', {**row, 'evidence_identity': identity, 'content_fingerprints': fingerprints,
                                 'receipt': receipt_id, 'request': request_id}, [receipt_id]))
        return {'request': request_id, 'receipt': receipt_id, 'contexts': ids}


def fetch_public(url):
    """Explicit public HTTPS destination, no auth/proxy/redirect/fallback."""
    parsed = urlparse(url)
    require(parsed.scheme == 'https' and parsed.hostname and not parsed.username and
            not parsed.password and parsed.port in (None, 443), 'only reviewed public HTTPS URLs')
    addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    require(addresses and all(ipaddress.ip_address(a[4][0]).is_global for a in addresses), 'nonpublic destination')
    with build_opener(ProxyHandler({}), NoRedirect).open(Request(url, headers={
            'User-Agent': 'AI-Job-Radar/0.3 (explicit bounded research)', 'Accept': 'text/plain,text/html'}), timeout=20) as response:
        content_type = response.headers.get('Content-Type', '')
        require(any(t in content_type for t in ('text/plain', 'text/html', 'text/markdown')), 'unsupported context representation')
        body = response.read(60_001)
        require(len(body) <= 60_000, 'context page too large')
        raw = body.decode('utf-8')
        return (html_text(raw) if 'html' in content_type else raw), 'html-text/1' if 'html' in content_type else 'utf8-text/1'


def acquire(store, bundle, *, fetch=fetch_public, repo=None):
    """Fill a reviewed request skeleton; failed attempts get receipts, never retries.

    Repository requests contain exact `COMMIT:path` locators. Git show reads object
    bytes only, with no checkout, hooks, dependencies, scripts or test execution.
    """
    data = deepcopy(bundle)
    require(data.get('records') == [], 'acquisition skeleton must contain no records')
    now = store.clock()
    validate_request(data['request'], data['policy'], now)
    require(data['request']['category'] != 'imported-assessment', 'use selected Radar report import')
    # Persist a pending receipt before any I/O so interruption leaves an honest attempt.
    request = data['request']
    receipt = data['receipt']
    receipt.update(started_at=now.isoformat(), finished_at=now.isoformat(), pages=[], completeness='partial')
    import_context(store, data)
    results = []
    try:
        for locator in request['locators'][:request['max_items']]:
            validate_request(request, data['policy'], store.clock())
            revision = None
            if repo is not None:
                require(request['category'] == 'repository', 'repository reads need repository category')
                match = re.fullmatch(r'([0-9a-f]{40}):([^\x00\r\n]+)', locator)
                require(match and not Path(match[2]).is_absolute() and '..' not in Path(match[2]).parts,
                        'repository locator must be pinned commit:relative-path')
                revision = match[1]
                args = ['git', '--no-replace-objects', '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null', '-C', str(Path(repo).resolve())]
                promisor = subprocess.run(args + ['config', '--get-regexp', r'^remote\..*\.promisor$'],
                                          capture_output=True, text=True, timeout=10)
                require(promisor.returncode == 1, 'partial/promisor repositories require a separate reviewed materialization')
                size = subprocess.run(args + ['cat-file', '-s', locator], capture_output=True, text=True, check=True, timeout=10)
                require(int(size.stdout) <= 60_000, 'repository object too large')
                result = subprocess.run(args + ['show', '--no-ext-diff', '--no-textconv', locator], capture_output=True, check=True, timeout=10)
                content, depth = result.stdout.decode('utf-8'), 'exact Git object inspected; no code/tests executed'
            else:
                content, depth = fetch(locator)
            results.append({'schema_version': 1, 'source': data['policy']['source'], 'evidence_type': request['category'],
                'original_date': None, 'date_precision': 'unknown', 'revision': revision,
                'captured_at': store.clock().isoformat(), 'content': content, 'locator': locator,
                'inspector': 'deterministic selected-content acquisition', 'inspection_depth': depth,
                'observation_basis': 'inspected', 'conditions': [], 'lineage': [locator],
                'limitations': ['Content inspected only; no reproduced results.', 'Original publication date unknown.']})
        data['records'] = results
        receipt.update(finished_at=store.clock().isoformat(), pages=[{'locator': r['locator'], 'status': 'ok', 'returned': 1, 'next_cursor': None} for r in results],
                       completeness='complete-request' if len(results) == len(request['locators']) else 'partial')
        return import_context(store, data)
    except (ValueError, OSError, subprocess.SubprocessError):
        data['records'] = []
        receipt.update(finished_at=store.clock().isoformat(), pages=[], completeness='failed')
        try:
            import_context(store, data)
        except EvidenceError:
            pass  # Expired authorization cannot be extended to preserve an error record.
        raise EvidenceError('context acquisition failed; no retry or alternate access') from None


def import_radar(store, report, bundle, selected):
    """Read-only schema-3.0 conversion. Quotes are imported, never newly verified.

    Per-source reviewed permission must cover selected report content and derivatives;
    report ownership alone cannot grant rights in linked third-party material.
    """
    require(report.get('schema_version') == '3.0', 'unsupported Radar report schema')
    text(report.get('scan_id')); timestamp(report.get('generated_at'))
    require(selected and len(selected) <= 10, 'select 1–10 Radar topic IDs')
    topics = report.get('recommendations', []) + report.get('watch', [])
    require(isinstance(topics, list), 'invalid Radar topics')
    selected_topics = [t for t in topics if t.get('topic_id') in selected]
    require(len(selected_topics) == len(set(selected)), 'selected topics missing or duplicate')
    data = deepcopy(bundle)
    require(data['request']['category'] == 'imported-assessment', 'Radar conversion is imported assessment')
    records = []
    for topic in selected_topics:
        topic_id = topic['topic_id']
        locator = 'radar:' + report['scan_id'] + ':' + topic_id
        payload = {k: topic.get(k) for k in ('title', 'what_changed', 'assessment_status', 'caveats', 'evidence_quotes', 'source_links', 'event_time', 'event_time_basis')}
        lineage = topic.get('source_links') or [locator]
        strings(lineage)
        records.append({'schema_version': 1, 'source': 'ai-trend-radar', 'evidence_type': 'imported-assessment',
            'original_date': None, 'date_precision': 'unknown', 'revision': str(topic.get('revision', 'unknown')),
            'captured_at': store.clock().isoformat(), 'content': json.dumps(payload, ensure_ascii=False), 'locator': locator,
            'inspector': data['policy']['reviewed_by'], 'inspection_depth': 'selected schema-3.0 report; linked sources not fetched',
            'observation_basis': 'imported-assessment', 'conditions': [], 'lineage': lineage,
            'limitations': ['Report time is not original source time or discussion freshness.',
                'Imported quotes and assessments are not independently inspected primary content.',
                'No audience-demand, reproduced-results or novelty validation.',
                'Report revision: ' + digest(report) + '; generated: ' + report['generated_at']]})
    data['records'] = records
    data['receipt'].update(finished_at=store.clock().isoformat(), pages=[{'locator': r['locator'], 'status': 'ok', 'returned': 1, 'next_cursor': None} for r in records], completeness='complete-request')
    return import_context(store, data)
