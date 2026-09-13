"""Fine-grained skill evidence and deterministic sampled-window projections.

Original words remain evidence. A catalog match is an exact reviewed alias, not
semantic similarity; new phrases remain separate until an explicit mapping review.
"""
from collections import Counter
from datetime import timedelta
import json
import re
import unicodedata

from tools.research_evidence import ROOT, digest, fields, require, text, timestamp, aggregate

CATALOG_PATH = ROOT / 'docs/research/skill-catalog-v1.json'
KINDS = ('practice', 'knowledge', 'technology', 'other-requirement')
MODALITIES = ('required', 'preferred', 'unspecified')


def normalized(value):
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


def catalog():
    row = json.loads(CATALOG_PATH.read_text())
    require(row['schema_version'] == 1, 'unsupported skill catalog')
    ids, aliases = set(), set()
    for skill in row['skills']:
        fields(skill, ['id', 'name', 'kind', 'aliases', 'definition', 'capabilities'])
        require(skill['id'] not in ids and skill['kind'] in KINDS, 'duplicate skill or invalid kind')
        ids.add(skill['id'])
        for alias in {normalized(s) for s in [skill['name'], *skill['aliases']]}:
            require(alias not in aliases, 'ambiguous catalog alias')
            aliases.add(alias)
    return row


def mention_schema():
    return {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False,
        'properties': {'surface': {'type': 'string'}, 'quote': {'type': 'string'},
                       'section_context': {'type': 'string'},
                       'kind': {'type': 'string', 'enum': list(KINDS)},
                       'modality': {'type': 'string', 'enum': list(MODALITIES)}},
        'required': ['surface', 'quote', 'section_context', 'kind', 'modality']}}


def normalize_mentions(mentions, description):
    require(isinstance(mentions, list) and len(mentions) <= 150, 'skill mention budget exceeded')
    cat = catalog()
    aliases = {normalized(alias): s for s in cat['skills'] for alias in [s['name'], *s['aliases']]}
    result = []
    for m in mentions:
        fields(m, ['surface', 'quote', 'section_context', 'kind', 'modality'])
        text(m['surface'], 180); text(m['quote'], 2000)
        require(description and m['quote'] in description and m['surface'] in m['quote'], 'skill must cite exact captured words')
        require(m['kind'] in KINDS and m['modality'] in MODALITIES, 'invalid skill classification')
        require(isinstance(m['section_context'], str) and len(m['section_context']) <= 2000 and
                (not m['section_context'] or m['section_context'] in description), 'section context must be exact')
        # These are employment/compensation terms, never technical skills. Other
        # semantic errors (including negation) also require held-out human review.
        require(normalized(m['surface']) not in {'h1b', 'h-1b', 'rsu', 'rsus', 'visa sponsorship'} or
                m['kind'] == 'other-requirement', 'employment terms are not technical skills')
        match = aliases.get(normalized(m['surface']))
        require(not match or match['kind'] == m['kind'], 'catalog kind conflicts with extraction')
        start = description.index(m['quote'])
        context_start = description.index(m['section_context']) if m['section_context'] else None
        result.append({**m, 'start': start, 'end': start + len(m['quote']),
                       'context_start': context_start,
                       'skill_id': match['id'] if match else 'unresolved-' + digest([m['kind'], normalized(m['surface'])])[:24],
                       'name': match['name'] if match else m['surface'],
                       'normalization': 'catalog-alias' if match else 'unresolved',
                       'catalog_revision': cat['revision']})
    return result


def latest_analysis(state, observations, *, detailed=False):
    chosen = {}
    for key, a in state['artifacts'].items():
        p = a['payload']
        if a['kind'] != 'analysis' or p['observation'] not in observations:
            continue
        if detailed and p.get('schema_version') != 2:
            continue
        old = chosen.get(p['observation'])
        if old is None or (timestamp(p['reviewed_at']), key) > (timestamp(state['artifacts'][old]['payload']['reviewed_at']), old):
            chosen[p['observation']] = key
    return chosen


