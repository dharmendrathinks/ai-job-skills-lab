"""Connected learn/build/teach drafts and independently sourced learning records."""
import json
import subprocess
from pathlib import Path

from tools.research_evidence import ROOT, aggregate, digest, fields, require, strings, text, timestamp, validate_policy
from tools.research_skills import catalog, skill_payload
from tools.research_briefs import obj, array, STRING, STRINGS, hosted_eligible
from tools.research_analysis import qualified
from tools.research_runtime import CodexWorker
from tools.research_outcomes import artifact

PATH_PROMPT = ROOT/'docs/research/prompts/learning-path-v1.md'
DEFAULT_PREFERENCES = {'direction': 'applied AI products', 'starting_point': 'software builder, growing AI',
                       'hours_per_week': [10, 15], 'hardware': 'Not specified; confirm before choosing a model runtime',
                       'additional_spending_inr': 0}


def model_operation(store, kind, data, schema, prompt, deps, validator, *, worker_factory=CodexWorker, retry_review=None):
    """Same qualified worker; durable intent, lifecycle rechecks and no automatic retry."""
    with store.transaction() as state:
        hosted_eligible(state, deps); qid, identity = qualified(state)
        versions = {'schema': digest(schema), 'prompt': digest(prompt), 'runtime': identity,
                    'validator': digest(Path(__file__).read_text())}
        fingerprint = digest([kind, data, versions])
        cached = [k for k,a in state['artifacts'].items() if a['kind'] == kind and a['payload'].get('cache_key') == fingerprint]
        if cached: return {kind: sorted(cached)[-1], 'cache_hit': True}
        attempts = [k for k,a in state['artifacts'].items() if a['kind'] == 'learning-intent' and a['payload']['cache_key'] == fingerprint]
        if attempts:
            require(retry_review, 'prior failed or ambiguous model intent requires explicit retry review')
            text(retry_review)
        intent = store.put(state, 'learning-intent', {'schema_version': 1, 'kind': kind, 'cache_key': fingerprint,
                            'created_at': store.clock().isoformat(), 'retry_review': retry_review,
                            'attempt_number': len(attempts) + 1, 'versions': versions, 'input': data}, [*deps, qid])
    output = None; metadata = {}; stage = 'runtime'
    try:
        worker = worker_factory(store.home)
        if kind in ('learning-path', 'learning-comparison') and isinstance(worker, CodexWorker): worker.timeout = 240
        with worker:
            with store.transaction() as state:
                artifact(state, intent, ('learning-intent',)); hosted_eligible(state, deps)
                require(qualified(state)[1] == identity, 'runtime changed')
            output, metadata = worker.run(prompt + '\nUntrusted input JSON:\n' + json.dumps(data, ensure_ascii=False), schema)
        stage = 'validation'
        with store.transaction() as state:
            artifact(state, intent, ('learning-intent',)); hosted_eligible(state, deps)
            require(qualified(state)[1] == identity, 'runtime changed')
            if kind in ('learning-path', 'curriculum-adaptation'):
                require([p for _,p in path_decisions(state).values()] == data['decision_memory'], 'learning decisions changed during generation')
            validated = validator(output, data)
            key = store.put(state, kind, {'schema_version': 1, 'created_at': store.clock().isoformat(),
                            'cache_key': fingerprint, 'versions': versions, 'metadata': metadata,
                            'status': 'draft-human-review', **validated}, [intent])
            return {kind: key, 'cache_hit': False, 'status': 'draft-human-review'}
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as exc:
        with store.transaction() as state:
            if intent in state['artifacts']:
                store.put(state, 'learning-failure', {'schema_version': 1, 'failure_stage': stage,
                          'diagnostic_code': 'runtime-deadline' if str(exc) == 'runtime deadline exceeded; work deferred' else
                              ('validation' if stage == 'validation' else 'runtime-or-lifecycle'),
                          'response': output, 'metadata': metadata, 'recorded_at': store.clock().isoformat(),
                          'reason': 'Failed validation or runtime; explicit review required before retry.'}, [intent])
        raise


