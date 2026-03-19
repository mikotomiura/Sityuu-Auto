"""命式表表示コンポーネント。"""

import pandas as pd
import streamlit as st

from fortune_engine.formatter import format_for_display
from fortune_engine.models import FortuneResult

# 五行の表示カラー（HTMLカラーコード）
_ELEMENT_COLORS: dict[str, str] = {
    "木": "#228B22",
    "火": "#DC143C",
    "土": "#DAA520",
    "金": "#C0C0C0",
    "水": "#4169E1",
}


def render_natal_chart(result: FortuneResult) -> None:
    """命式表を表示する。

    四柱推命の命式（年柱・月柱・日柱・時柱）をテーブルで表示し、
    日干と五行バランスをメトリクスで可視化する。

    Args:
        result: 命式算出の最終結果。
    """
    display_data = format_for_display(result)
    nc = result.natal_chart

    # --- 日干メトリクス ---
    day_element = nc.day_stem_element.value
    color = _ELEMENT_COLORS.get(day_element, "#333")
    st.markdown(
        f"### 日干: <span style='color:{color}; font-size:1.5em;'>"
        f"{nc.day_stem}（{day_element}）</span>",
        unsafe_allow_html=True,
    )

    # --- 四柱テーブル ---
    st.markdown("#### 四柱一覧")
    df_pillars = pd.DataFrame(display_data["pillars"])
    st.dataframe(df_pillars, use_container_width=True, hide_index=True)

    # --- 五行バランス ---
    st.markdown("#### 五行バランス")
    balance = display_data["five_elements_balance"]
    cols = st.columns(len(balance))
    for col, (element, count) in zip(cols, balance.items()):
        color = _ELEMENT_COLORS.get(element, "#333")
        col.markdown(
            f"<div style='text-align:center;'>"
            f"<span style='color:{color}; font-size:2em; font-weight:bold;'>{count}</span>"
            f"<br><span style='color:{color};'>{element}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
