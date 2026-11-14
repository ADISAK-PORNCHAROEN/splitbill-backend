# Schema

Alembic manages users, groups, memberships, expenses and shares. The initial migration defines group-scoped unique idempotency keys, membership-backed payer/share foreign keys and `NUMERIC(12,2)` amounts. Expense and shares are inserted in one transaction; expenses retain their idempotency keys when soft-deleted. Balances are derived from active expenses and shares. `app.seed` supplies the brief's users and groups separately from migrations and fails on conflicting seed identities rather than overwriting them. Models and migrations are the authoritative definitions.
