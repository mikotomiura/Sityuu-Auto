-- 003_add_users.sql: ユーザー管理テーブルを追加（認証・BYOK対応）

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    api_keys_json TEXT,
    preferred_provider TEXT,
    preferred_model TEXT,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
