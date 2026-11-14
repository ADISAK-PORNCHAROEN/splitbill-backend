# SplitBill Backend

FastAPI backend for SplitBill. It records shared expenses, allocates amounts to the satang and calculates group balances.

## Run locally

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and use Python
3.12 or newer. The development Compose file starts PostgreSQL 16 only; FastAPI runs on the host.
The database credentials below are local development placeholders, not production
secrets. Docker Desktop (or another Docker engine) must be running.

```powershell
docker compose up -d
docker compose ps
```

The database listens on `127.0.0.1:5433` and matches `.env.example`. The named
volume retains data across `docker compose down`. Use a separate database for tests.

From this repository root:

```powershell
uv sync --locked
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
uv run --locked alembic upgrade head
uv run --locked python -m app.seed
uv run --locked uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`; interactive docs are at `/docs`.
The `uv.lock` file records resolved dependencies. Development tools are installed
by default; use `uv sync --locked --no-dev` for runtime dependencies only. Run
`uv run --locked ruff check .` for linting and `uv run --locked pytest` for tests.
The test suite creates and drops its own uniquely named database on local
PostgreSQL. It requires a PostgreSQL role with `CREATEDB`; configure
`TEST_DATABASE_ADMIN_URL` to connect to the local `postgres` database if the
default local development credentials do not apply. It never uses the development
database for test data.

See [backend requirements and plan](docs/BACKEND-PLAN.md) for the brief's required
features, test cases and decisions still under discussion.

## Design decisions and limitations

- Group access returns 404 to nonmembers so the API does not disclose whether a
  group exists. `X-User` identifies a seeded user and is not authentication.
- Money is exchanged as strings, calculated with `Decimal` and stored in
  `NUMERIC(12,2)`. Equal splits allocate remaining satang in the requested order.
- Each group and idempotency key identify one expense. A database uniqueness
  constraint and transaction handle concurrent requests. A valid replay returns
  the original expense even after soft deletion or with a different valid body;
  an invalid replay receives 400. Deleted expenses are excluded from lists and
  balances. Only the payer can delete.
- The repeatable seed command fails instead of overwriting conflicting existing
  users or groups. A clean database can be migrated and seeded with the commands above.
- The frontend, production authentication, settlement suggestions and repayment
  endpoints are outside this repository's current implementation. The complete
  assignment submission also requires a frontend and the `backend/` and
  `frontend/` repository layout described in the brief.
- `CORS_ORIGINS` is a JSON array of allowed browser origins. It defaults to local
  frontend origins on port 3000 and must be configured for other deployments.

See [the frontend API handoff](docs/FRONTEND-API-HANDOFF.md) for request and
response examples. Approximate time spent across all prior sessions has not been
recorded; the submitter should add their own estimate before submission.
