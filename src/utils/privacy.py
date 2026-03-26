"""プライバシー保護ユーティリティ。

ブラウザの autocomplete 無効化など、相談者の個人情報が
ブラウザに残らないようにするための共通機能を提供する。
"""

import streamlit as st

# autofill時のスタイルをテーマカラーで上書きするCSS
_AUTOCOMPLETE_HIDE_CSS = """
<style>
/* Chrome/Edge の autofill スタイルをテーマに合わせる */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
textarea:-webkit-autofill,
textarea:-webkit-autofill:hover,
textarea:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0 1000px #1a1f50 inset !important;
    -webkit-text-fill-color: #e8e6f0 !important;
    caret-color: #e8e6f0 !important;
    transition: background-color 5000s ease-in-out 0s;
}
</style>
"""


def inject_autocomplete_off() -> None:
    """autofill 時のスタイルをテーマカラーで上書きする CSS を注入する。

    autocomplete の無効化は ``st.text_input`` の ``autocomplete``
    パラメータで行う（各フォームで直接設定済み）。
    本関数は autofill が発動した場合の見た目を整えるための
    CSS フォールバックのみ提供する。

    Note:
        注入する HTML はハードコードされた固定 CSS のみであり、
        外部入力は含まれないため XSS リスクはない。変更時は要レビュー。
    """
    # SECURITY: ハードコードされた固定CSSのみ。XSSリスクなし。
    st.markdown(_AUTOCOMPLETE_HIDE_CSS, unsafe_allow_html=True)
