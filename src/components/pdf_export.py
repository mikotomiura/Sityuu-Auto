"""PDF エクスポートコンポーネント。

reportlab を使用して鑑定レポートを PDF 形式で出力する。
CIDフォント（HeiseiKakuGo-W5 / HeiseiMin-W3）で日本語に対応。
"""

import io
import logging
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from fortune_engine.formatter import format_for_ai_prompt
from fortune_engine.models import FortuneResult
from utils.exceptions import PDFExportError

logger = logging.getLogger(__name__)

# --- CIDフォント定数 ---
_FONT_GOTHIC = "HeiseiKakuGo-W5"
_FONT_MINCHO = "HeiseiMin-W3"

_fonts_registered = False


def _ensure_fonts_registered() -> None:
    """CIDフォントを遅延登録する。

    初回呼び出し時のみフォント登録を行い、以降はスキップする。
    """
    global _fonts_registered  # noqa: PLW0603
    if _fonts_registered:
        return

    pdfmetrics.registerFont(UnicodeCIDFont(_FONT_GOTHIC))
    pdfmetrics.registerFont(UnicodeCIDFont(_FONT_MINCHO))
    _fonts_registered = True


def _create_styles() -> dict[str, ParagraphStyle]:
    """PDF用のスタイル定義を生成する。

    Returns:
        スタイル名をキーとする ParagraphStyle 辞書。
    """
    base = getSampleStyleSheet()

    styles: dict[str, ParagraphStyle] = {}

    styles["title"] = ParagraphStyle(
        "JaTitle",
        parent=base["Title"],
        fontName=_FONT_GOTHIC,
        fontSize=18,
        leading=24,
        spaceAfter=6 * mm,
    )
    styles["heading"] = ParagraphStyle(
        "JaHeading",
        parent=base["Heading2"],
        fontName=_FONT_GOTHIC,
        fontSize=14,
        leading=18,
        spaceBefore=6 * mm,
        spaceAfter=3 * mm,
    )
    styles["body"] = ParagraphStyle(
        "JaBody",
        parent=base["Normal"],
        fontName=_FONT_MINCHO,
        fontSize=10,
        leading=16,
        spaceAfter=2 * mm,
    )
    styles["caption"] = ParagraphStyle(
        "JaCaption",
        parent=base["Normal"],
        fontName=_FONT_MINCHO,
        fontSize=8,
        leading=12,
        textColor="grey",
    )
    styles["code"] = ParagraphStyle(
        "JaCode",
        parent=base["Code"],
        fontName=_FONT_GOTHIC,
        fontSize=8,
        leading=12,
        spaceAfter=2 * mm,
        leftIndent=10,
    )

    return styles


def _markdown_to_paragraphs(
    text: str,
    styles: dict[str, ParagraphStyle],
) -> list[Paragraph | Spacer]:
    """Markdownライクなテキストをreportlab要素のリストに変換する。

    簡易的な変換で、見出し（## / ###）と本文を区別する。
    複雑なMarkdown構文には対応しない。

    Args:
        text: 変換するテキスト。
        styles: スタイル辞書。

    Returns:
        reportlab 描画要素のリスト。
    """
    elements: list[Paragraph | Spacer] = []

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            elements.append(Spacer(1, 2 * mm))
            continue

        # --- 見出しの判定 ---
        if stripped.startswith("### "):
            heading_text = stripped[4:]
            elements.append(Paragraph(_escape_xml(heading_text), styles["heading"]))
        elif stripped.startswith("## "):
            heading_text = stripped[3:]
            elements.append(Paragraph(_escape_xml(heading_text), styles["heading"]))
        elif stripped.startswith("# "):
            heading_text = stripped[2:]
            elements.append(Paragraph(_escape_xml(heading_text), styles["title"]))
        elif stripped.startswith("---"):
            elements.append(Spacer(1, 4 * mm))
        elif stripped.startswith("```"):
            # コードブロックの開始/終了行はスキップ
            pass
        elif stripped.startswith("- ") or stripped.startswith("* "):
            bullet_text = stripped[2:]
            elements.append(
                Paragraph(f"・ {_escape_xml(bullet_text)}", styles["body"])
            )
        elif stripped.startswith("| "):
            # テーブル行は本文として出力
            elements.append(Paragraph(_escape_xml(stripped), styles["body"]))
        else:
            # Markdownの強調記法を除去
            cleaned = stripped.replace("**", "").replace("*", "")
            elements.append(Paragraph(_escape_xml(cleaned), styles["body"]))

    return elements