def path_schema(data):
    resource = {'type': 'string', 'enum': list(data['resources']) or ['unavailable']}
    skill = {'type': 'string', 'enum': list(data['skills'])}
    return obj({'title': STRING, 'experiment': STRING, 'why_now': STRING,
        'disposition': {'type': 'string', 'enum': ['propose', 'insufficient-evidence']},
        'skills': array(skill), 'prerequisites': STRINGS, 'assumptions': STRINGS,
        'market_evidence': array({'type': 'string', 'enum': list(data['evidence'])}),
        'milestones': array(obj({'id': STRING, 'title': STRING, 'understand': STRING, 'implement': STRING,
            'self_check': STRING, 'artifact': STRING, 'tests': STRING, 'resources': array(resource),
            'hours_min': {'type': 'integer', 'minimum': 1, 'maximum': 100},
            'hours_max': {'type': 'integer', 'minimum': 1, 'maximum': 100},
            'demonstrates': STRING, 'does_not_demonstrate': STRING})),
        'teaching_question': STRING, 'limitations': STRINGS})


def validate_path(output, data):
    fields(output, path_schema(data)['properties'])
    for k in ('title', 'experiment', 'why_now', 'teaching_question'): text(output[k], 2500)
    for k in ('skills', 'prerequisites', 'assumptions', 'market_evidence', 'limitations'): strings(output[k], 30)
    require(output['disposition'] in ('propose', 'insufficient-evidence'), 'invalid path disposition')
    require(output['skills'] and set(output['skills']) <= set(data['skills']), 'path uses unsupported skills')
    require(output['market_evidence'] and set(output['market_evidence']) <= set(data['evidence']), 'path needs retained job evidence')
    evidenced = {data['evidence'][e]['skill'] for e in output['market_evidence']}
    require(set(output['skills']) <= evidenced, 'each selected skill needs evidence')
    require(output['limitations'] and output['assumptions'], 'path limits and assumptions required')
    require(isinstance(output['milestones'], list) and
            (1 if output['disposition'] == 'propose' else 0) <= len(output['milestones']) <= 12, 'path milestone budget')
    from tools.research_skills import normalized
    require(output['disposition'] != 'propose' or normalized(output['experiment']) not in
            {normalized(x) for x in data.get('existing_paths', [])}, 'same experiment already proposed')
    seen = set()
    props = path_schema(data)['properties']['milestones']['items']['properties']
    for m in output['milestones']:
        fields(m, props)
        for k in props:
            if k not in ('hours_min', 'hours_max', 'resources'): text(m[k], 2500)
        require(m['id'] not in seen, 'duplicate milestone'); seen.add(m['id'])
        strings(m['resources'], 10)
        require(set(m['resources']) <= set(data['resources']), 'resource was not inspected')
        require(type(m['hours_min']) is int and type(m['hours_max']) is int and
                1 <= m['hours_min'] <= m['hours_max'] <= 100, 'invalid effort assumption')
    return {'proposal': output, 'skill_snapshot': data['skill_snapshot'], 'market_snapshot': data['market_snapshot'],
            'contexts': data['contexts'], 'profile': data['profile'], 'preferences': data['preferences'],
            'selection_limits': data['selection_limits']}


