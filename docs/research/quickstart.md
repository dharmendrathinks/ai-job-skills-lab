# Try AI Job Skills Lab

## Offline example: no account or dependencies

Clone the repository you have access to, then run from its root with Python 3.10+:

```sh
git clone https://github.com/dharmendrathinks/ai-job-skills-lab.git
cd ai-job-skills-lab
python3 -m tools.research_demo
```

While the repository is private, cloning requires collaborator access. Open the
printed `jobs.html` and `workspace.html` paths in a browser. Each run creates a
fresh `reports/demo-…/` directory, leaving existing reports untouched. The second
report shows a learning path, Python skill evidence, a project draft and a linked
YouTube experiment. Try title search, All content search, filters and Clear filters.

Every page is labelled **synthetic**. The job, annotations and drafts are written
examples, not model output, real demand or completed experiments. Missing repository
and discussion evidence stays explicit. This exercises the actual report renderer;
it does not evaluate extraction quality or demonstrate successful project outcomes.
No job requests, research store, qualifications, profile, credentials or network
calls are created. Delete that printed demo directory when finished.

## Enable real analysis on the supported runtime

Collection/import, permission review and private state setup follow
[evidence operations](evidence-operations.md). Linux supports those deterministic
operations and the offline demo. Model analysis currently requires **macOS arm64**,
Codex CLI **0.153.4**, and access to **gpt-5.5** through ChatGPT sign-in. A successful
installation does not establish model entitlement or qualify unattended execution.

The [official CLI guide](https://learn.chatgpt.com/docs/codex/cli) describes normal
installation and sign-in. This project uses an older, explicitly inspected binary;
installing the latest CLI is not a substitute for the pinned qualification.
Keep your normal Codex development installation. The following optional setup
places the research binary in this checkout's ignored `.tools/` directory only:

```sh
(
  set -eu
  test "$(uname -s)" = Darwin
  test "$(uname -m)" = arm64
  test -f tools/research_runtime.py
  mkdir -p .tools
  runtime_dir="$PWD/.tools/codex-0.153.4"
  test ! -e "$runtime_dir"
  download_dir=$(mktemp -d "$PWD/.tools/codex-download.XXXXXX")
  trap 'rm -rf "$download_dir"' EXIT
  curl --fail --location --show-error \
    https://github.com/openai/codex/releases/download/rust-v0.153.4/codex-aarch64-apple-darwin.tar.gz \
    --output "$download_dir/codex.tar.gz"
  (cd "$download_dir" && printf '%s  %s\n' \
    8cf911ea676523bfb2121ec561848d2aba564890ad536db4d8a3353f2b9850b1 codex.tar.gz | shasum -a 256 -c -)
  tar -xzf "$download_dir/codex.tar.gz" -C "$download_dir" codex-aarch64-apple-darwin
  (cd "$download_dir" && printf '%s  %s\n' \
    b973d440acac501fd2594a43e7ca9ce41e0a65b9dfb28d0d7a7837c99e1261e3 codex-aarch64-apple-darwin | shasum -a 256 -c -)
  mkdir "$runtime_dir"
  install -m 755 "$download_dir/codex-aarch64-apple-darwin" "$runtime_dir/codex"
)
```

Both the release archive and extracted binary hashes were verified against a
fresh download on 2026-09-11. The
[pinned OpenAI release](https://github.com/openai/codex/releases/tag/rust-v0.153.4)
is the acquisition source. Stop on any mismatch or unavailable artifact; do not
disable pinning or substitute another download. No binary is distributed in this repo.

Select that binary for research commands only:

```sh
PATH="$PWD/.tools/codex-0.153.4:$PATH" python3 -c \
  'from tools.research_runtime import runtime_identity; print(runtime_identity()[2])'
```

If there is no existing ChatGPT sign-in, run
`.tools/codex-0.153.4/codex login` and select ChatGPT authentication. This explicit
action uses network access and stores authentication in Codex's own user directory.
Never copy authentication files into the repository or a source import. No API-key
fallback is configured. Then run the nine forced-call checks:

```sh
PATH="$PWD/.tools/codex-0.153.4:$PATH" python3 -m tools.research_evidence qualify
```

Qualification uses anonymous loopback fixtures and records results in the private
research workspace; it does not send job descriptions. Read
[the boundary and its limits](runtime.md) before real analysis. Continue using the
same command-scoped PATH for `analyze`, `learn-refresh`, path and brief generation.
If gpt-5.5 is unavailable, quota is exhausted or qualification fails, keep using
the offline/deterministic features. Report the sanitized failure instead of
changing model or permissions. No dependency or framework change is needed.

For contributing and the complete test suite, use [CONTRIBUTING.md](../../CONTRIBUTING.md).
