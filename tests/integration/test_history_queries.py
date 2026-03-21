"""鑑定履歴クエリの統合テスト。

インメモリSQLiteを使用して、履歴ページ向けのJOINクエリを検証する。
"""

from __future__ import annotations

import json
from datetime import date

import pytest

from db_service.repositories.client_repo import ClientRepository
from db_service.repositories.session_repo import (
    SessionRepository,
    SessionWithClientName,
)

SAMPLE_NATAL_CHART_JSON = json.dumps(
    {"day_stem": "庚", "year_pillar": {"stem": "庚", "branch": "午"}},
    ensure_ascii=False,
)


@pytest.fixture()
def populated_data(
    client_repo: ClientRepository,
    session_repo: SessionRepository,
) -> dict[str, str]:
    """テスト用に相談者2名とセッション3件を作成する。"""
    client_a = client_repo.save(
        name="山田太郎",
        birth_date=date(1990, 5, 15),
        birth_time="10:30",
        gender="男性",
    )
    client_b = client_repo.save(
        name="佐藤花子",
        birth_date=date(1985, 3, 10),
        gender="女性",
    )

    session_1 = session_repo.save(
        client_id=client_a,
        concern="仕事の悩み",
        natal_chart_json=SAMPLE_NATAL_CHART_JSON,
        ai_reading_text="AIレポート1",
        ai_listening_hints="傾聴ヒント1",
    )
    session_2 = session_repo.save(
        client_id=client_a,
        concern="人間関係の悩み",
        natal_chart_json=SAMPLE_NATAL_CHART_JSON,
        ai_reading_text="AIレポート2",
    )
    session_3 = session_repo.save(
        client_id=client_b,
        concern="将来の不安",
        natal_chart_json=SAMPLE_NATAL_CHART_JSON,
    )

    return {
        "client_a": client_a,
        "client_b": client_b,
        "session_1": session_1,
        "session_2": session_2,
        "session_3": session_3,
    }


class TestFindAllWithClientName:
    """SessionRepository.find_all_with_client_name のテスト。"""

    def test_returns_all_sessions_with_names(
        self,
        session_repo: SessionRepository,
        populated_data: dict[str, str],
    ) -> None:
        """全セッションが相談者名付きで返ること。"""
        results = session_repo.find_all_with_client_name()
        assert len(results) == 3
        assert all(isinstance(r, SessionWithClientName) for r in results)

    def test_client_names_are_correct(
        self,
        session_repo: SessionRepository,
        populated_data: dict[str, str],
    ) -> None:
        """相談者名が正しく紐付いていること。"""
        results = session_repo.find_all_with_client_name()
        names = {r.client_name for r in results}
        assert names == {"山田太郎", "佐藤花子"}

    def test_ordered_by_created_at_desc(
        self,
        session_repo: SessionRepository,
        populated_data: dict[str, str],
    ) -> None:
        """作成日時の降順でソートされていること。"""
        results = session_repo.find_all_with_client_name()
        dates = [r.session.created_at for r in results]
        assert dates == sorted(dates, reverse=True)

    def test_limit_restricts_count(
        self,
        session_repo: SessionRepository,
        populated_data: dict[str, str],
    ) -> None:
        """limit指定で取得件数が制限されること。"""
        results = session_repo.find_all_with_client_name(limit=2)
        assert len(results) == 2

    def test_offset_skips_records(
        self,
        session_repo: SessionRepository,
        populated_data: dict[str, str],
    ) -> None:
        """offset指定でレコードがスキップされること。"""
        all_results = session_repo.find_all_with_client_name()
        offset_results = session_repo.find_all_with_client_name(offset=1)
        assert len(offset_results) == len(all_results) - 1

    def test_empty_database_returns_empty_list(
        self,
        session_repo: SessionRepository,
    ) -> None:
        """データが空の場合は空リストが返ること。"""
        results = session_repo.find_all_with_client_name()
        assert results == []


class TestSearchByClientName:
    """SessionRepository.search_by_client_name のテスト。"""

    def test_finds_sessions_by_partial_name(
        self,
        session_repo: SessionRepository,
        populated_data: dict[str, str],
    ) -> None:
        """名前の部分一致でセッションが検索できること。"""
        results = session_repo.search_by_client_name("山田")
        assert len(results) == 2
        assert all(r.client_name == "山田太郎" for r in results)

    def test_finds_sessions_by_full_name(
        self,
        session_repo: SessionRepository,
        populated_data: dict[str, str],
    ) -> None:
        """名前の完全一致でもセッションが検索できること。"""
        results = session_repo.search_by_client_name("佐藤花子")
        assert len(results) == 1
        assert results[0].client_name == "佐藤花子"

    def test_no_match_returns_empty_list(
        self,
        session_repo: SessionRepository,
        populated_data: dict[str, str],
    ) -> None:
        """一致なしの場合は空リストが返ること。"""
        results = session_repo.search_by_client_name("田中")
        assert results == []

    def test_session_data_is_complete(
        self,
        session_repo: SessionRepository,
        populated_data: dict[str, str],
    ) -> None:
        """検索結果のセッションデータが完全であること。"""
        results = session_repo.search_by_client_name("山田")
        session = results[0].session
        assert session.natal_chart_json == SAMPLE_NATAL_CHART_JSON
        assert session.client_id == populated_data["client_a"]

    def test_partial_name_matches_multiple_sessions(
        self,
        session_repo: SessionRepository,
        populated_data: dict[str, str],
    ) -> None:
        """名前の一部で複数セッションがヒットすること。"""
        results = session_repo.search_by_client_name("太郎")
        assert len(results) == 2

    def test_limit_works_with_search(
        self,
        session_repo: SessionRepository,
        populated_data: dict[str, str],
    ) -> None:
        """検索結果にもlimitが適用されること。"""
        results = session_repo.search_by_client_name("山田", limit=1)
        assert len(results) == 1
