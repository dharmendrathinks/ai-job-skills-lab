"""Bounded research refresh, durable inbox, managed HTML and operator schedules.

No arbitrary shell steps, automatic retries, publishing or application-state use.
"""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import sys
import subprocess

from tools.rank_state import save_state
from tools.research_evidence import (digest, fields, require, text, timestamp)
from tools.research_recovery import read, regular, backup
from tools.research_outcomes import artifact, latest_decisions


@contextmanager
def run_lock(store):
    with store.locked():
        pass  # private path/permissions validated by existing state helper
    fd = os.open(store.home / 'operations.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'r+') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('research operation already running') from None
        yield


def ledger(store):
    path = store.home / 'operations.json'
    marker = store.home / 'operations-origin.json'
    regular(marker)
    if not path.exists() and not path.is_symlink():
        require(not marker.exists(), 'operations ledger lost; manual reconciliation required')
        empty = {'schema_version': 1, 'runs': {}, 'slots': {}, 'deliveries': {}, 'health': []}
        # Two-file initialization can fail closed after a crash, never recreate old intents.
        save_state(path, empty)
        save_state(marker, {'schema_version': 1})
    require(marker.exists() and read(marker) == {'schema_version': 1}, 'operations origin missing or corrupt')
    row = read(path)
    fields(row, ['schema_version', 'runs', 'slots', 'deliveries', 'health'])
    require(row['schema_version'] == 1, 'unsupported operations schema')
    return row


def save_ledger(store, row):
    regular(store.home / 'operations.json')
    save_state(store.home / 'operations.json', row)


def monitor(store, row, status):
    # Fixed categories only; never copy exception text, queries or source prose.
    require(status in ('ok', 'failed', 'interrupted', 'blocked'), 'invalid monitor status')
    row['health'] = (row['health'] + [{'at': store.clock().isoformat(), 'status': status}])[-100:]
    save_ledger(store, row)


def inbox_rows(state, now):
    decisions = {v['brief']: (k, v) for k, v in latest_decisions(state).items()}
    briefs = {k:a['payload'] for k,a in state['artifacts'].items() if a['kind'] == 'brief'}
    revised = {b.get('revises') for b in briefs.values()}
    rows = []
    for key, brief in sorted(briefs.items()):
        if key in revised:
            continue
        pair = decisions.get(key)
        status = 'new'
        if pair:
            if pair[1]['decision'] != 'deferred':
                continue
            status = 'due' if timestamp(pair[1]['defer_until']) <= now else 'deferred'
        # Repeated renders preserve identity; due reminders change only on explicit re-deferral.
        identity = digest([brief.get('recommendation_id', key), brief.get('revision', 1),
                           brief.get('evidence_basis', []), pair[0] if pair else None])
        shown = any(a['kind'] == 'presentation' and a['payload']['identity'] == identity
                    for a in state['artifacts'].values())
        rows.append({'brief': key, 'identity': identity, 'status': status,
                     'presented': shown, 'decision': pair[0] if pair else None,
                     'kind': brief['kind'], 'revision': brief.get('revision', 1)})
    return rows


def inbox(store, limit=20, *, acknowledge=False):
    require(type(limit) is int and 1 <= limit <= 100, 'inbox limit must be 1–100')
    with store.transaction() as state:
        rows = inbox_rows(state, store.clock())
        pending = [r for r in rows if r['status'] != 'deferred' and not r['presented']]
        selected = pending[:limit]
        if acknowledge:
            for row in selected:
                store.put(state, 'presentation', {'identity': row['identity'], 'at': store.clock().isoformat(),
                          'meaning': 'explicit local acknowledgment, not acceptance or usefulness'},
                          [row['brief']] + ([row['decision']] if row['decision'] else []))
        return {'items': selected, 'overflow': len(pending) - len(selected),
                'deferred': sum(r['status'] == 'deferred' for r in rows),
                'previously_presented': sum(r['presented'] for r in rows)}


def report(store, limit=20):
    from tools.research_reports import render
    from tools.research_report_files import paths
    require(type(limit) is int and 1 <= limit <= 1000, 'report limit must be 1–1000')
    with store.transaction() as state:
        pages, dependencies, counts = render(state, store.clock().isoformat(), limit)
        require(all(len(html.encode()) <= 16_000_000 for html in pages.values()),
                'HTML budget exceeded; lower report limit')
        previous = [k for k,a in state['artifacts'].items() if a['kind'] == 'offline-report']
        revision = 1 + max([state['artifacts'][k]['payload'].get('revision', 0) for k in previous], default=0)
        store.remove(state, previous)
        key = store.put(state, 'offline-report', {'schema_version': 2, 'revision': revision,
                        'created_at': store.clock().isoformat(), 'pages': pages, 'counts': counts}, dependencies)
    with store.transaction() as state:
        artifact(state, key, ('offline-report',))
    targets = paths(store)
    return {'report': key, 'path': str(targets['projects.html']),
            'jobs': {'path': str(targets['jobs.html']), **counts['jobs']},
            'projects': {'path': str(targets['projects.html']), **counts['projects']},
            'youtube': {'path': str(targets['projects.html']), **counts['youtube']},
            'shown': counts['projects']['shown'] + counts['youtube']['shown'],
            'overflow': sum(counts[k]['total'] - counts[k]['shown'] for k in ('projects', 'youtube'))}


def configure(store, row):
    fields(row, ['schema_version', 'collect', 'analyze', 'brief_kinds', 'contexts', 'profile',
                 'analysis_limit', 'report_limit', 'backup', 'interval_seconds', 'reviewer'],
           ['unattended_qualification'])
    require(row['schema_version'] == 1 and type(row['analyze']) is bool and type(row['backup']) is bool,
            'invalid operation plan')
    text(row['reviewer'])
    require(type(row['analysis_limit']) is int and 1 <= row['analysis_limit'] <= 20 and
            type(row['report_limit']) is int and 1 <= row['report_limit'] <= 1000 and
            type(row['interval_seconds']) is int and 3600 <= row['interval_seconds'] <= 604800,
            'invalid operation budgets/cadence')
    from tools.research_briefs import SECTIONS
    require(isinstance(row['brief_kinds'], list) and len(row['brief_kinds']) <= 4 and
            len(set(row['brief_kinds'])) == len(row['brief_kinds']) and
            set(row['brief_kinds']) <= set(SECTIONS), 'unknown/duplicate brief workflows')
    require(isinstance(row['contexts'], list) and len(row['contexts']) <= 10, 'context budget exceeded')
    if row['collect'] is not None:
        fields(row['collect'], ['source', 'query', 'count'])
        require(row['collect']['source'] == 'jobicy', 'conditional provider not enabled')
        require(isinstance(row['collect']['query'], str) and 3 <= len(row['collect']['query']) <= 50 and
                type(row['collect']['count']) is int and 1 <= row['collect']['count'] <= 100,
                'invalid capture request')
    with store.transaction() as state:
        for key in row['contexts']:
            artifact(state, key, ('context',))
        deps = list(row['contexts'])
        if row['profile']:
            artifact(state, row['profile'], ('research-profile',)); deps.append(row['profile'])
        if row.get('unattended_qualification'):
            artifact(state, row['unattended_qualification'], ('unattended-qualification',))
        # Non-owning hash references: expired optional inputs block only their step.
        # The plan contains user configuration, never copied source/profile prose.
        return {'plan': store.put(state, 'operation-plan', row)}


def task_result_ids(value):
    if isinstance(value, str):
        return [value] if re.fullmatch('[0-9a-f]{64}', value) else []
    if isinstance(value, dict):
        return [x for v in value.values() for x in task_result_ids(v)]
    if isinstance(value, list):
        return [x for v in value for x in task_result_ids(v)]
    return []


def execute(store, plan_id, *, resume=None, scheduled=False, _handlers=None):
    with run_lock(store):
        return _execute(store, plan_id, resume=resume, scheduled=scheduled, handlers=_handlers)


def _execute(store, plan_id, *, resume=None, scheduled=False, handlers=None):
    from tools.research_sources import collect_jobicy
    from tools.research_analysis import analyze
    from tools.research_briefs import generate
    unattended_allowed = True
    with store.transaction() as state:
        plan = artifact(state, plan_id, ('operation-plan',))
        if scheduled and (plan['analyze'] or plan['brief_kinds']):
            from tools.research_model_eval import unattended_eligible
            try:
                unattended_eligible(state, plan.get('unattended_qualification'), store)
            except (ValueError, OSError, subprocess.SubprocessError):
                unattended_allowed = False
    log = ledger(store)
    run_id = resume or digest([plan_id, store.clock().isoformat(), len(log['runs'])])
    if resume:
        require(run_id in log['runs'] and log['runs'][run_id]['plan'] == plan_id, 'resume run/plan mismatch')
    else:
        log['runs'][run_id] = {'plan': plan_id, 'started_at': store.clock().isoformat(),
                               'steps': {}, 'status': 'running', 'analysis_queue': None, 'overflow': 0}
    run = log['runs'][run_id]
    # A process died after intent was persisted: do not repeat the uncertain call.
    for record in run['steps'].values():
        if record['status'] == 'running':
            record['status'] = 'ambiguous'
    save_ledger(store, log)

    def step(name, action):
        previous = run['steps'].get(name)
        if previous and previous['status'] != 'retry-approved':
            return previous if previous['status'] == 'done' else None
        run['steps'][name] = {'status': 'running', 'ids': []}
        save_ledger(store, log)
        try:
            value = handlers[name]() if handlers and name in handlers else action()
            record = {'status': 'done', 'ids': task_result_ids(value)}
        except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError):
            record = {'status': 'deferred', 'ids': []}
        run['steps'][name] = record
        save_ledger(store, log)
        return record if record['status'] == 'done' else None

    step('cleanup', store.status)
    if plan['collect']:
        step('collect', lambda: collect_jobicy(store, plan['collect']['query'], plan['collect']['count'], scheduled=scheduled))
    model_blocked = any(rid != run_id and r['plan'] == plan_id and
                        any((n.startswith('analyze:') or n.startswith('brief:')) and v['status'] != 'done'
                            for n,v in r['steps'].items()) for rid,r in log['runs'].items())
    run['model_gate'] = ('requires-unattended-qualification' if not unattended_allowed else
                         'blocked-by-prior-run' if model_blocked else 'open')
    model_blocked = model_blocked or not unattended_allowed
    if plan['analyze'] and not model_blocked:
        if run['analysis_queue'] is None:
            with store.transaction() as state:
                from tools.research_analysis import analysis_versions
                from tools.research_domains import pack_for
                expected = analysis_versions({}, pack_for(state))
                expected.pop('runtime')  # runtime qualification is checked before new invocations
                done = set()
                for a in state['artifacts'].values():
                    if a['kind'] != 'analysis':
                        continue
                    if a['payload'].get('method') != 'codex-extraction':
                        done.add(a['payload']['observation']); continue
                    execution = state['artifacts'].get(a['payload'].get('execution'), {}).get('payload', {})
                    if all(execution.get('versions', {}).get(k) == v for k,v in expected.items()):
                        done.add(a['payload']['observation'])
                # Prior failed executions require review; no quota retry loop across scheduled runs.
                blocked = {a['payload']['input_revision'] for a in state['artifacts'].values()
                           if a['kind'] == 'execution' and a['payload']['status'] != 'validated'}
                pending = sorted(k for k,a in state['artifacts'].items() if a['kind'] == 'observation' and k not in done | blocked)
                # Include ambiguous ops from earlier runs, even if source helpers did not commit an execution.
                uncertain = {name.split(':', 1)[1] for r in log['runs'].values() for name, v in r['steps'].items()
                             if name.startswith('analyze:') and v['status'] != 'done'}
                pending = [k for k in pending if k not in uncertain]
                run['analysis_queue'] = pending[:plan['analysis_limit']]
                run['overflow'] = max(0, len(pending)-plan['analysis_limit'])
            save_ledger(store, log)
        for key in run['analysis_queue']:
            if model_blocked:
                run['steps'].setdefault('analyze:' + key, {'status': 'deferred', 'ids': []})
            elif not step('analyze:' + key, lambda key=key: analyze(store, key)):
                model_blocked = True
    snap = step('snapshot', store.snapshot)
    if snap and run['model_gate'] == 'open':
        for kind in plan['brief_kinds']:
            # Semantic repetition checks remain in P4. Uncertain attempts with the
            # same plan/snapshot/kind need operator review before another invocation.
            label = 'brief:' + kind + ':' + snap['ids'][0]
            uncertain = any(label in r['steps'] and r['steps'][label]['status'] != 'done'
                            for rid,r in log['runs'].items() if rid != run_id and r['plan'] == plan_id)
            if uncertain or model_blocked:
                run['steps'][label] = {'status': 'deferred', 'ids': []}
            else:
                if not step(label, lambda kind=kind: generate(store, kind, snap['ids'][0], plan['contexts'], plan['profile'])):
                    model_blocked = True
    step('report', lambda: report(store, plan['report_limit']))
    if plan['backup']:
        step('backup', lambda: backup(store))
    run['status'] = 'complete' if run['model_gate'] == 'open' and all(s['status'] == 'done' for s in run['steps'].values()) else 'needs-review'
    run['finished_at'] = store.clock().isoformat()
    monitor(store, log, 'ok' if run['status'] == 'complete' else 'blocked')
    return {'run': run_id, **run}


