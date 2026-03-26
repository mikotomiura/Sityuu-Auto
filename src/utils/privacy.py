"""プライバシー保護ユーティリティ。

ブラウザの autocomplete 無効化など、相談者の個人情報が
ブラウザに残らないようにするための共通機能を提供する。
"""

import streamlit as st
import streamlit.components.v1 as components

# --- 防御層1: iframe経由で親ドキュメントのinput属性を書き換える ---
_AUTOCOMPLETE_OFF_IFRAME_JS = """
<script>
(function() {
    try {
        var doc = window.parent.document;
        var apply = function() {
            doc.querySelectorAll(
                'input[type="text"], input:not([type]), textarea'
            ).forEach(function(el) {
                el.setAttribute('autocomplete', 'new-password');
                el.setAttribute('data-lpignore', 'true');
                el.setAttribute('data-form-type', 'other');
            });
        };
        apply();
        new MutationObserver(apply).observe(
            doc.body, {childList: true, subtree: true}
        );
    } catch(e) {}
})();
</script>
"""

# --- 防御層2: st.markdown経由のscriptタグ（一部バージョンで有効） ---
_AUTOCOMPLETE_OFF_MARKDOWN = """
<script>
(function() {
    var apply = function() {
        document.querySelectorAll(
            'input[type="text"], input:not([type]), textarea'
        ).forEach(function(el) {
            el.setAttribute('autocomplete', 'new-password');
            el.setAttribute('data-lpignore', 'true');
            el.setAttribute('data-form-type', 'other');
        });
    };
    apply();
    new MutationObserver(apply).observe(
        document.body, {childList: true, subtree: true}
    );
})();
</script>
"""

# --- 防御層3: CSSでブラウザのautocomplete候補リストを不可視化 ---
_AUTOCOMPLETE_HIDE_CSS = """
<style>
/* Chrome/Edge の autocomplete ドロップダウンを非表示 */
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

/* Chrome のデータリスト/候補ポップアップを非表示 */
input::-webkit-calendar-picker-indicator,
input::-webkit-list-button {
    display: none !important;
}
</style>
"""


def inject_autocomplete_off() -> None:
    """全入力欄のブラウザ autocomplete を無効化する。

    相談者の名前・悩み等のプライバシー情報がブラウザの入力候補に
    残らないよう、3つの防御層で autocomplete を抑制する。

    1. ``st.components.v1.html()`` — iframe 経由で parent document の
       input に ``autocomplete="new-password"`` を設定
    2. ``st.markdown`` — ``<script>`` タグによる直接 DOM 操作
       （Streamlit バージョンにより有効/無効が異なる）
    3. CSS — autofill スタイルをテーマカラーで上書きし、
       候補選択時の視覚的な違和感を除去

    Note:
        注入する HTML はハードコードされた固定コンテンツのみであり、
        外部入力は含まれないため XSS リスクはない。変更時は要レビュー。
    """
    # 防御層1: iframe → parent document
    components.html(_AUTOCOMPLETE_OFF_IFRAME_JS, height=0, width=0)

    # 防御層2: st.markdown の script タグ（一部Streamlitで有効）
    # SECURITY: ハードコードされた固定スクリプトのみ。XSSリスクなし。
    st.markdown(_AUTOCOMPLETE_OFF_MARKDOWN, unsafe_allow_html=True)

    # 防御層3: CSS で autofill 候補の見た目を抑制
    st.markdown(_AUTOCOMPLETE_HIDE_CSS, unsafe_allow_html=True)
