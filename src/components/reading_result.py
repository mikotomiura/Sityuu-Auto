"""鑑定結果表示コンポーネント。"""

import pandas as pd
import streamlit as st

from components.natal_chart_display import render_natal_chart
from fortune_engine.formatter import format_for_display, format_human_star_chart_grid
from fortune_engine.models import FortuneResult


def render_reading_result(
    result: FortuneResult,
    ai_text: str | None = None,
    listening_hints: str | None = None,
) -> None:
    """鑑定結果をタブ構成で統合表示する。

    命式表、人体星図、AI鑑定テキスト、傾聴ヒントを
    タブで切り替えて見られるように表示する。

    Args:
        result: 命式算出の最終結果。
        ai_text: AI鑑定テキスト。未生成の場合はNone。
        listening_hints: 傾聴ヒントテキスト。未生成の場合はNone。
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


def _render_human_star_chart(
    sd: "FortuneResult.sanmei_data.__class__",  # type: ignore[name-defined]
    display_data: dict,
) -> None:
    """人体星図セクションを表示する。"""
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
    df_chart = pd.DataFrame(
        {"位置": list(chart_data.keys()), "星": list(chart_data.values())}
    )
    st.dataframe(df_chart, use_container_width=True, hide_index=True)


def _render_ai_reading(ai_text: str) -> None:
    """AI鑑定レポートを構造化表示する。"""
    st.subheader("AI鑑定レポート")
    st.markdown(ai_text)


def _render_listening_hints(hints_text: str) -> None:
    """傾聴ヒントを表示する。"""
    st.subheader("傾聴のヒント（メンター向け）")
    st.info("以下はメンタリングセッションで活用するための傾聴ガイドです。")
    st.markdown(hints_text)
