# Skills checklist

Standard bundle: **5**, of which **1 is excluded** at the user’s request. Selected total: **4**. Complete project-local packages: **4**. Incomplete selected packages: **0**.

Package completeness is independent of runtime discovery. All packages are exact copies of the captured Foundation bundle; no missing, changed or added paths. Source snapshot fingerprints identify the exact copied bytes; the full per-file source records are in [source inventories](skill-source-inventories.md). A fresh agent host catalog listed all four remaining project-local paths; actual skill execution was not exercised. The existing user-scoped installations and settings remain untouched.

| Skill | Scope / path | Invocation policy | Source → destination files | Source and destination SHA-256 | Discovery |
| --- | --- | --- | --- | --- | --- |
| test-engineering | project: `.agents/skills/test-engineering` | On behavior changes and test authoring | 2 → 2 | `48ab7a5135418971cc6e79b2bdc61e35008cde8c4fe7d1b99d7f5a57c0dd4bb5` | listed in fresh agent catalog; execution unverified |
| security-review | project: `.agents/skills/security-review` | On application-code, dependency, security-configuration, executable-configuration, or CI changes | 2 → 2 | `fd361917704ead6725794dea94fc08def2916ca5c8a561a9517192f7a4821d8a` | listed in fresh agent catalog; execution unverified |
| graphify | project: `.agents/skills/graphify` | Use for codebase/content discovery when relevant; CLI availability is separate | 12 → 12 | `aab00021382bf9fa662577f3db7605d38269edc8aa9f690d80a47176cd34ccd7` | listed in fresh agent catalog; execution unverified |
| hook-management | project: `.agents/skills/hook-management` | Only when the user requests hook inspection, configuration, migration, or removal | 2 → 2 | `01e66efa463c5fff70ccf3b1eee3cfc741b693de6de574d9c2dc2f91a18fd10b` | listed in fresh agent catalog; execution unverified |

Hook-management is explicit-request-only. Graphify CLI is a separate capability and was not installed or invoked. All relative Markdown links checked within each package resolved (external links, fragment-only links and dynamic placeholders excluded).

Foundation is the user-invoked host installer skill and is not counted in the five project workflow packages. No extra workflow skills were selected. Impeccable is explicitly excluded from project-local installation; the existing host-level copy was not changed.
