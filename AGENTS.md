---
framework_version: 1.0.2
---

# Agent Guidelines: AI Job Search

## Research fork routing — read before loading candidate data

This is AI Job Skills Lab, extending MadsLorentzen/ai-job-search. The active roadmap is
[PLAN_RESEARCH.md](PLAN_RESEARCH.md). Research requests use the canonical
[research specification](.claude/skills/research/SKILL.md) before any application
profile, tracker, or fit rule is loaded. Research is the default product mode;
explicit application commands retain their upstream application semantics.
Do not run application setup for research. Public-template profile writes are
blocked by the research preflight even when the GitHub repository is private.
Use only this checkout for development; keep personal research state outside it.
See [the runtime decision](docs/research/runtime.md) for enforced checks versus
instruction-level safeguards and the qualified Phase 2 extraction boundary and its limits.

This workspace is structured to manage job search activities, scraper tools, CVs, cover letters, and interview preparation.

## Thin-Pointer Design (Single Source of Truth)

To prevent duplication and configuration drift across different AI agent frameworks (Claude Code, Google Antigravity, Codex, Cursor, Gemini CLI, etc.), this workspace uses a unified thin-pointer design. All agent runtimes should load canonical specifications and, only in application mode, candidate profiles from the files and directories below:

1. **Personal Candidate Profile:**
   - The candidate profile, contact details, education, and target preferences are defined in [CLAUDE.md](CLAUDE.md) and the individual profile methodology files under [.claude/skills/job-application-assistant/](.claude/skills/job-application-assistant/) (specifically `01-*.md` etc.).
2. **Canonical Workflow Specifications:**
   - The step-by-step instructions and triggers for tasks (setup, scrape, rank, apply, upskill, interview) are defined in the [.claude/](.claude/) directory (specifically under `.claude/skills/` and `.claude/commands/`).
   - Do not duplicate these rules or specifications. Treat `.claude/` files as the single source of truth.
3. **Portal Search Skills:**
   - Job-portal search CLIs live under [.agents/skills/](.agents/skills/) in the portable Agent Skills format (with a `SKILL.md` per portal). Codex and Antigravity discover these automatically; the `/scrape` workflow in [.claude/skills/job-scraper/](.claude/skills/job-scraper/) orchestrates them.
