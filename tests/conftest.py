import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg import sql
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def test_database():
    admin_url = make_url(
        os.environ.get(
            "TEST_DATABASE_ADMIN_URL", "postgresql://splitbill:splitbill@127.0.0.1:5433/postgres"
        )
    )
    if (
        admin_url.get_backend_name() != "postgresql"
        or admin_url.host not in {"localhost", "127.0.0.1", "::1"}
        or admin_url.database != "postgres"
        or admin_url.query
    ):
        pytest.fail("TEST_DATABASE_ADMIN_URL must point to a local PostgreSQL postgres database")
    admin_conninfo = admin_url.set(drivername="postgresql").render_as_string(hide_password=False)
    name = f"splitbill_test_{uuid4().hex}"
    database_url = admin_url.set(drivername="postgresql+psycopg", database=name)
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url.render_as_string(hide_password=False)
    with psycopg.connect(admin_conninfo, autocommit=True, connect_timeout=5) as admin:
        admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
        try:
            subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                cwd=ROOT,
                env=env,
                check=True,
            )
            yield database_url, env
        finally:
            admin.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))


@pytest.fixture
def client(test_database, monkeypatch):
    database_url, env = test_database
    conninfo = database_url.set(drivername="postgresql").render_as_string(hide_password=False)
    with psycopg.connect(conninfo, autocommit=True) as connection:
        tables = connection.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' "
            "AND tablename <> 'alembic_version'"
        ).fetchall()
        if tables:
            names = sql.SQL(", ").join(sql.Identifier("public", table[0]) for table in tables)
            connection.execute(sql.SQL("TRUNCATE {} RESTART IDENTITY CASCADE").format(names))
    subprocess.run([sys.executable, "-m", "app.seed"], cwd=ROOT, env=env, check=True)
    monkeypatch.setenv("DATABASE_URL", env["DATABASE_URL"])
    from app.core.database import engine
    from app.main import app

    assert engine.url == database_url, "Application must use the isolated test database"

    with TestClient(app) as test_client:
        yield test_client