def propose_path(store, snapshot, skills, contexts=(), profile=None, *, worker_factory=CodexWorker, retry_review=None):
    require(1 <= len(set(skills)) <= 8 and len(contexts) <= 10, 'choose 1–8 skills and at most ten contexts')
    with store.transaction() as state:
        require('domain_pack' not in state, 'learning paths currently use the AI catalog')
        snap = artifact(state, snapshot, ('skill-snapshot',))
        require(set(skills) <= set(snap['skills']), 'selected skill absent from snapshot')
        for pid, (_, decision) in path_decisions(state).items():
            old = artifact(state, pid, ('learning-path',))
            if set(old['proposal']['skills']) == set(skills) and decision['decision'] in ('rejected', 'duplicate', 'deferred'):
                if decision['decision'] != 'deferred' or timestamp(decision['defer_until']) > store.clock():
                    require(False, 'matching path rejected, duplicate or deferred; select a different learning effort')
        # Finite evidence context; market statistics retain the full denominator.
        evidence = {}; employers = set(); analyses = set()
        for sid in skills:
            candidates = [e for e in snap['skills'][sid]['evidence']]
            candidates.sort(key=lambda e: (snap['evidence'][e]['employer'] in employers, e))
            for eid in candidates[:2]:
                ev = snap['evidence'][eid]; evidence[eid] = ev; employers.add(ev['employer']); analyses.add(ev['analysis'])
        ids = {snap['evidence'][eid]['observation'] for eid in evidence} | analyses
        ids |= {state['artifacts'][oid]['payload']['receipt'] for oid in list(ids) if state['artifacts'][oid]['kind'] == 'observation'}
        broad, broad_deps = aggregate({**state, 'artifacts': {k:state['artifacts'][k] for k in ids}})
        broad['scope'] = 'Explicit learning-path evidence selection; full skill counts are in the parent skill snapshot'
        market = store.put(state, 'snapshot', broad, [snapshot, *broad_deps])
        resources = {}
        for cid in contexts:
            c = artifact(state, cid, ('context',))
            if c['evidence_type'] in ('learning-resource', 'repository') and c['content'] and c['observation_basis'] == 'inspected': resources[cid] = c
        if profile: artifact(state, profile, ('research-profile',))
        # Preferences are planning assumptions, never silently accepted profile claims.
        data = {'skill_snapshot': snapshot, 'market_snapshot': market,
                'skills': {s:{**snap['skills'][s], 'evidence': [e for e,v in evidence.items() if v['skill'] == s],
                              'cooccurs': dict(sorted(snap['skills'][s]['cooccurs'].items(), key=lambda kv:(-kv[1],kv[0]))[:20])}
                           for s in skills}, 'evidence': evidence, 'resources': resources,
                'contexts': list(contexts), 'profile': profile, 'preferences': DEFAULT_PREFERENCES,
                'profile_evidence': artifact(state, profile, ('research-profile',)) if profile else None,
                'selection_limits': ['At most two evidence examples per chosen skill; full counts are separate.',
                                     'At most twenty co-occurring skill counts per selected skill in the model input.',
                                     'Employer names do not verify independent employers.',
                                     'Missing learning resources need inspection, not invented URLs.'],
                'existing_paths': [a['payload']['proposal']['experiment'] for a in state['artifacts'].values() if a['kind'] == 'learning-path']}
        data['decision_memory'] = [p for _,p in path_decisions(state).values()]
        deps_memory = [k for k,a in state['artifacts'].items() if a['kind'] == 'learning-decision']
        require(len(data['existing_paths']) <= 100, 'path history needs review before further generation')
        deps = [snapshot, market, *contexts] + ([profile] if profile else [])
        deps += deps_memory
        deps += [k for k,a in state['artifacts'].items() if a['kind'] == 'learning-path']
    return model_operation(store, 'learning-path', data, path_schema(data), PATH_PROMPT.read_text(), deps,
                           validate_path, worker_factory=worker_factory, retry_review=retry_review)


def select_path(store, key, reviewer):
    text(reviewer)
    with store.transaction() as state:
        p = artifact(state, key, ('learning-path',))
        require(p['proposal']['disposition'] == 'propose', 'cannot select an abstained path')
        decision = path_decisions(state).get(key)
        require(not decision or decision[1]['decision'] == 'deferred' and timestamp(decision[1]['defer_until']) <= store.clock(),
                'path was rejected, duplicated, archived or is still deferred')
        previous = [k for k,a in state['artifacts'].items() if a['kind'] == 'learning-selection']
        for old in previous: store.remove(state, [old])
        selection = store.put(state, 'learning-selection', {'schema_version': 1, 'path': key, 'reviewer': reviewer,
                              'selected_at': store.clock().isoformat()}, [key])
        return {'selection': selection, 'path': key, 'meaning': 'selected work, not a successful outcome'}


