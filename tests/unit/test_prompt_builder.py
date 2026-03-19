"""プロンプトビルダーのユニットテスト。"""

from ai_service.prompt_builder import build_listening_hint_prompt, build_reading_prompt

SAMPLE_NATAL_CHART_TEXT = (
    "【四柱推命 命式】\n"
    "  日干: 庚（金）\n"
    "  年柱: 庚午\n"
    "  月柱: 辛巳\n"
    "  日柱: 庚辰\n"
    "  時柱: 辛巳\n"
    "  五行バランス: 木:0 火:0 土:0 金:4 水:0"
)

SAMPLE_CONCERN = "仕事の方向性について悩んでいます。転職すべきか現職で頑張るべきか迷っています。"


class TestBuildReadingPrompt:
    """build_reading_prompt のテスト。"""

    def test_prompt_contains_natal_chart_data(self) -> None:
        """プロンプトに命式データが含まれること。"""
        _system, user = build_reading_prompt(
            natal_chart_text=SAMPLE_NATAL_CHART_TEXT,
            concern=SAMPLE_CONCERN,
        )

        assert "庚" in user
        assert "庚午" in user
        assert "五行バランス" in user

    def test_prompt_contains_concern_text(self) -> None:
        """プロンプトに悩みテキストが含まれること。"""
        _system, user = build_reading_prompt(
            natal_chart_text=SAMPLE_NATAL_CHART_TEXT,
            concern=SAMPLE_CONCERN,
        )

        assert SAMPLE_CONCERN in user

    def test_system_prompt_contains_role_definition(self) -> None:
        """system_prompt にロール定義が含まれること。"""
        system, _user = build_reading_prompt(
            natal_chart_text=SAMPLE_NATAL_CHART_TEXT,
            concern=SAMPLE_CONCERN,
        )

        assert "カウンセラー" in system
        assert "鑑定師" in system

    def test_returns_tuple_of_two_strings(self) -> None:
        """戻り値が (str, str) のタプルであること。"""
        result = build_reading_prompt(
            natal_chart_text=SAMPLE_NATAL_CHART_TEXT,
            concern=SAMPLE_CONCERN,
        )

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], str)

    def test_user_prompt_contains_output_format(self) -> None:
        """user_prompt に出力フォーマット指定が含まれること。"""
        _system, user = build_reading_prompt(
            natal_chart_text=SAMPLE_NATAL_CHART_TEXT,
            concern=SAMPLE_CONCERN,
        )

        assert "命式から読み取れる相談者の本質" in user
        assert "具体的なアドバイス案" in user


class TestBuildListeningHintPrompt:
    """build_listening_hint_prompt のテスト。"""

    def test_prompt_contains_natal_chart_data(self) -> None:
        """プロンプトに命式データが含まれること。"""
        _system, user = build_listening_hint_prompt(
            natal_chart_text=SAMPLE_NATAL_CHART_TEXT,
            concern=SAMPLE_CONCERN,
        )

        assert "庚" in user
        assert "庚午" in user

    def test_prompt_contains_concern_text(self) -> None:
        """プロンプトに悩みテキストが含まれること。"""
        _system, user = build_listening_hint_prompt(
            natal_chart_text=SAMPLE_NATAL_CHART_TEXT,
            concern=SAMPLE_CONCERN,
        )

        assert SAMPLE_CONCERN in user

    def test_system_prompt_contains_role_definition(self) -> None:
        """system_prompt にロール定義が含まれること。"""
        system, _user = build_listening_hint_prompt(
            natal_chart_text=SAMPLE_NATAL_CHART_TEXT,
            concern=SAMPLE_CONCERN,
        )

        assert "カウンセラー" in system
        assert "メンタリング" in system

    def test_user_prompt_contains_listening_format(self) -> None:
        """user_prompt に傾聴ヒントの出力フォーマットが含まれること。"""
        _system, user = build_listening_hint_prompt(
            natal_chart_text=SAMPLE_NATAL_CHART_TEXT,
            concern=SAMPLE_CONCERN,
        )

        assert "傾聴のポイント" in user
        assert "声掛け" in user
