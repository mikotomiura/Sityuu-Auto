"""DB操作の統合テスト。

インメモリSQLiteを使用してリポジトリのCRUD操作を検証する。
"""

from __future__ import annotations

import json
from datetime import date

import pytest

from db_service.models import ClientRecord, SessionRecord
from db_service.repositories.client_repo import UNSET, ClientRepository
from db_service.repositories.session_repo import SessionRepository
from tests.integration.conftest import OTHER_USER_ID, TEST_USER_ID
from utils.exceptions import DatabaseError


@pytest.fixture()
def saved_client_id(client_repo: ClientRepository) -> str:
    """テスト用の相談者を保存し、IDを返す。"""
    return client_repo.save(
        name="山田太郎",
        birth_date=date(1990, 5, 15),
        birth_time="10:30",
        gender="男性",
        notes="テスト用",
        user_id=TEST_USER_ID,
    )


SAMPLE_NATAL_CHART_JSON = json.dumps(
    {"day_stem": "庚", "year_pillar": {"stem": "庚", "branch": "午"}},
    ensure_ascii=False,
)

SAMPLE_SANMEI_JSON = json.dumps(
    {"center_star": "貫索星", "tenchusatsu": "戌亥"},
    ensure_ascii=False,
)


# ============================================================
# ClientRepository テスト
# ============================================================


class TestClientRepositorySave:
    """ClientRepository.save のテスト。"""

    def test_save_returns_uuid(self, client_repo: ClientRepository) -> None:
        """保存時にUUID文字列が返ること。"""
        client_id = client_repo.save(
            name="佐藤花子", birth_date=date(1985, 3, 10), user_id=TEST_USER_ID
        )
        assert isinstance(client_id, str)
        assert len(client_id) == 36  # UUID format

    def test_save_with_all_fields(self, client_repo: ClientRepository) -> None:
        """全フィールド指定で保存できること。"""
        client_id = client_repo.save(
            name="田中一郎",
            birth_date=date(2000, 1, 1),
            birth_time="14:00",
            gender="男性",
            notes="メモ",
            user_id=TEST_USER_ID,
        )
        record = client_repo.find_by_id(client_id, user_id=TEST_USER_ID)
        assert record is not None
        assert record.name == "田中一郎"
        assert record.birth_date == "2000-01-01"
        assert record.birth_time == "14:00"
        assert record.gender == "男性"
        assert record.notes == "メモ"
        assert record.user_id == TEST_USER_ID

    def test_save_with_minimal_fields(self, client_repo: ClientRepository) -> None:
        """必須フィールドのみで保存できること。"""
        client_id = client_repo.save(
            name="鈴木", birth_date=date(1975, 12, 25), user_id=TEST_USER_ID
        )
        record = client_repo.find_by_id(client_id, user_id=TEST_USER_ID)
        assert record is not None
        assert record.birth_time is None
        assert record.gender is None
        assert record.notes is None


class TestClientRepositoryFindById:
    """ClientRepository.find_by_id のテスト。"""

    def test_find_by_id_returns_record(
        self, client_repo: ClientRepository, saved_client_id: str
    ) -> None:
        """存在するIDで ClientRecord が返ること。"""
        record = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert record is not None
        assert isinstance(record, ClientRecord)
        assert record.id == saved_client_id
        assert record.name == "山田太郎"

    def test_find_by_id_returns_none_for_unknown_id(self, client_repo: ClientRepository) -> None:
        """存在しないIDで None が返ること。"""
        result = client_repo.find_by_id("nonexistent-uuid", user_id=TEST_USER_ID)
        assert result is None

    def test_find_by_id_with_wrong_user_returns_none(
        self, client_repo: ClientRepository, saved_client_id: str
    ) -> None:
        """別ユーザーIDでフィルタすると None が返ること。"""
        result = client_repo.find_by_id(saved_client_id, user_id=OTHER_USER_ID)
        assert result is None

    def test_find_by_id_with_correct_user_returns_record(
        self, client_repo: ClientRepository, saved_client_id: str
    ) -> None:
        """正しいユーザーIDでフィルタするとレコードが返ること。"""
        result = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert result is not None
        assert result.id == saved_client_id


