#!/usr/bin/env python3
"""Read-only Phase 1 routing and public-template checks; never initializes data.

These checks protect supported workflow entry points and CI. They are not an
OS sandbox, a secret scanner, or a tool-free model execution mechanism.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = "research-template-manifest.json"
CANONICAL = ".claude/skills/research/SKILL.md"
FUTURE = {"collect": 2, "import": 2, "analyze": 2, "brief": 3,
          "outcome": 4, "refresh": 2, "export": 2}


def private_state_path(root: Path, env: dict[str, str]) -> Path:
    """Resolve without creating a directory; reject paths overlapping source."""
    configured = env.get("AI_JOB_RADAR_HOME")
    if configured is not None:
        if not configured.strip():
            raise ValueError("AI_JOB_RADAR_HOME must not be empty")
        candidate = Path(configured).expanduser()
        if not candidate.is_absolute():
            raise ValueError("AI_JOB_RADAR_HOME must be absolute")
    elif sys.platform == "darwin":
        candidate = Path.home() / "Library/Application Support/ai-job-radar"
    else:
        base = Path(env.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
        if not base.is_absolute():
            raise ValueError("XDG_DATA_HOME must be absolute")
        candidate = base / "ai-job-radar"
    candidate, root = candidate.resolve(), root.resolve()
    if candidate == root or root in candidate.parents or candidate in root.parents:
        raise ValueError("research state must be outside, and not contain, the checkout")
    return candidate


def template_errors(root: Path) -> list[str]:
    """Check reviewed bytes on disk AND staged bytes, without printing payloads."""
    errors: list[str] = []
    try:
        manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
        files = manifest["files"]
        if manifest["schema_version"] != 1 or not isinstance(files, dict) or not files:
            raise ValueError("unsupported or empty template manifest")
        for name, hashes in files.items():
            path = root / name
            if Path(name).is_absolute() or ".." in Path(name).parts:
                raise ValueError("invalid manifest path")
            if (not isinstance(hashes, list) or not hashes
                    or any(not isinstance(h, str) or len(h) != 64
                           or any(c not in "0123456789abcdef" for c in h) for h in hashes)):
                raise ValueError("invalid reviewed hash list")
            if path.is_symlink() or not path.is_file():
                errors.append(f"template missing or symlinked: {name}")
            elif hashlib.sha256(path.read_bytes()).hexdigest() not in hashes:
                errors.append(f"template differs from reviewed public content: {name}")
            staged = subprocess.run(["git", "show", f":{name}"], cwd=root,
                                    capture_output=True, check=False)
            if staged.returncode:
                errors.append(f"template missing from Git index: {name}")
            elif hashlib.sha256(staged.stdout).hexdigest() not in hashes:
                errors.append(f"staged template differs from reviewed public content: {name}")
        ignored = subprocess.run(
            ["git", "ls-files", "-ci", "--exclude-standard", "-z"], cwd=root,
            capture_output=True, check=False)
        if ignored.returncode:
            errors.append("cannot check Git tracking")
        else:
            errors.extend(f"ignored file is still tracked: {name}"
                          for name in ignored.stdout.decode("utf-8").split("\0") if name)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"template check unavailable: {type(exc).__name__}")
    return errors


def portal_skills(root: Path) -> list[str]:
    return sorted(p.parent.name for p in (root / ".agents/skills").glob("*/SKILL.md")
                  if (p.parent / "cli/package.json").is_file()
                  and (p.parent / "cli/src/cli.ts").is_file())


def assess(root: Path, mode: str, action: str,
           env: dict[str, str] | None = None) -> dict:
    root = root.resolve()
    errors = template_errors(root)
    state = None
    try:
        state = str(private_state_path(root, dict(os.environ) if env is None else env))
    except ValueError as exc:
        errors.append(str(exc))
    blockers: list[str] = []
    if mode == "application":
        if action in ("setup", "profile-write", "configure"):
            blockers.append("public_template_profile_write_blocked")
        elif action != "status":
            blockers.append("use_explicit_upstream_application_command")
    elif action in FUTURE:
        blockers.append(f"capability_not_implemented_until_phase_{FUTURE[action]}")
    elif action not in ("status", "configure"):
        blockers.append("application_setup_not_used_by_research")
    return {
        "schema_version": 1,
        "mode": mode,
        "action": action,
        "status": "blocked" if errors or blockers else "ready_for_phase_1_only",
        "canonical_spec": CANONICAL if mode == "research" else ".claude/",
        "state_path": state,
        "writes_runtime_data": False,
        "template_errors": errors,
        "blockers": blockers,
        "extraction": {"qualification": "unverified", "enabled": False,
                       "reason": "complete_tool_free_codex_mechanism_not_verified"},
        "sources_enabled": [],
        "installed_portal_skills": portal_skills(root),
        "inference": {"authentication": "existing_codex_subscription",
                      "additional_spending_inr": 0, "paid_fallback": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["research", "application"], default="research")
    parser.add_argument("--action", choices=["status", "configure", "setup", "profile-write", *FUTURE],
                        default="status")
    args = parser.parse_args()
    result = assess(ROOT, args.mode, args.action)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
