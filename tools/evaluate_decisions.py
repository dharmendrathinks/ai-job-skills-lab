"""Opt-in live P3 scenario evaluation on owned synthetic inputs, separate from jobs.

No gold human ratings are fabricated. The scenarios check skill deepening and
abstention, and retain drafts for human review in a separate private child store.
"""
import json
import os

from tools.research_evidence import ROOT, Store, private_state_path, require
from tools.research_analysis import qualify
from tools.research_profile import propose, review
from tools.research_briefs import generate
from tests.test_research_evidence import bundle, annotation


def evaluate(home):
    store = Store(home)
    data = bundle()
    data['policy'].update(hosted_disclosure=True, hosted_retention='provider-managed-no-deletion-deadline',
                          hosted_permission_reference='Author-owned synthetic repository evaluation content')
    observation = store.import_bundle(data)['observations'][0]
    store.annotate(annotation(observation))
    snapshot = store.snapshot()['snapshot']
    qualify(store)
    proposal = propose(store, {'schema_version': 1, 'policy': data['policy'],
        'direction': ['Deepen already-known retrieval skills through held-out evaluation and failure analysis.'],
        'capabilities': [{'capability': 'retrieval-knowledge', 'level': 'self-declared', 'evidence': [],
                          'conditions': [], 'limitations': ['Fictional scenario; not the real user profile or demonstrated ability.']}],
        'supersedes': None})['proposal']
    profile = review(store, proposal, 'accept', 'synthetic scenario setup; NOT human evaluation')['profile']
    results = []
    for case, kind, selected_profile in [('known-skill-deepening', 'learning', profile),
                                          ('missing-alternatives', 'project', None)]:
        result = generate(store, kind, snapshot, profile=selected_profile)
        with store.transaction() as state:
            row = state['artifacts'][result['brief']]['payload']
            if kind == 'project':
                require(row['proposal']['disposition'] in ('no-project', 'insufficient-evidence'), 'abstention scenario failed')
                require(not row['proposal']['alternatives'], 'invented alternative in scenario')
            else:
                require(row['profile_evidence']['capabilities'][0]['level'] == 'self-declared', 'profile evidence upgraded')
                require(row['proposal']['sections']['known_skill_deepening'], 'missing deepening practice')
            results.append({'case': case, 'brief': result['brief'], 'disposition': row['proposal']['disposition'],
                            'structural_checks': 'passed', 'human_review': 'pending', 'versions': row['versions']})
    require(store.snapshot()['snapshot'] == snapshot, 'profile or brief changed market counts')
    return {'schema_version': 1, 'synthetic': True, 'results': results,
            'limitations': ['Fictional source/profile; no actual market or user capability claims.',
                           'Live model output inspected structurally; human usefulness review remains pending.']}


if __name__ == '__main__':
    home = private_state_path(ROOT, dict(os.environ)) / 'phase3-evaluation'
    print(json.dumps(evaluate(home), indent=2))
