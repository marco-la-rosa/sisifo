from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import chemistry
import db

app = FastAPI(title="Sisifo")


class MoleculeIn(BaseModel):
    smiles: str


class CompoundIn(BaseModel):
    name: str | None = None
    smiles: str


def parse_or_400(smiles: str):
    """return a Mol object from smiles or raise 400 error"""
    mol = chemistry.parse_smiles(smiles)
    if mol is None:
        raise HTTPException(status_code=400, detail="Invalid SMILES")
    return mol


@app.post("/properties")
def properties(data: MoleculeIn):
    mol = parse_or_400(data.smiles)
    props = chemistry.compute_properties(mol)
    rules = chemistry.check_rules(props)
    return {"smiles": chemistry.canonical_smiles(mol), **props, **rules}


@app.post("/compounds", status_code=201)
def create_compound(data: CompoundIn):
    mol = parse_or_400(data.smiles)
    smiles = chemistry.canonical_smiles(mol)
    props = chemistry.compute_properties(mol)

    try:
        return db.insert_compound(data.name, smiles, props)
    except db.DuplicateCompoundError:
        raise HTTPException(status_code=409, detail="Compound already registered")


@app.get("/compounds")
def list_compounds():
    return db.list_compounds()


@app.get("/compounds/search")
def search_compounds(substructure: str):
    parse_or_400(substructure)
    return db.search_substructure(substructure)
