-- Executar no Supabase SQL Editor
-- Cria tabela de histórico de copies geradas

CREATE TABLE IF NOT EXISTS copy_batches (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  client_name   TEXT        DEFAULT '',
  client_key    TEXT        DEFAULT '',
  product       TEXT        NOT NULL,
  niche         TEXT        DEFAULT '',
  sub_niche     TEXT        DEFAULT '',
  objective     TEXT        DEFAULT '',
  tone          TEXT        DEFAULT '',
  cta           TEXT        DEFAULT '',
  tipo_criativo TEXT        DEFAULT '',
  copies        JSONB       NOT NULL DEFAULT '[]',
  created_at    TIMESTAMPTZ DEFAULT now()
);

-- Índices para consultas rápidas
CREATE INDEX IF NOT EXISTS copy_batches_client_name_idx ON copy_batches (client_name);
CREATE INDEX IF NOT EXISTS copy_batches_created_at_idx  ON copy_batches (created_at DESC);