def resolve_step(store, run_id, name, action, reviewer, reason):
    """An explicit operator reconciliation; never infer remote success."""
    text(reviewer); text(reason)
    require(action in ('retry', 'skip'), 'resolution must be retry or skip')
    require(isinstance(name, str) and (name == 'collect' or name.startswith(('analyze:', 'brief:'))),
            'only external/model steps use manual reconciliation')
    with run_lock(store):
        log = ledger(store)
        require(run_id in log['runs'], 'run unavailable')
        run = log['runs'][run_id]
        require(name in run['steps'] and run['steps'][name]['status'] != 'done', 'step does not need review')
        with store.transaction() as state:
            artifact(state, run['plan'], ('operation-plan',))
            review = store.put(state, 'operation-review', {'run': run_id, 'step': name, 'action': action,
                'reviewer': reviewer, 'reason': reason, 'at': store.clock().isoformat(),
                'limitation': 'Retry may duplicate an uncertain prior invocation; skip is not proof of success.'}, [run['plan']])
        run['steps'][name] = {'status': 'retry-approved' if action == 'retry' else 'done',
                              'ids': [], 'resolution': review, 'skipped': action == 'skip'}
        save_ledger(store, log)
        return {'review': review, 'run': run_id, 'resume_required': True}


def tick(store, plan_id):
    with run_lock(store):
        log = ledger(store)
        try:
            with store.transaction() as state:
                plan = artifact(state, plan_id, ('operation-plan',))
            slot = int(store.clock().timestamp()) // plan['interval_seconds']
            previous = log['slots'].get(plan_id)
            if previous and slot <= previous['slot']:
                return {'status': 'not-due', 'slot': slot}
            missed = max(0, slot - previous['slot'] - 1) if previous else None
            # Intent before execution: a killed tick consumes its slot, never fakes past captures.
            log['slots'][plan_id] = {'slot': slot, 'missed': missed, 'status': 'running'}
            save_ledger(store, log)
            result = _execute(store, plan_id, scheduled=True)
            log = ledger(store)
            log['slots'][plan_id].update(status=result['status'], run=result['run'])
            save_ledger(store, log)
            return {'missed_slots': missed, **result}
        except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError):
            log = ledger(store)
            if plan_id in log['slots']:
                log['slots'][plan_id]['status'] = 'blocked'
            monitor(store, log, 'failed')
            raise