def _escape_xml(text: str) -> str:
    """XML特殊文字をエスケープする。

    reportlab の Paragraph は XML ベースのためエスケープが必要。

    Args:
        text: エスケープする文字列。

    Returns:
        エスケープ済みの文字列。
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_reading_report_pdf(
    result: FortuneResult,
    ai_text: str,
    listening_hints: str | None = None,
    client_name: str | None = None,
    *,
    include_mentor_content: bool = True,
) -> bytes:
    """鑑定結果をPDFバイナリとして生成する。

    Args:
        result: 命式算出の最終結果。
        ai_text: AI鑑定テキスト。
        listening_hints: 傾聴ヒントテキスト。
        client_name: 相談者名（タイトル・ファイル名に使用）。
        include_mentor_content: メンター向けコンテンツを含めるか。
            Falseの場合、セクション5と傾聴ヒントを除外する。

    Returns:
        PDF ファイルのバイナリデータ。

    Raises:
        PDFExportError: PDF生成に失敗した場合。
    """
    _ensure_fonts_registered()

    try:
        buffer = io.BytesIO()
        styles = _create_styles()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            leftMargin=15 * mm,
            rightMargin=15 * mm,
        )

        elements: list[Paragraph | Spacer] = []
        today = datetime.now().strftime("%Y-%m-%d")
        name_display = client_name or "（名前未設定）"

        # --- タイトル ---
        elements.append(
            Paragraph(f"鑑定レポート: {_escape_xml(name_display)}", styles["title"])
        )
        elements.append(Paragraph(f"鑑定日: {today}", styles["caption"]))
        elements.append(Spacer(1, 6 * mm))

        # --- 命式データ ---
        elements.append(Paragraph("命式データ", styles["heading"]))
        chart_text = format_for_ai_prompt(result)
        for line in chart_text.split("\n"):
            if line.strip():
                elements.append(Paragraph(_escape_xml(line), styles["code"]))

        elements.append(Spacer(1, 4 * mm))

        # --- AI鑑定レポート ---
        elements.append(Paragraph("AI鑑定レポート", styles["heading"]))
        export_ai_text = ai_text
        if not include_mentor_content:
            from utils.text_utils import strip_mentor_section

            export_ai_text = strip_mentor_section(ai_text)
        elements.extend(_markdown_to_paragraphs(export_ai_text, styles))

        # --- 傾聴ヒント ---
        if listening_hints and include_mentor_content:
            elements.append(Spacer(1, 4 * mm))
            elements.append(Paragraph("傾聴のヒント（メンター向け）", styles["heading"]))
            elements.extend(_markdown_to_paragraphs(listening_hints, styles))

        # --- フッター ---
        elements.append(Spacer(1, 8 * mm))
        elements.append(
            Paragraph(f"Generated by Sityuu-Auto on {today}", styles["caption"])
        )

        doc.build(elements)
        return buffer.getvalue()

    except PDFExportError:
        raise
    except (IOError, ValueError, KeyError) as e:
        raise PDFExportError(f"PDF生成に失敗しました: {e}") from e


def build_fallback_pdf(
    client_name: str,
    ai_text: str,
    listening_hints: str | None = None,
) -> bytes:
    """命式データなしの簡易PDFレポートを生成する。

    鑑定履歴で命式復元に失敗した場合に使用する。

    Args:
        client_name: 相談者名。
        ai_text: AI鑑定テキスト。
        listening_hints: 傾聴ヒントテキスト。

    Returns:
        PDF ファイルのバイナリデータ。

    Raises:
        PDFExportError: PDF生成に失敗した場合。
    """
    _ensure_fonts_registered()

    try:
        buffer = io.BytesIO()
        styles = _create_styles()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            leftMargin=15 * mm,
            rightMargin=15 * mm,
        )

        elements: list[Paragraph | Spacer] = []
        today = datetime.now().strftime("%Y-%m-%d")

        elements.append(
            Paragraph(f"鑑定レポート: {_escape_xml(client_name)}", styles["title"])
        )
        elements.append(Paragraph(f"鑑定日: {today}", styles["caption"]))
        elements.append(Spacer(1, 6 * mm))

        elements.append(Paragraph("AI鑑定レポート", styles["heading"]))
        elements.extend(_markdown_to_paragraphs(ai_text, styles))

        if listening_hints:
            elements.append(Spacer(1, 4 * mm))
            elements.append(Paragraph("傾聴のヒント（メンター向け）", styles["heading"]))
            elements.extend(_markdown_to_paragraphs(listening_hints, styles))

        elements.append(Spacer(1, 8 * mm))
        elements.append(
            Paragraph(f"Generated by Sityuu-Auto on {today}", styles["caption"])
        )

        doc.build(elements)
        return buffer.getvalue()

    except PDFExportError:
        raise
    except (IOError, ValueError, KeyError) as e:
        raise PDFExportError(f"PDF生成に失敗しました: {e}") from e