def skill_payload(state, now, *, days=30, basis='capture', end=None, source=None, responsibility=None, receipt_ids=None):
    require(type(days) is int and 1 <= days <= 366 and basis in ('capture', 'publication'), 'invalid skill window')
    require(responsibility in (None, 'applied', 'mixed', 'research-heavy', 'unknown'), 'invalid responsibility slice')
    end = timestamp(end) if isinstance(end, str) else end or now
    require(end <= now, 'future skill window')
    start = end - timedelta(days=days)
    arts = state['artifacts']; scoped = {}; missing_dates = 0
    # Filter revisions BEFORE choosing latest in the window. New captures must
    # not retroactively replace historical-window evidence.
    for key, a in arts.items():
        if a['kind'] == 'observation' and (not source or a['payload']['source'] == source) and (receipt_ids is None or a['payload']['receipt'] in receipt_ids):
            p = a['payload']; date = p['captured_at'] if basis == 'capture' else p['posted_at']
            if date is None: missing_dates += 1
            if date is not None and start <= timestamp(date) < end and timestamp(p['captured_at']) < end:
                scoped[key] = a
    selected = set(scoped)
    for key, a in arts.items():
        if a['kind'] == 'analysis' and a['payload']['observation'] in selected:
            scoped[key] = a
        if a['kind'] == 'receipt' and any(arts[o]['payload']['receipt'] == key for o in selected):
            scoped[key] = a
    # Preserve reviewed employer/requisition identity without name-only merging.
    for a in arts.values():
        if a['kind'] == 'board-link' and a['payload']['observation'] in selected:
            p = a['payload']; board = arts[p['board']]['payload']; o = p['observation']
            scoped[o] = {**scoped[o], 'payload': {**scoped[o]['payload'], 'employer_domain': board['employer_domain'],
                                                'employer_requisition': p['employer_requisition']}}
    view = {**state, 'artifacts': scoped}
    broad, _ = aggregate(view)
    observations = {o for g in broad['openings'] for o in g['observations']}
    detailed = latest_analysis(state, observations, detailed=True)
    latest = latest_analysis(state, observations)
    mappings = {}
    for key, a in sorted(arts.items(), key=lambda pair: (pair[1]['payload'].get('reviewed_at', ''), pair[0])):
        if a['kind'] == 'skill-mapping': mappings[a['payload']['from_id']] = (key, a['payload']['to_id'])
    cat = {s['id']: s for s in catalog()['skills']}
    aliases = {(normalized(alias), s['kind']): s['id'] for s in cat.values() for alias in [s['name'], *s['aliases']]}
    skills = {}; denominator = set(); analyzed = set(); classified = Counter(); dependencies = set(scoped)
    evidence = {}; opening_skills = {}
    versions = set(); missing_description = 0
    for group in broad['openings']:
        opening = group['opening']; opening_skills[opening] = set()
        rows = [scoped[o]['payload'] for o in group['observations']]
        if all(r['description'] is None for r in rows): missing_description += 1
        for oid in group['observations']:
            if oid not in detailed: continue
            aid = detailed[oid]; a = arts[aid]['payload']; analyzed.add(opening)
            classified[a.get('ai_domain', 'unknown')] += 1
            if a.get('ai_domain') != 'in-domain' or (responsibility and a['responsibility_class'] != responsibility): continue
            denominator.add(opening)
            execution = arts.get(a.get('execution'), {}).get('payload', {})
            versions.add(digest(execution.get('versions', {'unknown': True})))
            row = scoped[oid]['payload']
            for index, m in enumerate(a['skill_mentions']):
                if m['kind'] == 'other-requirement': continue
                mid = m['skill_id']; mapping = mappings.get(mid)
                if mapping:
                    dependencies.add(mapping[0]); mid = mapping[1]
                projected = None
                if not mapping and m['normalization'] == 'unresolved':
                    projected = aliases.get((normalized(m['surface']), m['kind']))
                    if projected: mid = projected
                entry = cat.get(mid)
                s = skills.setdefault(mid, {'id': mid, 'name': entry['name'] if entry else m['name'],
                    'kind': m['kind'], 'normalization': 'reviewed-mapping' if mapping else 'catalog-projection' if projected else m['normalization'],
                    'definition': entry['definition'] if entry else 'Source wording; normalization needs review.',
                    'capabilities': entry['capabilities'] if entry else [],
                    'openings': set(), 'reported_employers': set(), 'verified_employers': set(),
                    'modalities': {v: set() for v in MODALITIES}, 'evidence': [], 'cooccurs': Counter()})
                s['openings'].add(opening); s['modalities'][m['modality']].add(opening)
                if row['employer_name']: s['reported_employers'].add(normalized(row['employer_name']))
                if row['employer_domain']: s['verified_employers'].add(row['employer_domain'])
                eid = digest([aid, index]); s['evidence'].append(eid); opening_skills[opening].add(mid)
                evidence[eid] = {'analysis': aid, 'observation': oid, 'opening': opening, 'skill': mid,
                    'quote': m['quote'], 'surface': m['surface'], 'original_skill_id': m['skill_id'],
                    'original_catalog_revision': m['catalog_revision'], 'section_context': m['section_context'],
                    'modality': m['modality'], 'source': row['source'], 'url': row['url'],
                    'title': row['title'], 'employer': row['employer_name'], 'captured_at': row['captured_at'],
                    'posted_at': row['posted_at'], 'responsibility_class': a['responsibility_class']}
    for group_skills in opening_skills.values():
        for sid in group_skills: skills[sid]['cooccurs'].update(group_skills - {sid})
    for s in skills.values():
        for field in ('openings', 'reported_employers', 'verified_employers'): s[field] = len(s[field])
        s['modalities'] = {k: len(v) for k, v in s['modalities'].items()}
        s['share'] = s['openings'] / len(denominator) if denominator else None
        s['cooccurs'] = dict(sorted(s['cooccurs'].items()))
    # All receipts in the time window matter, including failures and empty runs.
    receipts = {k:a['payload'] for k,a in arts.items() if a['kind'] == 'receipt' and
                (not source or a['payload']['source'] == source) and (receipt_ids is None or k in receipt_ids) and start <= timestamp(a['payload']['finished_at']) < end}
    dependencies.update(receipts)
    dependencies.update(k for k,a in arts.items() if a['kind'] == 'board-link' and a['payload']['observation'] in selected)
    collection_days = sorted({timestamp(r['finished_at']).date().isoformat() for r in receipts.values()})
    counts = {'openings': len(broad['openings']), 'analysed_openings': len(analyzed),
              'in_domain_denominator': len(denominator), 'pending_or_legacy_openings': len(broad['openings']) - len(analyzed),
              'legacy_analysed_observations': len(set(latest) - set(detailed)), 'missing_descriptions': missing_description,
              'missing_date_revisions': missing_dates, 'classified_observations': dict(classified)}
    failures = {a['payload']['input_revision'] for a in arts.values() if a['kind'] == 'execution' and
                a['payload']['status'] != 'validated' and a['payload']['input_revision'] in observations}
    counts['failed_or_deferred_observations'] = len(failures - set(detailed))
    dependencies.update(k for k,a in arts.items() if a['kind'] == 'execution' and a['payload']['input_revision'] in failures)
    return {'schema_version': 1, 'catalog_revision': catalog()['revision'], 'catalog_digest': digest(catalog()),
            'period': {'from': start.isoformat(), 'to': end.isoformat(), 'basis': basis, 'end_exclusive': True},
            'filters': {'source': source, 'responsibility': responsibility}, 'counts': counts,
            'collection_days': collection_days, 'receipts': receipts, 'analysis_versions': sorted(versions),
            'skills': dict(sorted(skills.items(), key=lambda kv: (-kv[1]['openings'], kv[1]['name']))), 'evidence': evidence,
            'limitations': ['Observed sample, not worldwide demand or verified active vacancies.',
                'Denominator is detailed, in-domain analysed openings in this slice; missing analysis is unknown.',
                'Required/preferred/unspecified counts can overlap; total counts each opening once.',
                'Reported employer names are not verified identities. Normalized aliases do not prove semantic correctness.',
                'Collection gaps, partial receipts and extraction versions prevent unqualified trend claims.',
                'Exact spans pass deterministic validation; human semantic review remains separate.',
                'This new snapshot projects exact typed aliases through its recorded catalog revision; original analyses and prior snapshots are unchanged.']}, sorted(dependencies)


