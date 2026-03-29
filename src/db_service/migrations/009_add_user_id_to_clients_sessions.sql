-- clients テーブルにデータ所有者の user_id を追加
ALTER TABLE clients ADD COLUMN user_id TEXT REFERENCES users(id);

-- sessions テーブルにデータ所有者の user_id を追加
ALTER TABLE sessions ADD COLUMN user_id TEXT REFERENCES users(id);

-- user_id によるフィルタリングを高速化するインデックス
CREATE INDEX IF NOT EXISTS idx_clients_user_id ON clients(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
