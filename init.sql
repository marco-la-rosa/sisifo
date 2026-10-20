CREATE EXTENSION IF NOT EXISTS rdkit;

CREATE TABLE compounds (
    id         SERIAL PRIMARY KEY,
    name       TEXT,
    smiles     TEXT NOT NULL UNIQUE,
    mol        mol NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX compounds_mol_idx ON compounds USING gist (mol);
