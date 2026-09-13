"""Explicit research feedback, immutable revisions and scoped profile proposals.

Reuses upstream outcome/archive semantics; never touches application state.
Reviewer/observer names are assertions, not authenticated identities.
"""
from tools.research_evidence import (TAXONOMY, digest, fields, require, strings,
                                     text, timestamp, validate_policy)

DECISIONS = ('accepted', 'rejected', 'deferred', 'duplicate', 'superseded')
EVENTS = ('project-selected', 'implementation', 'test', 'held-out-evaluation',
          'correction', 'product-validation', 'published-experiment', 'lesson')
BASES = ('observed', 'user-reported', 'model-inferred')


def artifact(state, key, kinds):
    row = state['artifacts'].get(key)
    require(row and row['kind'] in kinds, 'required artifact unavailable or withdrawn')
    return row['payload']


def evidence_basis(state, snapshot, contexts):
    """Content identities, excluding capture time, profile, prompt and model prose."""
    rows = []
    for key in state['artifacts'][snapshot]['dependencies']:
        a = state['artifacts'][key]
        if a['kind'] == 'analysis':
            obs = artifact(state, a['payload']['observation'], ('observation',))
            if obs['description']:
                rows.append(digest(['description', obs['description']]))
    for key in contexts:
        ctx = artifact(state, key, ('context',))
        if ctx['content'] and ctx['observation_basis'] in ('inspected', 'reproduced'):
            rows.append(digest(['context', ctx['content']]))
    return sorted(set(rows))


def brief_basis(state, brief):
    row = artifact(state, brief, ('brief',))
    if row.get('basis_kind') == 'curriculum':
        return row['evidence_basis']
    return evidence_basis(state, row['snapshot'], row['contexts'])


def latest_decisions(state):
    events = {k: a['payload'] for k, a in state['artifacts'].items() if a['kind'] == 'decision'}
    replaced = {v['supersedes'] for v in events.values()}
    return {k: v for k, v in events.items() if k not in replaced}


def decide(store, row):
    fields(row, ['schema_version', 'brief', 'decision', 'reason', 'reviewer',
                 'decided_at', 'defer_until', 'target', 'supersedes'])
    require(row['schema_version'] == 1 and row['decision'] in DECISIONS, 'unknown decision schema/state')
    for name in ('reason', 'reviewer'): text(row[name])
    require(timestamp(row['decided_at']) <= store.clock(), 'future decision')
    if row['decision'] == 'deferred':
        require(timestamp(row['defer_until']) > store.clock(), 'defer date must be future')
    else: require(row['defer_until'] is None, 'defer date only for deferred decisions')
    with store.transaction() as state:
        brief = artifact(state, row['brief'], ('brief',))
        for key, a in state['artifacts'].items():
            if a['kind'] == 'decision' and a['payload'] == row:
                return {'decision': key, 'status': row['decision']}
        previous = [(k,v) for k,v in latest_decisions(state).items() if v['brief'] == row['brief']]
        require(row['supersedes'] == (previous[0][0] if previous else None), 'explicit latest decision revision required')
        deps = [row['brief']] + ([row['supersedes']] if row['supersedes'] else [])
        if row['decision'] in ('duplicate', 'superseded'):
            target = artifact(state, row['target'], ('brief',))
            require(row['target'] != row['brief'] and target['kind'] == brief['kind'], 'invalid target brief')
            deps.append(row['target'])
        else: require(row['target'] is None, 'target only for duplicate/superseded decisions')
        key = store.put(state, 'decision', row, deps)
        return {'decision': key, 'status': row['decision']}


