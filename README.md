# SplitBill

SplitBill is a shared-expense tracker scaffold based on the supplied developer take-home brief.

## Project layout

- `frontend/` — Next.js, React, TypeScript, and Tailwind CSS starter.
- `backend/` — FastAPI starter, settings, and a health endpoint.

## Current status

This repository contains the initial project structure only. Expense and group APIs, database models and migrations, balance calculations, idempotency, access controls, soft deletion, and the functional user interface still need implementation. The cases in `backend/tests/README.md` are requirements to cover later; no automated tests have been written in this scaffold.

## Run locally

Start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Start the backend in another terminal:

```powershell
cd backend
py -3.12 -m venv .venv
./.venv/Scripts/Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The frontend runs at `http://localhost:3000`; the API runs at `http://127.0.0.1:8000` and its interactive docs are at `/docs`.

## Next implementation steps

1. Define the database schema and Alembic migrations.
2. Implement exact-satang expense validation and equal-split remainder allocation.
3. Add group membership checks, idempotent writes, and payer-only soft deletion.
4. Implement group, expense, balance, and frontend flows.
5. Add the required automated tests and update `AI_NOTES.md` with observed AI-assisted changes and risks.
