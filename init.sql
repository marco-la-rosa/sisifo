CREATE EXTENSION IF NOT EXISTS rdkit;

CREATE TABLE compounds (
    id              SERIAL PRIMARY KEY,
    name            TEXT,
    smiles          TEXT NOT NULL UNIQUE,
    mol             mol NOT NULL,
    mw              DOUBLE PRECISION NOT NULL,
    logp            DOUBLE PRECISION NOT NULL,
    hbd             INTEGER NOT NULL,
    hba             INTEGER NOT NULL,
    tpsa            DOUBLE PRECISION NOT NULL,
    rotatable_bonds INTEGER NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX compounds_mol_idx ON compounds USING gist (mol);
