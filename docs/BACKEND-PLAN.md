# Backend requirements and implementation plan

Source: owner-supplied `Developer-Take-Home-Test.pdf`, pages 1–3 (backend), with submission requirements on pages 4–5. The original is outside this repository. This is a planning record; see the implementation and tests for current behavior.

Status: the user confirmed the plan and recorded decisions on 2026-11-14. The backend implementation follows the conventions below; see the frontend handoff for actual response fields.

## Required environment

- Python 3.12 or newer, FastAPI, PostgreSQL 16, schema managed by Alembic migrations, pytest and Ruff.
- Configuration via environment variables, with `.env.example`; never commit secrets. Separate routing, business rules and data access; return consistent JSON errors with appropriate status codes.
- Docker Compose starting the API and PostgreSQL is an optional extension in the brief. The user chose PostgreSQL in Docker and FastAPI on the host for development; the supplied Compose file starts the database only and is not the brief's full optional API-plus-database containerisation.
- A full submission also requires `backend/` and `frontend/`, setup/testing and decision rationale in README, AI usage and review details in AI_NOTES, and incremental commits. This repository currently holds only the backend scaffold; do not move it without a decision.

## Required data and API

Seed users alice, bob, carol, dan; group 1 `Chiang Mai trip` has alice, bob, carol; group 2 `Office lunch` has bob, dan. The user chose a seed command separate from migrations, designed to be safe to run repeatedly. `X-User` identifies the requester; full authentication is outside the brief.

The user chose to reject missing, empty or unknown `X-User` with HTTP 400 and an explanatory JSON error. Creating an expense requires a nonempty `Idempotency-Key`; a missing or empty key is rejected. An equal split with an empty member list or duplicate member names is also rejected. Invalid requests use HTTP 400; all errors use the JSON shape `{"error": {"code": "...", "message": "..."}}`.

| Method and path in brief | Observable behavior |
| --- | --- |
| `GET /groups` | Return the requesting user's groups. |
| `GET /groups/{group_id}` | Return the group and members, subject to access. |
| `POST /groups/{group_id}/expenses` | Record an expense with `Idempotency-Key`; accept equal or exact split. A new expense returns 201; a valid replay returns 200 and the original expense. |
| `GET /groups/{group_id}/expenses` | Return expenses newest first; when timestamps are equal, order by descending expense ID. |
| `DELETE /groups/{group_id}/expenses/{expense_id}` | Payer-only soft delete; successful deletion returns 204 with no body. A group member who is not the payer receives 403 for an active expense. |
| `GET /groups/{group_id}/balances` | Return every member's net balance, including 0.00; positive means money is owed to that member. |

The user chose the brief's `/groups` paths, even though the existing health route uses `/api`. The example create body has `description`, `paid_by`, string `amount` and `split`: equal has ordered `members`, exact has a map of member names to string `shares`. Success responses use straightforward JSON objects or arrays without an added `data` wrapper, and monetary values are strings. An expense response includes `id`, `group_id`, `description`, `paid_by`, `amount`, `shares` and `created_at`. The brief does not specify every response field; complete their precise schema during API design.

## Invariants

1. Parse and transmit money as strings, use Python `Decimal` and PostgreSQL `NUMERIC(12,2)`, never float; reject expense amounts at or below zero, any amount with more than two decimal places, and values outside the database numeric range before writing, with HTTP 400.
2. Exact shares must be greater than zero and total the amount to the satang; reject mismatches with a descriptive error. Equal division distributes remaining satang one at a time in the supplied member order. The user chose to allow zero shares produced by equal division, for example 0.01 split among three participants.
3. Group balances sum to exactly 0.00. For 1,000.00 paid by alice and split among alice, bob, carol in that order, shares are 333.34/333.33/333.33 and balances are +666.66/−333.33/−333.33.
4. Only members may read or modify their group; alice cannot access group 2. Every payer and split participant must be a group member. A payer need not be one of the split participants, as decided by the user. The user chose 404 for nonmembers to avoid disclosing group existence; record that rationale in README when implemented.
5. Repeating an `Idempotency-Key` in the same group returns the originally created expense and creates no duplicate, including under concurrency. Check group access before resolving the key: a nonmember gets 404 and no expense data. Any member may replay a key used in that group. The user chose to return the original even when a repeated request has a different valid body or the original was soft-deleted; replay does not restore it. A replay whose new body fails validation returns 400 instead; this interpretation of an invalid replay must be documented in README because the brief does not specify it. Ensure the database, transaction and retry design provide the concurrency guarantee; an in-process lock alone is insufficient.
6. Expenses cannot be edited. Only the payer may delete; retain the expense as soft-deleted and exclude it from balances. The user chose to hide soft-deleted expenses from the normal expense list and return 404 if the payer deletes the same expense again.

## Delivery sequence and evidence

1. Settle the open decisions below; describe the chosen contracts and security boundaries. Keep the brief's six paths and required example verifiable.
2. Configure migrations, persisted users/groups/memberships/expenses/shares and deterministic seed data. Decide transaction and isolation strategy, especially for concurrent creation. Verify fresh database migration and seeding.
3. Implement money validation, equal/exact allocation and balance logic independently of HTTP; test boundaries and zero-sum cases using decimal-safe expectations.
4. Add request identity, group authorization and group endpoints. Verify allowed and denied reads/writes against isolated PostgreSQL data.
5. Add expense create/list/delete with idempotency and soft deletion. Exercise concurrent identical-key requests, payer-only deletion and balances after deletion.
6. Run the whole pytest suite with one command, run Ruff, review the changed security boundaries, and record actual results. Document setup, decisions, assumptions, limitations, time and AI review evidence; do not invent an AI failure or claim tests passed without running them.

Required pytest minimum: 100.00 split 33.34/33.33/33.33 with zero-sum balances; reject mismatched exact shares; reject 3-decimal amount; repeated key creates one expense; alice cannot read or write group 2; only payer deletes. Concurrent duplicate requests are independently required by the business rule and need a real PostgreSQL integration scenario. Use a separate test database whose schema and seed data are managed by the tests; do not clear or reuse development data.

Optional after required scope is complete and tested: settlement suggestions, repayments, and the brief's one-command API plus PostgreSQL containerisation. The user separately requested development Compose configuration now.

## Decisions needing discussion

- 404 for nonmembers and a database-only development Compose topology are user decisions; apply 404 consistently with missing groups.
- Complete the precise success response schemas not specified in the brief, following the chosen expense fields, object/array and string-money conventions.
- The user chose to reject exact shares at or below 0.00; this is a decision for this project, not an independently specified share rule in the brief.
- Invalid input and numeric overflow use HTTP 400 with the chosen error shape; these choices are not independently specified by the brief.
- Define the test-database lifecycle and repeatable setup while preserving the chosen separation from development data.
