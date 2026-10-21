import os

import psycopg
from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://sisifo:sisifo@localhost:5433/sisifo"
)


class DuplicateCompoundError(Exception):
    """raised when inserting a compound whose canonical smiles is already in the db"""


def get_connection() -> psycopg.Connection:
    """open a new db connection, rows come back as dict"""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def insert_compound(name: str | None, smiles: str, props: dict) -> dict:
    """insert into database a compound and return the saved row"""
    try:
        with get_connection() as conn:
            return conn.execute(
                """
                INSERT INTO compounds
                    (name, smiles, mol, mw, logp, hbd, hba, tpsa, rotatable_bonds)
                VALUES
                    (%(name)s, %(smiles)s, mol_from_smiles(%(smiles)s::text::cstring),
                     %(mw)s, %(logp)s, %(hbd)s, %(hba)s, %(tpsa)s, %(rotatable_bonds)s)
                RETURNING id, name, smiles, mw, logp, hbd, hba, tpsa,
                          rotatable_bonds, created_at
                """,
                {"name": name, "smiles": smiles, **props},
            ).fetchone()
    except UniqueViolation:
        raise DuplicateCompoundError(smiles)


def list_compounds() -> list[dict]:
    """return a list of the compounds in database"""
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, name, smiles, mw, logp, hbd, hba, tpsa,
                   rotatable_bonds, created_at
            FROM compounds
            ORDER BY id
            """
        ).fetchall()


def search_substructure(smiles: str) -> list[dict]:
    """return compounds that contain a substructure"""
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, name, smiles, mw, logp, hbd, hba, tpsa,
                   rotatable_bonds, created_at
            FROM compounds
            WHERE mol @> mol_from_smiles(%(smiles)s::cstring)
            ORDER BY id
            """,
            {"smiles": smiles},
        ).fetchall()


def search_similar(smiles: str, threshold: float) -> list[dict]:
    """return compounds with tanimoto similarity >= threshold, most similar first"""
    with get_connection() as conn:
        conn.execute(
            "SELECT set_config('rdkit.tanimoto_threshold', %s, true)",
            (str(threshold),),
        )
        return conn.execute(
            """
            WITH query AS (
                SELECT morganbv_fp(mol_from_smiles(%(smiles)s::cstring)) AS fp
            )
            SELECT id, name, smiles, mw, logp, hbd, hba, tpsa,
                   rotatable_bonds, created_at,
                   tanimoto_sml(mfp, query.fp) AS similarity
            FROM compounds, query
            WHERE mfp %% query.fp
            ORDER BY similarity DESC
            """,
            {"smiles": smiles},
        ).fetchall()
