"""鑑定結果表示コンポーネント。"""

import pandas as pd
import streamlit as st

from components.natal_chart_display import render_natal_chart
from fortune_engine.formatter import format_for_display, format_human_star_chart_grid
from fortune_engine.models import FortuneResult


def render_reading_result(result: FortuneResult, ai_text: str | None = None) -> None:
    """鑑定結果を統合表示する。

    命式表、人体星図、AI鑑定テキストをまとめて表示する。

    Args:
        result: 命式算出の最終結果。
        ai_text: AI鑑定テキスト。未生成の場合はNone。
    """
    display_data = format_for_display(result)
    sd = result.sanmei_data

    st.header("鑑定結果")

    # --- 命式表（共通コンポーネントを再利用） ---
    render_natal_chart(result)

    # --- 人体星図 ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("算命学 人体星図")
        grid_text = format_human_star_chart_grid(sd.human_star_chart)
        st.code(grid_text, language=None)

        # 人体星図の詳細テーブル
        chart_data = display_data["human_star_chart"]
        df_chart = pd.DataFrame(
            {"位置": list(chart_data.keys()), "星": list(chart_data.values())}
        )
        st.table(df_chart)

    with col2:
        st.subheader("天中殺・エネルギー")
        st.metric("天中殺", display_data["tenchusatsu"])
        st.metric("エネルギー合計", display_data["total_energy"])

    # --- AI鑑定テキスト ---
    if ai_text:
        st.markdown("---")
        st.subheader("AI鑑定テキスト")
        st.markdown(ai_text)
