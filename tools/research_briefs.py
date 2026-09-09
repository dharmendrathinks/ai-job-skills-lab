"""Four evidence-bound draft workflows; no combined score or automatic publication."""
import json
from datetime import datetime
from pathlib import Path
import subprocess

from tools.research_analysis import qualified
from tools.research_evidence import ROOT, TAXONOMY, EvidenceError, digest, fields, require, strings, text
from tools.research_runtime import CodexWorker
from tools.research_outcomes import evidence_basis, check_memory, memory, outcome_memory, artifact

PROMPT = ROOT / 'docs/research/prompts/brief-v1.md'
SECTIONS = {
    'learning': ('direction_fit', 'practice', 'completion_checks', 'known_skill_deepening'),
    'project': ('problem_user', 'deliverable', 'architecture_interfaces', 'tradeoffs', 'tests_baseline',
                'benchmarks_heldout', 'failure_scenarios', 'demonstrates', 'does_not_demonstrate',
                'effort', 'hardware_cost', 'maintenance_license'),
    'product': ('user_buyer', 'workflow_workaround', 'suspected_pain', 'differentiation',
                'job_evidence_limits', 'validation_plan', 'success_criteria', 'rejection_criteria', 'unresolved_risks'),
    'youtube': ('problem', 'build_architecture', 'tradeoffs', 'baseline_measurements',
                'possible_failure_surprise', 'possible_fixes', 'useful_artifact', 'limitations', 'audience_validation'),
}
DIMENSIONS = ('learning_value', 'opensource_usefulness', 'commercial_validation', 'video_suitability', 'evidence_strength', 'feasibility')


