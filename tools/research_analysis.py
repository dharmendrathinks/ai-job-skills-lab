"""Evidence-bound model extraction, deterministic validation and cache lineage."""
import json
from pathlib import Path
import subprocess
import sys

from tools.research_evidence import EvidenceError, ROOT, TAXONOMY, digest, fields, require, validate_annotation
from tools.research_runtime import BOUNDARY_CONFIG, CodexWorker, runtime_identity

PROMPT_PATH = ROOT / "docs/research/prompts/extract-v1.md"
PROMPT_VERSION = "requirement-extraction/1"
CONCEPT_LABELS = {"ai", "artificial intelligence", "ml", "machine learning", "llm", "llms",
                  "large language model", "large language models", "rag", "retrieval", "agents"}
CLAIM_SCHEMA = {"type": "object", "additionalProperties": False,
    "properties": {"kind": {"type": "string", "enum": ["skill", "responsibility", "constraint"]},
                   "modality": {"type": "string", "enum": ["required", "preferred", "unspecified"]},
                   "quote": {"type": "string"},
                   "capabilities": {"type": "array", "items": {"type": "string", "enum": TAXONOMY["capabilities"]}},
                   "tools": {"type": "array", "items": {"type": "string"}}},
    "required": ["kind", "modality", "quote", "capabilities", "tools"]}
OUTPUT_SCHEMA = {"type": "object", "additionalProperties": False,
    "properties": {"ai_domain": {"type": "string", "enum": ["in-domain", "adjacent", "out-of-domain", "unknown"]},
                   "responsibility_class": {"type": "string", "enum": ["applied", "research-heavy", "mixed", "unknown"]},
                   "claims": {"type": "array", "items": CLAIM_SCHEMA},
                   "unknowns": {"type": "array", "items": {"type": "string"}}},
    "required": ["ai_domain", "responsibility_class", "claims", "unknowns"]}


def qualification_identity():
    _, _, identity = runtime_identity()
    return {**identity, "client_sha256": digest((ROOT / "tools/research_runtime.py").read_text()),
            "boundary_test_sha256": digest((ROOT / "tests/test_research_runtime_live.py").read_text())}


def qualify(store):
    """Run actual binary forced-call tests before recording local qualification."""
    import os
    identity = qualification_identity()
    env = dict(os.environ, RUN_CODEX_BOUNDARY_TESTS="1")
    result = subprocess.run([sys.executable, "-m", "unittest", "tests.test_research_runtime_live"],
                            cwd=ROOT, env=env, capture_output=True, text=True, timeout=90)
    require(result.returncode == 0, "installed runtime qualification failed; extraction stays disabled")
    require(qualification_identity() == identity, "runtime changed during qualification")
    with store.transaction() as state:
        key = store.put(state, "runtime-qualification", {
            "schema_version": 1, "identity": identity, "qualified_at": store.clock().isoformat(),
            "test": "installed binary + loopback forced responses", "forced_calls_denied": 9,
            "mechanism": "empty registered tools via no environments and pinned direct model/config",
            "limits": "No claim of OS isolation or hosted data deletion; production provider smoke is separate."})
    return {"qualification": key, "identity": identity}


def qualified(state):
    identity = qualification_identity()
    matches = [key for key, a in state["artifacts"].items()
               if a["kind"] == "runtime-qualification" and a["payload"].get("identity") == identity]
    require(matches, "run runtime qualification for this binary/client/model/config first")
    return sorted(matches)[-1], identity


def bounded_prompt(description):
    spec = PROMPT_PATH.read_text(encoding="utf-8")
    return spec + "\n\nCapability taxonomy:\n" + json.dumps(TAXONOMY) + "\n\nUntrusted description JSON:\n" + json.dumps(description, ensure_ascii=False)


