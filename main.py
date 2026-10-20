import os

import psycopg
from fastapi import FastAPI, HTTPException
from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row
from pydantic import BaseModel
from rdkit import Chem
from rdkit.Chem import Crippen, Descriptors, rdMolDescriptors

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://sisifo:sisifo@localhost:5433/sisifo"
)

app = FastAPI(title="Sisifo")

class MoleculeIn(BaseModel):
    smiles: str

class CompoundIn(BaseModel):
    name: str | None = None
    smiles: str

def parse_smiles(smiles: str) -> Chem.Mol:
    """Turn smiles into a rdkit molecule, or stop with 400 error"""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise HTTPException(status_code=400, detail="Invalid SMILES")
    return mol

def get_connection() -> psycopg.Connection:
    """Open a new database connection that returns rows as dicts"""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

@app.post("/properties")
def properties(data: MoleculeIn):
    mol = parse_smiles(data.smiles)

    mw = Descriptors.MolWt(mol)
    logp = Crippen.MolLogP(mol)
    hbd = rdMolDescriptors.CalcNumHBD(mol)
    hba = rdMolDescriptors.CalcNumHBA(mol)
    tpsa = rdMolDescriptors.CalcTPSA(mol)
    rotatable_bonds = rdMolDescriptors.CalcNumRotatableBonds(mol)

    violations = sum([mw > 500, logp > 5, hbd > 5, hba > 10])

    return {
        "smiles": Chem.MolToSmiles(mol),
        "mw": round(mw, 2),
        "logp": round(logp, 2),
        "hbd": hbd,
        "hba": hba,
        "tpsa": round(tpsa, 2),
        "rotatable_bonds": rotatable_bonds,
        "lipinski_violations": violations,
        "lipinski_ok": violations <= 1,
        "veber_ok": rotatable_bonds <= 10 and tpsa <= 140
    }

@app.post("/compounds", status_code=201)
def create_compound(data: CompoundIn):
    mol = parse_smiles(data.smiles)
    canonical = Chem.MolToSmiles(mol)

    try:
        with get_connection() as conn:
            row = conn.execute(
                """
                INSERT INTO compounds (name, smiles, mol)
                VALUES (%s, %s, mol_from_smiles(%s::cstring))
                RETURNING id, name, smiles, created_at
                """,
                (data.name, canonical, canonical)
            ).fetchone()
    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Compound already registered")

    return row

@app.get("/compounds")
def list_compounds():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, smiles, created_at
            FROM compounds
            ORDER BY id
            """
        ).fetchall()
    return rows

@app.get("/compounds/search")
def search_compounds(substructure: str):
    parse_smiles(substructure)

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, smiles, created_at
            FROM compounds
            WHERE mol @> mol_from_smiles(%s::cstring)
            ORDER BY id
            """,
            (substructure,),
        ).fetchall()
    return rows
