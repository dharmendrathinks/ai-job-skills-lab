"""Fixed managed report destinations; corpus and journals remain outside Git."""
import os
from pathlib import Path
import subprocess
import tempfile

from tools.research_evidence import digest, require, private_state_path
from tools.rank_state import save_state

NAMES = ('jobs.html', 'workspace.html', 'projects.html')
LEGACY_NAMES = ('jobs.html', 'projects.html')


def checked_directory(store, repository):
    repository = Path(repository)
    require(repository.is_absolute() and repository == repository.resolve(), 'invalid report repository')
    root = repository / 'reports'
    require(not root.is_symlink(), 'report directory may not be a symlink')
    tracked = subprocess.run(['git', 'ls-files', '--', 'reports'], cwd=repository, capture_output=True, check=True)
    require(not tracked.stdout, 'reports must not be tracked')
    for name in NAMES:
        ignored = subprocess.run(['git', 'check-ignore', '-q', 'reports/' + name],
                                 cwd=repository, capture_output=True)
        require(ignored.returncode == 0, 'report directory must be ignored')
    default = private_state_path(repository, {})
    target = root if store.home.resolve() == default else root / ('workspace-' + digest(str(store.home.resolve()))[:16])
    require(not target.is_symlink(), 'report workspace may not be a symlink')
    return target


def directory(store):
    from tools.research_recovery import read
    config = store.home / 'report-location.json'
    origin = store.home / 'report-origin.json'
    if config.exists() or config.is_symlink() or origin.exists() or origin.is_symlink():
        require(config.exists() and origin.exists(), 'report location lost; reconcile managed copies')
        row = read(config)
        require(read(origin) == row, 'report location mismatch')
        require(set(row) == {'schema_version', 'repository'} and row['schema_version'] == 1,
                'invalid report location')
        target = checked_directory(store, row['repository'])
        require(read(target / '.research-owner.json') == {'schema_version': 1,
                'workspace': digest(str(store.home.resolve()))}, 'report workspace owner mismatch')
        require(target.stat().st_mode & 0o077 == 0, 'report directory must be private')
        return target
    return store.home  # library/fixture use; CLI explicitly binds the repository


def bind(store, repository):
    from tools.research_recovery import read
    with store.locked():
        path = store.home / 'report-location.json'
        row = {'schema_version': 1, 'repository': str(Path(repository).resolve())}
        origin = store.home / 'report-origin.json'
        if path.exists() or path.is_symlink() or origin.exists() or origin.is_symlink():
            require(read(path) == row and read(origin) == row, 'report location changed or lost; reconcile copies')
        target = checked_directory(store, row['repository'])
        # Tighten the explicitly requested ignored directory; never follow aliases.
        root = Path(row['repository']) / 'reports'
        root.mkdir(mode=0o700, exist_ok=True)
        root.chmod(0o700)
        target.mkdir(mode=0o700, exist_ok=True)
        target.chmod(0o700)
        owner = target / '.research-owner.json'
        identity = {'schema_version': 1, 'workspace': digest(str(store.home.resolve()))}
        if owner.exists() or owner.is_symlink():
            require(read(owner) == identity, 'report directory belongs to another workspace')
        else:
            require(not any((target / name).exists() or (target / name).is_symlink() for name in NAMES),
                    'unowned report files require review')
            save_state(owner, identity)
        save_state(origin, row)
        save_state(path, row)


def paths(store):
    target = directory(store)
    return {name: target / name for name in NAMES}


def relocate_default(store, previous_repository, repository, previous_home):
    """Repair binding metadata after an explicit move of checkout + default state.

    Stop writers and move both directories first. Content-addressed artifacts,
    withdrawal history and backups are untouched. Partial metadata updates can be
    resumed with these exact arguments; ordinary operations fail closed meanwhile.
    """
    from tools.research_recovery import read
    old_repo, repo, old_home = map(Path, (previous_repository, repository, previous_home))
    require(all(p.is_absolute() and p == p.resolve() for p in (old_repo, repo, old_home)), 'relocation needs canonical absolute paths')
    require(not old_repo.exists() and not old_home.exists() and old_repo != repo and old_home != store.home.resolve(),
            'move original directories first; do not retain a second writer')
    require(store.home.resolve() == private_state_path(repo, {}), 'relocation supports the default workspace only')
    with store.locked():
        target = checked_directory(store, repo)
        require(target.is_dir() and target.stat().st_mode & 0o077 == 0, 'moved reports directory must remain private')
        old = {'schema_version': 1, 'repository': str(old_repo)}
        new = {'schema_version': 1, 'repository': str(repo)}
        old_owner = {'schema_version': 1, 'workspace': digest(str(old_home))}
        new_owner = {'schema_version': 1, 'workspace': digest(str(store.home.resolve()))}
        for name in ('report-location.json', 'report-origin.json'):
            require(read(store.home / name) in (old, new), 'unexpected report binding; no relocation')
        owner = target / '.research-owner.json'
        require(read(owner) in (old_owner, new_owner), 'moved reports belong to another workspace')
        save_state(owner, new_owner)
        save_state(store.home / 'report-origin.json', new)
        save_state(store.home / 'report-location.json', new)
    return {'repository': str(repo), 'state': str(store.home), 'reports': str(target)}


def remove_views(store):
    from tools.research_recovery import regular
    targets = [store.home / 'research-report.html', *paths(store).values()]
    target = directory(store)
    # Interrupted materializations are also derived content, removed on next use.
    targets += list(target.glob('.research-view.*')) if target.exists() else []
    for path in targets:
        regular(path)
        if path.exists():
            path.unlink()


def write(store, name, html):
    from tools.research_recovery import regular
    require(name in NAMES or name == 'research-report.html', 'unknown report name')
    path = store.home / name if name == 'research-report.html' else paths(store)[name]
    regular(path)
    fd, temporary = tempfile.mkstemp(prefix='.research-view.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(html)
        os.replace(temporary, path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()
    return path