class TestClientRepositoryFindAll:
    """ClientRepository.find_all のテスト。"""

    def test_find_all_returns_empty_list(self, client_repo: ClientRepository) -> None:
        """データなしで空リストが返ること。"""
        assert client_repo.find_all(user_id=TEST_USER_ID) == []

    def test_find_all_returns_records(
        self, client_repo: ClientRepository, saved_client_id: str
    ) -> None:
        """保存済みデータがリストで返ること。"""
        records = client_repo.find_all(user_id=TEST_USER_ID)
        assert len(records) == 1
        assert records[0].id == saved_client_id

    def test_find_all_respects_limit(self, client_repo: ClientRepository) -> None:
        """limit パラメータが効くこと。"""
        for i in range(5):
            client_repo.save(
                name=f"ユーザー{i}", birth_date=date(1990, 1, 1), user_id=TEST_USER_ID
            )
        records = client_repo.find_all(user_id=TEST_USER_ID, limit=3)
        assert len(records) == 3

    def test_find_all_respects_offset(self, client_repo: ClientRepository) -> None:
        """offset パラメータが効くこと。"""
        for i in range(5):
            client_repo.save(
                name=f"ユーザー{i}", birth_date=date(1990, 1, 1), user_id=TEST_USER_ID
            )
        all_records = client_repo.find_all(user_id=TEST_USER_ID)
        offset_records = client_repo.find_all(user_id=TEST_USER_ID, offset=2)
        assert len(offset_records) == 3
        assert offset_records[0].id == all_records[2].id

    def test_find_all_isolates_by_user(self, client_repo: ClientRepository) -> None:
        """別ユーザーのデータが返らないこと。"""
        client_repo.save(name="ユーザーA", birth_date=date(1990, 1, 1), user_id=TEST_USER_ID)
        client_repo.save(name="ユーザーB", birth_date=date(1990, 1, 1), user_id=OTHER_USER_ID)
        records_a = client_repo.find_all(user_id=TEST_USER_ID)
        records_b = client_repo.find_all(user_id=OTHER_USER_ID)
        assert len(records_a) == 1
        assert records_a[0].name == "ユーザーA"
        assert len(records_b) == 1
        assert records_b[0].name == "ユーザーB"


class TestClientRepositorySearchByName:
    """ClientRepository.search_by_name のテスト。"""

    def test_search_by_name_partial_match(self, client_repo: ClientRepository) -> None:
        """部分一致で検索できること。"""
        client_repo.save(name="山田太郎", birth_date=date(1990, 1, 1), user_id=TEST_USER_ID)
        client_repo.save(name="山田花子", birth_date=date(1985, 6, 15), user_id=TEST_USER_ID)
        client_repo.save(name="佐藤次郎", birth_date=date(2000, 3, 20), user_id=TEST_USER_ID)

        results = client_repo.search_by_name("山田", user_id=TEST_USER_ID)
        assert len(results) == 2
        assert all("山田" in r.name for r in results)

    def test_search_by_name_no_match(self, client_repo: ClientRepository) -> None:
        """一致なしで空リストが返ること。"""
        client_repo.save(name="山田太郎", birth_date=date(1990, 1, 1), user_id=TEST_USER_ID)
        results = client_repo.search_by_name("田中", user_id=TEST_USER_ID)
        assert results == []

    def test_search_by_name_isolates_by_user(self, client_repo: ClientRepository) -> None:
        """別ユーザーのデータが検索に含まれないこと。"""
        client_repo.save(name="山田太郎", birth_date=date(1990, 1, 1), user_id=TEST_USER_ID)
        client_repo.save(name="山田花子", birth_date=date(1985, 6, 15), user_id=OTHER_USER_ID)
        results = client_repo.search_by_name("山田", user_id=TEST_USER_ID)
        assert len(results) == 1
        assert results[0].name == "山田太郎"


