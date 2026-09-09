"""Reviewable research direction/evidence profile, independent of application data."""
from tools.research_evidence import TAXONOMY, fields, require, strings, text, validate_policy

LEVELS = ('self-declared', 'inspected', 'demonstrated', 'not-evidenced')


def propose(store, bundle, *, outcome=None):
    fields(bundle, ['schema_version', 'policy', 'direction', 'capabilities', 'supersedes'])
    require(bundle['schema_version'] == 1, 'unsupported research profile version')
    validate_policy(bundle['policy'], store.clock())
    strings(bundle['direction'], 20)
    require(isinstance(bundle['capabilities'], list) and len(bundle['capabilities']) <= 30, 'profile budget exceeded')
    with store.transaction() as state:
        deps = []
        if outcome:
            from tools.research_outcomes import artifact
            result = artifact(state, outcome, ('outcome',))
            require(result['basis'] == 'observed' and result['event_type'] in ('test', 'held-out-evaluation'),
                    'outcome unavailable for profile proposal')
            require(not any(a['kind'] == 'outcome' and a['payload'].get('supersedes') == outcome
                            for a in state['artifacts'].values()), 'superseded outcome cannot propose a profile')
            require(all(r['capability'] in result['capabilities'] and r['evidence'] == result['evidence']
                        and r['conditions'] == result['conditions'] for r in bundle['capabilities']),
                    'proposal cannot broaden outcome evidence/conditions')
            deps.append(outcome)
        if bundle['supersedes'] is not None:
            old = state['artifacts'].get(bundle['supersedes'])
            require(old and old['kind'] == 'research-profile', 'profile revision unavailable')
            deps.append(bundle['supersedes'])
        seen = set()
        for row in bundle['capabilities']:
            fields(row, ['capability', 'level', 'evidence', 'conditions', 'limitations'])
            require(row['capability'] in TAXONOMY['capabilities'] and row['capability'] not in seen, 'unknown/duplicate capability')
            seen.add(row['capability'])
            require(row['level'] in LEVELS, 'unknown evidence level')
            strings(row['evidence']); strings(row['conditions']); strings(row['limitations'])
            if row['level'] in ('inspected', 'demonstrated'):
                require(row['evidence'], 'profile evidence required')
            for key in row['evidence']:
                artifact = state['artifacts'].get(key)
                require(artifact and artifact['kind'] == 'context' and artifact['payload']['content'], 'profile context unavailable')
                context = artifact['payload']
                require(context['observation_basis'] in ('inspected', 'reproduced'), 'assessment or self-report is not inspected work')
                if row['level'] == 'demonstrated':
                    require(context['evidence_type'] == 'experiment-result' and context['observation_basis'] == 'reproduced'
                            and row['conditions'] and context['conditions'], 'demonstration needs inspected results under conditions')
                deps.append(key)
        policy = store.put(state, 'policy', bundle['policy'], use_until=bundle['policy'].get('use_until'))
        key = store.put(state, 'profile-proposal', {'schema_version': 1, 'direction': bundle['direction'],
                'capabilities': bundle['capabilities'], 'supersedes': bundle['supersedes'],
                'status': 'pending-human-review', **({'outcome': outcome} if outcome else {})}, [policy, *deps])
    return {'proposal': key, 'status': 'pending-human-review'}


def review(store, proposal, decision, reviewer):
    require(decision in ('accept', 'reject'), 'invalid profile review decision')
    text(reviewer)
    with store.transaction() as state:
        artifact = state['artifacts'].get(proposal)
        require(artifact and artifact['kind'] == 'profile-proposal', 'proposal unavailable')
        record = {'schema_version': 1, 'proposal': proposal, 'decision': decision,
                  'reviewer': reviewer, 'reviewed_at': store.clock().isoformat(),
                  'limitation': 'Reviewer assertion, not independently authenticated identity.'}
        key = store.put(state, 'profile-review', record, [proposal])
        if decision == 'reject':
            return {'review': key, 'status': 'rejected-no-profile-change'}
        profile = store.put(state, 'research-profile', {**artifact['payload'], 'status': 'reviewed', 'review': key}, [proposal, key])
        return {'profile': profile, 'review': key}
