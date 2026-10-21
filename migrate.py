from pathlib import Path

from psycopg.rows import dict_row

import db

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def ensure_migrations_table(conn):
    """create schema_migrations table"""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            filename   TEXT PRIMARY KEY,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )


def applied_migrations(conn):
    """return set of filenames in schema_migrations"""
    cur = conn.cursor(row_factory=dict_row)
    rows = cur.execute("SELECT filename FROM schema_migrations").fetchall()
    return {row["filename"] for row in rows}


def migration_files():
    """return files in /migrations"""
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def migrate(conn):
    """apply new migrations from /migrations in order, recording each one in schema_migrations"""
    ensure_migrations_table(conn)
    applied = applied_migrations(conn)

    for path in migration_files():
        if path.name in applied:
            continue
        conn.execute(path.read_text())
        conn.execute(
            "INSERT INTO schema_migrations (filename) VALUES (%s)",
            (path.name,),
        )
        print(f"applied {path.name}")


if __name__ == "__main__":
    with db.get_connection() as conn:
        migrate(conn)
