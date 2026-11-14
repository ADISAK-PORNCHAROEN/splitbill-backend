# SplitBill Backend

FastAPI backend for SplitBill. This repository currently contains application configuration and `GET /api/health` only. Expense/group endpoints, database models and migrations, exact-satang calculations, access control, idempotency, and soft deletion remain to be implemented from the take-home brief.

## Run locally

The development Compose file starts PostgreSQL 16 only; FastAPI runs on the host.
The database credentials below are local development placeholders, not production
secrets. Docker Desktop (or another Docker engine) must be running.

```powershell
docker compose up -d
docker compose ps
```

The database listens on `127.0.0.1:5433` and matches `.env.example`. Copy that
file to `.env` as shown below: without it, the application's existing default
still points to port 5432. The named
volume retains data across `docker compose down`; this scaffold does not yet
configure Alembic migrations or seed data. Use a separate database for tests.

From this repository root:

```powershell
py -3.12 -m venv .venv
./.venv/Scripts/Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`; interactive docs are at `/docs`.

See [backend requirements and plan](docs/BACKEND-PLAN.md) for the brief's required
features, test cases and decisions still under discussion.

## Planned access behavior

The selected behavior is to return 404 when a requester is not a group member,
so the API does not disclose whether that group exists. This is a design decision;
the group endpoints and access checks are not implemented yet.
