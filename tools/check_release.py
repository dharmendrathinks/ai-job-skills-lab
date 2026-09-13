#!/usr/bin/env python3
"""Local release guards, using the same reviewed base as PR Ready."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def main():
    config = json.loads((ROOT / '.pr-ready.json').read_text())
    base = config['baseRef']
    checks = [
        ['tools/security_guards.py'],
        ['tools/check_framework_version.py', '--base', base],
        ['tools/research_preflight.py', '--mode', 'research', '--action', 'status'],
    ]
    for command in checks:
        result = subprocess.run([sys.executable, *command], cwd=ROOT)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == '__main__':
    sys.exit(main())
