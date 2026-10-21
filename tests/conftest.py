from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient

import db
import main

ADMIN_URL = "postgresql://sisifo:sisifo@localhost:5433/sisifo"
TEST_URL = "postgresql://sisifo:sisifo@localhost:5433/sisifo_test"
INIT_SQL = Path(__file__).parent.parent / "init.sql"


@pytest.fixture(scope="session")
def test_db():
    """recreate the test db from scratch with init.sql and point the app to it"""
    with psycopg.connect(ADMIN_URL, autocommit=True) as conn:
        conn.execute("DROP DATABASE IF EXISTS sisifo_test")
        conn.execute("CREATE DATABASE sisifo_test")
    with psycopg.connect(TEST_URL) as conn:
        conn.execute(INIT_SQL.read_text())
    db.DATABASE_URL = TEST_URL


@pytest.fixture
def clean_db(test_db):
    """clean db before starting test so that each test starts from an empty table with ids from 1"""
    with psycopg.connect(TEST_URL) as conn:
        conn.execute("TRUNCATE compounds RESTART IDENTITY")


@pytest.fixture
def client():
    """return a fake client to do HTTP requests"""
    return TestClient(main.app)