def path_briefs(store, key, *, worker_factory=CodexWorker, retry_review=None, refresh=False):
    """Resume the linked pair without regenerating its already completed half."""
    from tools.research_briefs import generate
    with store.transaction() as state:
        path = artifact(state,key,('learning-path',))
        curriculum_only = path.get('schema_version') == 2 and not path.get('market_snapshot')
    if curriculum_only:
        from tools.research_curricula import curriculum_briefs
        return curriculum_briefs(store,key)
    result = {}
    for kind in ('project', 'youtube'):
        with store.transaction() as state:
            p = artifact(state, key, ('learning-path',))
            require(p['proposal']['disposition'] == 'propose', 'abstained path needs evidence before briefs')
            decision = path_decisions(state).get(key)
            require(not decision or decision[1]['decision'] == 'deferred' and timestamp(decision[1]['defer_until']) <= store.clock(),
                    'path was rejected, duplicated, archived or is still deferred')
            progress = {k:a['payload'] for k,a in state['artifacts'].items() if a['kind'] == 'learning-progress' and a['payload']['path'] == key}
            corrected = {v['supersedes'] for v in progress.values()}
            progress = sorted(set(progress) - corrected)
            basis = digest([key, kind, progress])
            cached = []
            for bid, a in state['artifacts'].items():
                if a['kind'] != 'brief' or a['payload'].get('learning_path') != key or a['payload']['kind'] != kind: continue
                execution = state['artifacts'][a['payload']['execution']]
                used = sorted(d for d in execution['dependencies'] if state['artifacts'][d]['kind'] == 'learning-progress')
                if used == progress: cached.append((execution['payload'].get('recorded_at', ''), bid))
            if cached and not refresh:
                result[kind] = {'brief': sorted(cached)[-1][1], 'cache_hit': True}; continue
            prior = any(a['kind'] == 'path-brief-intent' and a['payload']['basis'] == basis or
                        a['kind'] == 'brief-failure' and a['payload']['kind'] == kind and key in a['dependencies']
                        for a in state['artifacts'].values())
            if prior: require(retry_review, 'linked brief attempt requires explicit retry review')
            if retry_review: text(retry_review)
            intent = store.put(state, 'path-brief-intent', {'schema_version':1,'path':key,'kind':kind,'basis':basis,
                               'created_at':store.clock().isoformat(),'retry_review':retry_review}, [key,*progress])
        generated = generate(store, kind, p['market_snapshot'], p['contexts'], p['profile'],
                             learning_path=key, worker_factory=worker_factory, refresh=refresh)
        with store.transaction() as state:
            artifact(state, intent, ('path-brief-intent',))
            store.put(state, 'path-brief-result', {'schema_version':1,'basis':basis,'brief':generated['brief']}, [intent,generated['brief']])
        result[kind] = generated
    return result


def record_progress(store, row):
    fields(row, ['schema_version', 'path', 'milestone', 'event', 'basis', 'summary', 'observer', 'occurred_at',
                 'evidence', 'conditions', 'capabilities', 'result_quotes', 'supersedes', 'policy'])
    require(row['schema_version'] == 1, 'unsupported progress version')
    require(row['event'] in ('attempt', 'self-check', 'implementation', 'test', 'failure', 'lesson', 'correction', 'completed'), 'invalid progress event')
    require(row['basis'] in ('self-reported', 'observed'), 'model generation is not learning progress')
    text(row['summary'], 3000); text(row['observer']); text(row['milestone'])
    require(timestamp(row['occurred_at']) <= store.clock(), 'future progress')
    for k in ('evidence', 'conditions', 'capabilities', 'result_quotes'): strings(row[k], 30)
    validate_policy(row['policy'], store.clock())
    with store.transaction() as state:
        p = artifact(state, row['path'], ('learning-path',))
        require(row['milestone'] in {m['id'] for m in p['proposal']['milestones']}, 'unknown milestone')
        from tools.research_domains import taxonomy_for
        require(set(row['capabilities']) <= set(taxonomy_for(state)['capabilities']), 'unknown capability')
        contexts = [artifact(state, cid, ('context',)) for cid in row['evidence']]
        if row['basis'] == 'observed':
            require(contexts and row['conditions'] and row['result_quotes'], 'observed work needs inspected results and conditions')
            require(all(c['evidence_type'] == 'experiment-result' and c['observation_basis'] == 'reproduced' for c in contexts),
                    'observed progress needs reproduced experiment contexts')
            require(all(any(q in c['content'] for c in contexts) for q in row['result_quotes']), 'result quote absent')
            require(set(row['conditions']) <= {x for c in contexts for x in c['conditions']}, 'conditions broaden source evidence')
        if row['supersedes']:
            old = artifact(state, row['supersedes'], ('learning-progress',))
            require(old['path'] == row['path'] and old['milestone'] == row['milestone'], 'correction targets another effort')
            # The transaction retracts all consumers of superseded progress,
            # including briefs, profiles and managed reports; retain audit events.
        policy = store.put(state, 'policy', row['policy'], use_until=row['policy'].get('use_until'))
        payload = {k:v for k,v in row.items() if k != 'policy'}
        # path is a hash-only association, NOT source-derived copied prose. Own
        # results retain their own policies; market justification can be withdrawn.
        payload['recorded_at'] = store.clock().isoformat()
        key = store.put(state, 'learning-progress', payload, [policy, *row['evidence']] + ([row['supersedes']] if row['supersedes'] else []))
        return {'progress': key, 'basis': row['basis'], 'profile_changed': False}


