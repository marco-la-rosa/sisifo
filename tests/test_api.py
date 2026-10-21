import pytest

ASPIRIN = "CC(=O)Oc1ccccc1C(=O)O"
SALICYLIC_ACID = "O=C(O)c1ccccc1O"
METHYL_SALICYLATE = "COC(=O)c1ccccc1O"
CAFFEINE = "Cn1c(=O)c2c(ncn2C)n(C)c1=O"


def add(client, smiles, name=None):
    return client.post("/compounds", json={"name": name, "smiles": smiles})


def names(response):
    return [c["name"] for c in response.json()]


def test_properties(client):
    r = client.post("/properties", json={"smiles": ASPIRIN})
    assert r.status_code == 200
    body = r.json()
    assert body["smiles"] == ASPIRIN
    assert body["hbd"] == 1
    assert body["lipinski_ok"]


def test_properties_invalid_smiles(client):
    r = client.post("/properties", json={"smiles": "C(C(C"})
    assert r.status_code == 400


def test_create_compound(client, clean_db):
    r = add(client, "OCC", "ethanol")
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 1
    assert body["name"] == "ethanol"
    assert body["smiles"] == "CCO"


def test_create_duplicate_returns_409(client, clean_db):
    add(client, "CCO")
    r = add(client, "OCC")
    assert r.status_code == 409


def test_create_invalid_smiles(client, clean_db):
    assert add(client, "C(C(C").status_code == 400


def test_list_compounds(client, clean_db):
    assert client.get("/compounds").json() == []
    add(client, "CCO", "ethanol")
    add(client, ASPIRIN, "aspirin")
    assert names(client.get("/compounds")) == ["ethanol", "aspirin"]


def test_search_substructure(client, clean_db):
    add(client, "CCO", "ethanol")
    add(client, "Oc1ccccc1", "phenol")
    r = client.get("/compounds/search", params={"substructure": "c1ccccc1"})
    assert names(r) == ["phenol"]


def test_search_smarts(client, clean_db):
    add(client, "Clc1ccccc1", "chlorobenzene")
    add(client, "Brc1ccccc1", "bromobenzene")
    add(client, "CCCCCl", "1-chlorobutane")
    add(client, "c1ccccc1", "benzene")
    r = client.get("/compounds/search", params={"substructure": "c[F,Cl,Br,I]"})
    assert names(r) == ["chlorobenzene", "bromobenzene"]


def test_search_invalid_smarts(client):
    r = client.get("/compounds/search", params={"substructure": "c[F,Cl"})
    assert r.status_code == 400


@pytest.fixture
def salicylates(client, clean_db):
    """salicylic acid analogs with decreasing similarity, plus caffeine as negative control"""
    add(client, ASPIRIN, "aspirin")
    add(client, SALICYLIC_ACID, "salicylic acid")
    add(client, METHYL_SALICYLATE, "methyl salicylate")
    add(client, CAFFEINE, "caffeine")


def test_similar_most_similar_first(client, salicylates):
    r = client.get("/compounds/similar", params={"smiles": SALICYLIC_ACID, "threshold": 0.3})
    assert names(r) == ["salicylic acid", "methyl salicylate", "aspirin"]
    assert r.json()[0]["similarity"] == pytest.approx(1)


def test_similar_threshold_filters(client, salicylates):
    r = client.get("/compounds/similar", params={"smiles": SALICYLIC_ACID, "threshold": 0.5})
    assert names(r) == ["salicylic acid", "methyl salicylate"]


@pytest.mark.parametrize("threshold", [-0.1, 1.1])
def test_similar_threshold_out_of_range(client, threshold):
    r = client.get("/compounds/similar", params={"smiles": "CCO", "threshold": threshold})
    assert r.status_code == 422
