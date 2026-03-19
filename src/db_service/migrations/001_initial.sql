-- 001_initial.sql: 初期スキーマ作成

-- 相談者テーブル
CREATE TABLE IF NOT EXISTS clients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    birth_time TEXT,
    gender TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 鑑定セッションテーブル
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    concern TEXT NOT NULL,
    natal_chart_json TEXT NOT NULL,
    sanmei_data_json TEXT,
    ai_reading_text TEXT,
    ai_listening_hints TEXT,
    mentor_notes TEXT,
    api_provider TEXT,
    api_model TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- プロンプトテンプレートテーブル
CREATE TABLE IF NOT EXISTS prompt_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    system_prompt TEXT NOT NULL,
    description TEXT,
    is_default INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_sessions_client_id ON sessions(client_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(name);
