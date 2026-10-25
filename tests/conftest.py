import psycopg
import pytest
from fastapi.testclient import TestClient

import db
import main
import migrate

ADMIN_URL = "postgresql://sisifo:sisifo@localhost:5433/sisifo"
TEST_URL = "postgresql://sisifo:sisifo@localhost:5433/sisifo_test"


@pytest.fixture(scope="session")
def test_db():
    """recreate the test db from scratch with the migrations and point the app to it"""
    with psycopg.connect(ADMIN_URL, autocommit=True) as conn:
        conn.execute("DROP DATABASE IF EXISTS sisifo_test")
        conn.execute("CREATE DATABASE sisifo_test")
    with psycopg.connect(TEST_URL) as conn:
        migrate.migrate(conn)
    db.DATABASE_URL = TEST_URL


@pytest.fixture
def clean_db(test_db):
    """clean db before starting test so that each test starts from an empty table with ids from 1"""
    with psycopg.connect(TEST_URL) as conn:
        conn.execute("TRUNCATE compounds, experiments, notes RESTART IDENTITY")


@pytest.fixture
def client():
    """return a fake client to do HTTP requests"""
    return TestClient(main.app)
