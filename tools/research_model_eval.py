"""Owned-fixture evaluation only; local inference is not a production fallback."""
from datetime import timedelta
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.request import build_opener, ProxyHandler, Request

from tools.research_evidence import Store, ROOT, digest, require, text, private_state_path, validate_annotation
from tools.research_analysis import (OUTPUT_SCHEMA, PROMPT_PATH, bounded_prompt, normalize_output,
                                     qualified, qualification_identity)
from tools.evaluate_research import DATASET, score
from tools.research_runtime import CodexWorker


def local_request(path, body=None):
    require(path in ('tags', 'ps', 'version', 'generate'), 'unreviewed local model endpoint')
    request = Request('http://127.0.0.1:11434/api/' + path,
                      json.dumps(body).encode() if body is not None else None,
                      {'Content-Type': 'application/json'})
    from tools.research_delivery import NoRedirect
    with build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=120) as response:
        raw = response.read(1_000_001)
        require(len(raw) <= 1_000_000, 'local output budget exceeded')
        return json.loads(raw)


def evaluate_local(store, model, *, request=local_request):
    # No pull/create/exec API; require a model that is already installed.
    catalog = request('tags')
    matches = [m for m in catalog['models'] if m['name'] == model]
    require(len(matches) == 1, 'choose an already installed local model')
    installed = matches[0]
    dataset = json.loads(DATASET.read_text())
    version = request('version')
    before = request('ps')
    results = []
    for example in dataset['examples']:
        start = time.monotonic()
        output = None
        raw = {}
        try:
            raw = request('generate', {'model': model, 'prompt': bounded_prompt(example['description']),
                    'format': OUTPUT_SCHEMA, 'stream': False, 'keep_alive': '2m',
                    'options': {'temperature': 0, 'seed': 42, 'num_ctx': 4096, 'num_predict': 1500}})
            require(raw.get('done') is True, 'local inference incomplete')
            output = json.loads(raw['response'])
            checked_at = store.clock()
            normalized = normalize_output(output, example['id'], example['description'], checked_at)
            fake = {'artifacts': {example['id']: {'kind': 'observation', 'payload': {
                'description': example['description'], 'captured_at': checked_at.isoformat(), 'receipt': 'owned'}},
                'owned': {'payload': {'kind': 'synthetic'}}}}
            validate_annotation(normalized, fake, checked_at, automated=True)
            result = {'valid': True, 'score': score(output, example), 'output': output}
        except (ValueError, OSError, KeyError, TypeError):
            result = {'valid': False, 'score': None, 'output': output}
        result.update(example=example['id'], latency_seconds=round(time.monotonic()-start, 3),
                      metrics={k:raw.get(k) for k in ('total_duration', 'load_duration', 'prompt_eval_count', 'eval_count', 'eval_duration')},
                      resident=request('ps'))
        results.append(result)
    with store.transaction() as state:
        key = store.put(state, 'model-evaluation', {'schema_version': 1, 'runtime': 'ollama-owned-fixture-only',
             'version': version, 'model': installed, 'recorded_at': store.clock().isoformat(),
             'dataset_sha256': digest(dataset), 'prompt_sha256': digest(PROMPT_PATH.read_text()),
             'schema_sha256': digest(OUTPUT_SCHEMA), 'harness_sha256': digest(Path(__file__).read_text()),
             'settings': {'num_ctx': 4096, 'num_predict': 1500, 'seed': 42, 'temperature': 0},
             'resident_before': before, 'results': results, 'human_review': 'pending',
             'limitations': ['Six previously evaluated author-owned snippets, provisional labels; not a newly unseen held-out set.',
                'Resident API estimates are not peak unified-memory, pressure, swap or energy measurements.',
                'No research source disclosure or runtime promotion. Brief quality, long descriptions and multilingual quality unmeasured.',
                'No downloading, paid fallback or production tool-boundary claim. Existing local server is trusted separately.']})
    return {'evaluation': key, 'valid': sum(r['valid'] for r in results), 'examples': len(results), 'results': results}