class TestClientRepositoryUpdate:
    """ClientRepository.update のテスト。"""

    def test_update_name(self, client_repo: ClientRepository, saved_client_id: str) -> None:
        """名前の更新が反映されること。"""
        result = client_repo.update(saved_client_id, name="山田次郎")
        assert result is True

        record = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert record is not None
        assert record.name == "山田次郎"

    def test_update_name_kana(self, client_repo: ClientRepository, saved_client_id: str) -> None:
        """フリガナの更新が反映されること。"""
        result = client_repo.update(saved_client_id, name_kana="ヤマダ ジロウ")
        assert result is True

        record = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert record is not None
        assert record.name_kana == "ヤマダ ジロウ"

    def test_update_name_kana_to_empty(
        self, client_repo: ClientRepository, saved_client_id: str
    ) -> None:
        """フリガナを空文字列で更新できること。"""
        client_repo.update(saved_client_id, name_kana="テスト")
        result = client_repo.update(saved_client_id, name_kana="")
        assert result is True

        record = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert record is not None
        assert record.name_kana == ""

    def test_update_notes(self, client_repo: ClientRepository, saved_client_id: str) -> None:
        """メモの更新が反映されること。"""
        result = client_repo.update(saved_client_id, notes="新しいメモ")
        assert result is True

        record = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert record is not None
        assert record.notes == "新しいメモ"

    def test_update_updates_timestamp(
        self, client_repo: ClientRepository, saved_client_id: str
    ) -> None:
        """更新時に updated_at が変わること。"""
        before = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert before is not None

        client_repo.update(saved_client_id, name="変更後")

        after = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert after is not None
        assert after.updated_at >= before.updated_at

    def test_update_returns_false_for_no_changes(
        self, client_repo: ClientRepository, saved_client_id: str
    ) -> None:
        """更新項目なしで False が返ること。"""
        result = client_repo.update(saved_client_id)
        assert result is False

    def test_update_returns_false_for_unknown_id(self, client_repo: ClientRepository) -> None:
        """存在しないIDで False が返ること。"""
        result = client_repo.update("nonexistent-uuid", name="テスト")
        assert result is False

    def test_update_birth_date(self, client_repo: ClientRepository, saved_client_id: str) -> None:
        """生年月日の更新が反映されること。"""
        new_date = date(1995, 12, 25)
        result = client_repo.update(saved_client_id, birth_date=new_date)
        assert result is True

        record = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert record is not None
        assert record.birth_date == "1995-12-25"

    def test_update_birth_time(self, client_repo: ClientRepository, saved_client_id: str) -> None:
        """出生時間の更新が反映されること。"""
        result = client_repo.update(saved_client_id, birth_time="14:30")
        assert result is True

        record = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert record is not None
        assert record.birth_time == "14:30"

    def test_update_birth_time_to_none(
        self, client_repo: ClientRepository, saved_client_id: str
    ) -> None:
        """出生時間を None に更新できること。"""
        client_repo.update(saved_client_id, birth_time="10:00")
        result = client_repo.update(saved_client_id, birth_time=None)
        assert result is True

        record = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert record is not None
        assert record.birth_time is None

    def test_update_birth_time_unset_no_change(
        self, client_repo: ClientRepository, saved_client_id: str
    ) -> None:
        """birth_time=UNSET ではカラムが変更されないこと。"""
        client_repo.update(saved_client_id, birth_time="09:00")
        # UNSET + name 変更のみ → birth_time は変わらない
        client_repo.update(saved_client_id, name="別名", birth_time=UNSET)

        record = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert record is not None
        assert record.birth_time == "09:00"

    def test_update_gender(self, client_repo: ClientRepository, saved_client_id: str) -> None:
        """性別の更新が反映されること。"""
        result = client_repo.update(saved_client_id, gender="女性")
        assert result is True

        record = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert record is not None
        assert record.gender == "女性"

    def test_update_gender_to_none(
        self, client_repo: ClientRepository, saved_client_id: str
    ) -> None:
        """性別を None に更新できること。"""
        client_repo.update(saved_client_id, gender="男性")
        result = client_repo.update(saved_client_id, gender=None)
        assert result is True

        record = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert record is not None
        assert record.gender is None

    def test_update_gender_unset_no_change(
        self, client_repo: ClientRepository, saved_client_id: str
    ) -> None:
        """gender=UNSET ではカラムが変更されないこと。"""
        client_repo.update(saved_client_id, gender="女性")
        client_repo.update(saved_client_id, name="別名2", gender=UNSET)

        record = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert record is not None
        assert record.gender == "女性"

    def test_update_with_user_id_filter(
        self, client_repo: ClientRepository, saved_client_id: str
    ) -> None:
        """user_id フィルタ付きの更新が正しく動作すること。"""
        # 正しいユーザーで更新
        result = client_repo.update(
            saved_client_id, name="正しいユーザー", user_id=TEST_USER_ID
        )
        assert result is True

        # 別ユーザーでは更新できない
        result = client_repo.update(
            saved_client_id, name="不正ユーザー", user_id=OTHER_USER_ID
        )
        assert result is False

        record = client_repo.find_by_id(saved_client_id, user_id=TEST_USER_ID)
        assert record is not None
        assert record.name == "正しいユーザー"


