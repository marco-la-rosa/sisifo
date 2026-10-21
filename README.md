# Sisifo

An assistant for chemists working in small labs: pharma R&D teams, PhD groups,
any lab where people make and test molecules.

## The problem

Lab results end up everywhere: Excel sheets, CSV exports, spectra, Word files
with notes. Months later nobody knows which file belongs to which compound,
what was already tried, or where that HPLC trace went.

## The idea

Sisifo keeps everything in one place, organized around the molecules, and lets
you talk to it.

1. **Tell it what you're doing.** Write what you're working on or what you need
   ("I want to make this compound and check its properties") and Sisifo figures
   out the steps and runs them.
2. **Compound registry with linked data.** Every molecule you use or make is
   registered once, with its properties, and everything about it (results,
   files, notes) is attached to it. Search by structure across all of it.
3. **Retrosynthesis.** Give it a target molecule and it proposes possible
   synthetic routes.

## What works today

- `POST /properties`: computes MW, LogP, HBD, HBA, TPSA, rotatable bonds and
  checks Lipinski and Veber rules for a SMILES
- `POST /compounds`: registers a compound (canonical SMILES, properties);
  duplicates are rejected
- `GET /compounds`: lists registered compounds
- `GET /compounds/search?substructure=...`: substructure search, accepts SMARTS (e.g. `c[F,Cl,Br,I]`) and plain SMILES
- `GET /compounds/similar?smiles=...&threshold=0.5`: compounds similar to a molecule (Tanimoto on Morgan fingerprints), most similar first

## Roadmap

- [ ] attach data and files to compounds
- [x] similarity search (Tanimoto)
- [x] substructure search with SMARTS
- [ ] retrosynthesis
- [ ] conversational assistant on top of the tools above
- [ ] database migrations

Ideas for later: import of messy Excel/CSV files, reaction notebook (failures
included), spectra and HPLC reading, SAR tables, export of characterization
data for papers and theses, reagent inventory.

## Running it

Requirements: Python, Docker.

```bash
# database (PostgreSQL + RDKit cartridge, port 5433)
docker compose up -d

# python environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# api, docs at http://localhost:8000/docs
uvicorn main:app --reload

# tests
pytest
```

The database URL can be changed with the `DATABASE_URL` environment variable.

## Stack

FastAPI, RDKit, PostgreSQL with the RDKit cartridge, psycopg 3, pytest.
