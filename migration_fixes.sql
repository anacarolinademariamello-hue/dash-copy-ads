-- Executar no Supabase SQL Editor

-- 1. Campo separado para contexto de performance (separar do tom de voz)
ALTER TABLE clients
  ADD COLUMN IF NOT EXISTS performance_context TEXT DEFAULT '';

-- 2. Salvar hook_score na tabela de copies
ALTER TABLE saved_copies
  ADD COLUMN IF NOT EXISTS hook_score TEXT DEFAULT '';