def snapshot(store, **kwargs):
    with store.transaction() as state:
        require('domain_pack' not in state, 'fine-grained AI catalog is not qualified for another domain')
        payload, deps = skill_payload(state, store.clock(), **kwargs)
        key = store.put(state, 'skill-snapshot', payload, deps)
        return {'snapshot': key, 'counts': payload['counts']}


def review_mapping(store, row):
    fields(row, ['schema_version', 'from_id', 'to_id', 'analyses', 'reviewer', 'reason'])
    require(row['schema_version'] == 1 and row['analyses'], 'mapping requires reviewed source analyses')
    text(row['reviewer']); text(row['reason'])
    target = next((s for s in catalog()['skills'] if s['id'] == row['to_id']), None)
    require(target, 'unknown target skill')
    with store.transaction() as state:
        for aid in row['analyses']:
            a = state['artifacts'].get(aid)
            require(a and a['kind'] == 'analysis', 'analysis unavailable')
            require(any(m['skill_id'] == row['from_id'] and m['kind'] == target['kind'] for m in a['payload'].get('skill_mentions', [])),
                    'mapping needs matching source words and kind')
        key = store.put(state, 'skill-mapping', {**row, 'reviewed_at': store.clock().isoformat(),
                        'catalog_digest': digest(catalog())}, row['analyses'])
        return {'mapping': key}