def progress_profile(store, key):
    from tools.research_profile import propose
    with store.transaction() as state:
        p = artifact(state, key, ('learning-progress',))
        require(p['basis'] == 'observed' and p['capabilities'], 'only scoped observed work can propose demonstrated capability')
        require(not any(a['kind'] == 'learning-progress' and a['payload']['supersedes'] == key for a in state['artifacts'].values()), 'progress was corrected')
        policies = [artifact(state, d, ('policy',)) for d in state['artifacts'][key]['dependencies'] if state['artifacts'][d]['kind'] == 'policy']
        bundle = {'schema_version': 1, 'policy': policies[0], 'direction': ['Learning evidence under recorded conditions'],
                  'supersedes': None, 'capabilities': [{'capability': c, 'level': 'demonstrated', 'evidence': p['evidence'],
                    'conditions': p['conditions'], 'limitations': ['Proposal needs user review of semantic alignment; not general mastery.']} for c in p['capabilities']]}
    result = propose(store, bundle)
    with store.transaction() as state:
        # Link proposal lifecycle to the progress event as well as its results.
        original = state['artifacts'][result['proposal']]
        new = store.put(state, 'profile-proposal', original['payload'], [*original['dependencies'], key])
        store.remove(state, [result['proposal']])
        result['proposal'] = new
    return result


def path_decision(store, row):
    fields(row, ['schema_version', 'path', 'decision', 'reason', 'reviewer', 'defer_until'])
    require(row['schema_version'] == 1 and row['decision'] in ('rejected', 'deferred', 'duplicate', 'archived'), 'invalid learning decision')
    text(row['reason']); text(row['reviewer'])
    require((row['decision'] == 'deferred') == (row['defer_until'] is not None), 'deferral needs a due date')
    if row['defer_until']: require(timestamp(row['defer_until']) > store.clock(), 'deferral date must be future')
    with store.transaction() as state:
        artifact(state, row['path'], ('learning-path',))
        selections = [k for k,a in state['artifacts'].items() if a['kind'] == 'learning-selection' and a['payload']['path'] == row['path']]
        store.remove(state, selections)
        key = store.put(state, 'learning-decision', {**row, 'decided_at':store.clock().isoformat()}, [row['path']])
        return {'decision':key}


def path_decisions(state):
    rows = sorted([(k,a['payload']) for k,a in state['artifacts'].items() if a['kind'] == 'learning-decision'],
                  key=lambda kv:(kv[1]['decided_at'], kv[0]))
    return {p['path']:(k,p) for k,p in rows}


def compare_path(store, key, *, worker_factory=CodexWorker, retry_review=None):
    """Same frozen evidence/preferences, straightforward-prompt learning baseline."""
    with store.transaction() as state:
        path = artifact(state, key, ('learning-path',))
        require(path.get('schema_version') != 2, 'curriculum paths use a reviewed syllabus; compare their exercises and adaptations through curriculum-inspect')
        intent = artifact(state, state['artifacts'][key]['dependencies'][0], ('learning-intent',))
        data = intent['input']
    return model_operation(store, 'learning-comparison', data, path_schema(data),
        'Create a practical learning plan and engineering project from these skills and descriptions using the supplied schema. '
        'Use only supplied resource/evidence IDs; preserve unknowns and do not invent results.',
        [key], validate_path, worker_factory=worker_factory, retry_review=retry_review)
