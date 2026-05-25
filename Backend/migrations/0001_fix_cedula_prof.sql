-- Migration: fix cedula_prof type to numeric(8,0)
-- Safe ALTER: handles cases where cedula_prof is numeric[], text, or numeric
-- Make a backup before running on production.

BEGIN;

-- Optional: create a small backup table of current values
CREATE TABLE IF NOT EXISTS escuela._backup_profesores_cedula AS
SELECT id_profesor, cedula_prof, anu_prof, now() AS backed_at
FROM escuela.profesores;

-- Convert cedula_prof to numeric(8,0) safely
ALTER TABLE escuela.profesores
  ALTER COLUMN cedula_prof TYPE numeric(8,0)
  USING (
    CASE
      WHEN cedula_prof IS NULL THEN NULL
      -- If it's an array (eg numeric[]), take first element
      WHEN pg_typeof(cedula_prof)::text = 'numeric[]' THEN (cedula_prof)[1]::numeric(8,0)
      -- If it's text or other scalar, try cast
      ELSE cedula_prof::numeric(8,0)
    END
  );

COMMIT;

-- To review backup: SELECT * FROM escuela._backup_profesores_cedula LIMIT 50;
