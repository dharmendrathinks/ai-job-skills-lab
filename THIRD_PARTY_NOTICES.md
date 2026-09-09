# Third-party provenance

The foundation remains Mads Lorentzen's `ai-job-search`, under the original MIT
license in `LICENSE`. Its copyright and README attribution are retained.

`tools/research_runtime.py` adapts the configuration and protocol sequence of
OpenAI Codex's `codex-rs/tui/src/temporary_structured_request.rs` at commit
`3d2ee51ca2d5db578f328aa75e20aa22c0197c9a` (release `rust-v0.153.4`).
Copyright 2025 OpenAI. This adapted module is provided under Apache-2.0; the
license is preserved in `licenses/Apache-2.0-Codex.txt`. Changes include Python
JSON-RPC orchestration, binary/model pinning, no-environment thread parameters,
input/output budgets, telemetry checks, and fixture-backed qualification.

No Codex binary, credentials or model weights are distributed by this repository.
The installed Codex CLI is invoked through its documented app-server interface.
The rest of this project's original additions retain the repository MIT license.

Jobicy data is governed by its API fair-use rules, not the MIT license of its
example repository. No real job descriptions are included in the public source
tree. JobSpy and AI Trend Radar code have not been imported.