# ============================================================
# SessionRepository テスト
# ============================================================


class TestSessionRepositorySave:
    """SessionRepository.save のテスト。"""

    def test_save_returns_uuid(
        self,
        session_repo: SessionRepository,
        saved_client_id: str,
    ) -> None:
        """保存時にUUID文字列が返ること。"""
        session_id = session_repo.save(
            client_id=saved_client_id,
            concern="仕事の悩み",
            natal_chart_json=SAMPLE_NATAL_CHART_JSON,
            user_id=TEST_USER_ID,
        )
        assert isinstance(session_id, str)
        assert len(session_id) == 36

    def test_save_with_all_fields(
        self,
        session_repo: SessionRepository,
        saved_client_id: str,
    ) -> None:
        """全フィールド指定で保存できること。"""
        session_id = session_repo.save(
            client_id=saved_client_id,
            concern="人間関係の悩み",
            natal_chart_json=SAMPLE_NATAL_CHART_JSON,
            sanmei_data_json=SAMPLE_SANMEI_JSON,
            ai_reading_text="AI鑑定結果テキスト",
            ai_listening_hints="傾聴ヒント",
            mentor_notes="出品者メモ",
            api_provider="anthropic",
            api_model="claude-3-5-sonnet",
            user_id=TEST_USER_ID,
        )
        record = session_repo.find_by_id(session_id, user_id=TEST_USER_ID)
        assert record is not None
        assert record.client_id == saved_client_id
        assert record.concern == "人間関係の悩み"
        assert json.loads(record.natal_chart_json)["day_stem"] == "庚"
        assert record.sanmei_data_json is not None
        assert json.loads(record.sanmei_data_json)["center_star"] == "貫索星"
        assert record.ai_reading_text == "AI鑑定結果テキスト"
        assert record.ai_listening_hints == "傾聴ヒント"
        assert record.mentor_notes == "出品者メモ"
        assert record.api_provider == "anthropic"
        assert record.api_model == "claude-3-5-sonnet"
        assert record.user_id == TEST_USER_ID

    def test_save_fails_with_invalid_client_id(
        self,
        session_repo: SessionRepository,
    ) -> None:
        """存在しない client_id で DatabaseError が発生すること。"""
        with pytest.raises(DatabaseError):
            session_repo.save(
                client_id="nonexistent-client-id",
                concern="テスト",
                natal_chart_json=SAMPLE_NATAL_CHART_JSON,
                user_id=TEST_USER_ID,
            )


class TestSessionRepositoryFindById:
    """SessionRepository.find_by_id のテスト。"""

    def test_find_by_id_returns_record(
        self,
        session_repo: SessionRepository,
        saved_client_id: str,
    ) -> None:
        """存在するIDで SessionRecord が返ること。"""
        session_id = session_repo.save(
            client_id=saved_client_id,
            concern="テスト",
            natal_chart_json=SAMPLE_NATAL_CHART_JSON,
            user_id=TEST_USER_ID,
        )
        record = session_repo.find_by_id(session_id, user_id=TEST_USER_ID)
        assert record is not None
        assert isinstance(record, SessionRecord)
        assert record.id == session_id

    def test_find_by_id_returns_none_for_unknown_id(self, session_repo: SessionRepository) -> None:
        """存在しないIDで None が返ること。"""
        assert session_repo.find_by_id("nonexistent-uuid", user_id=TEST_USER_ID) is None

    def test_find_by_id_with_wrong_user_returns_none(
        self,
        session_repo: SessionRepository,
        saved_client_id: str,
    ) -> None:
        """別ユーザーIDでフィルタすると None が返ること。"""
        session_id = session_repo.save(
            client_id=saved_client_id,
            concern="テスト",
            natal_chart_json=SAMPLE_NATAL_CHART_JSON,
            user_id=TEST_USER_ID,
        )
        result = session_repo.find_by_id(session_id, user_id=OTHER_USER_ID)
        assert result is None


