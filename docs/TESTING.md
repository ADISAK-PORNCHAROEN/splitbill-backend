# Testing

`pyproject.toml` configures pytest and Ruff; `tests/README.md` lists required cases and states no automated tests exist yet. When implemented, use isolated test data and verify the required cases in PRODUCT.md, including concurrent idempotency and access control. Install the locked development environment with `uv sync --locked`. Run tests with `uv run --locked pytest` and lint with `uv run --locked ruff check .`. Until tests are implemented, pytest reports that no tests were collected and returns exit code 5; do not report that as a passing suite. See README.md for setup.
