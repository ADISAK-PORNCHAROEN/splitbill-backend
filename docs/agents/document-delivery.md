# Document delivery

| Path | Status | Evidence | Content review |
| --- | --- | --- | --- |
| `AGENTS.md` | Required | foundation-v1 routing and source ownership | source, guide and routes reviewed |
| `CLAUDE.md` | Required | exact @AGENTS.md bridge | content reviewed |
| `PRODUCT.md` | Required | owner PDF and README scaffold | requirements vs implementation reviewed |
| `CONTEXT.md` | Required | owner PDF | terminology reviewed |
| `DESIGN.md` | Required | no UI source in backend scaffold | unknown state reviewed |
| `SECURITY.md` | Required | security model and unspecified reporting policy | unknown policy reviewed |
| `docs/ARCHITECTURE.md` | Applicable | app/main.py, configuration and brief | entry point and pending layers reviewed |
| `docs/SCHEMA.md` | Applicable | brief and absent models/migrations | pending schema reviewed |
| `docs/TESTING.md` | Applicable | pyproject.toml and tests/README.md | commands and gaps reviewed |
| `docs/SECURITY-MODEL.md` | Applicable | brief trust boundaries | target controls vs current implementation reviewed |
| `docs/agents/foundation.json` | Required | Foundation manifest | four selected package inventories and paths checked; Impeccable excluded by user |
| `docs/agents/skills-checklist.md` | Required | installed packages and host state | counts and scope checked |
| `docs/agents/skill-source-inventories.md` | Required | captured bundle source | per-file hashes checked |
| `docs/AI-FOUNDATION-REPORT.md` | Required | setup evidence | status and scope reviewed |
| `docs/agents/document-delivery.md` | Required | Foundation setup contract | delivery coverage reviewed |
| `docs/history/agent-instructions/index.md` | Applicable | prior AGENTS.md | archive hash recorded |

Local guide links and package Markdown links were checked. The target expense API contract and migrations remain unimplemented; FastAPI currently exposes a health endpoint contract. ADRs become applicable for consequential decisions. Mermaid viewer, hooks and executable tooling were not requested. The four selected local skill packages and their required internal references are inventoried in the manifest and checklist.