def probe_unattended(store):
    # Uses existing account via unchanged worker; no terminal input or API fallback.
    with store.transaction() as state:
        qualification, identity = qualified(state)
    codex = shutil.which('codex')
    require(codex, 'Codex unavailable')
    env = {'HOME': str(Path.home()), 'PATH': str(Path(codex).parent) + ':/usr/bin:/bin:/usr/sbin:/sbin',
           'AI_JOB_SKILLS_LAB_HOME': str(store.home), 'LANG': 'en_US.UTF-8'}
    started = time.monotonic()
    result = subprocess.run([sys.executable, '-m', 'tools.research_model_eval', 'probe-child'],
                            cwd=ROOT, env=env, stdin=subprocess.DEVNULL, capture_output=True, timeout=120)
    metadata = json.loads(result.stdout) if result.returncode == 0 else {'status': 'blocked'}
    with store.transaction() as state:
        qualified(state)
        key = store.put(state, 'unattended-probe', {'schema_version': 1, 'recorded_at': store.clock().isoformat(),
             'identity': identity, 'executable': str(Path(sys.executable).absolute()), 'codex_path': codex,
             'harness_sha256': digest(Path(__file__).read_text()), 'metadata': metadata,
             'latency_seconds': round(time.monotonic()-started, 3),
             'limitations': ['Owned synthetic smoke with stdin closed and reduced environment, while this user session is awake.',
                'Does not validate a sleeping/locked laptop, future token refresh, quotas or entitlement to scheduled account use.',
                'Operator must review account suitability and explicitly configure scheduled model use.']}, [qualification])
    return {'probe': key, 'metadata': metadata}


def authorize_unattended(store, probe, reviewer, permission_reference):
    from tools.research_outcomes import artifact
    text(reviewer); text(permission_reference)
    with store.transaction() as state:
        row = artifact(state, probe, ('unattended-probe',))
        require(row['metadata'].get('status') == 'passed' and row['identity'] == qualification_identity() and
                row['harness_sha256'] == digest(Path(__file__).read_text()), 'matching successful probe required')
        key = store.put(state, 'unattended-qualification', {'probe': probe, 'reviewer': reviewer,
                'permission_reference': permission_reference, 'identity': row['identity'],
                'executable': row['executable'], 'codex_path': row['codex_path'],
                'harness_sha256': row['harness_sha256'],
                'limitation': 'Operator assertion of account suitability, not authentication or proof of provider permission.'},
                [probe], use_until=(store.clock()+timedelta(days=7)).isoformat())
    return {'qualification': key}


def unattended_eligible(state, key, store):
    from tools.research_outcomes import artifact
    row = artifact(state, key, ('unattended-qualification',))
    require(row['identity'] == qualification_identity() and row['harness_sha256'] == digest(Path(__file__).read_text()) and
            row['executable'] == str(Path(sys.executable).absolute()) and row['codex_path'] == shutil.which('codex'),
            'unattended environment drift; repeat probe/review')
    qualified(state)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['local', 'probe', 'probe-child', 'authorize'])
    parser.add_argument('--model'); parser.add_argument('--probe'); parser.add_argument('--reviewer'); parser.add_argument('--permission-reference')
    args = parser.parse_args()
    store = Store(private_state_path(ROOT, dict(os.environ)))
    try:
        if args.action == 'local': result = evaluate_local(store, args.model)
        elif args.action == 'probe': result = probe_unattended(store)
        elif args.action == 'authorize': result = authorize_unattended(store, args.probe, args.reviewer, args.permission_reference)
        else:
            with CodexWorker(store.home) as worker:
                output, metadata = worker.run('Owned synthetic automation check. Return {"ok":true}. Do not use tools.',
                    {'type': 'object', 'properties': {'ok': {'type': 'boolean'}}, 'required': ['ok'], 'additionalProperties': False})
            require(output == {'ok': True} and metadata['authentication'] == 'chatgpt', 'subscription probe failed')
            result = {'status': 'passed', 'execution': metadata}
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError):
        print(json.dumps({'status': 'blocked', 'paid_fallback': False})); return 1


if __name__ == '__main__':
    raise SystemExit(main())
