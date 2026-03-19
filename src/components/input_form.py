"""相談者情報入力フォームコンポーネント。"""

from dataclasses import dataclass
from datetime import date, time

import streamlit as st


@dataclass
class ClientInputData:
    """フォームから取得した入力データ。

    Attributes:
        name: 相談者の名前（仮名可）。
        birth_date: 生年月日。
        birth_time: 出生時間。不明の場合はNone。
        gender: 性別。
        concern: 現在の主な悩み。
    """

    name: str
    birth_date: date
    birth_time: time | None
    gender: str | None
    concern: str


def render_client_input_form() -> ClientInputData | None:
    """相談者情報の入力フォームを表示し、送信された場合にデータを返す。

    Returns:
        フォーム送信時: ClientInputData。
        未送信時: None。
    """
    with st.form("client_input_form"):
        st.subheader("相談者情報")

        # --- 基本情報（2カラム） ---
        col_name, col_gender = st.columns([3, 1])
        with col_name:
            name = st.text_input(
                "お名前（仮名可）",
                max_chars=50,
                placeholder="例: 山田太郎",
            )
        with col_gender:
            gender = st.selectbox(
                "性別",
                options=["回答しない", "男性", "女性"],
            )

        # --- 生年月日・出生時間（2カラム） ---
        col_date, col_time = st.columns(2)
        with col_date:
            birth_date = st.date_input(
                "生年月日",
                value=date(1990, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
            )
        with col_time:
            birth_time_unknown = st.checkbox("出生時間不明")
            birth_time_input = st.time_input(
                "出生時間",
                disabled=birth_time_unknown,
            )

        # --- 悩み ---
        st.markdown("---")
        concern = st.text_area(
            "現在の主な悩み",
            max_chars=2000,
            height=120,
            placeholder="相談したい内容を入力してください（10文字以上）",
        )

        submitted = st.form_submit_button(
            "命式を算出して鑑定を開始",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return None

    # バリデーション
    if len(name.strip()) < 1:
        st.warning("お名前を入力してください。")
        return None

    if len(concern.strip()) < 10:
        st.warning("悩みは10文字以上入力してください。")
        return None

    return ClientInputData(
        name=name.strip(),
        birth_date=birth_date,
        birth_time=None if birth_time_unknown else birth_time_input,
        gender=gender if gender != "回答しない" else None,
        concern=concern.strip(),
    )
