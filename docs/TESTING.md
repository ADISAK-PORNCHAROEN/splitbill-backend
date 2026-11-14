# Testing

Install the locked development environment with `uv sync --locked`. Run `uv run --locked pytest` for the full suite and `uv run --locked ruff check .` for lint. The suite exercises HTTP through FastAPI and PostgreSQL, including concurrent requests, money precision, access control, idempotency and deletion. See `tests/test_api.py` for scenarios and [README](../README.md) for setup.

Tests require a local PostgreSQL role with `CREATEDB`. By default they connect to `127.0.0.1:5433` as the local development role using the `postgres` administration database. Set `TEST_DATABASE_ADMIN_URL` for a different local port or credentials; it must still point to the local `postgres` database. Each test session creates a uniquely named temporary database, applies migrations, resets and seeds it between tests, then drops only that database. It never truncates the development database. Concurrent tests use separate requests against the isolated PostgreSQL instance.
