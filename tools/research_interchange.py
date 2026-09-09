"""Reviewed radar-interchange/1.0 projections, never a database/state restore.

No network writes. Release returns only a previously previewed envelope. Only
sources allowing downstream copies without recall/expiry obligations qualify.
Imported assertions never become primary evidence, outcomes or profiles.
"""
import json
import re
from urllib.parse import urlsplit
from tools.research_evidence import digest, fields, require, strings, text, timestamp, validate_policy
from tools.research_outcomes import artifact

SCHEMA = 'radar-interchange/1.0'
PRODUCER = 'ai-job-radar'


def closure(state, keys):
    found, todo = set(), list(keys)
    while todo:
        key = todo.pop()
        require(key in state['artifacts'], 'export dependency withdrawn or unavailable')
        if key in found: continue
        found.add(key); todo.extend(state['artifacts'][key]['dependencies'])
    return sorted(found)


def exportable(state, keys, now):
    deps = closure(state, keys)
    policies = []
    for key in deps:
        a = state['artifacts'][key]
        require(a['kind'] not in ('research-profile', 'profile-proposal', 'profile-review'), 'private profile lineage excluded from interchange')
        require(not a['use_until'], 'downstream expiry cannot be enforced')
        if a['kind'] == 'policy':
            p = a['payload']; validate_policy(p, now)
            require(p['export'] and p.get('export_retention') == 'no-recall-required', 'source export forbidden')
            policies.append(p)
    require(policies, 'export requires reviewed source permissions')
    return deps, policies


def public_url(value):
    text(value, 2000)
    u = urlsplit(value)
    require(u.scheme == 'https' and u.hostname and not u.username and not u.password
            and not u.query and not u.fragment, 'only credential-free public HTTPS locators without query/fragment')
    # Display only; not fetched. Review must also establish whether the URL is public.
    return value


def withdrawal_tokens(row):
    result = {digest(['interchange-origin', row['origin']]),
              digest(['interchange-content', row['content'], row['sources']])}
    # Withdraw the echoed original, never all unrelated ancestor policies.
    if row['origin']['producer'] == PRODUCER and re.fullmatch('[0-9a-f]{64}', row['origin']['id']):
        result.add(row['origin']['id'])
    return result


def tokens(state, deps):
    result = set(deps)
    for key in deps:
        a = state['artifacts'][key]; p = a['payload']
        if a['kind'] == 'observation' and p['description']:
            result.add(digest(['withdrawn-description', p['description']]))
        if a['kind'] == 'context':
            result.update(p.get('content_fingerprints', []))
            if p['content']: result.add(digest(['withdrawn-context', p['content']]))
        if a['kind'] == 'interchange-item': result.update(p['lineage'])
    return sorted(result)


def projection(state, request, now):
    fields(request, ['artifact', 'summary', 'excerpts'])
    key = request['artifact']; text(request['summary'], 4000)
    require(isinstance(request['excerpts'], list) and len(request['excerpts']) <= 10, 'excerpt budget exceeded')
    a = state['artifacts'].get(key)
    require(a and a['kind'] in ('brief', 'decision', 'outcome', 'context', 'interchange-item'), 'unsupported public projection')
    deps, policies = exportable(state, [key], now)
    if a['kind'] == 'interchange-item':
        require(request['summary'] == a['payload']['content']['summary'] and not request['excerpts'], 'echo must preserve original content and identity')
        return a['payload']
    p = a['payload']
    title, caps, decision, event_type = '', [], None, None
    if a['kind'] == 'brief':
        title, caps = p['proposal']['title'], p['proposal']['capabilities']
        kind, basis = p['kind'], 'model-inferred'
    elif a['kind'] in ('outcome', 'decision'):
        b = artifact(state, p['brief'], ('brief',))
        title = b['proposal']['title']; caps = p.get('capabilities', [])
        kind = a['kind']; basis = p.get('basis', 'user-reported')
        decision = p.get('decision'); event_type = p.get('event_type')
    else:
        require(p['evidence_type'] != 'repository', 'source-code export excluded')
        title = 'Reviewed ' + p['evidence_type']; kind = p['evidence_type']
        basis = 'imported-assessment' if p['observation_basis'] == 'imported-assessment' else 'user-reported'
    sources = []
    for item in request['excerpts']:
        fields(item, ['context', 'quote'])
        require(item['context'] in deps, 'excerpt outside selected lineage')
        c = artifact(state, item['context'], ('context',))
        require(c['evidence_type'] != 'repository' and c['observation_basis'] != 'imported-assessment'
                and c['content'], 'source code and imported assessments are not export excerpts')
        text(item['quote'], 2000); require(item['quote'] in c['content'], 'excerpt must match retained source')
        sources.append({'url': public_url(c['locator']), 'evidence_type': c['evidence_type'],
                        'date': c['original_date'], 'revision': c['revision'], 'quote': item['quote']})
    omitted_sources = False
    for dep in deps:
        source = state['artifacts'][dep]
        if source['kind'] == 'observation':
            row = source['payload']
            sources.append({'url': public_url(row['url']), 'evidence_type': 'job', 'date': row['posted_at'],
                            'revision': row['source_revision'], 'quote': None})
        elif source['kind'] == 'context':
            row = source['payload']
            candidate = row['locator'] if row['locator'].startswith('https://') else row['source']
            try:
                locator = public_url(candidate)
            except ValueError:
                omitted_sources = True
                continue
            sources.append({'url': locator, 'evidence_type': row['evidence_type'], 'date': row['original_date'],
                            'revision': row['revision'], 'quote': None})
    # Public projection never copies reviewer names, profile, credentials, raw
    # descriptions, source files, commands/results or the original internal payload.
    restrictions = [{'source': p['source'], 'permission_reference': p['export_permission_reference'],
                     'retention': 'no-recall-required', 'limitations': p['limitations']} for p in policies]
    limits = ['Reviewed summary is an assessment; imported provenance is not independent corroboration.',
              'No raw descriptions, private profile, test logs or source code included.']
    if omitted_sources: limits.append('Some original locators lack reviewed public URL form; content/paths omitted, hash lineage retained.')
    result = {'origin': {'producer': PRODUCER, 'id': key, 'revision': key},
              'producer_schema': 'research-artifact/1', 'parents': sorted(a['dependencies']),
              'lineage': tokens(state, deps), 'kind': kind, 'basis': basis,
              'observed_at': p.get('occurred_at', p.get('decided_at', p.get('original_date'))),
              'sources': sorted(sources, key=digest), 'restrictions': sorted(restrictions, key=digest),
              'content': {'title': title, 'summary': request['summary'], 'capabilities': caps,
                          'decision': decision, 'outcome_type': event_type, 'limitations': limits + p.get('limitations', [])}}
    return result