def record_outcome(store, row):
    fields(row, ['schema_version', 'brief', 'event_type', 'basis', 'observer', 'occurred_at',
                 'summary', 'project', 'evidence', 'capabilities', 'conditions', 'limitations', 'supersedes', 'tests', 'policy'])
    require(row['schema_version'] == 1 and row['event_type'] in EVENTS and row['basis'] in BASES, 'unknown outcome schema/type/basis')
    for name in ('observer', 'summary'): text(row[name], 4000)
    require(timestamp(row['occurred_at']) <= store.clock(), 'future outcome')
    for name in ('evidence', 'capabilities', 'conditions', 'limitations'): strings(row[name], 30)
    require(row['limitations'], 'outcome limitations required')
    validate_policy(row['policy'], store.clock())
    require(isinstance(row['tests'], list) and len(row['tests']) <= 20, 'test-run budget exceeded')
    project = row['project']
    if project is not None:
        fields(project, ['url', 'revision', 'action'])
        from urllib.parse import urlsplit
        url = urlsplit(project['url'])
        require(url.scheme == 'https' and url.hostname and not url.username and not url.password, 'project needs credential-free HTTPS locator')
        import re
        require(re.fullmatch('[0-9a-f]{40,64}', project['revision']) and project['action'] in ('extend', 'contribute', 'new', 'inspect'), 'pinned project/action required')
    if row['event_type'] == 'project-selected': require(project, 'selected project required')
    with store.transaction() as state:
        from tools.research_domains import taxonomy_for
        require(set(row['capabilities']) <= set(taxonomy_for(state)['capabilities']), 'outcome capabilities outside workspace taxonomy')
        artifact(state, row['brief'], ('brief',))
        deps = [row['brief']]
        if row['supersedes']:
            old = artifact(state, row['supersedes'], ('outcome',))
            require(old['brief'] == row['brief'], 'correction must retain brief identity')
            require(not any(a['kind'] == 'outcome' and a['payload'].get('supersedes') == row['supersedes']
                            and a['payload'] != row for a in state['artifacts'].values()), 'correct latest outcome revision')
            deps.append(row['supersedes'])
        if row['basis'] == 'observed': require(row['evidence'], 'observed outcome requires inspected evidence')
        for key in row['evidence']:
            ctx = artifact(state, key, ('context',))
            if row['basis'] == 'observed':
                require(ctx['content'] and ctx['observation_basis'] in ('inspected', 'reproduced'), 'import or self-report cannot establish observation')
                if row['event_type'] in ('test', 'held-out-evaluation'):
                    require(ctx['evidence_type'] == 'experiment-result' and ctx['observation_basis'] == 'reproduced'
                            and row['conditions'] and set(row['conditions']) <= set(ctx['conditions']), 'test result needs reproduced evidence and matching conditions')
            deps.append(key)
        if row['basis'] == 'observed' and row['event_type'] in ('test', 'held-out-evaluation'):
            require(row['tests'], 'inspected test command/results required')
        for run in row['tests']:
            fields(run, ['context', 'command', 'revision', 'exit_code', 'result_quote', 'held_out'])
            require(run['context'] in row['evidence'], 'test outside outcome evidence')
            ctx = artifact(state, run['context'], ('context',))
            import re
            text(run['command'], 2000); text(run['held_out'], 2000); text(run['result_quote'], 4000)
            require(isinstance(run['revision'], str) and re.fullmatch('[0-9a-f]{40,64}', run['revision'])
                    and run['revision'] == ctx['revision'], 'test revision must match inspected result')
            require(type(run['exit_code']) is int and -255 <= run['exit_code'] <= 255, 'invalid recorded exit code')
            require(ctx['content'] and run['result_quote'] in ctx['content'], 'test quote must match inspected content')
        policy = store.put(state, 'policy', row['policy'], use_until=row['policy'].get('use_until'))
        key = store.put(state, 'outcome', row, [policy, *deps])
        if row['supersedes']:
            # Keep event history, but retract capability proposals and every
            # profile/brief derived from corrected work evidence.
            proposals = [k for k,a in state['artifacts'].items() if a['kind'] == 'profile-proposal'
                         and a['payload'].get('outcome') == row['supersedes']]
            store.remove(state, proposals)
        return {'outcome': key, 'basis': row['basis'], 'profile_changed': False}


