# SplitBill Backend

FastAPI backend for SplitBill. This repository currently contains application configuration and `GET /api/health` only. Expense/group endpoints, database models and migrations, exact-satang calculations, access control, idempotency, and soft deletion remain to be implemented from the take-home brief.

## Run locally

From this repository root:

```powershell
py -3.12 -m venv .venv
./.venv/Scripts/Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`; interactive docs are at `/docs`.
