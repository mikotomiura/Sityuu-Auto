"""プライバシー保護ユーティリティ。

ブラウザの autocomplete 無効化など、相談者の個人情報が
ブラウザに残らないようにするための共通機能を提供する。
"""

import streamlit.components.v1 as components

_AUTOCOMPLETE_OFF_JS = """
<script>
(function() {
    // st.components.v1.html() は iframe 内で実行されるため、
    // window.parent.document で Streamlit メインページの DOM にアクセスする
    const parentDoc = window.parent.document;

    const disableAutocomplete = () => {
        const selectors = 'input[type="text"], input:not([type]), textarea';
        parentDoc.querySelectorAll(selectors).forEach(el => {
            // "new-password" はほとんどのブラウザで autocomplete を確実に無効化する
            el.setAttribute('autocomplete', 'new-password');
        });
    };
    // 初回実行
    disableAutocomplete();
    // DOM変更時にも再適用（Streamlitの動的レンダリングに対応）
    const observer = new MutationObserver(disableAutocomplete);
    observer.observe(parentDoc.body, {childList: true, subtree: true});
})();
</script>
"""


def inject_autocomplete_off() -> None:
    """全入力欄のブラウザ autocomplete を無効化する。

    相談者の名前・悩み等のプライバシー情報がブラウザの入力候補に
    残らないよう、autocomplete 属性を設定する JavaScript を注入する。

    ``st.components.v1.html()`` で iframe を生成し、その中から
    ``window.parent.document`` 経由でメインページの入力欄に
    ``autocomplete="new-password"`` を設定する。

    Note:
        注入する HTML はハードコードされた固定スクリプトのみであり、
        外部入力は含まれないため XSS リスクはない。変更時は要レビュー。
    """
    components.html(_AUTOCOMPLETE_OFF_JS, height=0, width=0)
