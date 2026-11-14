# Backend scaffold

FastAPI starter for SplitBill. At this stage it contains configuration and GET /api/health only. Expense, group, balance, idempotency, soft-delete, and database migration behavior remain to be implemented from the take-home brief.

## Run locally

From backend/:

    py -3.12 -m venv .venv
    ./.venv/Scripts/Activate.ps1
    python -m pip install -e ".[dev]"
    Copy-Item .env.example .env
    uvicorn app.main:app --reload

The API is available at http://127.0.0.1:8000; interactive docs are at /docs.
