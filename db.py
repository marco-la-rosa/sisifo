import os

import psycopg
from psycopg.errors import UniqueViolation, ForeignKeyViolation
from psycopg.rows import dict_row

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://sisifo:sisifo@localhost:5433/sisifo"
)


class DuplicateCompoundError(Exception):
    """raised when inserting a compound whose canonical smiles is already in the db"""


class DuplicateExperimentError(Exception):
    """raised when inserting an experiment whose code is already in the db"""


class ExperimentNotFoundError(Exception):
    """raised when the requested experiment doesn't exist"""


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


def search_substructure(smarts: str) -> list[dict]:
    """return compounds that contain a substructure, given as smarts"""
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, name, smiles, mw, logp, hbd, hba, tpsa,
                   rotatable_bonds, created_at
            FROM compounds
            WHERE mol @> qmol_from_smarts(%(smarts)s::cstring)
            ORDER BY id
            """,
            {"smarts": smarts},
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


def insert_experiment(code: str) -> dict:
    """insert into database an experiment and return the saved row"""
    try:
        with get_connection() as conn:
            return conn.execute(
                """
                INSERT INTO experiments (code)
                VALUES (%(code)s)
                RETURNING id, code, created_at
                """,
                {"code": code},
            ).fetchone()
    except UniqueViolation:
        raise DuplicateExperimentError(code)


def list_experiments() -> list[dict]:
    """return a list of the experiments in database"""
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, code, created_at
            FROM experiments
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()


def insert_note(body: str, experiment_id: int | None = None) -> dict:
    """insert into database a note and return the saved row"""
    try:
        with get_connection() as conn:
            return conn.execute(
                """
                INSERT INTO notes (body, experiment_id)
                VALUES (%(body)s, %(experiment_id)s)
                RETURNING id, experiment_id, body, created_at
                """,
                {"body": body, "experiment_id": experiment_id},
            ).fetchone()
    except ForeignKeyViolation:
        raise ExperimentNotFoundError(experiment_id)


def list_notes(experiment_id: int) -> list[dict]:
    """return a list of the notes of a certain experiment"""
    with get_connection() as conn:
        experiment = conn.execute(
            """
            SELECT 1 FROM experiments WHERE id = %(experiment_id)s
            """,
            {"experiment_id": experiment_id},
        ).fetchone()
        if experiment is None:
            raise ExperimentNotFoundError(experiment_id)
        return conn.execute(
            """
            SELECT id, experiment_id, body, created_at
            FROM notes
            WHERE experiment_id = %(experiment_id)s
            ORDER BY created_at, id
            """,
            {"experiment_id": experiment_id},
        ).fetchall()


def list_unassigned_notes() -> list[dict]:
    """return a list of notes that don't belong to any experiment"""
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, experiment_id, body, created_at
            FROM notes
            WHERE experiment_id IS NULL
            ORDER BY created_at, id
            """,
        ).fetchall()


def list_all_notes() -> list[dict]:
    """return a list of all the notes, with or without experiment"""
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, experiment_id, body, created_at
            FROM notes
            ORDER BY created_at, id
            """
        ).fetchall()
