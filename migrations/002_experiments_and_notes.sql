CREATE TABLE experiments (
  id              SERIAL PRIMARY KEY,
  code            TEXT NOT NULL UNIQUE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE notes (
  id              SERIAL PRIMARY KEY,
  experiment_id   INTEGER REFERENCES experiments (id),
  body            TEXT NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