def markdown(bundle):
    """One canonical safe companion; imported HTML/links are never rendered active."""
    def safe(s):
        return re.sub(r'[\x00-\x1f\x7f\u202a-\u202e\u2066-\u2069]', ' ', str(s)).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('[', '&#91;').replace(']', '&#93;').replace('`', '&#96;')
    lines = ['# Reviewed research interchange', '', 'Imported assessments are not independent corroboration.', '']
    if bundle.get('domain'):
        lines += ['Domain: ' + safe(json.dumps(bundle['domain'])), '']
    for row in bundle['items']:
        lines += ['## ' + safe(row['content']['title']), '', '> ' + safe(row['content']['summary']), '',
                  'Origin: ' + safe(json.dumps(row['origin'])), 'Basis (producer assertion): ' + safe(row['basis'])]
        lines += ['- ' + safe(x) for x in row['content']['limitations']]
    return '\n'.join(lines) + '\n'


def validate(bundle, now, pack=None):
    fields(bundle, ['schema', 'producer', 'exported_at', 'items', 'markdown'], ['domain'])
    from tools.research_domains import reference
    require(bundle['schema'] == ('radar-interchange/1.1' if pack else SCHEMA), 'interchange domain/version mismatch')
    require(bundle.get('domain') == (reference(pack) if pack else None), 'interchange pack revision mismatch')
    require(len(json.dumps(bundle).encode()) <= 2_000_000, 'interchange exceeds byte budget')
    text(bundle['producer']); require(timestamp(bundle['exported_at']) <= now, 'future export time')
    require(isinstance(bundle['items'], list) and 0 < len(bundle['items']) <= 20, 'invalid interchange budget')
    from tools.research_evidence import TAXONOMY
    taxonomy = pack['taxonomy'] if pack else TAXONOMY
    for row in bundle['items']:
        fields(row, ['origin', 'producer_schema', 'parents', 'lineage', 'kind', 'basis', 'observed_at', 'sources', 'restrictions', 'content'])
        fields(row['origin'], ['producer', 'id', 'revision'])
        for name in row['origin']: text(row['origin'][name])
        text(row['producer_schema']); text(row['kind'])
        require(row['basis'] in ('observed', 'user-reported', 'model-inferred', 'imported-assessment'), 'unknown basis')
        for name in ('parents', 'lineage'):
            strings(row[name], 10000)
            require(all(re.fullmatch('[0-9a-f]{64}', v) for v in row[name]), 'lineage must contain immutable hashes')
        require(row['lineage'] and set(row['parents']) <= set(row['lineage']), 'missing original lineage')
        if row['observed_at'] is not None:
            from datetime import date
            observed = row['observed_at']
            text(observed)
            if len(observed) == 10: require(date.fromisoformat(observed) <= now.date(), 'future observation')
            else: require(timestamp(observed) <= now, 'future observation')
        c = row['content']; fields(c, ['title', 'summary', 'capabilities', 'decision', 'outcome_type', 'limitations'])
        text(c['title'], 200); text(c['summary'], 4000); strings(c['capabilities'], 30); strings(c['limitations'], 100)
        require(c['limitations'] and set(c['capabilities']) <= set(taxonomy['capabilities']), 'missing limits/unknown capability')
        from tools.research_outcomes import DECISIONS, EVENTS
        require(c['decision'] is None or c['decision'] in DECISIONS, 'unknown decision')
        require(c['outcome_type'] is None or c['outcome_type'] in EVENTS, 'unknown outcome type')
        require(isinstance(row['sources'], list) and len(row['sources']) <= 200, 'source budget exceeded')
        for source in row['sources']:
            fields(source, ['url', 'evidence_type', 'date', 'revision', 'quote']); public_url(source['url']); text(source['evidence_type'])
            for n in ('date', 'revision', 'quote'):
                if source[n] is not None: text(source[n], 2000)
        require(isinstance(row['restrictions'], list) and 0 < len(row['restrictions']) <= 200, 'source restrictions required')
        for p in row['restrictions']:
            fields(p, ['source', 'permission_reference', 'retention', 'limitations'])
            text(p['source']); text(p['permission_reference']); strings(p['limitations'])
            require(p['retention'] == 'no-recall-required', 'downstream retention unsupported')
    require(bundle['markdown'] == markdown(bundle), 'companion differs from exact reviewed JSON')


