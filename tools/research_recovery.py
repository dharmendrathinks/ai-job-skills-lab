"""Managed local copies and monotone withdrawal journal, under Store's lock.

Reuses the upstream atomic JSON writer. Logical deletion only; not an encrypted
backup service, physical erasure, hostile-process boundary or power-loss WAL.
"""
import json
import os
from pathlib import Path
import stat
import tempfile

from tools.rank_state import save_state
from tools.research_evidence import VERSION, digest, fields, require, timestamp


def regular(path):
    require(not path.is_symlink(), 'managed path may not be a symlink')
    if path.exists():
        require(path.is_file() and stat.S_IMODE(path.stat().st_mode) & 0o077 == 0,
                'managed file must be regular and private')


def read(path):
    regular(path)
    try:
        return json.loads(path.read_text())
    except (ValueError, UnicodeError):
        raise ValueError('corrupt managed JSON; explicit recovery required') from None


def journal(store, state=None):
    path = store.home / 'withdrawals.json'
    if not path.exists() and not path.is_symlink():
        require(state is not None and not (store.home / 'backup.json').exists(),
                'withdrawal journal missing; restore blocked')
        save_state(path, {'schema_version': 1, 'withdrawn': state['withdrawn']})
    row = read(path)
    fields(row, ['schema_version', 'withdrawn'])
    require(row['schema_version'] == 1 and isinstance(row['withdrawn'], list) and
            all(isinstance(x, str) and len(x) == 64 and all(c in '0123456789abcdef' for c in x)
                for x in row['withdrawn']), 'invalid withdrawal journal')
    return row


def apply_journal(store, state):
    row = journal(store, state)
    removed = set(row['withdrawn']) | set(state['withdrawn'])
    ids = set(state['artifacts']) & removed
    for key, a in state['artifacts'].items():
        p = a['payload']
        if a['kind'] == 'observation' and digest(['withdrawn-description', p['description']]) in removed:
            ids.add(key)
        if a['kind'] == 'context' and (digest(['withdrawn-context', p['content']]) in removed or
                                      removed.intersection(p.get('content_fingerprints', []))):
            ids.add(key)
        if a['kind'] == 'interchange-item' and removed.intersection(p['lineage']):
            ids.add(key)
    state['withdrawn'] = sorted(removed)
    if ids:
        store.remove(state, ids)


def persist(store, path, state):
    """Journal precedes primary replacement; stale backups fail closed on restore."""
    regular(path)
    row = journal(store, state)
    merged = sorted(set(row['withdrawn']) | set(state['withdrawn']))
    if merged != row['withdrawn']:
        save_state(store.home / 'withdrawals.json', {'schema_version': 1, 'withdrawn': merged})
    state['withdrawn'] = merged
    backup_path = store.home / 'backup.json'
    if backup_path.exists() or backup_path.is_symlink():
        regular(backup_path)
        try:
            backup = read(backup_path)
            valid = backup.get('withdrawal_digest') == digest(merged) and all(
                not a['use_until'] or timestamp(a['use_until']) > store.clock()
                for a in backup['state']['artifacts'].values())
        except (ValueError, KeyError, TypeError):
            valid = False
        if not valid:
            backup_path.unlink()  # conservative whole-copy invalidation
    # A stale HTML file is removed before the primary state can advertise deletion.
    view = store.home / 'research-report.html'
    regular(view)
    if view.exists():
        view.unlink()
    save_state(path, state)
    reports = [(a['payload']['created_at'], key, a['payload']['html'])
               for key,a in state['artifacts'].items() if a['kind'] == 'offline-report']
    if reports:
        materialize(store, max(reports)[2])


def materialize(store, html):
    path = store.home / 'research-report.html'
    regular(path)
    fd, temporary = tempfile.mkstemp(prefix='.research-view.', dir=store.home)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(html)
        os.replace(temporary, path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()
    return path


def validate_state(state):
    fields(state, ['schema_version', 'artifacts', 'withdrawn'])
    require(state['schema_version'] == VERSION and isinstance(state['artifacts'], dict) and
            isinstance(state['withdrawn'], list), 'invalid backup state')
    for key, a in state['artifacts'].items():
        fields(a, ['schema_version', 'kind', 'payload', 'dependencies', 'use_until'])
        require(digest(a) == key and key not in state['withdrawn'] and
                all(d in state['artifacts'] for d in a['dependencies']), 'invalid backup lineage/hash')


def backup(store):
    # Fixed private destination; no shell, remote location, or unmanaged copy.
    with store.transaction() as state:
        for a in state['artifacts'].values():
            if a['kind'] == 'policy':
                require(a['payload']['retention'] == 'indefinite-logical-deletion', 'unsupported backup retention')
        row = {'schema_version': 1, 'created_at': store.clock().isoformat(),
               'withdrawal_digest': digest(journal(store)['withdrawn']), 'state': state,
               'state_digest': digest(state)}
        path = store.home / 'backup.json'
        regular(path)
        save_state(path, row)
        return {'backup': row['state_digest'], 'artifacts': len(state['artifacts'])}


def restore(store):
    # Use the same lock but do not try to parse a potentially corrupt primary.
    from tools.research_operations import run_lock, ledger
    with run_lock(store), store.locked():
        ledger(store)  # never silently reset uncertain external intents during recovery
        row = journal(store)  # never recreate from an old backup
        copy = read(store.home / 'backup.json')
        fields(copy, ['schema_version', 'created_at', 'withdrawal_digest', 'state', 'state_digest'])
        require(copy['schema_version'] == 1 and copy['withdrawal_digest'] == digest(row['withdrawn']) and
                copy['state_digest'] == digest(copy['state']), 'backup stale, corrupt or withdrawn')
        state = copy['state']
        validate_state(state)
        apply_journal(store, state)
        store.sweep(state)
        persist(store, store.home / 'research-state.json', state)
        return {'restored_artifacts': len(state['artifacts']), 'withdrawn_hashes': len(state['withdrawn'])}
