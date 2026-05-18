-- Executar no Supabase SQL Editor
-- Cria tabela de copies aprovadas

CREATE TABLE IF NOT EXISTS approved_copies (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  client_name      TEXT        DEFAULT '',
  product          TEXT        NOT NULL,
  niche            TEXT        DEFAULT '',
  sub_niche        TEXT        DEFAULT '',
  objective        TEXT        DEFAULT '',
  tone             TEXT        DEFAULT '',
  cta              TEXT        DEFAULT '',
  tipo_criativo    TEXT        DEFAULT '',
  copy_index       INT,
  tipo_nome        TEXT        DEFAULT '',
  legenda_hook     TEXT        DEFAULT '',
  legenda_corpo    TEXT        DEFAULT '',
  legenda_cta      TEXT        DEFAULT '',
  legenda_completa TEXT        DEFAULT '',
  criativo         TEXT        DEFAULT '',
  created_at       TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS approved_copies_client_name_idx ON approved_copies (client_name);
CREATE INDEX IF NOT EXISTS approved_copies_created_at_idx  ON approved_copies (created_at DESC);
