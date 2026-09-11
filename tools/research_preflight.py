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
STATE_ENV = "AI_JOB_SKILLS_LAB_HOME"
LEGACY_STATE_ENV = "AI_JOB_RADAR_HOME"  # Compatibility with existing private workspaces.
FUTURE = {"collect": 2, "import": 2, "analyze": 2, "brief": 3,
          "outcome": 4, "refresh": 2, "export": 2, "coverage": 5, "compare": 5, "translate": 5, "domain": 7}


def private_state_path(root: Path, env: dict[str, str]) -> Path:
    """Resolve without creating a directory; reject paths overlapping source."""
    configured = env.get(STATE_ENV)
    legacy = env.get(LEGACY_STATE_ENV)
    if configured is not None and legacy is not None and Path(configured).expanduser() != Path(legacy).expanduser():
        raise ValueError("conflicting current and legacy research workspace variables")
    if configured is None: configured = legacy
    if configured is not None:
        if not configured.strip():
            raise ValueError("AI_JOB_SKILLS_LAB_HOME must not be empty")
        candidate = Path(configured).expanduser()
        if not candidate.is_absolute():
            raise ValueError("AI_JOB_SKILLS_LAB_HOME must be absolute")
    else:
        base = Path.home() / "Library/Application Support" if sys.platform == "darwin" else Path(env.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
        if not base.is_absolute():
            raise ValueError("XDG_DATA_HOME must be absolute")
        candidate = base / "ai-job-skills-lab"
        previous = base / "ai-job-radar"
        if previous.exists():
            if candidate.exists():
                raise ValueError("both current and legacy data directories exist; select an explicit private workspace")
            candidate = previous  # Never hide an existing corpus behind an empty new default.
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
    elif action in ("import", "collect", "analyze", "refresh", "brief", "outcome", "coverage", "compare", "translate", "domain"):
        pass  # Readiness only; execution checks qualification and current source policy.
    elif action == "export":
        blockers.append("unmanaged_exports_not_supported")
    elif action in FUTURE:
        blockers.append(f"capability_not_implemented_until_phase_{FUTURE[action]}")
    elif action not in ("status", "configure"):
        blockers.append("application_setup_not_used_by_research")
    return {
        "schema_version": 1,
        "mode": mode,
        "action": action,
        "status": "blocked" if errors or blockers else (
            "ready_for_gated_research" if mode == "research" else "ready_for_application_routing"),
        "canonical_spec": CANONICAL if mode == "research" else ".claude/",
        "state_path": state,
        "writes_runtime_data": False,
        "template_errors": errors,
        "blockers": blockers,
        "extraction": {"qualification": "checked_by_execution_helper", "enabled": False,
                       "reason": "read_only_preflight_does_not_qualify_or_invoke_runtime"},
        "sources_enabled": [],
        "phase_2": {"reviewed_local_import": "available_with_supported_policy",
                    "human_annotation_and_snapshot": "available",
                    "retention": "logical_deletion_only_no_hard_deadlines",
                    "live_collection": "jobicy_explicit_invocation_with_current_policy",
                    "model_analysis": "requires_matching_runtime_qualification_and_source_permission",
                    "completion": "see_phase2_validation_record"},
        "phase_3": {"draft_briefs": "four_types_require_qualified_evidence",
                    "context": "reviewed_import_or_explicit_bounded_acquisition",
                    "radar_import": "selected_schema_3_0_report_only",
                    "profile": "proposal_and_explicit_review_no_application_writes"},
        "phase_4": {
            "outcomes": "explicit_revision_ledger_observed_self_reported_model_inferred",
            "memory": "reviewed_reconsideration_required_for_blocked_recommendations",
            "profile": "scoped_test_outcome_proposal_requires_review",
            "interchange": "reviewed_1_0_projections_only_with_compatible_export_permission",
            "imported_outcomes": "assessments_only_no_automatic_profile_or_market_evidence"
        },
        "phase_5": {
            "coverage": "source_receipts_segments_unknowns_and_reviewed_board_identity",
            "cohorts": "equal_windows_frozen_protocol_and_cadence_sufficiency_required",
            "languages": "indexed_translation_proposals_and_explicit_review_no_eligibility_filter",
            "source_registry": "all_candidates_recorded_only_existing_jobicy_go_limited",
            "promotion": "conditional_source_and_language_quality_evidence_required"
        },
        "phase_7": {
            "default_domain": "ai-engineering",
            "opt_in": "backend_platform_requires_empty_explicit_private_workspace",
            "binding": "immutable_pack_digest_and_taxonomy_no_historical_reclassification",
            "comparison": "local_descriptive_samples_no_pooled_demand_ratio",
            "evaluation": "owned_fixtures_and_pending_human_domain_quality_review"
        },
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