def history_payload(state, now, days=30, *, basis='capture', comparison=None):
    """Derive skill change only from the same frozen receipts checked by P5."""
    from tools.research_coverage import analysis_version
    issues = []; dependencies = []; windows = []
    if comparison:
        basis = comparison['basis']
        if comparison['status'] != 'comparable-sample': issues.extend(comparison['collection_issues'])
        if comparison['capability_comparison'] != 'comparable-within-sample': issues.append('Missing or changed analysis prevents comparison.')
        periods = [w['period'] for w in comparison['windows']]
        protocol_ids = set(comparison['protocols'])
    else:
        periods = [{'to':(now-timedelta(days=days*offset)).isoformat()} for offset in (1,0)]
        protocol_ids = None
        issues.append('No reviewed comparable cohort; windows are descriptive observations only.')
    for period in periods:
        window_days = days
        selected = None
        if comparison:
            duration = timestamp(period['to']) - timestamp(period['from'])
            require(duration.total_seconds() % 86400 == 0, 'skill windows must cover whole days')
            window_days = duration.days
            selected = {a['payload']['receipt'] for a in state['artifacts'].values()
                        if a['kind'] == 'capture-assessment' and a['payload']['protocol'] in protocol_ids}
        window, deps = skill_payload(state, now, days=window_days, end=period['to'], basis=basis, receipt_ids=selected)
        windows.append(window); dependencies += deps
        if window['counts']['pending_or_legacy_openings']: issues.append('Detailed skill analysis does not cover every opening in both windows.')
        if not window['counts']['in_domain_denominator']: issues.append('Both windows need analysed in-domain openings.')
        analyses = {e['analysis'] for e in window['evidence'].values()}
        if any(analysis_version(state, state['artifacts'][a]['payload']) is None for a in analyses):
            issues.append('Extraction version is unknown.')
    if windows[0]['catalog_digest'] != windows[1]['catalog_digest'] or windows[0]['analysis_versions'] != windows[1]['analysis_versions']:
        issues.append('Catalog or extraction revisions differ between windows.')
    revisions = [{e['original_catalog_revision'] for e in w['evidence'].values()} for w in windows]
    if revisions[0] != revisions[1]: issues.append('Original normalization revisions differ between windows.')
    indicators = None
    if not issues:
        indicators = []
        for sid in sorted(set(windows[0]['skills']) | set(windows[1]['skills'])):
            previous, current = [w['skills'].get(sid) for w in windows]
            if any(s and s['normalization'] == 'unresolved' for s in (previous,current)): continue
            counts = [s['openings'] if s else 0 for s in (previous,current)]
            shares = [n / w['counts']['in_domain_denominator'] for n,w in zip(counts,windows)]
            indicators.append({'skill':sid, 'name':(current or previous)['name'], 'previous':counts[0],
                'current':counts[1], 'percentage_points':(shares[1]-shares[0])*100})
        indicators.sort(key=lambda s:(-s['percentage_points'],s['name'].casefold()))
    return {'schema_version':2,'windows':windows,'basis':basis,'change_indicators':indicators,
            'status':'comparable-within-sample' if indicators is not None else 'descriptive-observations-only',
            'issues':sorted(set(issues)),
            'limitation':'Sample observations, not worldwide demand or hiring. Unreviewed terms receive no change indicators.' if indicators is not None else
                'Collection or analysis is not comparable; no growth or decline is inferred.'}, sorted(set(dependencies))


def monthly(store, days=30, *, basis='capture', cohort=None):
    from tools.research_outcomes import artifact
    comparison_id = None
    if cohort:
        from tools.research_coverage import compare
        comparison_id = compare(store, cohort)['comparison']
    with store.transaction() as state:
        require('domain_pack' not in state, 'skill history requires the AI workspace')
        comparison = artifact(state, comparison_id, ('cohort-comparison',)) if comparison_id else None
        payload, deps = history_payload(state, store.clock(), days, basis=basis, comparison=comparison)
        if comparison_id: deps.append(comparison_id); payload['comparison'] = comparison_id
        key = store.put(state, 'skill-history', payload, deps)
        return {'history':key, 'status':payload['status']}
