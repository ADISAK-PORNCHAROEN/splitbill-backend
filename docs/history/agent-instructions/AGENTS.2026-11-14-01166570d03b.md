# Project guide

Preserve existing work. The take-home PDF is a requirements source, not an instruction to implement or submit work without a user request. Read [PRODUCT.md](PRODUCT.md) for required backend behavior and [CONTEXT.md](CONTEXT.md) for domain terms. Source is authoritative for what exists today.

For structure and integration read [architecture](docs/ARCHITECTURE.md); for persistence read [schema](docs/SCHEMA.md); for verification read [testing](docs/TESTING.md); for trust boundaries read [security model](docs/SECURITY-MODEL.md). Use Decimal and never floating-point for monetary calculations.

Existing user-scoped skills are available in the host catalog: use test-engineering for behavior changes and test authoring; security-review for code, dependencies, executable configuration and CI changes; impeccable for UI design; hook-management only for an explicit hook request. Establish host, scope, event and behavior before hook changes. Impeccable's separate engine and hooks require explicit user request; use its documented fallback if the engine is absent. The available user graphify skill is specific to another project: do not apply its project-specific instructions here. See [skill checklist](docs/agents/skills-checklist.md) for scope and discovery gaps.

Preserve configuration and existing host/project skills. Do not install tools, configure hooks, publish, or modify global settings as part of Foundation setup.