def health(store):
    with run_lock(store):
        log = ledger(store)
        try:
            status = store.status()
        except (ValueError, OSError):
            monitor(store, log, 'failed')
            return {'status': 'failed', 'action': 'inspect private state; do not auto-restore'}
        return {'status': 'ok', **status, 'recent_checks': log['health'], 'slots': log['slots'],
                'runs_needing_review': [k for k,r in log['runs'].items() if r['status'] != 'complete'],
                'ambiguous_deliveries': [k for k,r in log['deliveries'].items() if r['status'] != 'sent']}


def launchd(store, plan_id):
    with store.transaction() as state:
        artifact(state, plan_id, ('operation-plan',))
    root = Path(__file__).resolve().parents[1]
    executable = Path(sys.executable).absolute()  # preserve venv path, don't resolve its symlink
    row = {'Label': 'local.ai-job-radar.' + plan_id[:12], 'ProgramArguments': [str(executable), '-m',
           'tools.research_ops', 'tick', '--plan', plan_id], 'WorkingDirectory': str(root),
           'EnvironmentVariables': {'AI_JOB_RADAR_HOME': str(store.home), 'PATH': '/usr/bin:/bin:/usr/sbin:/sbin',
                                    'HOME': str(Path.home())},
           'StartInterval': 300, 'RunAtLoad': True, 'ProcessType': 'Background', 'Umask': 0o077,
           'StandardOutPath': '/dev/null', 'StandardErrorPath': '/dev/null'}
    codex = shutil.which('codex')
    if codex:
        row['EnvironmentVariables']['PATH'] = str(Path(codex).parent) + ':' + row['EnvironmentVariables']['PATH']
    # Generate only. Never install/bootstrap a persistent agent as a side effect.
    return plistlib.dumps(row).decode()