def obj(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


def array(items):
    return {'type': 'array', 'items': items}


STRING = {'type': 'string'}
STRINGS = array(STRING)


def schema(kind, data=None):
    require(kind in SECTIONS, 'unknown brief type')
    analysis_id = {'type': 'string', 'description': 'Existing analysis artifact ID; never prose or a summary.'}
    context_id = {'type': 'string', 'description': 'Existing context artifact ID; never a repository name or prose.'}
    if data is not None:
        analysis_id['enum'] = list(data['analyses']) or ['unavailable']
        context_id['enum'] = list(data['contexts']) or ['unavailable']
    return obj({'title': STRING, 'disposition': {'type': 'string', 'enum': ['propose', 'contribute', 'no-project', 'insufficient-evidence']},
        'capabilities': array({'type': 'string', 'enum': TAXONOMY['capabilities']}),
        'prerequisites': array({'type': 'string', 'enum': TAXONOMY['capabilities']}),
        'market_claims': array(obj({'analysis': analysis_id, 'quote': STRING})),
        'context_claims': array(obj({'context': context_id, 'quote': STRING, 'relation': {'type': 'string', 'enum': ['supports', 'contradicts']}})),
        'alternatives': array(obj({'context': context_id, 'reason': STRING})),
        'sections': obj({name: STRING for name in SECTIONS[kind]}),
        'judgments': obj({name: obj({'rating': {'type': 'string', 'enum': ['unknown', 'low', 'medium', 'high']}, 'reason': STRING}) for name in DIMENSIONS}),
        'limitations': STRINGS})


def hosted_eligible(state, ids):
    seen, todo = set(), list(ids)
    policies = []
    while todo:
        key = todo.pop()
        require(key in state['artifacts'], 'brief input unavailable or withdrawn')
        if key in seen:
            continue
        seen.add(key)
        a = state['artifacts'][key]
        if a['kind'] == 'policy':
            policies.append(a['payload'])
        todo.extend(a['dependencies'])
    require(policies and all(p['hosted_disclosure'] and p.get('hosted_retention') ==
                            'provider-managed-no-deletion-deadline' for p in policies), 'brief inputs lack compatible hosted permission')


def inputs(state, snapshot, contexts, profile, now):
    snap = state['artifacts'].get(snapshot)
    require(snap and snap['kind'] in ('snapshot', 'coverage-report'), 'market snapshot unavailable')
    ids = [snapshot, *contexts] + ([profile] if profile else [])
    hosted_eligible(state, ids)
    analyses = {}
    for key in snap['dependencies']:
        a = state['artifacts'][key]
        if a['kind'] == 'analysis' and (a['payload']['method'] != 'codex-extraction' or a['payload'].get('ai_domain') == 'in-domain'):
            analyses[key] = a['payload']
    context_map = {}
    identities = set()
    for key in contexts:
        a = state['artifacts'].get(key)
        require(a and a['kind'] == 'context', 'context unavailable')
        row = a['payload']
        # Repeated imports are not independent corroboration.
        if row['evidence_identity'] not in identities:
            context_map[key] = row
            identities.add(row['evidence_identity'])
    profile_data = None
    if profile:
        a = state['artifacts'].get(profile)
        require(a and a['kind'] == 'research-profile', 'reviewed research profile required')
        profile_data = a['payload']
    return {'snapshot': snapshot, 'as_of': now.date().isoformat(), 'discussion_window_days': 90,
            'counts': snap['payload']['counts'], 'capabilities': snap['payload']['capabilities'],
            'analyses': analyses, 'contexts': context_map, 'profile': profile_data,
            'limitations': snap['payload']['limitations'],
            'coverage': {k:snap['payload'][k] for k in ('period','segments','missing_segments','source_health','analysis_versions')}
                        if snap['kind'] == 'coverage-report' else None}


def validate(output, kind, data):
    fields(output, list(schema(kind)['properties']))
    text(output['title'], 200)
    require(output['disposition'] in ('propose', 'contribute', 'no-project', 'insufficient-evidence'), 'unknown disposition')
    require(kind == 'project' or output['disposition'] in ('propose', 'insufficient-evidence'), 'project-only disposition')
    strings(output['capabilities']); strings(output['prerequisites']); strings(output['limitations'])
    require(set(output['capabilities']) <= set(data['capabilities']) and set(output['prerequisites']) <= set(TAXONOMY['capabilities']),
            'unsupported capability or prerequisite')
    require(isinstance(output['market_claims'], list) and len(output['market_claims']) <= 20, 'market claim budget exceeded')
    for claim in output['market_claims']:
        fields(claim, ['analysis', 'quote'])
        a = data['analyses'].get(claim['analysis'])
        require(a and any(claim['quote'] == c['quote'] for c in a['claims']), 'market claim must copy a validated source statement')
    require(output['market_claims'] or output['disposition'] == 'insufficient-evidence', 'brief needs job evidence or abstention')
    require(isinstance(output['context_claims'], list) and len(output['context_claims']) <= 20, 'context claim budget exceeded')
    for claim in output['context_claims']:
        fields(claim, ['context', 'quote', 'relation'])
        row = data['contexts'].get(claim['context'])
        text(claim['quote'], 2000)
        require(row and row['content'] and claim['quote'] in row['content'] and
                row['observation_basis'] != 'imported-assessment', 'context quote must be inspected source evidence')
        require(claim['relation'] in ('supports', 'contradicts'), 'invalid evidence relationship')
    require(isinstance(output['alternatives'], list) and len(output['alternatives']) <= 10, 'alternative budget exceeded')
    for alt in output['alternatives']:
        fields(alt, ['context', 'reason']); text(alt['reason'], 3000)
        row = data['contexts'].get(alt['context'])
        require(row and row['content'] and row['evidence_type'] in ('repository', 'product') and row['observation_basis'] == 'inspected',
                'alternative needs inspected repository/product evidence')
    if kind == 'project' and output['disposition'] in ('propose', 'contribute'):
        require(output['alternatives'] and any(data['contexts'][a['context']]['evidence_type'] == 'repository' for a in output['alternatives']),
                'project proposal needs inspected repository alternatives; abstain if missing')
    fields(output['sections'], SECTIONS[kind])
    for value in output['sections'].values():
        text(value, 3500)
    fields(output['judgments'], DIMENSIONS)
    for judgment in output['judgments'].values():
        fields(judgment, ['rating', 'reason'])
        require(judgment['rating'] in ('unknown', 'low', 'medium', 'high'), 'no numeric or composite opportunity score')
        text(judgment['reason'], 2000)
    # Domain-specific support gates; generation prose remains a proposal for human review.
    types = {r['evidence_type'] for r in data['contexts'].values() if r['content'] and r['observation_basis'] != 'imported-assessment'}
    if not types.intersection({'product', 'problem'}):
        require(output['judgments']['commercial_validation']['rating'] == 'unknown', 'commercial assessment needs non-job problem evidence')
    def recent(row):
        if not row['original_date']:
            return False
        original = datetime.fromisoformat(row['original_date'].replace('Z', '+00:00')).date()
        return 0 <= (datetime.fromisoformat(data['as_of']).date() - original).days <= data['discussion_window_days']
    dated = any(r['evidence_type'] in ('discussion', 'trend') and recent(r) and r['content']
                and r['observation_basis'] != 'imported-assessment' for r in data['contexts'].values())
    if not dated:
        require(output['judgments']['video_suitability']['rating'] == 'unknown', 'video judgment needs dated external evidence')
    require(output['limitations'], 'brief must disclose evidence limitations')
    return output


def generate(store, kind, snapshot, contexts=(), profile=None, *, refresh=False, worker_factory=CodexWorker, reconsideration=None, exchanges=()):
    require(kind in SECTIONS and len(contexts) <= 10 and len(exchanges) <= 10, 'invalid brief request')
    with store.transaction() as state:
        data = inputs(state, snapshot, contexts, profile, store.clock())
        data['interchange_assessments'] = {k: artifact(state, k, ('interchange-item',)) for k in exchanges}
        if exchanges: hosted_eligible(state, exchanges)
        basis = evidence_basis(state, snapshot, contexts)
        check_memory(state, kind, basis, contexts, store.clock(), reconsideration=reconsideration)
        feedback = memory(state, kind)
        work_memory = outcome_memory(state, kind)
        require(len(feedback) + len(work_memory) <= 100, 'memory review budget exceeded; no silent history truncation')
        memory_deps = [r['id'] for r in [*feedback, *work_memory]] + ([reconsideration] if reconsideration else [])
        if memory_deps or exchanges: hosted_eligible(state, [*memory_deps, *exchanges])
        data['recommendation_memory'] = feedback
        data['outcome_memory'] = work_memory
        if reconsideration:
            rec = artifact(state, reconsideration, ('reconsideration',))
            data['reconsideration'] = {k: rec[k] for k in ('brief', 'reason', 'evidence')}
        qualification, identity = qualified(state)
        versions = {'schema': 'brief/1', 'prompt': digest(PROMPT.read_text()), 'runtime': identity,
                    'validator': digest(Path(__file__).read_text()), 'output_schema': digest(schema(kind, data))}
        cache_key = digest([kind, data, versions])
        cached = [k for k,a in state['artifacts'].items() if a['kind'] == 'brief' and a['payload'].get('cache_key') == cache_key]
        if cached and not refresh:
            return {'brief': sorted(cached)[-1], 'cache_hit': True}
    prompt = PROMPT.read_text() + '\nRequested workflow: ' + kind + '\nUntrusted evidence JSON:\n' + json.dumps(data, ensure_ascii=False)
    # CodexWorker applies its existing input/output/turn budgets and empty registry.
    try:
        with worker_factory(store.home) as worker:
            with store.transaction() as state:
                inputs(state, snapshot, contexts, profile, store.clock()); qualified(state)
                require(memory(state, kind) == feedback and outcome_memory(state, kind) == work_memory, 'feedback changed before invocation')
                if memory_deps or exchanges: hosted_eligible(state, [*memory_deps, *exchanges])
            response, metadata = worker.run(prompt, schema(kind, data))
    except (ValueError, OSError, subprocess.SubprocessError):
        with store.transaction() as state:
            deps = [snapshot, *contexts, qualification, *memory_deps, *exchanges] + ([profile] if profile else [])
            if all(key in state['artifacts'] for key in deps):
                store.put(state, 'brief-failure', {'schema_version': 1, 'kind': kind, 'versions': versions,
                          'recorded_at': store.clock().isoformat(), 'status': 'deferred',
                          'reason': 'Runtime, quota or input lifecycle failed; no automatic retry or paid fallback.'}, deps)
        raise
    with store.transaction() as state:
        current = inputs(state, snapshot, contexts, profile, store.clock()); qualified(state)
        require(memory(state, kind) == feedback and outcome_memory(state, kind) == work_memory, 'feedback changed during generation; retry review')
        if memory_deps or exchanges: hosted_eligible(state, [*memory_deps, *exchanges])
        error = None
        try:
            output = validate(response, kind, current)
            check_memory(state, kind, basis, contexts, store.clock(), output, reconsideration)
        except EvidenceError as exc:
            error = str(exc)
        deps = [snapshot, *contexts, qualification, *memory_deps, *exchanges] + ([profile] if profile else [])
        execution = store.put(state, 'brief-execution', {'schema_version': 1, 'metadata': metadata, 'versions': versions,
                                  'recorded_at': store.clock().isoformat(), 'response': response,
                                  'status': 'rejected' if error else 'validated', 'reason': error}, deps)
        if not error:
            record = {'schema_version': 1, 'kind': kind, 'status': 'draft-human-review', 'cache_key': cache_key,
                  'versions': versions, 'snapshot': snapshot, 'contexts': list(contexts), 'profile': profile,
                  'execution': execution, 'proposal': output, 'evidence_basis': basis, 'exchanges': list(exchanges),
                  'revises': artifact(state, reconsideration, ('reconsideration',))['brief'] if reconsideration else None,
                  'profile_evidence': current['profile'],
                  'evidence_limits': [*current['limitations'], *[x for r in current['contexts'].values() for x in r['limitations']]],
                  'notice': 'Sections and judgments are model proposals, not observed outcomes or demonstrated demand.'}
            old = artifact(state, record['revises'], ('brief',)) if record['revises'] else None
            record['recommendation_id'] = old.get('recommendation_id', record['revises']) if old else digest(['recommendation/1', kind, output['title'], basis])
            record['revision'] = old.get('revision', 1) + 1 if old else 1
            record['markdown'] = render(record)
            key = store.put(state, 'brief', record, [execution])
    if error:
        raise EvidenceError(error)
    return {'brief': key, 'cache_hit': False, 'status': 'draft-human-review'}


def render(record):
    # Render as quoted plain text; never execute or auto-open model content/links.
    def safe(value):
        return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('`', '&#96;').replace('[', '&#91;').replace(']', '&#93;')
    p = record['proposal']
    lines = ['# ' + safe(p['title']), '', record['status'], '', record['notice'], '', 'Disposition: ' + p['disposition'],
             'Snapshot: ' + record['snapshot'], 'Capabilities: ' + ', '.join(p['capabilities']),
             'Prerequisites (proposed): ' + ', '.join(p['prerequisites']), '']
    for name, value in p['sections'].items():
        lines += ['## ' + name.replace('_', ' '), '', '> ' + safe(value).replace('\n', '\n> '), '']
    for name, judgment in p['judgments'].items():
        lines += ['- ' + name + ': ' + judgment['rating'] + ' — ' + safe(judgment['reason'])]
    lines += ['', 'Evidence IDs and exact source statements are in the same artifact JSON.', '']
    lines += ['- ' + safe(x) for x in [*p['limitations'], *record['evidence_limits']]]
    return '\n'.join(lines) + '\n'
