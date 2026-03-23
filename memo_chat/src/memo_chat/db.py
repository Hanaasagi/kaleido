SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS memories (
  id              UUID PRIMARY KEY,
  content         TEXT NOT NULL,
  tags            JSONB NOT NULL DEFAULT '[]'::jsonb,
  metadata        JSONB,
  embedding       vector(1536),
  memory_type     VARCHAR(20) NOT NULL DEFAULT 'insight',
  source          VARCHAR(100),
  agent_id        VARCHAR(100),
  session_id      VARCHAR(100),
  state           VARCHAR(20) NOT NULL DEFAULT 'active',
  version         INT NOT NULL DEFAULT 1,
  updated_by      VARCHAR(100),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_memories_agent ON memories (agent_id);
CREATE INDEX IF NOT EXISTS idx_memories_session ON memories (session_id);
CREATE INDEX IF NOT EXISTS idx_memories_state ON memories (state);
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories (memory_type);

CREATE INDEX IF NOT EXISTS idx_memories_content_trgm ON memories USING gin (content gin_trgm_ops);
"""
