#!/usr/bin/env python3
"""Private evidence lifecycle and deterministic validation; gated acquisition/analysis.

Use `python3 -m tools.research_evidence --help` from the checkout. All content
stays in one atomic state file; stdout contains only operation IDs and counts.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from tools.rank_state import save_state
from tools.research_preflight import ROOT, private_state_path, template_errors

VERSION = 1
MAX_INPUT_BYTES = 2_000_000
TAXONOMY = {
    "version": "ai-capabilities/1",
    "capabilities": ["ai-product-engineering", "agent-tool-engineering",
                     "retrieval-knowledge", "data-pipelines", "evaluation",
                     "reliability-observability", "security", "inference-deployment",
                     "ml-engineering", "model-research"],
}


class EvidenceError(ValueError):
    """Fail closed without echoing imported content."""


def require(condition, message):
    if not condition:
        raise EvidenceError(message)


def utcnow():
    return datetime.now(timezone.utc)


def timestamp(value):
    require(isinstance(value, str), "timestamp must be an ISO string")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(result.tzinfo is not None, "timestamp must include timezone")
        return result.astimezone(timezone.utc)
    except ValueError:
        raise EvidenceError("invalid timestamp") from None


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def fields(value, required, optional=()):
    require(isinstance(value, dict), "expected object")
    require(set(required) <= value.keys() <= set(required) | set(optional),
            "missing or unsupported fields")


def text(value, maximum=1000):
    require(isinstance(value, str) and 0 < len(value) <= maximum,
            "expected bounded nonempty text")


def strings(value, maximum=100):
    require(isinstance(value, list) and len(value) <= maximum, "expected bounded list")
    for item in value:
        text(item)


def read_input(path):
    path = Path(path)
    require(not path.is_symlink() and path.is_file(), "input must be a regular file")
    require(path.stat().st_size <= MAX_INPUT_BYTES, "input exceeds byte budget")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError):
        raise EvidenceError("input is not valid UTF-8 JSON") from None


def validate_policy(policy, now):
    fields(policy, ["schema_version", "source", "method", "reviewed_by", "reviewed_at",
                    "permission_basis", "permission_reference", "local_processing",
                    "retention", "hosted_disclosure", "export", "audit_hashes",
                    "limitations"], ["use_until", "hosted_retention", "hosted_permission_reference",
                    "export_permission_reference", "export_retention"])
    require(policy["schema_version"] == VERSION, "unsupported policy schema")
    for key in ("source", "reviewed_by", "permission_basis", "permission_reference"):
        text(policy[key])
    require(timestamp(policy["reviewed_at"]) <= now, "future policy review")
    require(policy["method"] in ("reviewed-local-import", "jobicy-api-v2", "reviewed-context"), "collector not qualified")
    require(policy["local_processing"] is True and policy["audit_hashes"] is True,
            "processing and minimal withdrawal hashes require permission")
    require(type(policy["hosted_disclosure"]) is bool and type(policy["export"]) is bool,
            "invalid hosted permission or unsupported unmanaged export")
    if policy['export']:
        text(policy.get('export_permission_reference'))
        require(policy.get('export_retention') == 'no-recall-required' and not policy.get('use_until'),
                'interchange cannot guarantee downstream deletion or expiry')
    else:
        require('export_permission_reference' not in policy and 'export_retention' not in policy,
                'export permission fields require explicit enabled policy')
    if policy["hosted_disclosure"]:
        require(policy.get("hosted_retention") == "provider-managed-no-deletion-deadline",
                "hosted deletion guarantees are unavailable")
        text(policy.get("hosted_permission_reference"))
    require(policy["retention"] == "indefinite-logical-deletion",
            "hard deadlines, backup recall and physical erasure are unsupported")
    strings(policy["limitations"])
    if policy.get("use_until") is not None:
        require(timestamp(policy["use_until"]) > now, "policy use authorization expired")


def validate_receipt(receipt, source, now):
    fields(receipt, ["schema_version", "source", "kind", "query", "requested_filters",
                     "effective_filters", "started_at", "finished_at", "pages",
                     "completeness", "limitations"])
    require(receipt["schema_version"] == VERSION and receipt["source"] == source,
            "receipt schema or source mismatch")
    require(receipt["kind"] in ("synthetic", "job", "context"), "unsupported receipt kind")
    text(receipt["query"])
    for key in ("requested_filters", "effective_filters"):
        require(isinstance(receipt[key], dict), "filters must be objects")
    require(timestamp(receipt["started_at"]) <= timestamp(receipt["finished_at"]) <= now,
            "invalid receipt period")
    require(receipt["completeness"] in ("complete-request", "partial", "failed", "blocked"),
            "completeness must describe the bounded request")
    require(isinstance(receipt["pages"], list) and len(receipt["pages"]) <= 100,
            "invalid pages")
    for page in receipt["pages"]:
        fields(page, ["locator", "status", "returned", "next_cursor"])
        text(page["locator"])
        require(page["status"] in ("ok", "failed", "blocked"), "invalid page status")
        require(type(page["returned"]) is int and page["returned"] >= 0,
                "invalid page count")
        if page["next_cursor"] is not None:
            text(page["next_cursor"])
    strings(receipt["limitations"])


def validate_observation(row, now):
    fields(row, ["native_id", "employer_name", "employer_domain", "employer_requisition",
                 "url", "title", "description", "captured_at", "source_revision",
                 "posted_at_original", "posted_at", "language", "country",
                 "availability", "availability_evidence", "segments", "limitations"],
           ["raw_description", "description_transform"])
    if "raw_description" in row:
        from tools.research_sources import html_text
        text(row["raw_description"], 150_000)
        require(row.get("description_transform") == "html-text/1" and
                html_text(row["raw_description"]) == row["description"], "description transform mismatch")
    for key in ("native_id", "url", "title", "source_revision"):
        text(row[key])
    for key in ("employer_name", "employer_requisition", "posted_at_original", "language", "country"):
        if row[key] is not None:
            text(row[key])
    domain = row["employer_domain"]
    if domain is not None:
        require(isinstance(domain, str) and re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\.[a-z]{2,}", domain),
                "employer domain must be reviewed, normalized and non-ATS")
    require(timestamp(row["captured_at"]) <= now, "future capture")
    if row["posted_at"] is not None:
        require(timestamp(row["posted_at"]) <= timestamp(row["captured_at"]), "invalid posting date")
    if row["description"] is not None:
        text(row["description"], 100_000)
    require(row["availability"] in ("open", "closed", "unknown"), "invalid availability")
    if row["availability"] != "unknown":
        text(row["availability_evidence"])
    else:
        require(row["availability_evidence"] is None or isinstance(row["availability_evidence"], str),
                "invalid availability evidence")
    require(isinstance(row["segments"], dict), "segments must be an object")
    strings(row["limitations"])


def extraction_gate():
    # No user-supplied qualification boolean can enable a model invocation.
    raise EvidenceError("automated extraction blocked: provide --id for an observation and a matching runtime qualification")


class Store:
    """One writer, one atomic content manifest, no content-addressed disk cache.

    Supported on macOS/Linux. Private directory is not an OS security boundary.
    Filesystem backups and physical media erasure are outside this implementation.
    """

    def __init__(self, home, clock=utcnow):
        self.home = Path(home)
        self.clock = clock

    @contextmanager
    def transaction(self):
        require(not self.home.is_symlink(), "state directory may not be a symlink")
        self.home.mkdir(mode=0o700, parents=True, exist_ok=True)
        require(stat.S_IMODE(self.home.stat().st_mode) & 0o077 == 0,
                "state directory must be private (mode 0700)")
        lock = self.home / "research.lock"
        fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "r+") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            path = self.home / "research-state.json"
            require(not path.is_symlink(), "state file may not be a symlink")
            if path.exists():
                require(stat.S_IMODE(path.stat().st_mode) & 0o077 == 0,
                        "state file must be private (mode 0600)")
                state = json.loads(path.read_text(encoding="utf-8"))
                fields(state, ["schema_version", "artifacts", "withdrawn"])
                require(state["schema_version"] == VERSION, "unsupported state schema; no implicit migration")
                require(isinstance(state["artifacts"], dict) and isinstance(state["withdrawn"], list),
                        "invalid state manifest")
                for key, artifact in state["artifacts"].items():
                    fields(artifact, ["schema_version", "kind", "payload", "dependencies", "use_until"])
                    require(digest(artifact) == key and key not in state["withdrawn"],
                            "corrupt or withdrawn artifact in manifest")
                    require(all(d in state["artifacts"] for d in artifact["dependencies"]),
                            "incomplete artifact lineage")
            else:
                state = {"schema_version": VERSION, "artifacts": {}, "withdrawn": []}
            # Interrupted upstream atomic writes are never loaded or restored.
            for orphan in self.home.glob(".seen_jobs.*.tmp"):
                require(not orphan.is_symlink(), "unsafe orphan state file")
                orphan.unlink()
            self.sweep(state)
            save_state(path, state)  # expiry withdrawal is durable even if the action fails
            try:
                yield state
            except Exception:
                raise
            else:
                expired = self.sweep(state)  # authorization can expire during work
                save_state(path, state)
                require(not expired, "evidence expired during operation; retry on surviving state")

    def remove(self, state, ids):
        removed = set(ids)
        contexts = {a['payload']['content'] for key, a in state['artifacts'].items()
                    if key in removed and a['kind'] == 'context' and a['payload']['content'] is not None}
        fingerprints = {f for key, a in state['artifacts'].items() if key in removed and a['kind'] == 'context'
                        for f in a['payload'].get('content_fingerprints', [])}
        bodies = {a["payload"]["description"] for key, a in state["artifacts"].items()
                  if key in removed and a["kind"] == "observation" and a["payload"]["description"] is not None}
        while True:
            descendants = {i for i, a in state["artifacts"].items()
                           if set(a["dependencies"]) & removed or
                           (a["kind"] == "observation" and a["payload"]["description"] in bodies) or
                           (a['kind'] == 'context' and (a['payload']['content'] in contexts or
                            fingerprints.intersection(a['payload'].get('content_fingerprints', []))))}
            contexts |= {a['payload']['content'] for key, a in state['artifacts'].items()
                         if key in descendants and a['kind'] == 'context' and a['payload']['content'] is not None}
            fingerprints |= {f for key, a in state['artifacts'].items() if key in descendants and a['kind'] == 'context'
                             for f in a['payload'].get('content_fingerprints', [])}
            bodies |= {a["payload"]["description"] for key, a in state["artifacts"].items()
                       if key in descendants and a["kind"] == "observation" and a["payload"]["description"] is not None}
            if descendants <= removed:
                break
            removed |= descendants
        from tools.research_interchange import withdrawal_tokens
        shared = {t for key in removed if key in state['artifacts']
                  and state['artifacts'][key]['kind'] == 'interchange-item'
                  for t in withdrawal_tokens(state['artifacts'][key]['payload'])}
        copies = {key for key,a in state['artifacts'].items() if a['kind'] == 'interchange-item'
                  and shared.intersection(a['payload']['lineage'])}
        copies |= shared.intersection(state['artifacts'])
        if copies - removed:
            return self.remove(state, removed | copies)
        state['withdrawn'].extend(shared)
        for key in removed:
            artifact = state["artifacts"].pop(key, None)
            if artifact and artifact['kind'] == 'context' and artifact['payload']['content'] is not None:
                state['withdrawn'].append(digest(['withdrawn-context', artifact['payload']['content']]))
                state['withdrawn'].extend(artifact['payload'].get('content_fingerprints', []))
            if artifact and artifact["kind"] == "observation":
                # Independent of receipt/capture metadata: revised envelopes cannot
                # restore the same withdrawn description under a fresh artifact ID.
                body = artifact["payload"]["description"]
                if body is not None:
                    state["withdrawn"].append(digest(["withdrawn-description", body]))
        state["withdrawn"] = sorted(set(state["withdrawn"]) | removed)
        return len(removed)

    def sweep(self, state):
        expired = [key for key, artifact in state["artifacts"].items()
                   if artifact["use_until"] and timestamp(artifact["use_until"]) <= self.clock()]
        return self.remove(state, expired)

    def put(self, state, kind, payload, dependencies=(), use_until=None):
        deps = sorted(set(dependencies))
        require(all(d in state["artifacts"] for d in deps), "missing or withdrawn dependency")
        limits = [state["artifacts"][d]["use_until"] for d in deps]
        limits = [t for t in [use_until, *limits] if t is not None]
        expiry = min(limits, key=timestamp) if limits else None
        require(expiry is None or timestamp(expiry) > self.clock(), "evidence expired before commit")
        record = {"schema_version": VERSION, "kind": kind, "payload": payload,
                  "dependencies": deps, "use_until": expiry}
        key = digest(record)
        require(key not in state["withdrawn"], "withdrawn revision cannot be restored")
        state["artifacts"][key] = record
        return key

    def import_bundle(self, bundle):
        fields(bundle, ["schema_version", "policy", "receipt", "observations"])
        require(bundle["schema_version"] == VERSION, "unsupported import schema")
        now = self.clock()
        validate_policy(bundle["policy"], now)
        validate_receipt(bundle["receipt"], bundle["policy"]["source"], now)
        require(bundle['receipt']['kind'] in ('job', 'synthetic'), 'use context importer for context receipts')
        rows = bundle["observations"]
        require(isinstance(rows, list) and len(rows) <= 100, "import limited to 100 observations")
        for row in rows:
            validate_observation(row, now)
        require(len({r["native_id"] for r in rows}) == len(rows), "duplicate native IDs within capture")
        receipt = bundle["receipt"]
        require(all(timestamp(receipt["started_at"]) <= timestamp(r["captured_at"]) <=
                    timestamp(receipt["finished_at"]) for r in rows), "capture outside receipt period")
        require(sum(p["returned"] for p in receipt["pages"]) == len(rows), "receipt count mismatch")
        require(receipt["completeness"] not in ("failed", "blocked") or not rows,
                "failed or blocked receipt cannot carry observations")
        with self.transaction() as state:
            policy = self.put(state, "policy", bundle["policy"], use_until=bundle["policy"].get("use_until"))
            receipt_id = self.put(state, "receipt", receipt, [policy])
            ids = []
            existing_kinds = {a["payload"]["kind"] for a in state["artifacts"].values()
                              if a["kind"] == "receipt"}
            require(existing_kinds <= {receipt["kind"]}, "synthetic and job corpora must use separate stores")
            for row in rows:
                require(row["description"] is None or digest(["withdrawn-description", row["description"]])
                        not in state["withdrawn"], "withdrawn description cannot be recaptured")
                for artifact in state["artifacts"].values():
                    if artifact["kind"] != "observation":
                        continue
                    old = artifact["payload"]
                    if (old["source"], old["native_id"], timestamp(old["captured_at"])) == (
                            bundle["policy"]["source"], row["native_id"], timestamp(row["captured_at"])):
                        require(all(old[k] == v for k, v in row.items()),
                                "conflicting revisions share a capture timestamp")
                content = {**row, "schema_version": VERSION, "source": bundle["policy"]["source"],
                           "description_sha256": digest(row["description"]), "receipt": receipt_id}
                ids.append(self.put(state, "observation", content, [receipt_id]))
            return {"receipt": receipt_id, "observations": ids}

    def annotate(self, annotation):
        """Reviewed human labels and synthetic tests only; never disguised as LLM output."""
        with self.transaction() as state:
            payload = validate_annotation(annotation, state, self.clock())
            key = self.put(state, "analysis", payload, [annotation["observation"]])
            return {"analysis": key}

    def withdraw(self, key):
        require(isinstance(key, str) and re.fullmatch(r"[0-9a-f]{64}", key), "invalid artifact ID")
        with self.transaction() as state:
            return {"withdrawn_count": self.remove(state, [key])}

    def status(self):
        with self.transaction() as state:
            kinds = {}
            for a in state["artifacts"].values():
                kinds[a["kind"]] = kinds.get(a["kind"], 0) + 1
            return {"counts": kinds, "withdrawn_count": len(state["withdrawn"]),
                    "automated_extraction": "requires_matching_qualification_and_source_policy",
                    "unmanaged_export": "blocked"}

    def snapshot(self):
        with self.transaction() as state:
            report, dependencies = aggregate(state)
            key = self.put(state, "snapshot", report, dependencies)
            return {"snapshot": key, "counts": report["counts"]}

    def analyze(self, observation, *, refresh=False):
        from tools.research_analysis import analyze
        return analyze(self, observation, refresh=refresh)


def validate_annotation(annotation, state, now, *, automated=False):
    fields(annotation, ["schema_version", "observation", "method", "reviewer", "reviewed_at",
                        "taxonomy_version", "responsibility_class", "claims", "unknowns"])
    require(annotation["schema_version"] == VERSION, "unsupported analysis schema")
    require(annotation["taxonomy_version"] == TAXONOMY["version"], "unknown taxonomy")
    allowed = ("codex-extraction",) if automated else ("human-reviewed", "synthetic-fixture")
    require(annotation["method"] in allowed,
            "automated extraction not qualified; no external model output accepted")
    text(annotation["reviewer"])
    require(timestamp(annotation["reviewed_at"]) <= now, "future annotation review")
    item = state["artifacts"].get(annotation["observation"])
    require(item is not None and item["kind"] == "observation", "observation unavailable")
    description = item["payload"]["description"]
    require(timestamp(annotation["reviewed_at"]) >= timestamp(item["payload"]["captured_at"]),
            "annotation predates capture")
    receipt = state["artifacts"][item["payload"]["receipt"]]["payload"]
    require(annotation["method"] != "synthetic-fixture" or receipt["kind"] == "synthetic",
            "synthetic annotation requires a synthetic corpus")
    require(annotation["responsibility_class"] in ("applied", "research-heavy", "mixed", "unknown"),
            "invalid responsibility class")
    claims = annotation["claims"]
    require(isinstance(claims, list) and len(claims) <= 100, "invalid claims list")
    require(annotation["responsibility_class"] == "unknown" or bool(claims),
            "responsibility classification needs description evidence")
    if description is None:
        require(not claims and annotation["responsibility_class"] == "unknown",
                "missing descriptions require abstention")
    for claim in claims:
        fields(claim, ["kind", "modality", "start", "end", "quote", "capabilities", "tools"])
        require(claim["kind"] in ("responsibility", "skill", "constraint"), "invalid claim kind")
        require(claim["modality"] in ("required", "preferred", "unspecified"), "invalid modality")
        start, end = claim["start"], claim["end"]
        require(type(start) is int and type(end) is int and description is not None
                and 0 <= start < end <= len(description), "invalid evidence offsets")
        require(description[start:end] == claim["quote"], "evidence quote does not match captured revision")
        strings(claim["capabilities"])
        require(set(claim["capabilities"]) <= set(TAXONOMY["capabilities"]), "unknown capability")
        strings(claim["tools"])
    strings(annotation["unknowns"])
    require(description is not None or annotation["unknowns"], "missing-description limit required")
    return {**annotation, "source_statements": "claims.quote", "normalization": "reviewed labels",
            "cross_source_inference": [], "model_recommendations": []}


def aggregate(state):
    artifacts = state["artifacts"]
    observations = {i: a["payload"] for i, a in artifacts.items() if a["kind"] == "observation"}
    receipts = {i: a["payload"] for i, a in artifacts.items() if a["kind"] == "receipt"}
    # Keep all revisions as history; latest capture per source/native ID drives current views.
    latest = {}
    for key, row in observations.items():
        identity = (row["source"], row["native_id"])
        if identity not in latest or (timestamp(row["captured_at"]), key) > (
                timestamp(observations[latest[identity]]["captured_at"]), latest[identity]):
            latest[identity] = key
    analyses = {}
    for key, a in artifacts.items():
        if a["kind"] == "analysis":
            p = a["payload"]
            old = analyses.get(p["observation"])
            if old is None or (timestamp(p["reviewed_at"]), key) > (
                    timestamp(artifacts[old]["payload"]["reviewed_at"]), old):
                analyses[p["observation"]] = key
    groups = {}
    for key in latest.values():
        row = observations[key]
        # Cross-source merge only on reviewed employer domain AND requisition.
        identity = ("employer-req", row["employer_domain"], row["employer_requisition"]) if (
            row["employer_domain"] and row["employer_requisition"]) else ("source-id", row["source"], row["native_id"])
        groups.setdefault(identity, []).append(key)
    capabilities, tools_seen, employers = {}, {}, set()
    modalities = {m: {} for m in ("required", "preferred", "unspecified")}
    active, closed, unknown, conflicting = 0, 0, 0, 0
    opening_rows = []
    for identity, keys in sorted(groups.items()):
        opening = digest(identity)
        domains = {observations[k]["employer_domain"] for k in keys} - {None}
        employers |= domains
        states = {observations[k]["availability"] for k in keys}
        if states == {"open"}:
            active += 1
        elif states == {"closed"}:
            closed += 1
        else:
            unknown += 1
            conflicting += "open" in states and "closed" in states
        for key in keys:
            if key not in analyses:
                continue
            analysis = artifacts[analyses[key]]["payload"]
            if analysis["method"] == "codex-extraction" and analysis.get("ai_domain") != "in-domain":
                continue
            for claim in analysis["claims"]:
                for label in claim["capabilities"]:
                    modalities[claim["modality"]].setdefault(label, set()).add(opening)
                    counter = capabilities.setdefault(label, {"openings": set(), "employers": set()})
                    counter["openings"].add(opening)
                    counter["employers"] |= domains
                for tool in claim["tools"]:
                    tools_seen.setdefault(tool, set()).add(opening)
        opening_rows.append({"opening": opening, "observations": sorted(keys),
                             "availability": next(iter(states)) if len(states) == 1 else "unknown"})
    deps = sorted(set(observations) | set(receipts) | set(analyses.values()))
    report = {
        "schema_version": VERSION, "taxonomy_version": TAXONOMY["version"],
        "scope": "synthetic test corpus" if receipts and all(r["kind"] == "synthetic" for r in receipts.values())
                 else "historical captured sample; capabilities count latest source observations",
        "counts": {"captured_revisions": len(observations), "source_listings": len(latest),
                   "deduplicated_openings": len(groups), "distinct_verified_employer_domains": len(employers),
                   "openings_without_employer_identity": sum(not any(observations[k]["employer_domain"] for k in keys) for keys in groups.values()),
                   "observed_open": active, "observed_closed": closed, "availability_unknown": unknown,
                   "availability_conflicts": conflicting,
                   "missing_descriptions": sum(observations[k]["description"] is None for k in latest.values()),
                   "analyzed_latest_observations": sum(k in analyses for k in latest.values())},
        "distinct_reported_source_employers": len({(r["source"], r["employer_name"])
                                                   for r in observations.values() if r["employer_name"]}),
        "countries": sorted({r["country"] for r in observations.values()} - {None}),
        "languages": sorted({r["language"] for r in observations.values()} - {None}),
        "unknown_country_revisions": sum(r["country"] is None for r in observations.values()),
        "unknown_language_revisions": sum(r["language"] is None for r in observations.values()),
        "receipts": receipts, "openings": opening_rows,
        "capabilities": {k: {n: len(s) for n, s in v.items()} for k, v in sorted(capabilities.items())},
        "tools": {k: len(v) for k, v in sorted(tools_seen.items())},
        "capabilities_by_modality": {m: {k: len(v) for k, v in sorted(labels.items())}
                                     for m, labels in modalities.items()},
        "analysis_methods": sorted({artifacts[a]["payload"]["method"] for a in analyses.values()}),
        "ai_domain_latest_observations": {
            domain: sum(k in analyses and artifacts[analyses[k]]["payload"].get("ai_domain") == domain
                        for k in latest.values())
            for domain in ("in-domain", "adjacent", "out-of-domain", "unknown")},
        "limitations": ["Sample, not global market coverage or growth evidence.",
                        "Observed-open means open at capture, not verified open now.",
                        "Unknown employers are excluded from verified-employer counts.",
                        "Source expansion and revision counts cannot establish demand growth.",
                        "Validated spans do not imply human-reviewed semantic accuracy.",
                        "Conflicting source availability is unknown; no title-only deduplication."],
    }
    report["markdown"] = render_markdown(report)
    return report, deps


def render_markdown(report):
    # Only controlled labels/counts; untrusted imported strings remain in private JSON.
    lines = ["# Captured AI capability sample", "", report["scope"], "", "| Measure | Count |", "|---|---:|"]
    lines += [f"| {key} | {value} |" for key, value in report["counts"].items()]
    lines += ["", "| Capability | Openings | Verified employers |", "|---|---:|---:|"]
    lines += [f"| {key} | {v['openings']} | {v['employers']} |" for key, v in report["capabilities"].items()]
    lines += ["", "Inspect this snapshot's JSON receipts for queries, filters, dates and collection limits.", ""]
    lines += [f"- {line}" for line in report["limitations"]]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["import", "annotate", "snapshot", "status", "withdraw", "extract", "analyze", "qualify", "collect", "export", "restore"])
    parser.add_argument("--input", type=Path)
    parser.add_argument("--id")
    parser.add_argument("--query", default="machine learning")
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    try:
        if args.action in ("extract", "analyze") and not args.id:
            extraction_gate()
        require(args.action not in ("export", "restore"), "unmanaged export and restore are not supported")
        require(not template_errors(ROOT), "public-template preflight failed")
        store = Store(private_state_path(ROOT, dict(os.environ)))
        if args.action in ("import", "annotate"):
            require(args.input is not None, "--input required")
            payload = read_input(args.input)
            result = store.import_bundle(payload) if args.action == "import" else store.annotate(payload)
        elif args.action == "withdraw":
            result = store.withdraw(args.id)
        elif args.action == "qualify":
            from tools.research_analysis import qualify
            result = qualify(store)
        elif args.action == "collect":
            from tools.research_sources import collect_jobicy
            result = collect_jobicy(store, args.query, args.count)
        elif args.action in ("extract", "analyze"):
            result = store.analyze(args.id, refresh=args.refresh)
        else:
            result = getattr(store, args.action)()
        print(json.dumps(result, indent=2))
        return 0
    except EvidenceError as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}))
        return 1
    except (OSError, ValueError, KeyError, TypeError):
        # No raw input, filesystem paths, model text or credentials in diagnostics.
        print(json.dumps({"status": "blocked", "reason": "invalid or unsupported operation; see research contracts and runtime gate"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
