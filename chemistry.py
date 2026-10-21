from rdkit import Chem
from rdkit.Chem import Crippen, Descriptors, rdMolDescriptors


def parse_smiles(smiles: str) -> Chem.Mol | None:
    """return a Mol object from smiles, None if the smiles is invalid"""
    return Chem.MolFromSmiles(smiles)


def parse_smarts(smarts: str) -> Chem.Mol | None:
    """return a Mol object from smarts, None if the smarts is invalid"""
    return Chem.MolFromSmarts(smarts)


def canonical_smiles(mol: Chem.Mol) -> str:
    """return the canonical smiles, one unique string per molecule"""
    return Chem.MolToSmiles(mol)


def compute_properties(mol: Chem.Mol) -> dict:
    """return a dict with the descriptors"""
    return {
        "mw": Descriptors.MolWt(mol),
        "logp": Crippen.MolLogP(mol),
        "hbd": rdMolDescriptors.CalcNumHBD(mol),
        "hba": rdMolDescriptors.CalcNumHBA(mol),
        "tpsa": rdMolDescriptors.CalcTPSA(mol),
        "rotatable_bonds": rdMolDescriptors.CalcNumRotatableBonds(mol),
    }


def check_rules(props: dict) -> dict:
    """return lipinski and veber results from the properties"""
    violations = sum([
        props["mw"] > 500,
        props["logp"] > 5,
        props["hbd"] > 5,
        props["hba"] > 10,
    ])
    return {
        "lipinski_violations": violations,
        "lipinski_ok": violations <= 1,
        "veber_ok": props["rotatable_bonds"] <= 10 and props["tpsa"] <= 140,
    }
