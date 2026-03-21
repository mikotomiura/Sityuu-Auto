"""鑑定履歴一覧テーブルコンポーネント。"""

import streamlit as st

from config import CONCERN_PREVIEW_LENGTH
from db_service.repositories.session_repo import SessionWithClientName


def render_history_table(
    sessions: list[SessionWithClientName],
) -> str | None:
    """鑑定履歴の一覧テーブルを表示し、選択されたセッションIDを返す。

    各行に相談者名・悩みの概要・鑑定日時・詳細ボタンを表示する。

    Args:
        sessions: 相談者名付きセッションのリスト。

    Returns:
        選択されたセッションのUUID。未選択の場合はNone。
    """
    if not sessions:
        st.info("鑑定履歴がありません。")
        return None

    selected_id: str | None = None

    for item in sessions:
        s = item.session
        concern_preview = (
            s.concern[:CONCERN_PREVIEW_LENGTH] + "..."
            if len(s.concern) > CONCERN_PREVIEW_LENGTH
            else s.concern
        )
        created_date = s.created_at[:10] if s.created_at else "不明"
        has_ai = "AI鑑定あり" if s.ai_reading_text else "命式のみ"

        with st.container(border=True):
            col_info, col_action = st.columns([4, 1])

            with col_info:
                st.write(f"**{item.client_name}** — {created_date}")
                st.caption(f"{concern_preview} | {has_ai}")

            with col_action:
                if st.button("詳細", key=f"detail_{s.id}", use_container_width=True):
                    selected_id = s.id

    return selected_id