def propose_from_outcome(store, outcome, direction, supersedes=None):
    from tools.research_profile import propose
    with store.transaction() as state:
        row = artifact(state, outcome, ('outcome',))
        require(not any(a['kind'] == 'outcome' and a['payload'].get('supersedes') == outcome
                        for a in state['artifacts'].values()), 'superseded outcome cannot propose a profile')
        require(row['basis'] == 'observed' and row['event_type'] in ('test', 'held-out-evaluation')
                and row['capabilities'], 'only scoped inspected test outcomes can propose demonstration')
        # Re-run the profile validator; the result remains pending human review.
        bundle = {'schema_version': 1, 'policy': row['policy'], 'direction': direction, 'supersedes': supersedes,
                  'capabilities': [{'capability': c, 'level': 'demonstrated', 'evidence': row['evidence'],
                    'conditions': row['conditions'], 'limitations': row['limitations']} for c in row['capabilities']]}
    return propose(store, bundle, outcome=outcome)


def reconsider(store, row):
    fields(row, ['schema_version', 'brief', 'evidence', 'reason', 'reviewer'])
    require(row['schema_version'] == 1, 'unknown reconsideration version')
    text(row['reason']); text(row['reviewer']); strings(row['evidence'], 10)
    require(row['evidence'], 'material new evidence required')
    with store.transaction() as state:
        old = set(brief_basis(state, row['brief']))
        for key in row['evidence']:
            ctx = artifact(state, key, ('context',))
            require(ctx['content'] and ctx['observation_basis'] in ('inspected', 'reproduced')
                    and digest(['context', ctx['content']]) not in old, 'wrapper/profile/model changes are not new evidence')
        key = store.put(state, 'reconsideration', row, [row['brief'], *row['evidence']])
        return {'reconsideration': key}


def memory(state, kind):
    return [{'id': key, **row, 'title': artifact(state, row['brief'], ('brief',))['proposal']['title'],
             'capabilities': artifact(state, row['brief'], ('brief',))['proposal']['capabilities']}
            for key, row in latest_decisions(state).items()
            if artifact(state, row['brief'], ('brief',))['kind'] == kind]


def outcome_memory(state, kind):
    rows = {k: a['payload'] for k,a in state['artifacts'].items() if a['kind'] == 'outcome'}
    replaced = {r['supersedes'] for r in rows.values()}
    return [{'id': k, **{name: row[name] for name in ('brief', 'event_type', 'basis', 'summary',
             'project', 'evidence', 'capabilities', 'conditions', 'limitations', 'tests')}}
            for k,row in rows.items() if k not in replaced and artifact(state, row['brief'], ('brief',))['kind'] == kind]


def check_memory(state, kind, basis, contexts, now, output=None, reconsideration=None):
    """Conservative capability overlap; semantic novelty still requires review."""
    for row in memory(state, kind):
        blocked = row['decision'] in ('rejected', 'duplicate', 'superseded') or (
            row['decision'] == 'deferred' and timestamp(row['defer_until']) > now)
        if not blocked: continue
        previous = brief_basis(state, row['brief'])
        if output is None and set(basis) != set(previous): continue
        if output is not None and not set(output['capabilities']) & set(row['capabilities']): continue
        require(row['decision'] != 'deferred', 'recommendation deferred until explicit date or reviewed decision change')
        rec = artifact(state, reconsideration, ('reconsideration',)) if reconsideration else None
        require(rec and rec['brief'] == row['brief'] and set(rec['evidence']) <= set(contexts)
                and set(basis) - set(previous), 'recommendation suppressed; reviewed material evidence required')


def history(store, brief):
    with store.transaction() as state:
        artifact(state, brief, ('brief',))
        events = {k: a['payload'] for k,a in state['artifacts'].items()
                  if a['kind'] in ('decision', 'outcome', 'reconsideration') and a['payload']['brief'] == brief}
        return {'brief': brief, 'events': events, 'latest_decisions': {
            k:v for k,v in latest_decisions(state).items() if v['brief'] == brief},
            'limitation': 'Generation and acceptance are not work success; names and semantic scope require human review.'}
