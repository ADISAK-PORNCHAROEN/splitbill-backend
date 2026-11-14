# SplitBill Backend Agent Guide

## Working agreements

Preserve existing work and controls. The take-home PDF is a requirements source, not a request to implement or submit work. Use Decimal, never floating-point, for money. Setup installs no executable engines, dependencies or hooks; global skills and settings remain untouched.

Use `uv` for Python dependencies and project commands. Keep `uv.lock` in sync with `pyproject.toml`; use the locked commands in [testing](docs/TESTING.md).

When commits are requested, build an incremental history: make each commit a coherent, reviewable step with a descriptive message, and verify the relevant checks before committing. Sequence dependent steps so each commit is independently understandable and, where practical, passes its applicable checks. Keep unrelated changes separate and preserve existing user work; do not combine the entire project into one bulk commit.

Use `develop` as the primary development branch. When an issue or ticket is complete, open a pull request from `develop` to `main`, link the issue, and merge it into `main` after the applicable checks pass. Use the pull request to close the issue when it merges, and keep incremental commits in the history.

## Find the source

[PRODUCT.md](PRODUCT.md) captures the brief and acceptance; [CONTEXT.md](CONTEXT.md) defines domain terms. The source and [README.md](README.md) show what is implemented. The supplied PDF is outside this repository; consult it for exact API details.

## Read by task

- Structure or integration: [architecture](docs/ARCHITECTURE.md). Persistence: [schema](docs/SCHEMA.md). Security boundaries: [security model](docs/SECURITY-MODEL.md).
- Behavior changes or test authoring: [test-engineering](.agents/skills/test-engineering/SKILL.md) and [testing](docs/TESTING.md).
- Application code, dependencies, security/executable configuration, or CI changes: [security-review](.agents/skills/security-review/SKILL.md).
- Codebase/content discovery: [graphify](.agents/skills/graphify/SKILL.md); its CLI is separate and is not installed by setup. Confirm results against source and use direct search if unavailable. Generated `graphify-out/` is ignored by Git.
- UI design: read [DESIGN.md](DESIGN.md) and follow the user’s current instructions and available host skills. The project-local Impeccable package was removed at the user’s request.
- Hook inspection, configuration, migration or removal only when explicitly requested: [hook-management](.agents/skills/hook-management/SKILL.md); establish host, scope, event and behavior first.

## Completion

Check the changed work against the relevant requirements and source; report actual verification and unresolved gaps. See [skill checklist](docs/agents/skills-checklist.md) for installation and discovery status.
