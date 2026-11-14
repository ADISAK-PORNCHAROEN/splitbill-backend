# SplitBill backend specification

Status: approved and published as [GitHub issue #1](https://github.com/ADISAK-PORNCHAROEN/splitbill-backend/issues/1). Based on the confirmed [backend plan](BACKEND-PLAN.md), the supplied take-home brief and the current scaffold. This document describes the target; the existing application exposes only a health endpoint.

## Problem Statement

Members sharing a bill need a reliable record of who paid and how much each person owes. Manual calculations can lose satang, expose another group's information, or duplicate an expense when a request is retried.

## Solution

Provide a FastAPI service backed by PostgreSQL 16 that records immutable group expenses, allocates every satang, returns zero-sum member balances and controls group access. Callers can retry a valid create request safely. The backend must be reproducible from setup and verified through observable API behavior.

## User Stories

1. As a member, I want to identify myself by name, so that I can use the group data relevant to me.
2. As a member, I want to list only my groups, so that other groups are not exposed.
3. As a member, I want to see my group's members, so that I can select a valid payer and participants.
4. As a member, I want nonmember access to fail without revealing group existence, so that group data remains private.
5. As a member, I want invalid identity headers to receive a clear error, so that I can correct my request.
6. As a member, I want to record who paid a shared cost, so that the amount owed can be calculated.
7. As a member, I want a payer to be able to pay for other members without sharing the expense, so that the record reflects what happened.
8. As a member, I want to split an expense equally among selected members, so that each share is fair to the satang.
9. As a member, I want leftover satang allocated in the listed order, so that results are predictable.
10. As a member, I want small equal splits to allow zero shares, so that the total still allocates correctly.
11. As a member, I want to enter exact positive shares, so that unequal expenses are represented correctly.
12. As a member, I want incorrect share totals and malformed amounts rejected, so that expenses always balance.
13. As a member, I want amounts returned as decimal strings, so that consumers avoid floating-point errors.
14. As a member, I want nonmembers excluded from payer and participant selections, so that a group cannot be charged for outsiders.
15. As a member, I want duplicate or empty equal-split participant lists rejected, so that allocations remain unambiguous.
16. As a member, I want a repeated idempotency key to return its original expense, so that retries cannot double-charge the group.
17. As a member, I want concurrent retries to create at most one expense, so that network races do not duplicate charges.
18. As a member, I want a key to be scoped to a group, so that another group does not collide with it.
19. As a member, I want another member to replay the same group key, so that any authorized caller gets the original result.
20. As a member, I want expense records listed newest first, so that recent spending is easy to find.
21. As a member, I want stable ordering for equal timestamps, so that repeated lists are predictable.
22. As a payer, I want to delete my expense, so that a mistaken entry no longer affects balances.
23. As a member, I want only the payer to delete an expense, so that others cannot remove it.
24. As a member, I want deleted expenses hidden from normal lists and balances, so that the current view is accurate.
25. As a member, I want each member's balance including zero, so that I can see who owes or is owed money.
26. As a member, I want balances to sum to zero exactly, so that the group ledger reconciles.
27. As a developer, I want schema migrations, repeatable seed data and isolated tests, so that the backend is reproducible without destroying development data.
28. As an API consumer, I want consistent JSON errors, so that I can present meaningful failures.

## Implementation Decisions

- Use Python 3.12+, FastAPI, PostgreSQL 16, Alembic, pytest and Ruff, with environment-based settings and separate routing, business rules and data access. Run the existing development database through Compose and the API on the host.
- Seed alice, bob, carol and dan; Chiang Mai trip includes alice, bob and carol, while Office lunch includes bob and dan. Seed separately from migrations with a repeatable command.
- The user identity is `X-User`, a deliberately simplified identifier and not full authentication. Missing, empty or unknown identities return 400. A nonmember gets 404 to avoid disclosing group existence.
- Implement the six paths in the confirmed plan: group list/detail, expense create/list/delete and balances. Use `/groups` paths as in the brief. Success responses use JSON objects or arrays without a data wrapper. Expense data includes ID, group ID, description, payer, amount, shares and creation time.
- Money travels as strings, uses Decimal in Python and NUMERIC(12,2) in PostgreSQL, and never uses float. Reject nonpositive expense amounts, more than two decimal places and numeric overflow with 400. Exact shares are positive and must add up to the total; equal allocation distributes satang in request order, including possible zero shares.
- Members may access only their group; payer and split participants must be members, but the payer need not participate in the split. Return errors in the `error` object with `code` and `message`; validation errors use 400.
- Require a nonempty `Idempotency-Key` on create. Validate identity, group access and request body before replay; a member replaying a valid request with a matching group-scoped key receives the original expense, even with a different valid body, another requester or a soft-deleted original. Do not restore the deleted expense. A new create returns 201; replay returns 200. A database-backed atomic guarantee must survive concurrent requests.
- Expenses cannot be edited. A payer's delete returns 204 and retains the record as deleted; a nonpayer group member gets 403 for an active expense, and a repeat delete gets 404. Normal lists and balances exclude deleted expenses. Order expense lists by creation time descending, then ID descending.
- Return all members' balances including zero as strings; positive means owed to that member, and all balances sum to zero exactly.

## Testing Decisions

- Prefer the existing HTTP API boundary as the main test seam: assert status, JSON, authorization and persisted outcomes rather than internal calls. Exercise real PostgreSQL transactions in a separate test database, especially simultaneous idempotency requests. Add focused unit tests for allocation and money boundaries where they make failures easier to diagnose.
- Cover the required six scenarios: 100.00 → 33.34/33.33/33.33 and zero-sum balances; incorrect exact sum; three decimal places; duplicate key; alice denied reading and writing group 2; payer-only deletion. Include concurrent retries, replay after deletion, different valid versus invalid replay bodies, overflow, no/duplicate participants, zero equal shares and stable ordering.
- The scaffold documents expected tests but currently has no automated tests to copy; pytest is configured. The suite must run in one command with isolated schema and seed data, and Ruff must run separately.

## Out of Scope

Full authentication, frontend implementation, settlement suggestions, repayments, API-plus-database one-command containerisation and deploying the service. Those optional extensions must not displace required scope. Repository restructuring for a full frontend/backend submission requires a separate decision.

## Further Notes

README must record setup, tests, decisions, assumptions, limitations and time spent; AI_NOTES must truthfully record AI use, review and an observed correction. The owner-supplied PDF remains outside this repository. The user confirmed the plan on 2026-11-14 and approved the test seam and ticket breakdown.
