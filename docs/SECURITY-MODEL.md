# Security model

Target trust boundaries from the brief: `X-User` identifies a requester without full authentication; callers and request bodies are untrusted. Check membership before reading or mutating a group, validate payer and participants, and permit deletion only by the payer. Enforce idempotency transactionally under concurrent requests. Reject invalid monetary input at the boundary and keep secrets outside source. These are requirements, not verified protections in the current scaffold. The 403/404 disclosure policy remains to be decided and documented.
