"""命式表表示コンポーネント。"""

import pandas as pd
import streamlit as st

from fortune_engine.formatter import format_for_display
from fortune_engine.models import FortuneResult


def render_natal_chart(result: FortuneResult) -> None:
    """命式表を表示する。

    四柱推命の命式（年柱・月柱・日柱・時柱）をテーブルで表示し、
    五行バランスを棒グラフで可視化する。

    Args:
        result: 命式算出の最終結果。
    """
    display_data = format_for_display(result)
    nc = result.natal_chart

    st.subheader("命式表")
    st.markdown(f"**日干: {nc.day_stem}（{nc.day_stem_element.value}）**")

    # 四柱テーブル
    df_pillars = pd.DataFrame(display_data["pillars"])
    st.table(df_pillars)

    # 五行バランス
    st.subheader("五行バランス")
    balance = display_data["five_elements_balance"]
    df_balance = pd.DataFrame(
        {"五行": list(balance.keys()), "数": list(balance.values())}
    )
    st.bar_chart(df_balance, x="五行", y="数")
