"""Opt-in model evaluation with versioned inputs; no invented human labels.

Produces managed evaluation artifacts, not public copies of source descriptions.
Research and simple-prompt use the same model/inputs. The upstream comparison
replays its targeted analytical rules with supplied description/profile inputs;
it does not claim to exercise unavailable application setup or fetch tools.
"""
import argparse
import json
import os
from pathlib import Path

from tools.research_analysis import OUTPUT_SCHEMA, PROMPT_PATH, bounded_prompt, normalize_output, qualified, _eligible
from tools.research_evidence import ROOT, Store, digest, private_state_path, require, validate_annotation
from tools.research_runtime import CodexWorker

DATASET = ROOT / "tests/fixtures/research/heldout-v1.json"
UPSTREAM = ROOT / ".claude/skills/upskill/SKILL.md"


def atoms(output):
    found = set()
    for claim in output["claims"]:
        found |= {"capability:" + c for c in claim["capabilities"]}
        found |= {f"tool:{tool}:{claim['modality']}" for tool in claim["tools"]}
    return found


def score(output, example):
    actual, expected = atoms(output), set(example["expected_atoms"])
    return {"true_positive": len(actual & expected), "false_positive": len(actual - expected),
            "false_negative": len(expected - actual), "actual_atoms": sorted(actual),
            "class_correct": None if example["expected_class"] is None else output["responsibility_class"] == example["expected_class"],
            "domain_correct": None if example["expected_domain"] is None else output["ai_domain"] == example["expected_domain"]}


def prompt_for(arm, example):
    if arm == "research":
        return bounded_prompt(example["description"])
    if arm == "simple-prompt":
        return "Extract the AI-engineering skills and responsibilities from this description using the requested JSON schema.\n" + json.dumps(example["description"], ensure_ascii=False)
    require(arm == "upstream-targeted-replay", "unknown baseline")
    return ("Replay the targeted /upskill <URL> analysis in this unmodified specification. The fetched description and a synthetic candidate profile are supplied, so no fetching, profile loading or file writes are needed. Preserve its analytical rules, including removal of known skills. Adapt presentation to the requested JSON schema; this comparison covers extraction/capability analysis, not learning links.\n\n"
            + UPSTREAM.read_text() + "\n\nSupplied profile: the candidate already knows Python. All other capabilities are unassessed.\nSupplied description:\n"
            + json.dumps(example["description"], ensure_ascii=False))


def evaluate(store, arms, *, repeat=False):
    dataset = json.loads(DATASET.read_text())
    with store.transaction() as state:
        qualification, identity = qualified(state)
    versions = {"dataset_sha256": digest(dataset), "prompt_sha256": digest(PROMPT_PATH.read_text()),
                "schema_sha256": digest(OUTPUT_SCHEMA), "upstream_spec_sha256": digest(UPSTREAM.read_text()),
                "runtime": identity, "harness_sha256": digest(Path(__file__).read_text())}
    results = []
    for arm in arms:
        for example in dataset["examples"]:
            run_key = digest({"versions": versions, "arm": arm, "example": example["id"]})
            with store.transaction() as state:
                cached = [a["payload"] for a in state["artifacts"].values()
                          if a["kind"] == "evaluation-case" and a["payload"]["run_key"] == run_key]
            if cached and not repeat:
                results.append(cached[-1])
                continue
            with CodexWorker(store.home) as worker:
                output, execution = worker.run(prompt_for(arm, example), OUTPUT_SCHEMA)
            valid = True
            try:
                normalize_output(output, example["id"], example["description"], store.clock())
            except ValueError:
                valid = False
            record = {"schema_version": 1, "run_key": run_key, "arm": arm,
                      "example": example["id"], "versions": versions,
                      "recorded_at": store.clock().isoformat(), "source_spans_valid": valid,
                      "output": output, "score": score(output, example), "execution": execution,
                      "human_review": dataset["human_review"], "synthetic": True}
            with store.transaction() as state:
                qualified(state)
                store.put(state, "evaluation-case", record, [qualification])
            results.append(record)
            print(json.dumps({"arm": arm, "example": example["id"], "source_spans_valid": valid,
                              "score": record["score"]}), flush=True)
    summaries = {}
    for arm in arms:
        rows = [r for r in results if r["arm"] == arm]
        tp, fp, fn = [sum(r["score"][k] for r in rows) for k in ("true_positive", "false_positive", "false_negative")]
        summaries[arm] = {"examples": len(rows), "true_positive": tp, "false_positive": fp, "false_negative": fn,
                          "precision": tp / (tp + fp) if tp + fp else None,
                          "recall": tp / (tp + fn) if tp + fn else None,
                          "valid_span_examples": sum(r["source_spans_valid"] for r in rows),
                          "latency_seconds": sum(r["execution"]["latency_seconds"] for r in rows)}
    return {"versions": versions, "human_review": dataset["human_review"], "summaries": summaries,
            "limitations": ["Six short synthetic cases, not 120 descriptions/40 employers or operational prevalence.",
                            "Upstream targeted analytical replay with supplied inputs, not full application workflow.",
                            "Commercial, project and content recommendation ratings begin with P3 outputs."]}


def evaluate_observation(store, observation, arm, *, worker_factory=CodexWorker):
    """Uncached comparison/repeat on retained real text; derivatives inherit policy.

    No accuracy labels are manufactured for real descriptions. Human adjudication
    must precede any precision/recall claim about these records.
    """
    with store.transaction() as state:
        row = _eligible(state, observation)
        qualification, identity = qualified(state)
        require(row["description"] is not None, "comparison needs captured description")
    with worker_factory(store.home) as worker:
        with store.transaction() as state:
            _eligible(state, observation)
            qualified(state)
        output, execution = worker.run(prompt_for(arm, row), OUTPUT_SCHEMA)
    with store.transaction() as state:
        _eligible(state, observation)
        qualified(state)
        annotation = normalize_output(output, observation, row["description"], store.clock())
        validate_annotation(annotation, state, store.clock(), automated=True)
        record = {"schema_version": 1, "arm": arm, "observation": observation,
                  "recorded_at": store.clock().isoformat(), "output": output,
                  "execution": execution, "runtime": identity, "human_review": "pending",
                  "source_spans_valid": True, "synthetic": False,
                  "harness_sha256": digest(Path(__file__).read_text()),
                  "prompt_sha256": digest(prompt_for(arm, row)),
                  "schema_sha256": digest(OUTPUT_SCHEMA),
                  "upstream_spec_sha256": digest(UPSTREAM.read_text())}
        key = store.put(state, "evaluation-observation", record, [observation, qualification])
    return {"evaluation": key, "arm": arm, "source_spans_valid": True,
            "latency_seconds": execution.get("latency_seconds"), "human_review": "pending"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", action="append", choices=["research", "simple-prompt", "upstream-targeted-replay"])
    parser.add_argument("--repeat", action="store_true")
    parser.add_argument("--observation", help="Compare retained real text; outputs inherit its policy")
    args = parser.parse_args()
    store = Store(private_state_path(ROOT, dict(os.environ)))
    arms = args.arm or ["research", "simple-prompt", "upstream-targeted-replay"]
    result = ([evaluate_observation(store, args.observation, arm) for arm in arms]
              if args.observation else evaluate(store, arms, repeat=args.repeat))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
