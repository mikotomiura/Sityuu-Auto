"""プロンプトテンプレートリポジトリのユニットテスト。"""

import sqlite3

import pytest

from db_service.repositories.prompt_template_repo import PromptTemplateRepository
from utils.exceptions import DatabaseError


@pytest.fixture()
def db_conn() -> sqlite3.Connection:
    """テスト用のインメモリDB接続を生成する。"""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE prompt_templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            system_prompt TEXT NOT NULL,
            description TEXT,
            is_default INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


@pytest.fixture()
def repo(db_conn: sqlite3.Connection) -> PromptTemplateRepository:
    """テスト用リポジトリを生成する。"""
    return PromptTemplateRepository(db_conn)


class TestSave:
    """save メソッドのテスト。"""

    def test_save_returns_uuid(self, repo: PromptTemplateRepository) -> None:
        """保存成功時にUUID文字列が返ること。"""
        template_id = repo.save(
            name="テスト",
            system_prompt="テスト用プロンプト",
        )
        assert isinstance(template_id, str)
        assert len(template_id) == 36  # UUID format

    def test_save_with_default(self, repo: PromptTemplateRepository) -> None:
        """デフォルトフラグ付きで保存できること。"""
        template_id = repo.save(
            name="デフォルト",
            system_prompt="テスト",
            is_default=True,
        )
        record = repo.find_by_id(template_id)
        assert record is not None
        assert record.is_default == 1

    def test_save_duplicate_name_raises_error(self, repo: PromptTemplateRepository) -> None:
        """同名テンプレートの保存でDatabaseErrorが発生すること。"""
        repo.save(name="重複テスト", system_prompt="1")
        with pytest.raises(DatabaseError, match="既に使用されています"):
            repo.save(name="重複テスト", system_prompt="2")

    def test_save_default_clears_previous_default(
        self, repo: PromptTemplateRepository
    ) -> None:
        """新しいデフォルト設定時に既存のデフォルトが解除されること。"""
        id1 = repo.save(name="テンプレ1", system_prompt="1", is_default=True)
        id2 = repo.save(name="テンプレ2", system_prompt="2", is_default=True)

        rec1 = repo.find_by_id(id1)
        rec2 = repo.find_by_id(id2)
        assert rec1 is not None and rec1.is_default == 0
        assert rec2 is not None and rec2.is_default == 1


class TestFindAll:
    """find_all メソッドのテスト。"""

    def test_empty_returns_empty_list(self, repo: PromptTemplateRepository) -> None:
        """テンプレートなしの場合は空リストが返ること。"""
        assert repo.find_all() == []

    def test_returns_all_templates_default_first(
        self, repo: PromptTemplateRepository
    ) -> None:
        """全テンプレートがデフォルト優先で返ること。"""
        repo.save(name="B通常", system_prompt="b")
        repo.save(name="Aデフォルト", system_prompt="a", is_default=True)

        results = repo.find_all()
        assert len(results) == 2
        assert results[0].name == "Aデフォルト"


class TestFindDefault:
    """find_default メソッドのテスト。"""

    def test_no_default_returns_none(self, repo: PromptTemplateRepository) -> None:
        """デフォルト未設定の場合はNoneが返ること。"""
        repo.save(name="通常", system_prompt="test")
        assert repo.find_default() is None

    def test_returns_default_template(self, repo: PromptTemplateRepository) -> None:
        """デフォルトテンプレートが返ること。"""
        repo.save(name="デフォルト", system_prompt="default", is_default=True)
        result = repo.find_default()
        assert result is not None
        assert result.name == "デフォルト"


class TestUpdate:
    """update メソッドのテスト。"""

    def test_update_name(self, repo: PromptTemplateRepository) -> None:
        """名前の更新が成功すること。"""
        template_id = repo.save(name="旧名", system_prompt="test")
        assert repo.update(template_id, name="新名")

        record = repo.find_by_id(template_id)
        assert record is not None
        assert record.name == "新名"

    def test_update_system_prompt(self, repo: PromptTemplateRepository) -> None:
        """システムプロンプトの更新が成功すること。"""
        template_id = repo.save(name="テスト", system_prompt="旧プロンプト")
        repo.update(template_id, system_prompt="新プロンプト")

        record = repo.find_by_id(template_id)
        assert record is not None
        assert record.system_prompt == "新プロンプト"

    def test_update_nonexistent_returns_false(self, repo: PromptTemplateRepository) -> None:
        """存在しないIDの更新でFalseが返ること。"""
        assert not repo.update("nonexistent-id", name="test")


class TestSetDefault:
    """set_default メソッドのテスト。"""

    def test_set_default(self, repo: PromptTemplateRepository) -> None:
        """デフォルト設定が成功すること。"""
        id1 = repo.save(name="テンプレ1", system_prompt="1")
        assert repo.set_default(id1)

        record = repo.find_by_id(id1)
        assert record is not None
        assert record.is_default == 1


class TestDelete:
    """delete メソッドのテスト。"""

    def test_delete_existing(self, repo: PromptTemplateRepository) -> None:
        """既存テンプレートの削除が成功すること。"""
        template_id = repo.save(name="削除対象", system_prompt="test")
        assert repo.delete(template_id)
        assert repo.find_by_id(template_id) is None

    def test_delete_nonexistent_returns_false(self, repo: PromptTemplateRepository) -> None:
        """存在しないIDの削除でFalseが返ること。"""
        assert not repo.delete("nonexistent-id")


class TestCount:
    """count メソッドのテスト。"""

    def test_count_empty(self, repo: PromptTemplateRepository) -> None:
        """空の場合は0が返ること。"""
        assert repo.count() == 0

    def test_count_after_save(self, repo: PromptTemplateRepository) -> None:
        """保存後にカウントが増えること。"""
        repo.save(name="1", system_prompt="a")
        repo.save(name="2", system_prompt="b")
        assert repo.count() == 2