class TestSessionRepositoryFindByClientId:
    """SessionRepository.find_by_client_id のテスト。"""

    def test_find_by_client_id_returns_sessions(
        self,
        session_repo: SessionRepository,
        saved_client_id: str,
    ) -> None:
        """相談者IDに紐づくセッションが返ること。"""
        session_repo.save(
            client_id=saved_client_id,
            concern="悩み1",
            natal_chart_json=SAMPLE_NATAL_CHART_JSON,
            user_id=TEST_USER_ID,
        )
        session_repo.save(
            client_id=saved_client_id,
            concern="悩み2",
            natal_chart_json=SAMPLE_NATAL_CHART_JSON,
            user_id=TEST_USER_ID,
        )
        records = session_repo.find_by_client_id(saved_client_id, user_id=TEST_USER_ID)
        assert len(records) == 2
        assert all(r.client_id == saved_client_id for r in records)

    def test_find_by_client_id_returns_empty_for_no_sessions(
        self,
        session_repo: SessionRepository,
        saved_client_id: str,
    ) -> None:
        """セッションなしの相談者IDで空リストが返ること。"""
        assert session_repo.find_by_client_id(saved_client_id, user_id=TEST_USER_ID) == []

    def test_find_by_client_id_respects_limit(
        self,
        session_repo: SessionRepository,
        saved_client_id: str,
    ) -> None:
        """limit パラメータが効くこと。"""
        for i in range(5):
            session_repo.save(
                client_id=saved_client_id,
                concern=f"悩み{i}",
                natal_chart_json=SAMPLE_NATAL_CHART_JSON,
                user_id=TEST_USER_ID,
            )
        records = session_repo.find_by_client_id(saved_client_id, user_id=TEST_USER_ID, limit=2)
        assert len(records) == 2


class TestSessionRepositoryFindAll:
    """SessionRepository.find_all のテスト。"""

    def test_find_all_returns_empty_list(self, session_repo: SessionRepository) -> None:
        """データなしで空リストが返ること。"""
        assert session_repo.find_all(user_id=TEST_USER_ID) == []

    def test_find_all_returns_all_sessions(
        self,
        session_repo: SessionRepository,
        saved_client_id: str,
    ) -> None:
        """全セッションがリストで返ること。"""
        session_repo.save(
            client_id=saved_client_id,
            concern="悩み1",
            natal_chart_json=SAMPLE_NATAL_CHART_JSON,
            user_id=TEST_USER_ID,
        )
        session_repo.save(
            client_id=saved_client_id,
            concern="悩み2",
            natal_chart_json=SAMPLE_NATAL_CHART_JSON,
            user_id=TEST_USER_ID,
        )
        records = session_repo.find_all(user_id=TEST_USER_ID)
        assert len(records) == 2

    def test_find_all_isolates_by_user(
        self,
        session_repo: SessionRepository,
        saved_client_id: str,
    ) -> None:
        """別ユーザーのセッションが返らないこと。"""
        session_repo.save(
            client_id=saved_client_id,
            concern="ユーザーAの悩み",
            natal_chart_json=SAMPLE_NATAL_CHART_JSON,
            user_id=TEST_USER_ID,
        )
        session_repo.save(
            client_id=saved_client_id,
            concern="ユーザーBの悩み",
            natal_chart_json=SAMPLE_NATAL_CHART_JSON,
            user_id=OTHER_USER_ID,
        )
        records_a = session_repo.find_all(user_id=TEST_USER_ID)
        records_b = session_repo.find_all(user_id=OTHER_USER_ID)
        assert len(records_a) == 1
        assert records_a[0].concern == "ユーザーAの悩み"
        assert len(records_b) == 1
        assert records_b[0].concern == "ユーザーBの悩み"
