"""PDFエクスポートのユニットテスト。"""

import pytest

from components.pdf_export import build_fallback_pdf, build_reading_report_pdf
from fortune_engine.models import FortuneResult


class TestBuildReadingReportPdf:
    """build_reading_report_pdf のテスト。"""

    def test_returns_bytes(self, sample_fortune_result: FortuneResult) -> None:
        """PDF バイナリが返ること。"""
        pdf_data = build_reading_report_pdf(
            result=sample_fortune_result,
            ai_text="テスト鑑定テキスト",
            client_name="テスト太郎",
        )
        assert isinstance(pdf_data, bytes)
        assert len(pdf_data) > 0

    def test_pdf_starts_with_header(self, sample_fortune_result: FortuneResult) -> None:
        """PDF ヘッダー（%PDF）で始まること。"""
        pdf_data = build_reading_report_pdf(
            result=sample_fortune_result,
            ai_text="テスト鑑定テキスト",
        )
        assert pdf_data[:5] == b"%PDF-"

    def test_with_listening_hints(self, sample_fortune_result: FortuneResult) -> None:
        """傾聴ヒント付きでも正常に生成されること。"""
        pdf_data = build_reading_report_pdf(
            result=sample_fortune_result,
            ai_text="鑑定テキスト",
            listening_hints="傾聴ヒントテキスト",
            client_name="テスト花子",
        )
        assert pdf_data[:5] == b"%PDF-"

    def test_with_markdown_content(self, sample_fortune_result: FortuneResult) -> None:
        """Markdown記法を含むAIテキストで正常に生成されること。"""
        ai_text = (
            "## 1. 命式の総合評価\n\n"
            "- **日干の特徴**: 庚は陽の金です\n"
            "- 五行バランスが偏っています\n\n"
            "### 強み\n"
            "| 項目 | 分析 |\n"
            "|------|------|\n"
            "| 最大の強み | リーダーシップ |\n"
        )
        pdf_data = build_reading_report_pdf(
            result=sample_fortune_result,
            ai_text=ai_text,
        )
        assert pdf_data[:5] == b"%PDF-"

    def test_with_xml_special_chars(self, sample_fortune_result: FortuneResult) -> None:
        """XML特殊文字（<>&）を含むテキストで正常に生成されること。"""
        pdf_data = build_reading_report_pdf(
            result=sample_fortune_result,
            ai_text="テスト: A < B & C > D",
        )
        assert pdf_data[:5] == b"%PDF-"


class TestBuildFallbackPdf:
    """build_fallback_pdf のテスト。"""

    def test_returns_valid_pdf(self) -> None:
        """有効なPDFバイナリが返ること。"""
        pdf_data = build_fallback_pdf(
            client_name="テスト太郎",
            ai_text="テスト鑑定テキスト",
        )
        assert isinstance(pdf_data, bytes)
        assert pdf_data[:5] == b"%PDF-"

    def test_with_listening_hints(self) -> None:
        """傾聴ヒント付きでも正常に生成されること。"""
        pdf_data = build_fallback_pdf(
            client_name="テスト花子",
            ai_text="鑑定テキスト",
            listening_hints="傾聴ヒントテキスト",
        )
        assert pdf_data[:5] == b"%PDF-"
