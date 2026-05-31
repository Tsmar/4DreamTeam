CREATE TABLE IF NOT EXISTS memory_items (
  id TEXT PRIMARY KEY,

  scope TEXT NOT NULL,
  type TEXT NOT NULL,
  role TEXT,

  content TEXT NOT NULL,
  summary TEXT,
  metadata_json TEXT NOT NULL DEFAULT '{}',

  confidence REAL NOT NULL DEFAULT 0.70,
  source_type TEXT,
  source_ref TEXT,
  evidence_hash TEXT,

  ttl_at TEXT,

  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  deleted_at TEXT
);

CREATE TABLE IF NOT EXISTS memory_evidence (
  id TEXT PRIMARY KEY,
  memory_id TEXT NOT NULL REFERENCES memory_items(id) ON DELETE CASCADE,
  source_type TEXT NOT NULL,
  source_ref TEXT,
  quote_hash TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_agent_sessions (
  id TEXT PRIMARY KEY,
  state_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_audit_log (
  id TEXT PRIMARY KEY,
  action TEXT NOT NULL,
  memory_id TEXT,
  payload_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_contract_entries (
  key TEXT NOT NULL,
  value_json TEXT NOT NULL,
  value_type TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (key)
);

CREATE INDEX IF NOT EXISTS idx_memory_items_live
  ON memory_items(deleted_at, ttl_at);

CREATE INDEX IF NOT EXISTS idx_memory_items_filters
  ON memory_items(scope, type, role);

CREATE INDEX IF NOT EXISTS idx_memory_evidence_memory
  ON memory_evidence(memory_id);

CREATE INDEX IF NOT EXISTS idx_memory_audit_log_action
  ON memory_audit_log(action);