def normalize_output(output, observation_id, description, now):
    fields(output, ["ai_domain", "responsibility_class", "claims", "unknowns"])
    require(output["ai_domain"] in ("in-domain", "adjacent", "out-of-domain", "unknown"), "unknown AI-domain classification")
    require(isinstance(output["claims"], list) and len(output["claims"]) <= 100, "model claim budget exceeded")
    claims = []
    for claim in output["claims"]:
        fields(claim, ["kind", "modality", "quote", "capabilities", "tools"])
        quote = claim["quote"]
        require(description is not None and isinstance(quote, str) and quote and quote in description,
                "model quote absent from exact captured description")
        require(isinstance(claim["tools"], list) and all(isinstance(t, str) and t.casefold() in quote.casefold()
                for t in claim["tools"]), "tool label not explicitly evidenced by its quote")
        # Preserve the exact statement but separate generic concepts from concrete
        # implementation names. The original model response remains in execution.
        tools = [t for t in claim["tools"] if t.casefold() not in CONCEPT_LABELS]
        start = description.index(quote)  # deterministic first exact occurrence, never fuzzy repair
        claims.append({**claim, "tools": tools, "start": start, "end": start + len(quote)})
    return {"schema_version": 1, "observation": observation_id, "method": "codex-extraction",
            "reviewer": "deterministic validator; human review pending", "reviewed_at": now.isoformat(),
            "taxonomy_version": TAXONOMY["version"], "responsibility_class": output["responsibility_class"],
            "claims": claims, "unknowns": output["unknowns"]}


def _eligible(state, observation):
    artifact = state["artifacts"].get(observation)
    require(artifact and artifact["kind"] == "observation", "observation unavailable or withdrawn")
    receipt = state["artifacts"][artifact["payload"]["receipt"]]
    policies = [state["artifacts"][d]["payload"] for d in receipt["dependencies"]]
    require(policies and all(p["hosted_disclosure"] and p.get("hosted_retention") ==
                            "provider-managed-no-deletion-deadline" for p in policies),
            "source has no compatible hosted-processing permission")
    return artifact["payload"]


def analyze(store, observation, *, refresh=False, worker_factory=CodexWorker):
    with store.transaction() as state:
        row = _eligible(state, observation)
        qualification, identity = qualified(state)
        versions = {"prompt_version": PROMPT_VERSION, "prompt_sha256": digest(PROMPT_PATH.read_text()),
                    "validation_sha256": digest(Path(__file__).read_text()),
                    "schema_sha256": digest(OUTPUT_SCHEMA), "taxonomy_sha256": digest(TAXONOMY),
                    "runtime": identity, "boundary_config_sha256": digest(BOUNDARY_CONFIG)}
        cache_key = digest({"observation": observation, "versions": versions})
        if not refresh:
            cached = [key for key, a in state["artifacts"].items() if a["kind"] == "analysis"
                      and a["payload"].get("cache_key") == cache_key]
            if cached:
                return {"analysis": sorted(cached)[-1], "cache_hit": True}
        prompt = bounded_prompt(row["description"])
    metadata = {"authentication": "none", "token_usage": {}, "latency_seconds": 0}
    try:
        if row["description"] is None:
            output = {"ai_domain": "unknown", "responsibility_class": "unknown", "claims": [], "unknowns": ["Description missing; no extraction."]}
        else:
            with worker_factory(store.home) as worker:
                # Check again after potentially slow runtime startup, immediately before disclosure.
                with store.transaction() as state:
                    _eligible(state, observation)
                    qualified(state)
                output, metadata = worker.run(prompt, OUTPUT_SCHEMA)
        with store.transaction() as state:
            _eligible(state, observation)
            qualified(state)
            annotation = normalize_output(output, observation, row["description"], store.clock())
            analysis = validate_annotation(annotation, state, store.clock(), automated=True)
            execution = store.put(state, "execution", {"schema_version": 1, "status": "validated",
                "input_revision": observation, "versions": versions, "cache_key": cache_key,
                "recorded_at": store.clock().isoformat(), "metadata": metadata,
                "response": output, "human_review": "pending"}, [observation, qualification])
            key = store.put(state, "analysis", {**analysis, "ai_domain": output["ai_domain"], "cache_key": cache_key, "execution": execution,
                            "human_review": "pending"}, [observation, execution])
        return {"analysis": key, "execution": execution, "cache_hit": False}
    except (EvidenceError, ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError):
        with store.transaction() as state:
            if observation in state["artifacts"] and qualification in state["artifacts"]:
                store.put(state, "execution", {"schema_version": 1, "status": "rejected-or-deferred",
                    "input_revision": observation, "versions": versions, "cache_key": cache_key,
                    "recorded_at": store.clock().isoformat(), "metadata": metadata,
                    "reason": "runtime, quota, validation or lifecycle check failed; no automatic retry"},
                          [observation, qualification])
        raise