def preview(store, requests):
    require(isinstance(requests, list) and 0 < len(requests) <= 20, 'preview requires selected records')
    with store.transaction() as state:
        rows = [projection(state, r, store.clock()) for r in requests]
        bundle = {'schema': SCHEMA, 'producer': PRODUCER, 'exported_at': store.clock().isoformat(), 'items': rows}
        from tools.research_domains import pack_for, reference
        pack = pack_for(state)
        if pack:
            bundle.update(schema='radar-interchange/1.1', domain=reference(pack))
        bundle['markdown'] = markdown(bundle); validate(bundle, store.clock(), pack)
        key = store.put(state, 'interchange-preview', bundle, [r['artifact'] for r in requests])
        return {'preview': key, 'review_digest': digest(bundle), 'bundle': bundle}


def release(store, key, review_digest, reviewer):
    text(reviewer)
    with store.transaction() as state:
        bundle = artifact(state, key, ('interchange-preview',))
        exportable(state, [key], store.clock())
        from tools.research_domains import pack_for
        validate(bundle, store.clock(), pack_for(state))
        require(digest(bundle) == review_digest, 'review must match exact current preview')
        store.put(state, 'interchange-release', {'preview': key, 'review_digest': review_digest, 'reviewer': reviewer,
                  'released_at': store.clock().isoformat(), 'limitation': 'Explicit review assertion; no recipient identity or remote recall guarantee.'}, [key])
        return bundle


def import_interchange(store, bundle, policy):
    validate_policy(policy, store.clock())
    require(policy['method'] == 'reviewed-context', 'reviewed import permission required')
    require(policy['export'] and not policy.get('use_until'), 'interchange import must preserve no-recall restrictions; narrower local paths use P3 context import')
    with store.transaction() as state:
        from tools.research_domains import pack_for
        validate(bundle, store.clock(), pack_for(state))
        pol = store.put(state, 'policy', policy)
        ids = []
        for row in bundle['items']:
            fingerprint = digest(['interchange-content', row['content'], row['sources']])
            identity = digest(['interchange-origin', row['origin']])
            require(not (set(row['lineage']) | {identity, fingerprint}) & set(state['withdrawn']), 'withdrawn lineage/content cannot return')
            old = [(k,a['payload']) for k,a in state['artifacts'].items() if a['kind'] == 'interchange-item' and a['payload']['origin'] == row['origin']]
            if old:
                require(old[0][1] == {**row, 'lineage': sorted(set(row['lineage']) | {identity, fingerprint})}, 'conflicting immutable origin revision')
                ids.append(old[0][0]); continue
            # An echo of a locally available artifact depends on that original.
            deps = [pol, *[k for k in row['lineage'] if k in state['artifacts']]]
            imported = {**row, 'lineage': sorted(set(row['lineage']) | {identity, fingerprint})}
            ids.append(store.put(state, 'interchange-item', imported, deps))
        store.put(state, 'interchange-receipt', {'schema': bundle['schema'], 'producer': bundle['producer'],
                  'exported_at': bundle['exported_at'], 'bundle_digest': digest(bundle)}, [pol, *ids])
        return {'imports': ids, 'status': 'imported-assessments-only', 'market_observations_added': 0}
