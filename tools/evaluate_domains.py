"""Opt-in owned domain extraction and four-workflow evaluation using existing helpers."""
from datetime import timedelta
import json
from pathlib import Path
import subprocess

from tools.research_evidence import ROOT, digest, require
from tools.research_domains import pack_for, reference
from tools.research_analysis import analyze, qualified, analysis_versions
from tools.research_runtime import CodexWorker
from tools.research_briefs import generate, SECTIONS
from tools.evaluate_research import score


def owned_bundle(example, now):
    at = now.isoformat()
    return {'schema_version': 1, 'policy': {'schema_version': 1, 'source': 'owned-backend-evaluation',
        'method': 'reviewed-local-import', 'reviewed_by': 'fixture author', 'reviewed_at': at,
        'permission_basis': 'Author-owned synthetic examples; no real organization or listing.',
        'permission_reference': 'tests/fixtures/research/backend-platform-v1.json', 'local_processing': True,
        'retention': 'indefinite-logical-deletion', 'hosted_disclosure': True,
        'hosted_retention': 'provider-managed-no-deletion-deadline', 'hosted_permission_reference': 'Owned evaluation only.',
        'export': False, 'audit_hashes': True, 'limitations': ['Owned examples are not market evidence.']},
        'receipt': {'schema_version': 1, 'source': 'owned-backend-evaluation', 'kind': 'synthetic',
        'query': example['id'], 'requested_filters': {}, 'effective_filters': {}, 'started_at': at, 'finished_at': at,
        'pages': [{'locator': 'owned:'+example['id'], 'status': 'ok', 'returned': 1, 'next_cursor': None}],
        'completeness': 'complete-request', 'limitations': ['One owned synthetic example.']},
        'observations': [{'native_id': example['id'], 'employer_name': 'Owned fictional employer',
        'employer_domain': 'fixture.example', 'employer_requisition': example['id'],
        'url': 'https://fixture.example/'+example['id'], 'title': 'Owned evaluation role',
        'description': example['description'], 'captured_at': at, 'source_revision': digest(example),
        'posted_at_original': None, 'posted_at': None, 'language': 'en', 'country': None,
        'availability': 'unknown', 'availability_evidence': None, 'segments': {},
        'limitations': ['Not an actual vacancy.']}]}


def evaluate(store, *, worker_factory=CodexWorker):
    with store.transaction() as state:
        pack = pack_for(state)
        require(pack and pack['id'] == 'backend-platform', 'explicit backend evaluation workspace required')
        allowed = {'runtime-qualification', 'policy', 'receipt', 'observation', 'analysis', 'execution',
                   'snapshot', 'brief', 'brief-execution', 'brief-failure', 'domain-evaluation-case', 'domain-evaluation', 'domain-brief-evaluation'}
        require(all(a['kind'] in allowed for a in state['artifacts'].values()),
                'use a dedicated evaluation workspace without private feedback/context/profile records')
        require(all(a['payload']['kind'] == 'synthetic' and a['payload']['source'] == 'owned-backend-evaluation'
                    for a in state['artifacts'].values() if a['kind'] == 'receipt'),
                'owned evaluation cannot mix with other evidence')
        qualification, identity = qualified(state)
    # Only the known checked-in fixture, never execute a path supplied in a pack.
    dataset = json.loads((ROOT/'tests/fixtures/research/backend-platform-v1.json').read_text())
    require(digest(dataset) == pack['evaluation']['sha256'], 'frozen dataset drift')
    examples = {e['id']: e['description'] for e in dataset['examples']}
    with store.transaction() as state:
        require(all(a['payload']['native_id'] in examples and a['payload']['description'] == examples[a['payload']['native_id']]
                    for a in state['artifacts'].values() if a['kind'] == 'observation'),
                'evaluation workspace contains content outside the frozen owned set')
    versions = {'domain': reference(pack), 'dataset': digest(dataset), 'runtime': identity,
                'harness': digest(Path(__file__).read_text()), 'analysis': analysis_versions(identity, pack),
                'brief_validator': digest((ROOT/'tools/research_briefs.py').read_text()),
                'brief_prompt': digest((ROOT/'docs/research/prompts/brief-v1.md').read_text())}
    results, brief_results = [], []
    for example in dataset['examples']:
        with store.transaction() as state:
            cached = [a['payload'] for a in state['artifacts'].values() if a['kind'] == 'domain-evaluation-case'
                      and a['payload']['versions'] == versions and a['payload']['example'] == example['id']]
        if cached:
            results.append(cached[-1]); continue
        imported = store.import_bundle(owned_bundle(example, store.clock()))
        obs = imported['observations'][0]
        capture = {}
        class RecordingWorker:
            def __init__(self, home): self.delegate = worker_factory(home)
            def __enter__(self): self.delegate.__enter__(); return self
            def __exit__(self, *args): return self.delegate.__exit__(*args)
            def run(self, prompt, schema):
                value, metadata = self.delegate.run(prompt, schema)
                capture.update(output=value, metadata=metadata)
                return value, metadata
        try:
            result = analyze(store, obs, worker_factory=RecordingWorker)
            with store.transaction() as state:
                row = state['artifacts'][result['analysis']]['payload']
            output = {**row, 'ai_domain': row['domain_fit']}
            record = {'example': example['id'], 'valid': True, 'score': score(output, example), 'analysis': result['analysis']}
        except (ValueError, OSError, subprocess.SubprocessError):
            record = {'example': example['id'], 'valid': False, 'score': None, 'analysis': None}
        record.update(versions=versions, capture=capture, human_review='pending', recorded_at=store.clock().isoformat())
        with store.transaction() as state:
            store.put(state, 'domain-evaluation-case', record, [obs, qualification] + ([record['analysis']] if record['analysis'] else []))
        results.append(record)
        print(json.dumps({'example': example['id'], 'valid': record['valid'], 'score': record['score']}), flush=True)
        if not record['valid'] and not capture:
            break  # authentication/quota/runtime failure: no retry or fallback
    if len(results) == len(dataset['examples']):
        snapshot = store.snapshot()['snapshot']
        for kind in SECTIONS:
            try:
                result = generate(store, kind, snapshot, worker_factory=worker_factory)
                with store.transaction() as state:
                    proposal = state['artifacts'][result['brief']]['payload']['proposal']
                brief_results.append({'kind': kind, 'valid': True, 'brief': result['brief'],
                    'disposition': proposal['disposition'], 'capabilities': proposal['capabilities'],
                    'judgments': proposal['judgments'], 'human_review': 'pending'})
            except (ValueError, OSError, subprocess.SubprocessError):
                brief_results.append({'kind': kind, 'valid': False, 'human_review': 'pending'})
                break  # stop the batch; inspect retained failure records
    summary = {'schema_version': 1, 'versions': versions, 'cases': results, 'briefs': brief_results,
               'human_review': 'pending', 'limitations': ['Twelve author-owned cases with provisional labels; not field quality.',
                'All four briefs lack external alternatives/problem/discussion evidence; limits and abstention are expected.',
                'No human usefulness/feasibility ratings, executed project or commercial/audience validation is invented.']}
    with store.transaction() as state:
        deps = [k for k,a in state['artifacts'].items() if a['kind'] in ('domain-evaluation-case', 'brief')]
        key = store.put(state, 'domain-evaluation', summary, deps)
    return {'evaluation': key, 'valid_extractions': sum(r['valid'] for r in results),
            'cases': len(results), 'briefs': brief_results, 'human_review': 'pending'}
