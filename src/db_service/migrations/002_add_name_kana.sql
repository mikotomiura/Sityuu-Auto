-- 002_add_name_kana.sql: clients テーブルにフリガナカラムを追加

ALTER TABLE clients ADD COLUMN name_kana TEXT;
