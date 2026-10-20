import pytest

import chemistry

ASPIRIN = "CC(=O)Oc1ccccc1C(=O)O"


def props(**overrides):
    # hypothetical molecule that passes all rules, each test changes only what it needs
    base = {"mw": 300, "logp": 2, "hbd": 1, "hba": 4, "tpsa": 60, "rotatable_bonds": 3}
    return {**base, **overrides}


def test_parse_valid_smiles():
    assert chemistry.parse_smiles(ASPIRIN) is not None


def test_parse_invalid_smiles():
    assert chemistry.parse_smiles("C(C(C") is None


def test_canonical_smiles_same_molecule():
    a = chemistry.parse_smiles("CCO")
    b = chemistry.parse_smiles("OCC")
    assert chemistry.canonical_smiles(a) == chemistry.canonical_smiles(b)


def test_aspirin_properties():
    p = chemistry.compute_properties(chemistry.parse_smiles(ASPIRIN))
    assert p["mw"] == pytest.approx(180.16, abs=0.01)
    assert p["logp"] == pytest.approx(1.31, abs=0.01)
    assert p["hbd"] == 1
    assert p["hba"] == 3
    assert p["tpsa"] == pytest.approx(63.6, abs=0.01)
    assert p["rotatable_bonds"] == 2


def test_lipinski_no_violations():
    rules = chemistry.check_rules(props())
    assert rules["lipinski_violations"] == 0
    assert rules["lipinski_ok"]


def test_lipinski_one_violation_is_ok():
    rules = chemistry.check_rules(props(mw=600))
    assert rules["lipinski_violations"] == 1
    assert rules["lipinski_ok"]


def test_lipinski_two_violations_fail():
    rules = chemistry.check_rules(props(mw=600, logp=6))
    assert rules["lipinski_violations"] == 2
    assert not rules["lipinski_ok"]


def test_lipinski_limits_are_not_violations():
    rules = chemistry.check_rules(props(mw=500, logp=5, hbd=5, hba=10))
    assert rules["lipinski_violations"] == 0


@pytest.mark.parametrize(
    "overrides, expected",
    [
        ({}, True),
        ({"rotatable_bonds": 10, "tpsa": 140}, True),
        ({"rotatable_bonds": 11}, False),
        ({"tpsa": 141}, False),
    ],
)
def test_veber(overrides, expected):
    assert chemistry.check_rules(props(**overrides))["veber_ok"] is expected
