# Architecture

Currently `app/main.py` mounts the health router at `/api`; `app/core/config.py` supplies settings. The brief calls for separate routes, business logic and data access, FastAPI, PostgreSQL 16 and Alembic; these are target requirements, not evidence of implemented layers. Establish contracts from the brief before adding APIs and document choices as they are made.
