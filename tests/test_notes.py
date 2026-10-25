def add_experiment(client, code):
    return client.post("/experiments", json={"code": code})


def add_note(client, body, experiment_id=None):
    return client.post("/notes", json={"body": body, "experiment_id": experiment_id})


def bodies(response):
    return [n["body"] for n in response.json()]


def test_create_experiment(client, clean_db):
    r = add_experiment(client, "ML-042")
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 1
    assert body["code"] == "ML-042"


def test_create_duplicate_experiment_returns_409(client, clean_db):
    add_experiment(client, "ML-042")
    assert add_experiment(client, "ML-042").status_code == 409


def test_list_experiments_newest_first(client, clean_db):
    add_experiment(client, "ML-041")
    add_experiment(client, "ML-042")
    codes = [e["code"] for e in client.get("/experiments").json()]
    assert codes == ["ML-042", "ML-041"]


def test_create_note(client, clean_db):
    add_experiment(client, "ML-042")
    r = add_note(client, "added 2 mL Ac2O", 1)
    assert r.status_code == 201
    assert r.json()["experiment_id"] == 1


def test_create_unassigned_note(client, clean_db):
    r = add_note(client, "order more DCM")
    assert r.status_code == 201
    assert r.json()["experiment_id"] is None


def test_create_note_unknown_experiment_returns_404(client, clean_db):
    assert add_note(client, "lost note", 99).status_code == 404


def test_experiment_notes_in_order(client, clean_db):
    add_experiment(client, "ML-042")
    add_experiment(client, "ML-043")
    add_note(client, "added Ac2O", 1)
    add_note(client, "degassed with Ar", 2)
    add_note(client, "TLC: SM gone", 1)
    add_note(client, "order more DCM")
    r = client.get("/experiments/1/notes")
    assert r.status_code == 200
    assert bodies(r) == ["added Ac2O", "TLC: SM gone"]


def test_experiment_without_notes_returns_empty_list(client, clean_db):
    add_experiment(client, "ML-042")
    assert client.get("/experiments/1/notes").json() == []


def test_notes_unknown_experiment_returns_404(client, clean_db):
    assert client.get("/experiments/99/notes").status_code == 404


def test_unassigned_notes(client, clean_db):
    add_experiment(client, "ML-042")
    add_note(client, "added Ac2O", 1)
    add_note(client, "order more DCM")
    assert bodies(client.get("/notes", params={"unassigned": True})) == ["order more DCM"]
    assert bodies(client.get("/notes")) == ["added Ac2O", "order more DCM"]
