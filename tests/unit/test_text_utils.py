"""text_utils モジュールのユニットテスト。"""

from utils.text_utils import strip_mentor_section


class TestStripMentorSection:
    """strip_mentor_section のテスト。"""

    def test_strip_mentor_section_removes_section5(self) -> None:
        """セクション5が除去されること。"""
        ai_text = (
            "## 1. 総合評価\nテキスト1\n\n"
            "## 2. 強みと課題\nテキスト2\n\n"
            "## 5. メンター向けガイド\nメンター向けテキスト\n\n"
        )
        result = strip_mentor_section(ai_text)
        assert "## 5." not in result
        assert "メンター向けテキスト" not in result

    def test_strip_mentor_section_preserves_other_sections(self) -> None:
        """他セクションに影響がないこと。"""
        ai_text = (
            "## 1. 総合評価\nテキスト1\n\n"
            "## 2. 強みと課題\nテキスト2\n\n"
            "## 5. メンター向けガイド\nメンター向けテキスト\n"
        )
        result = strip_mentor_section(ai_text)
        assert "## 1. 総合評価" in result
        assert "テキスト1" in result
        assert "## 2. 強みと課題" in result
        assert "テキスト2" in result

    def test_strip_mentor_section_with_no_section5_returns_unchanged(self) -> None:
        """セクション5がない場合にテキストが変わらないこと。"""
        ai_text = "## 1. 総合評価\nテキスト1\n\n## 2. 強みと課題\nテキスト2"
        result = strip_mentor_section(ai_text)
        assert result == ai_text.rstrip()

    def test_strip_mentor_section_with_section5_followed_by_section6(self) -> None:
        """セクション5の後に別セクションがある場合、セクション5のみ除去されること。"""
        ai_text = (
            "## 4. アドバイス\nテキスト4\n\n"
            "## 5. メンター向けガイド\nメンター向けテキスト\n\n"
            "## 6. まとめ\nまとめテキスト\n"
        )
        result = strip_mentor_section(ai_text)
        assert "## 5." not in result
        assert "## 4. アドバイス" in result
        assert "## 6. まとめ" in result
        assert "まとめテキスト" in result

    def test_strip_mentor_section_with_trailing_newlines(self) -> None:
        """末尾の改行が適切に処理されること。"""
        ai_text = "## 1. テスト\nテキスト\n\n## 5. メンター\nガイド\n\n\n"
        result = strip_mentor_section(ai_text)
        assert not result.endswith("\n\n\n")

    def test_strip_mentor_section_empty_text(self) -> None:
        """空文字列で空文字列が返ること。"""
        assert strip_mentor_section("") == ""

    def test_strip_mentor_section_only_section5(self) -> None:
        """セクション5のみのテキストで空に近い結果が返ること。"""
        ai_text = "## 5. メンター向け\nテキスト"
        result = strip_mentor_section(ai_text)
        assert "## 5." not in result
