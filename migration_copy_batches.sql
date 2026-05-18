-- Executar no Supabase SQL Editor
-- Tabela unificada de copies salvas (aprovadas e rejeitadas)

CREATE TABLE IF NOT EXISTS saved_copies (
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
  status           TEXT        NOT NULL DEFAULT 'aprovada', -- 'aprovada' | 'rejeitada'
  reason           TEXT        DEFAULT '', -- motivo da rejeição (preenchido quando rejeitada)
  created_at       TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS saved_copies_client_name_idx ON saved_copies (client_name);
CREATE INDEX IF NOT EXISTS saved_copies_status_idx      ON saved_copies (status);
CREATE INDEX IF NOT EXISTS saved_copies_created_at_idx  ON saved_copies (created_at DESC);
