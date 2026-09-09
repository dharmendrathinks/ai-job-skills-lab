"""Measured coverage and equal-window cohorts over P2 evidence, without fit gates."""
from collections import Counter
from pathlib import Path
from datetime import timedelta
import json
import re

from tools.research_evidence import (TAXONOMY, aggregate, digest, fields, require, strings,
                                     text, timestamp)


def item(state, key, kind):
    a = state['artifacts'].get(key)
    require(a and a['kind'] == kind, 'required evidence unavailable or withdrawn')
    return a['payload']


def register_protocol(store, row):
    fields(row, ['schema_version', 'source', 'instance', 'board', 'query', 'requested_filters',
                 'effective_filters', 'collector_version', 'query_pack_version', 'scope', 'cadence_seconds',
                 'reviewer', 'limitations'], ['capture_offset_seconds', 'capture_tolerance_seconds'])
    require(row['schema_version'] == 1 and row['scope'] in ('bounded-sample', 'board-inventory'), 'unknown protocol schema/scope')
    for n in ('source', 'instance', 'board', 'query', 'collector_version', 'query_pack_version', 'reviewer'): text(row[n])
    for n in ('requested_filters', 'effective_filters'): require(isinstance(row[n], dict), 'filters must be objects')
    require(type(row['cadence_seconds']) is int and 3600 <= row['cadence_seconds'] <= 86400 * 7, 'cadence must be one hour to seven days')
    row = {**row, 'capture_offset_seconds': row.get('capture_offset_seconds', 0),
           'capture_tolerance_seconds': row.get('capture_tolerance_seconds', 300)}
    require(type(row['capture_offset_seconds']) is int and 0 <= row['capture_offset_seconds'] < row['cadence_seconds'], 'invalid capture offset')
    require(type(row['capture_tolerance_seconds']) is int and 0 <= row['capture_tolerance_seconds'] <= row['cadence_seconds'] // 4, 'invalid capture tolerance')
    strings(row['limitations']); require(row['limitations'], 'protocol limits required')
    with store.transaction() as state:
        require(not any(a['kind'] == 'collection-protocol' and a['payload']['source'] == row['source']
                        and (a['payload']['instance'], a['payload']['board']) != (row['instance'], row['board'])
                        for a in state['artifacts'].values()), 'distinct board/instance requires a distinct source identity')
        return {'protocol': store.put(state, 'collection-protocol', row)}


def assess_capture(store, row):
    fields(row, ['schema_version', 'receipt', 'protocol', 'fresh', 'terminal', 'evidence', 'reviewer', 'changes'])
    require(row['schema_version'] == 1 and type(row['fresh']) is bool and type(row['terminal']) is bool, 'invalid capture assessment')
    text(row['reviewer']); text(row['evidence'], 4000); strings(row['changes'])
    with store.transaction() as state:
        receipt = item(state, row['receipt'], 'receipt'); protocol = item(state, row['protocol'], 'collection-protocol')
        require(all(receipt[n] == protocol[n] for n in ('source', 'query', 'requested_filters', 'effective_filters')), 'capture differs from frozen protocol')
        require(not any(a['kind'] == 'capture-assessment' and a['payload']['receipt'] == row['receipt']
                        and a['payload'] != row for a in state['artifacts'].values()), 'capture already assessed; create a revised protocol/capture')
        if row['terminal']:
            require(receipt['completeness'] == 'complete-request' and receipt['pages']
                    and all(p['status'] == 'ok' for p in receipt['pages'])
                    and receipt['pages'][-1]['next_cursor'] is None, 'no terminal inventory/request evidence')
        return {'capture': store.put(state, 'capture-assessment', row, [row['receipt'], row['protocol']])}


def review_segments(store, row):
    fields(row, ['schema_version', 'observation', 'reviewer', 'reviewed_at', 'values', 'evidence', 'limitations', 'supersedes'])
    require(row['schema_version'] == 1, 'unknown segment schema')
    text(row['reviewer']); strings(row['limitations']); require(row['limitations'], 'review limits required')
    require(timestamp(row['reviewed_at']) <= store.clock(), 'future review')
    fields(row['values'], [], ['countries', 'language', 'industry', 'seniority', 'arrangement', 'employment_type'])
    require(row['values'] and set(row['evidence']) == set(row['values']), 'each segment needs source evidence')
    with store.transaction() as state:
        obs = item(state, row['observation'], 'observation')
        for name, value in row['values'].items():
            if name == 'countries':
                strings(value, 30); require(value and all(re.fullmatch('[A-Z]{2}', x) for x in value), 'country labels must be reviewed alpha-2 codes')
            else:
                text(value)
                if name == 'language': require(re.fullmatch('[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*', value), 'language must be a reviewed language tag')
            e = row['evidence'][name]; fields(e, ['source_field', 'quote', 'reason'])
            require(e['source_field'] in ('description', 'segments', 'country', 'language'), 'title/profile inference is not segment evidence')
            raw = obs[e['source_field']]
            raw = json.dumps(raw, ensure_ascii=False, sort_keys=True) if isinstance(raw, dict) else raw
            text(e['quote'], 4000); text(e['reason'], 2000)
            require(raw and e['quote'] in raw, 'segment evidence must match original source field')
        previous = [k for k,a in state['artifacts'].items() if a['kind'] == 'segment-review' and a['payload']['observation'] == row['observation']]
        replaced = {a['payload']['supersedes'] for a in state['artifacts'].values() if a['kind'] == 'segment-review'}
        current = [k for k in previous if k not in replaced]
        deps = [row['observation']]
        if row['supersedes']:
            require(row['supersedes'] in current, 'segment revision is stale'); deps.append(row['supersedes'])
        else: require(not current, 'explicit segment supersession required')
        return {'segments': store.put(state, 'segment-review', row, deps)}


def register_board(store, row):
    fields(row, ['schema_version', 'source', 'instance', 'board', 'employer_domain', 'ownership_context',
                 'quote', 'reviewer', 'limitations'])
    require(row['schema_version'] == 1, 'unknown board schema')
    for n in ('source', 'instance', 'board', 'reviewer', 'quote'): text(row[n])
    require(re.fullmatch(r'[a-z0-9]+(?:[.-][a-z0-9]+)*\.[a-z]{2,}', row['employer_domain']), 'reviewed employer domain required')
    strings(row['limitations']); require(row['limitations'], 'board review limits required')
    with store.transaction() as state:
        ctx = item(state, row['ownership_context'], 'context')
        require(ctx['content'] and ctx['observation_basis'] == 'inspected' and row['quote'] in ctx['content'], 'board ownership requires inspected source evidence')
        require(not any(a['kind'] == 'employer-board' and a['payload']['source'] == row['source']
                        and (a['payload']['instance'], a['payload']['board'], a['payload']['employer_domain']) !=
                            (row['instance'], row['board'], row['employer_domain'])
                        for a in state['artifacts'].values()), 'conflicting board ownership/source identity requires review')
        return {'board': store.put(state, 'employer-board', row, [row['ownership_context']])}


def link_board(store, row):
    fields(row, ['schema_version', 'observation', 'board', 'source_field', 'quote', 'employer_requisition', 'reviewer'])
    require(row['schema_version'] == 1 and row['source_field'] in ('url', 'segments'), 'board linkage requires original source locator/metadata')
    text(row['quote']); text(row['reviewer'])
    with store.transaction() as state:
        obs = item(state, row['observation'], 'observation'); board = item(state, row['board'], 'employer-board')
        require(obs['source'] == board['source'], 'board/source mismatch')
        raw = obs[row['source_field']]
        raw = json.dumps(raw, ensure_ascii=False, sort_keys=True) if isinstance(raw, dict) else raw
        require(row['quote'] in raw, 'link quote absent from original source')
        if row['employer_requisition'] is not None:
            text(row['employer_requisition']); require(row['employer_requisition'] in row['quote'], 'requisition needs explicit source evidence')
        require(not any(a['kind'] == 'board-link' and a['payload']['observation'] == row['observation'] and a['payload'] != row
                        for a in state['artifacts'].values()), 'withdraw incorrect board linkage before relinking')
        return {'link': store.put(state, 'board-link', row, [row['observation'], row['board']])}


def selected_state(state, receipts, start=None, end=None, basis='capture'):
    """Reuse the upstream-derived P2 aggregate on an explicit observation slice."""
    selected = {k:a for k,a in state['artifacts'].items() if k in receipts}
    for k,a in state['artifacts'].items():
        if a['kind'] != 'observation' or a['payload']['receipt'] not in receipts: continue
        date = a['payload']['captured_at'] if basis == 'capture' else a['payload']['posted_at']
        if start and (date is None or not start <= timestamp(date) < end): continue
        selected[k] = a
        links = [v['payload'] for v in state['artifacts'].values() if v['kind'] == 'board-link' and v['payload']['observation'] == k]
        if links:
            board = item(state, links[0]['board'], 'employer-board')
            selected[k] = {**a, 'payload': {**a['payload'], 'employer_domain': board['employer_domain'],
                                          'employer_requisition': links[0]['employer_requisition']}}
    for k,a in state['artifacts'].items():
        if a['kind'] == 'analysis' and a['payload']['observation'] in selected: selected[k] = a
    return {'schema_version': 1, 'artifacts': selected, 'withdrawn': []}


def analysis_version(state, payload):
    versions = None
    if payload['method'] == 'codex-extraction':
        execution = state['artifacts'].get(payload.get('execution'))
        if not execution or not execution['payload'].get('versions'): return None
        versions = execution['payload']['versions']
    return digest([versions, payload['taxonomy_version'], payload['method']])


def coverage_payload(state, receipts, start, end, expected, basis='capture'):
    scoped = selected_state(state, receipts, start, end, basis)
    report, deps = aggregate(scoped)
    deps += [k for k,a in state['artifacts'].items() if a['kind'] == 'board-link' and a['payload']['observation'] in scoped['artifacts']]
    latest = {key for group in report['openings'] for key in group['observations']}
    reviews = {k:a['payload'] for k,a in state['artifacts'].items() if a['kind'] == 'segment-review'
               and a['payload']['observation'] in latest}
    replaced = {r['supersedes'] for r in reviews.values()}
    reviews = {k:r for k,r in reviews.items() if k not in replaced}
    by_obs = {r['observation']: r['values'] for r in reviews.values()}
    dimensions = {name: {} for name in ('countries', 'language', 'industry', 'seniority', 'arrangement', 'employment_type')}
    employers = Counter()
    for group in report['openings']:
        values = {name:set() for name in dimensions}
        for key in group['observations']:
            obs = scoped['artifacts'][key]['payload']; reviewed = by_obs.get(key, {})
            for name in dimensions:
                if name == 'countries': v = reviewed.get(name, [obs['country']] if obs['country'] else [])
                elif name == 'language': v = [reviewed.get(name, obs['language'])]
                else:
                    raw = reviewed.get(name, obs['segments'].get(name))
                    v = raw if isinstance(raw, list) else [raw]
                if not isinstance(v, list): v = [v]
                values[name].update(x for x in v if isinstance(x, str) and x)
            if obs['employer_domain']: employers[obs['employer_domain']] += 0
        for name, labels in values.items():
            for label in labels or {'unknown'}:
                dimensions[name].setdefault(label, set()).add(group['opening'])
        domains = {scoped['artifacts'][k]['payload']['employer_domain'] for k in group['observations']} - {None}
        for domain in domains: employers[domain] += 1
    counts = {n:{k:len(v) for k,v in sorted(vals.items())} for n,vals in dimensions.items()}
    trans = [k for k,a in state['artifacts'].items() if a['kind'] == 'translation-review'
             and a['payload']['decision'] == 'accept' and
             state['artifacts'][a['payload']['proposal']]['payload']['observation'] in latest]
    translated = {state['artifacts'][state['artifacts'][k]['payload']['proposal']]['payload']['observation'] for k in trans}
    latest_analyses = {}
    for a in scoped['artifacts'].values():
        if a['kind'] == 'analysis' and a['payload']['observation'] in latest:
            p = a['payload']; old = latest_analyses.get(p['observation'])
            if old is None or timestamp(p['reviewed_at']) > timestamp(old['reviewed_at']): latest_analyses[p['observation']] = p
    version_values = [analysis_version(state,p) for p in latest_analyses.values()]
    versions = sorted({v for v in version_values if v})
    report['analysis_version_unknown'] = version_values.count(None)
    health = {}
    for key in receipts:
        r = item(state, key, 'receipt')
        counts_for_source = health.setdefault(r['source'], {'receipts': 0, 'complete-request': 0, 'partial': 0, 'failed': 0, 'blocked': 0})
        counts_for_source['receipts'] += 1; counts_for_source[r['completeness']] += 1
    report['source_health'] = health
    report['coverage_version'] = digest(Path(__file__).read_text())
    report.update(period={'from': start.isoformat(), 'to': end.isoformat(), 'basis': basis, 'end_exclusive': True},
                  segments=counts, missing_segments={n:sorted(set(labels) - set(counts[n])) for n,labels in expected.items()},
                  employer_opening_counts=dict(sorted(employers.items())),
                  translated_observations=len(translated), untranslated_observations=len(latest - translated),
                  analysis_versions=versions)
    report['limitations'] += ['Segment counts overlap for multi-country openings; unknown is not exclusion.',
                              'Reviewed labels are assertions linked to exact source fields, not inferred from profile/title.',
                              'No translation does not exclude an observation or mean missing ability.']
    report['markdown'] = render_coverage(report)
    return report, sorted(set(deps) | set(reviews) | set(trans))


def render_coverage(report):
    def safe(s): return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\n', ' ').replace('[', '&#91;')
    lines = ['# Observed research coverage', '', 'Sample counts, not worldwide demand.', '', '| Measure | Count |', '|---|---:|']
    lines += [f'| {safe(k)} | {v} |' for k,v in report['counts'].items()]
    for name, values in report['segments'].items():
        lines += ['', '## ' + name, '', '| Segment | Distinct openings |', '|---|---:|']
        lines += [f'| {safe(k)} | {v} |' for k,v in values.items()]
    lines += ['', 'Period: ' + safe(json.dumps(report['period'])), '', 'Missing selected segments: ' + safe(json.dumps(report['missing_segments']))]
    lines += ['', '## Source requests', '']
    for key,receipt in report['receipts'].items():
        lines += ['- ' + safe(json.dumps({'receipt':key, **receipt}, ensure_ascii=False))]
    lines += ['', 'Analysis versions: ' + safe(json.dumps(report['analysis_versions'])),
              'Employer opening counts: ' + safe(json.dumps(report['employer_opening_counts'])),
              'Reviewed translations: ' + str(report['translated_observations'])]
    lines += ['- ' + safe(x) for x in report['limitations']]
    return '\n'.join(lines) + '\n'


def coverage(store, *, start=None, end=None, expected=None):
    end = timestamp(end) if end else store.clock()
    start = timestamp(start) if start else end - timedelta(days=28)
    require(start < end <= store.clock(), 'invalid coverage period')
    expected = expected or {}
    fields(expected, [], ['countries', 'language', 'industry', 'seniority', 'arrangement', 'employment_type'])
    for values in expected.values(): strings(values, 100)
    with store.transaction() as state:
        receipts = [k for k,a in state['artifacts'].items() if a['kind'] == 'receipt'
                    and start <= timestamp(a['payload']['finished_at']) < end]
        report, deps = coverage_payload(state, receipts, start, end, expected)
        key = store.put(state, 'coverage-report', report, deps)
        return {'coverage': key, 'counts': report['counts'], 'segments': report['segments'], 'missing_segments': report['missing_segments']}


def define_cohort(store, row):
    fields(row, ['schema_version', 'name', 'protocols', 'basis', 'windows', 'reviewer', 'limitations'])
    require(row['schema_version'] == 1 and row['basis'] in ('capture', 'publication'), 'invalid cohort version/date basis')
    text(row['name']); text(row['reviewer']); strings(row['protocols'], 20); strings(row['limitations'])
    require(row['protocols'] and len(set(row['protocols'])) == len(row['protocols']) and row['limitations'], 'cohort protocols/limits required')
    require(isinstance(row['windows'], list) and len(row['windows']) == 2, 'two explicit equal windows required')
    parsed = []
    for w in row['windows']:
        fields(w, ['from', 'to']); a,b = timestamp(w['from']), timestamp(w['to'])
        require(a < b <= store.clock(), 'windows must be complete elapsed periods'); parsed.append((a,b))
    require(parsed[0][1] == parsed[1][0] and parsed[0][1]-parsed[0][0] == parsed[1][1]-parsed[1][0], 'windows must be adjacent and equal duration')
    with store.transaction() as state:
        for key in row['protocols']:
            p = item(state, key, 'collection-protocol')
            require((parsed[0][1]-parsed[0][0]).total_seconds() % p['cadence_seconds'] == 0, 'window must cover whole cadence slots')
        return {'cohort': store.put(state, 'cohort', row, row['protocols'])}


def compare(store, key):
    with store.transaction() as state:
        cohort = item(state, key, 'cohort')
        protocols = {k:item(state,k,'collection-protocol') for k in cohort['protocols']}
        assessments = {k:a['payload'] for k,a in state['artifacts'].items() if a['kind'] == 'capture-assessment'}
        reports, problems, deps, extras = [], [], [key], []
        for wi, window in enumerate(cohort['windows']):
            start,end = timestamp(window['from']), timestamp(window['to'])
            window_receipts = {k:a['payload'] for k,a in state['artifacts'].items() if a['kind'] == 'receipt'
                               and start <= timestamp(a['payload']['finished_at']) < end}
            chosen = set()
            for pk,p in protocols.items():
                slots = int((end-start).total_seconds() // p['cadence_seconds']); occupied = Counter()
                relevant = {k:r for k,r in window_receipts.items() if r['source'] == p['source']}
                for rk,r in relevant.items():
                    matches = [(ak,a) for ak,a in assessments.items() if a['receipt'] == rk and a['protocol'] == pk]
                    # Unknown/unassessed or changed queries for a selected source
                    # are disclosed and make a comparison insufficient, not silently dropped.
                    if not matches and any(a['receipt'] == rk and a['protocol'] in protocols for a in assessments.values()):
                        continue
                    if not matches:
                        problems.append(f'window-{wi+1}: unassessed or changed collection for {p["source"]}')
                        deps.append(rk); continue
                    ak,a = matches[0]; deps.append(ak); chosen.add(rk)
                    if not (a['fresh'] and a['terminal'] and not a['changes'] and r['completeness'] == 'complete-request'):
                        problems.append(f'window-{wi+1}: partial, stale, failed or changed capture')
                    if timestamp(r['started_at']) < start: problems.append(f'window-{wi+1}: capture crosses window boundary')
                    elapsed = (timestamp(r['finished_at'])-start).total_seconds()
                    slot = int(elapsed // p['cadence_seconds']); occupied[slot] += 1
                    offset = elapsed % p['cadence_seconds']
                    if abs(offset - p.get('capture_offset_seconds', 0)) > p.get('capture_tolerance_seconds', 300):
                        problems.append(f'window-{wi+1}: capture timing differs from frozen schedule')
                    actual = sum(1 for v in state['artifacts'].values() if v['kind'] == 'observation' and v['payload']['receipt'] == rk)
                    if actual != sum(page['returned'] for page in r['pages']): problems.append(f'window-{wi+1}: withdrawn or missing captured observations')
                if len(occupied) != slots or any(v != 1 for v in occupied.values()):
                    problems.append(f'window-{wi+1}: missing or duplicate cadence slots for {p["source"]}')
            sources = {p['source'] for p in protocols.values()}
            extra = [k for k,r in window_receipts.items() if r['source'] not in sources]
            extras.append({'receipts': extra, 'sources': sorted({window_receipts[k]['source'] for k in extra})})
            report, used = coverage_payload(state, chosen, start, end, {}, cohort['basis'])
            deps.extend(used); deps.extend(extra)
            if cohort['basis'] == 'publication' and any(a['kind'] == 'observation' and a['payload']['receipt'] in chosen
                                                        and a['payload']['posted_at'] is None for a in state['artifacts'].values()):
                problems.append(f'window-{wi+1}: publication dates missing; discovery is not substituted')
            reports.append(report)
        comparable = not problems
        capabilities_ok = comparable and reports[0]['analysis_versions'] == reports[1]['analysis_versions'] and len(reports[0]['analysis_versions']) == 1
        capabilities_ok &= not any(r['analysis_version_unknown'] for r in reports)
        capabilities_ok &= all(r['counts']['analyzed_latest_observations'] == r['counts']['source_listings'] for r in reports)
        result = {'schema_version': 1, 'cohort': key, 'comparison_version': digest(Path(__file__).read_text()), 'status': 'comparable-sample' if comparable else 'insufficient-longitudinal-evidence',
                  'basis': cohort['basis'], 'protocols': protocols, 'target_window_days': 28, 'windows': reports, 'collection_issues': sorted(set(problems)), 'expanded_coverage': extras,
                  'opening_delta': reports[1]['counts']['deduplicated_openings'] - reports[0]['counts']['deduplicated_openings'] if comparable else None,
                  'capability_comparison': 'comparable-within-sample' if capabilities_ok else 'insufficient-or-changed-analysis',
                  'capability_deltas': {c: reports[1]['capabilities'].get(c,{}).get('openings',0) - reports[0]['capabilities'].get(c,{}).get('openings',0)
                                         for c in TAXONOMY['capabilities']} if capabilities_ok else None,
                  'limitations': ['Counts are openings observed in each window, not new hires or worldwide demand growth.',
                                  'Equal sampling protocols do not remove provider/employer selection bias.',
                                  'Missing a listing in a sample is not evidence of closure.', *cohort['limitations']]}
        result['markdown'] = '# Stable cohort comparison\n\n' + result['status'] + '\n\n'
        result['markdown'] += 'Opening delta: ' + str(result['opening_delta']) + '\n\n'
        result['markdown'] += 'Capability comparison: ' + result['capability_comparison'] + '\n\n'
        for n,report in enumerate(reports,1):
            result['markdown'] += '## Window ' + str(n) + '\n\n' + report['markdown'] + '\n'
        result['markdown'] += 'Collection issues and added sources (see exact JSON):\n\n' + json.dumps({'issues':result['collection_issues'],'expanded_sources':[e['sources'] for e in extras]}, ensure_ascii=True).replace('<','&lt;').replace('[','&#91;') + '\n\n'
        result['markdown'] += '\n'.join(result['limitations'])
        result_id = store.put(state, 'cohort-comparison', result, deps)
        return {'comparison': result_id, 'status': result['status'], 'opening_delta': result['opening_delta'], 'issues': result['collection_issues']}


def vacancy_view(store, protocol_id):
    """Authoritative board observations only; feed disappearance cannot close jobs."""
    with store.transaction() as state:
        p = item(state, protocol_id, 'collection-protocol')
        captures = [(k,a['payload']) for k,a in state['artifacts'].items() if a['kind'] == 'capture-assessment'
                    and a['payload']['protocol'] == protocol_id]
        receipt_ids = {a['receipt'] for _,a in captures}
        observations = {k:a['payload'] for k,a in state['artifacts'].items() if a['kind'] == 'observation'
                        and a['payload']['receipt'] in receipt_ids}
        grouped = {}
        for k,row in observations.items(): grouped.setdefault(row['native_id'], []).append((k,row))
        eligible = []
        for _,assessment in captures:
            r = item(state, assessment['receipt'], 'receipt')
            count = sum(x['receipt'] == assessment['receipt'] for x in observations.values())
            if (p['scope'] == 'board-inventory' and not p['requested_filters'] and not p['effective_filters']
                and assessment['fresh'] and assessment['terminal'] and not assessment['changes']
                and r['completeness'] == 'complete-request' and count == sum(page['returned'] for page in r['pages'])):
                eligible.append((timestamp(r['finished_at']), assessment['receipt']))
        rows = []
        for native_id, history in sorted(grouped.items()):
            k,latest = max(history, key=lambda pair: timestamp(pair[1]['captured_at']))
            seen = timestamp(latest['captured_at']); status = latest['availability']
            absences = sorted((date,rid) for date,rid in eligible if date > seen and not any(
                x['receipt'] == rid and x['native_id'] == native_id for x in observations.values()))
            proof = []
            if absences and absences[-1][0] - absences[0][0] >= timedelta(hours=24):
                status = 'no-longer-listed'; proof = [absences[0][1], absences[-1][1]]
            elif store.clock() - seen > timedelta(seconds=p['cadence_seconds'] * 2) and status != 'closed': status = 'stale'
            elif status == 'open': status = 'last-seen-open'
            rows.append({'source': p['source'], 'native_id': native_id, 'latest_observation': k,
                         'last_seen_at': latest['captured_at'], 'status': status, 'absence_receipts': proof})
        latest_receipt = max((item(state,a['receipt'],'receipt') for _,a in captures),
                             key=lambda r: timestamp(r['finished_at']), default=None)
        source_health = 'unavailable' if latest_receipt and latest_receipt['completeness'] in ('failed', 'blocked') else (
            'partial' if latest_receipt and latest_receipt['completeness'] == 'partial' else 'observed-request-complete' if latest_receipt else 'unassessed')
        payload = {'schema_version': 1, 'source_health': source_health, 'protocol': protocol_id, 'as_of': store.clock().isoformat(), 'openings': rows,
                   'limitations': ['Source-level availability, not live verification; other aggregators cannot reopen this board view.',
                                   'Only two complete fresh unfiltered board absences >=24h apart establish no-longer-listed.',
                                   'Feed disappearance, outages, cap/304/cache or a failed detail never establish closure.']}
        key = store.put(state, 'vacancy-view', payload, [protocol_id, *observations, *[k for k,_ in captures]])
        return {'view': key, 'statuses': dict(Counter(r['status'] for r in rows))}
