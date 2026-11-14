# Backend ticket breakdown

Status: approved and published. Parent: [backend specification](BACKEND-SPEC.md) / [GitHub issue #1](https://github.com/ADISAK-PORNCHAROEN/splitbill-backend/issues/1). Testing primarily exercises HTTP with an isolated PostgreSQL database; focused pure allocation tests supplement that seam. Blocking edges are recorded in each issue and as GitHub-native dependencies.

| Draft | GitHub issue | Blocked by |
| --- | --- | --- |
| T1 | [#2 List and inspect authorized groups](https://github.com/ADISAK-PORNCHAROEN/splitbill-backend/issues/2) | None |
| T2 | [#3 Record an equal-split expense safely](https://github.com/ADISAK-PORNCHAROEN/splitbill-backend/issues/3) | #2 |
| T3 | [#4 Record an exact-split expense](https://github.com/ADISAK-PORNCHAROEN/splitbill-backend/issues/4) | #3 |
| T4 | [#5 View zero-sum member balances](https://github.com/ADISAK-PORNCHAROEN/splitbill-backend/issues/5) | #3 |
| T5 | [#6 List and soft-delete expenses](https://github.com/ADISAK-PORNCHAROEN/splitbill-backend/issues/6) | #3 |
| T6 | [#7 Verify full backend journeys and handoff](https://github.com/ADISAK-PORNCHAROEN/splitbill-backend/issues/7) | #4, #5, #6 |

## T1 — List and inspect authorized groups

**Blocked by:** None.

Deliver seeded users and groups, repeatable migration/seed setup, X-User validation and group list/detail endpoints through the API. A user sees only their groups, can inspect a member group, and receives 404 for another group. Deliver consistent 400 identity errors and isolated PostgreSQL integration tests.

## T2 — Record an equal-split expense safely

**Blocked by:** T1.

Deliver a complete create request for equal splits, including member/payer checks, decimal validation, ordered satang allocation, persisted shares, group-scoped keys, valid replay and atomic concurrent deduplication. A group member can create and retry an expense and observe the correct original response; unauthorized access fails. Cover exact 100.00 allocation, 0.01 zero-share edge case, malformed input, group-scoped keys, changed valid or invalid replay bodies, different members and concurrent requests against PostgreSQL.

## T3 — Record an exact-split expense

**Blocked by:** T2.

Extend the create journey so a member can provide exact positive shares that sum to the expense. Reject invalid totals, outsider participants, nonpositive shares, excessive precision and numeric overflow with the agreed 400 error, without creating partial records. Preserve T2's replay guarantees.

## T4 — View zero-sum member balances

**Blocked by:** T2.

Provide group balances for all members, including 0.00, using persisted shares and payer amounts. Demonstrate positive-is-owed semantics, a payer who does not participate, correct satang amounts and exact zero sum; deny nonmembers. The slice works for equal splits independently of T3 and handles exact splits when T3 lands.

## T5 — List and soft-delete expenses

**Blocked by:** T2.

Provide newest-first expense lists with stable ID tie-breaks and payer-only soft deletion. Verify payer 204, nonpayer 403, repeated delete 404, hidden deleted entries and replay of the original key without restoring the expense. Excluding deleted expenses from balances is verified when T4 is available.

## T6 — Verify full backend journeys and handoff

**Blocked by:** T3, T4, T5.

Exercise the entire backend contract against isolated PostgreSQL: all required pytest cases, balances after soft deletion, retry races, access-control failures, structured errors and one-command test execution. Run Ruff and document actual setup, seed/migration instructions, access and idempotency decisions, known limitations, time spent and truthful AI review evidence. Do not implement optional frontend, repayments or settlement.
