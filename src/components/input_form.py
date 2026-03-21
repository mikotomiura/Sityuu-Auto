"""相談者情報入力フォームコンポーネント。"""

from dataclasses import dataclass
from datetime import date, time

import streamlit as st

from config import SESSION_KEY_FORM_VERSION
from utils.validators import validate_client_name, validate_concern


@dataclass
class ClientInputData:
    """フォームから取得した入力データ。

    Attributes:
        name: 相談者の名前（仮名可）。
        name_kana: フリガナ（カタカナ）。未入力の場合はNone。
        birth_date: 生年月日。
        birth_time: 出生時間。不明の場合はNone。
        gender: 性別。
        concern: 現在の主な悩み。
    """

    name: str
    name_kana: str | None
    birth_date: date
    birth_time: time | None
    gender: str | None
    concern: str


def _inject_autocomplete_off() -> None:
    """フォーム内の入力欄でブラウザの autocomplete を無効化する。

    相談者の名前等はプライバシー情報であるため、ブラウザの入力候補に
    残らないよう autocomplete 属性を off に設定する。
    """
    st.markdown(
        """
        <script>
        const disableAutocomplete = () => {
            document.querySelectorAll(
                'input[type="text"], textarea'
            ).forEach(el => {
                el.setAttribute('autocomplete', 'off');
            });
        };
        // 初回実行 + DOM変更時にも再適用
        disableAutocomplete();
        const observer = new MutationObserver(disableAutocomplete);
        observer.observe(document.body, {childList: true, subtree: true});
        </script>
        """,
        # SECURITY: 注入するHTMLはハードコードされた固定スクリプトのみ。
        # 外部入力は含まれないためXSSリスクなし。変更時は要レビュー。
        unsafe_allow_html=True,
    )


def render_client_input_form() -> ClientInputData | None:
    """相談者情報の入力フォームを表示し、送信された場合にデータを返す。

    Note:
        プライバシー保護のため、内部で JavaScript を注入してブラウザの
        autocomplete を無効化する。

    Returns:
        フォーム送信時: ClientInputData。
        未送信時: None。
    """
    _inject_autocomplete_off()

    form_version = st.session_state.get(SESSION_KEY_FORM_VERSION, 0)
    with st.form(f"client_input_form_{form_version}"):
        st.subheader("相談者情報")

        # --- 基本情報 ---
        col_name, col_kana, col_gender = st.columns([2, 2, 1])
        with col_name:
            name = st.text_input(
                "お名前（仮名可）",
                max_chars=50,
                placeholder="例: 山田太郎",
            )
        with col_kana:
            name_kana = st.text_input(
                "フリガナ",
                max_chars=50,
                placeholder="例: ヤマダ タロウ",
                help="名前の音韻（響き）を鑑定に活用します。",
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

    # バリデーション（validators モジュールに委譲）
    name_error = validate_client_name(name)
    if name_error:
        st.warning(name_error)
        return None

    concern_error = validate_concern(concern)
    if concern_error:
        st.warning(concern_error)
        return None

    return ClientInputData(
        name=name.strip(),
        name_kana=name_kana.strip() if name_kana.strip() else None,
        birth_date=birth_date,
        birth_time=None if birth_time_unknown else birth_time_input,
        gender=gender if gender != "回答しない" else None,
        concern=concern.strip(),
    )
