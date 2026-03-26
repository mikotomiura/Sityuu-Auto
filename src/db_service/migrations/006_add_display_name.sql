-- ユーザーの表示名カラム追加
-- ログイン用ID (username) とUI表示名 (display_name) を分離する
ALTER TABLE users ADD COLUMN display_name TEXT;

-- 既存ユーザーはusernameを表示名として初期化
UPDATE users SET display_name = username WHERE display_name IS NULL;
