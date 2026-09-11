# Phase 3 human acceptance checklist

Implementation and automated/live execution checks are complete. This checklist
covers the remaining **human** acceptance requirement in `PLAN_RESEARCH.md`,
Phase 3: “Human-reviewed briefs across all four outputs; a valid contribution
case, known-skill deepening case, and no-project/insufficient-evidence case.”
An instruction to implement or commit is not recorded as a fabricated review.

The drafts remain in managed private state, not this public document. To view one:

```sh
.venv/bin/python -m tools.research_decisions inspect --id BRIEF_ID
```

This local view includes draft text, exact source quotes, captured dates and
inspected alternative paths. It checks expiry/withdrawal and writes no exported
report. Use a terminal whose history is compatible with the source policy.

| Case | What the reviewer should assess | Brief ID |
|---|---|---|
| Learning | Are the dependency/practice/completion steps useful and feasible, with no claimed missing ability from absent profile evidence? | `6652ac54d95a8862658eb49531eec13250a51bc22b4b85d2112c5e8db51f3243` |
| Existing-project contribution, refreshed | Is adding human adjudication to the **existing** evaluation records a concrete useful addition? Check the evaluator/test paths inspected and the limits of that inspection. | `bb32396061a68307f3c88ef911f3cfb130c5b8511daa8a7f14cde8a71a4a7acb` |
| Product hypothesis | Are buyer, workaround and pain honestly hypotheses, with useful validation/rejection criteria? Earlier packaging/UI suggestions need review against the now-explicit reuse rule. | `9b7c772345c7437719eac00bffb97720789ff0094f1491b6a35bce0aed898e0e` |
| YouTube experiment | Is the experiment reproducible and useful, with possible outcomes rather than invented results and audience suitability unknown? | `df5d37cd7e33533387a2576af331f20816be9452d4fa94cb7904c4fbcd5b9a00` |

For the two **fictional** completion scenarios, use the separate private store:

```sh
AI_JOB_SKILLS_LAB_HOME="$HOME/Library/Application Support/ai-job-skills-lab/phase3-evaluation" \
  .venv/bin/python -m tools.research_decisions inspect --id BRIEF_ID
```

| Case | What the reviewer should assess | Brief ID |
|---|---|---|
| Known-skill deepening | Does it deepen retrieval through hard negatives, query/corpus mismatch and failure explanations while keeping self-declared experience separate from demonstrated ability? | `b8113af330228c34e2fe6f4ded2cc453a974d245164eb0ac9c7fb69637648fc9` |
| Missing alternatives | Is `insufficient-evidence` appropriate, with the optional retrieval exercise explicitly practice rather than a new contribution? | `dc50330ccbd27ed1a18258baed2bf61024462d083582f49e365dda3c17c91a53` |

For each case, record **useful / needs changes / reject**, the reason, whether it
is feasible, and any unsupported claim noticed. A review of direction alone is
recorded only as direction feedback, not source-accuracy verification. Corrections
are welcome; no usefulness percentage or successful human review is presumed.
This is acceptance evaluation, not approval to execute, publish or sell a brief.

Phase 2's pending requirement labels remain a separate review; approving these
briefs does not silently adjudicate those labels or establish extraction accuracy.
