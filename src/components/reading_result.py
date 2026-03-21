"""鑑定結果表示コンポーネント。"""

import logging
from datetime import datetime

import pandas as pd
import streamlit as st

from components.natal_chart_display import render_natal_chart
from components.pdf_export import build_reading_report_pdf
from fortune_engine.formatter import (
    DisplayData,
    format_for_ai_prompt,
    format_for_display,
    format_human_star_chart_grid,
)
from fortune_engine.models import FortuneResult, SanmeiData
from utils.exceptions import PDFExportError
from utils.text_utils import strip_mentor_section

logger = logging.getLogger(__name__)


def render_reading_result(
    result: FortuneResult,
    ai_text: str | None = None,
    listening_hints: str | None = None,
    client_name: str | None = None,
) -> None:
    """鑑定結果をタブ構成で統合表示する。

    命式表、人体星図、AI鑑定テキスト、傾聴ヒントを
    タブで切り替えて見られるように表示する。

    Args:
        result: 命式算出の最終結果。
        ai_text: AI鑑定テキスト。未生成の場合はNone。
        listening_hints: 傾聴ヒントテキスト。未生成の場合はNone。
        client_name: 相談者名。MDエクスポートのファイル名に使用。
    """
    display_data = format_for_display(result)
    sd = result.sanmei_data

    st.header("鑑定結果")

    # --- タブの構成 ---
    tab_titles = ["命式・五行", "人体星図"]
    if ai_text:
        tab_titles.append("AI鑑定レポート")
    if listening_hints:
        tab_titles.append("傾聴ヒント")

    tabs = st.tabs(tab_titles)
    tab_index = 0

    # ===== Tab 1: 命式・五行 =====
    with tabs[tab_index]:
        render_natal_chart(result)
    tab_index += 1

    # ===== Tab 2: 人体星図 =====
    with tabs[tab_index]:
        _render_human_star_chart(sd, display_data)
    tab_index += 1

    # ===== Tab 3: AI鑑定レポート（存在時） =====
    if ai_text:
        with tabs[tab_index]:
            _render_ai_reading(ai_text)
        tab_index += 1

    # ===== Tab 4: 傾聴ヒント（存在時） =====
    if listening_hints:
        with tabs[tab_index]:
            _render_listening_hints(listening_hints)

    # ===== エクスポートボタン =====
    if ai_text:
        today = datetime.now().strftime("%Y%m%d")
        name_part = client_name or "unknown"

        export_mode = st.radio(
            "エクスポート形式",
            options=["相談者向け（メンター情報を除外）", "メンター用（全情報）"],
            horizontal=True,
            help="相談者向けでは傾聴ヒントやメンター向けガイドを除外します。",
        )
        include_mentor = export_mode == "メンター用（全情報）"

        md_content = build_reading_report_markdown(
            result=result,
            ai_text=ai_text,
            listening_hints=listening_hints if include_mentor else None,
            client_name=client_name,
            include_mentor_content=include_mentor,
        )

        col_md, col_pdf = st.columns(2)
        with col_md:
            st.download_button(
                label="Markdownで保存",
                data=md_content,
                file_name=f"鑑定レポート_{name_part}_{today}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_pdf:
            try:
                pdf_data = build_reading_report_pdf(
                    result=result,
                    ai_text=ai_text,
                    listening_hints=listening_hints if include_mentor else None,
                    client_name=client_name,
                    include_mentor_content=include_mentor,
                )
                st.download_button(
                    label="PDFで保存",
                    data=pdf_data,
                    file_name=f"鑑定レポート_{name_part}_{today}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except PDFExportError:
                logger.exception("PDF生成に失敗しました")
                st.error("PDF生成に失敗しました。Markdownでの保存をお試しください。")


def _render_human_star_chart(
    sd: SanmeiData,
    display_data: DisplayData,
) -> None:
    """人体星図セクションを表示する。

    Args:
        sd: 算命学データ。
        display_data: UI表示用の命式データ辞書。
    """
    col_grid, col_info = st.columns([3, 2])

    with col_grid:
        st.subheader("人体星図")
        grid_text = format_human_star_chart_grid(sd.human_star_chart)
        st.code(grid_text, language=None)

    with col_info:
        st.subheader("天中殺・エネルギー")
        metric_col1, metric_col2 = st.columns(2)
        metric_col1.metric("天中殺", display_data["tenchusatsu"])
        metric_col2.metric("エネルギー合計", display_data["total_energy"])

    # 人体星図詳細テーブル
    st.markdown("#### 配置詳細")
    chart_data = display_data["human_star_chart"]
    df_chart = pd.DataFrame({"位置": list(chart_data.keys()), "星": list(chart_data.values())})
    st.dataframe(df_chart, use_container_width=True, hide_index=True)


def _render_ai_reading(ai_text: str) -> None:
    """AI鑑定レポートを構造化表示する。

    Args:
        ai_text: AI生成の鑑定テキスト。
    """
    st.subheader("AI鑑定レポート")
    st.markdown(ai_text)


def _render_listening_hints(hints_text: str) -> None:
    """傾聴ヒントを表示する。

    Args:
        hints_text: 傾聴ヒントテキスト。
    """
    st.subheader("傾聴のヒント（メンター向け）")
    st.info("以下はメンタリングセッションで活用するための傾聴ガイドです。")
    st.markdown(hints_text)


def build_reading_report_markdown(
    result: FortuneResult,
    ai_text: str,
    listening_hints: str | None = None,
    client_name: str | None = None,
    *,
    include_mentor_content: bool = True,
) -> str:
    """鑑定結果を統合したMarkdownテキストを生成する。

    命式情報・AI鑑定テキスト・傾聴ヒントを1つのMarkdownドキュメントに
    まとめて返す。ファイル保存やエクスポート用途。

    Args:
        result: 命式算出の最終結果。
        ai_text: AI鑑定テキスト。
        listening_hints: 傾聴ヒントテキスト。
        client_name: 相談者名（ヘッダーに表示）。
        include_mentor_content: メンター向けコンテンツを含めるか。
            Falseの場合、AI鑑定テキスト内のセクション5と傾聴ヒントを除外する。

    Returns:
        Markdown形式の鑑定レポート文字列。
    """
    today = datetime.now().strftime("%Y-%m-%d")
    name_display = client_name or "（名前未設定）"

    export_ai_text = ai_text if include_mentor_content else strip_mentor_section(ai_text)

    sections = [
        f"# 鑑定レポート: {name_display}",
        f"- 鑑定日: {today}",
        "",
        "---",
        "",
        "## 命式データ",
        "",
        "```",
        format_for_ai_prompt(result),
        "```",
        "",
        "---",
        "",
        "## AI鑑定レポート",
        "",
        export_ai_text,
    ]

    if listening_hints and include_mentor_content:
        sections.extend(
            [
                "",
                "---",
                "",
                "## 傾聴のヒント（メンター向け）",
                "",
                listening_hints,
            ]
        )

    sections.extend(["", "---", f"*Generated by Sityuu-Auto on {today}*", ""])

    return "\n".join(sections)
