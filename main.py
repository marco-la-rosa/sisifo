from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors

app = FastAPI(title="Sisifo")

class MoleculeIn(BaseModel):
    smiles: str

@app.post("/properties")
def properties(data: MoleculeIn):
    mol = Chem.MolFromSmiles(data.smiles)
    if mol is None:
        raise HTTPException(status_code=400, detail="SMILES not valid")

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
