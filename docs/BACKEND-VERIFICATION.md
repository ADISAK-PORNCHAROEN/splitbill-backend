# Backend verification against the brief

The source is the owner-provided Developer Take-Home Test, pages 1–5, and the agreed [backend specification](BACKEND-SPEC.md). This document records evidence, not an assigned score. The project is a backend-only repository; a complete submission also requires the frontend and the requested `backend/` and `frontend/` directory layout.

## Requirements and evidence

| Requirement | Evidence and scope |
| --- | --- |
| FastAPI, Python 3.12+, PostgreSQL 16 and Alembic | Project configuration, Compose and migration; local PostgreSQL 16 used for integration tests. |
| Seed users and groups | `app.seed`, HTTP group tests and repeat-seed test; migration and seed are separate. |
| Six group/expense/balance routes | `app/api/controllers` and HTTP integration tests. `/api/health` remains available separately. |
| Decimal strings, equal and exact allocation, precision and zero-sum balances | Domain allocation tests plus HTTP tests for 100.00, exact mismatch, precision, range, small equal split and balances. |
| Group access, membership and payer-only soft deletion | HTTP tests for missing/unknown users, nonmember reads and writes, nonpayer deletion, repeated deletion and excluded deleted amounts. `X-User` is identification only, not production authentication. |
| Group-scoped idempotency and concurrency | Concurrent HTTP tests include bursts of eight and 48 requests, each creating one expense and returning the same result; replay after deletion and across members is also tested. |
| .env configuration, errors, Ruff and separated layers | Settings and `.env.example`, HTTP error-envelope tests, Ruff, and controller/service/repository/entity structure. Local CORS origins are configurable. |

## Evaluation criteria

| PDF criterion | Weight | Evidence and limitations |
| --- | ---: | --- |
| Backend business rules | 35% | Automated API tests and an independent live HTTP/PostgreSQL smoke journey cover the specified rules. No production authentication is claimed. |
| Required test coverage | 20% | Pytest covers the six mandated scenarios and additional validation, concurrency, authorization and deletion cases. No coverage percentage or evaluator score is claimed. |
| Code structure and maintainability | 15% | The implementation follows the selected controller, service, repository and entity boundaries; Ruff and type checks pass. Independent review identified issues that were fixed and retested. |
| Frontend behavior | 15% | Out of scope for this backend-only repository. Browser CORS preflight is tested, but the actual frontend has not been integrated or tested here. |
| README, AI notes and commit history | 15% | Setup, decisions, limitations and AI usage are documented. The submitter still needs to supply their own approximate total time and ensure the full submission layout. |

## Observed checks

- `uv lock --check` confirmed the lockfile is in sync.
- `uv run --locked ruff check .` and `uv run --locked ruff format --check .` passed.
- `uvx ty check app` passed; `ty` is run as a separate uv tool, not added to project dependencies.
- `uv run --locked pytest -q` passed 37 tests in the isolated PostgreSQL suite, with one Starlette TestClient deprecation warning.
- A separately started Uvicorn process was exercised over local HTTP against a fresh temporary PostgreSQL database. Health returned 200, expense creation 201, key replay 200, balances 200, nonmember access 404, nonpayer deletion 403 and payer deletion 204. Direct SQL confirmed one expense and three shares, then confirmed the soft-deleted row remained. The temporary database was removed.
- Security review traced identity, authorization, input validation, scoped idempotency, soft deletion, request-body handling, CORS and test-database cleanup. Independent review findings were corrected; this is a scoped code review, not a complete security audit. The `X-User` identity can be spoofed by design.

The installed Starlette TestClient emits a deprecation warning about `httpx`; tests still ran. Automated coverage measurement and actual frontend integration were not performed. The submitter should record the overall time spent; prior sessions were not timed.
