"""プレミアムUI テーマコンポーネント。

占い・四柱推命にふさわしい神秘的で高級感のあるカスタムCSSを
全ページに一括適用する。app.py のページ設定直後に呼び出すこと。
"""

import streamlit as st

# --- カラーパレット定数 ---
_BG_PRIMARY = "#0a0e27"
_BG_SECONDARY = "#111638"
_BG_CARD = "#161b4a"
_BG_INPUT = "#1a1f50"
_TEXT_PRIMARY = "#e8e6f0"
_TEXT_SECONDARY = "#a8a4c0"
_ACCENT_GOLD = "#d4af37"
_ACCENT_GOLD_LIGHT = "#f0d060"
_ACCENT_SILVER = "#c0c0c0"
_BORDER_SUBTLE = "#2a2f6a"
_SHADOW_COLOR = "rgba(0, 0, 0, 0.4)"

_CUSTOM_CSS = f"""
<style>
/* ===== 全体背景・テキスト ===== */
.stApp {{
    background: linear-gradient(160deg, {_BG_PRIMARY} 0%, {_BG_SECONDARY} 50%, #0d1230 100%);
    color: {_TEXT_PRIMARY};
}}

/* ===== Streamlit ヘッダー/ツールバー非表示 ===== */
header[data-testid="stHeader"] {{
    background: transparent !important;
    backdrop-filter: none !important;
}}

/* ===== 非表示iframeコンテナ（autocomplete無効化JS用）===== */
/* display:none はJS実行を阻害するため使用しない */
div:has(> iframe[height="0"]) {{
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    border: none !important;
}}

/* ===== サイドバー ===== */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0c1035 0%, #151a48 100%);
    border-right: 1px solid {_BORDER_SUBTLE};
}}

section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li {{
    color: {_TEXT_SECONDARY};
}}

/* サイドバータイトル */
section[data-testid="stSidebar"] h1 {{
    color: {_ACCENT_GOLD} !important;
    text-shadow: 0 0 12px rgba(212, 175, 55, 0.3);
}}

/* ===== ページタイトル (h1) ===== */
.stApp h1 {{
    color: {_ACCENT_GOLD} !important;
    text-shadow: 0 0 16px rgba(212, 175, 55, 0.25);
    letter-spacing: 0.04em;
}}

/* ===== 見出し (h2, h3, h4) ===== */
.stApp h2 {{
    color: {_TEXT_PRIMARY} !important;
    border-bottom: 1px solid {_BORDER_SUBTLE};
    padding-bottom: 0.3em;
}}

.stApp h3, .stApp h4 {{
    color: {_ACCENT_SILVER} !important;
}}

/* ===== フォームラベル ===== */
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stDateInput label,
.stTimeInput label,
.stCheckbox label,
.stNumberInput label {{
    color: {_TEXT_PRIMARY} !important;
}}

/* ===== テキスト入力・テキストエリア ===== */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    background-color: {_BG_INPUT} !important;
    color: {_TEXT_PRIMARY} !important;
    border: 1px solid {_BORDER_SUBTLE} !important;
    border-radius: 10px !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {_ACCENT_GOLD} !important;
    box-shadow: 0 0 8px rgba(212, 175, 55, 0.3) !important;
}}

/* ===== セレクトボックス ===== */
.stSelectbox > div > div {{
    background-color: {_BG_INPUT} !important;
    border: 1px solid {_BORDER_SUBTLE} !important;
    border-radius: 10px !important;
}}

/* ===== 日付入力 ===== */
.stDateInput > div > div > input {{
    background-color: {_BG_INPUT} !important;
    color: {_TEXT_PRIMARY} !important;
    border: 1px solid {_BORDER_SUBTLE} !important;
    border-radius: 10px !important;
}}

/* ===== プライマリボタン ===== */
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {_ACCENT_GOLD} 0%, #c9a227 100%) !important;
    color: {_BG_PRIMARY} !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em;
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
    transition: all 0.3s ease !important;
}}

.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover {{
    background: linear-gradient(135deg, {_ACCENT_GOLD_LIGHT} 0%, {_ACCENT_GOLD} 100%) !important;
    box-shadow: 0 6px 20px rgba(212, 175, 55, 0.5) !important;
    transform: translateY(-1px);
}}

/* ===== セカンダリボタン ===== */
.stButton > button[kind="secondary"],
.stButton > button:not([kind]) {{
    background-color: transparent !important;
    color: {_ACCENT_SILVER} !important;
    border: 1px solid {_BORDER_SUBTLE} !important;
    border-radius: 10px !important;
    transition: all 0.3s ease !important;
}}

.stButton > button[kind="secondary"]:hover,
.stButton > button:not([kind]):hover {{
    border-color: {_ACCENT_GOLD} !important;
    color: {_ACCENT_GOLD} !important;
    box-shadow: 0 0 12px rgba(212, 175, 55, 0.2) !important;
}}

/* ===== カード風コンテナ (st.container(border=True)) ===== */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: {_BG_CARD} !important;
    border: 1px solid {_BORDER_SUBTLE} !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 16px {_SHADOW_COLOR} !important;
    transition: box-shadow 0.3s ease, border-color 0.3s ease;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    border-color: rgba(212, 175, 55, 0.3) !important;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.5) !important;
}}

/* ===== エキスパンダー ===== */
.streamlit-expanderHeader {{
    background-color: {_BG_CARD} !important;
    border-radius: 10px !important;
    color: {_TEXT_PRIMARY} !important;
}}

details[data-testid="stExpander"] {{
    background-color: {_BG_CARD} !important;
    border: 1px solid {_BORDER_SUBTLE} !important;
    border-radius: 12px !important;
}}

/* ===== タブ ===== */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    border-bottom: 1px solid {_BORDER_SUBTLE};
}}

.stTabs [data-baseweb="tab"] {{
    background-color: transparent;
    color: {_TEXT_SECONDARY} !important;
    border-radius: 8px 8px 0 0;
    transition: all 0.3s ease;
}}

.stTabs [data-baseweb="tab"][aria-selected="true"] {{
    background-color: {_BG_CARD};
    color: {_ACCENT_GOLD} !important;
    border-bottom: 2px solid {_ACCENT_GOLD};
}}

/* ===== メトリクス ===== */
div[data-testid="stMetric"] {{
    background-color: {_BG_CARD};
    border: 1px solid {_BORDER_SUBTLE};
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 8px {_SHADOW_COLOR};
}}

div[data-testid="stMetric"] label {{
    color: {_TEXT_SECONDARY} !important;
}}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {_ACCENT_GOLD} !important;
}}

/* ===== 通知メッセージのスタイル調整 ===== */
.stAlert {{
    border-radius: 10px !important;
}}

/* st.success */
div[data-testid="stAlert"][data-baseweb="notification"][kind="positive"] {{
    background-color: rgba(34, 139, 34, 0.15) !important;
    border-left: 4px solid #228B22 !important;
}}

/* st.info */
div[data-testid="stAlert"][data-baseweb="notification"][kind="info"] {{
    background-color: rgba(65, 105, 225, 0.15) !important;
    border-left: 4px solid #4169E1 !important;
}}

/* st.warning */
div[data-testid="stAlert"][data-baseweb="notification"][kind="warning"] {{
    background-color: rgba(212, 175, 55, 0.15) !important;
    border-left: 4px solid {_ACCENT_GOLD} !important;
}}

/* st.error */
div[data-testid="stAlert"][data-baseweb="notification"][kind="negative"] {{
    background-color: rgba(220, 20, 60, 0.15) !important;
    border-left: 4px solid #DC143C !important;
}}

/* ===== テーブル / DataFrame ===== */
.stDataFrame {{
    border-radius: 10px !important;
    overflow: hidden;
}}

/* ===== ダウンロードボタン ===== */
.stDownloadButton > button {{
    background-color: {_BG_CARD} !important;
    color: {_ACCENT_SILVER} !important;
    border: 1px solid {_BORDER_SUBTLE} !important;
    border-radius: 10px !important;
    transition: all 0.3s ease !important;
}}

.stDownloadButton > button:hover {{
    border-color: {_ACCENT_GOLD} !important;
    color: {_ACCENT_GOLD} !important;
    box-shadow: 0 0 12px rgba(212, 175, 55, 0.2) !important;
}}

/* ===== フォーム ===== */
div[data-testid="stForm"] {{
    background-color: {_BG_CARD} !important;
    border: 1px solid {_BORDER_SUBTLE} !important;
    border-radius: 14px !important;
    padding: 1.5rem !important;
    box-shadow: 0 4px 20px {_SHADOW_COLOR} !important;
}}

/* ===== キャプション ===== */
.stCaption, .stMarkdown small {{
    color: {_TEXT_SECONDARY} !important;
}}

/* ===== 区切り線 ===== */
hr {{
    border-color: {_BORDER_SUBTLE} !important;
}}

/* ===== スピナー ===== */
.stSpinner > div {{
    border-top-color: {_ACCENT_GOLD} !important;
}}

/* ===== チェックボックス ===== */
.stCheckbox label span {{
    color: {_TEXT_PRIMARY} !important;
}}

/* ===== ラジオボタン ===== */
.stRadio label {{
    color: {_TEXT_PRIMARY} !important;
}}

/* ===== スクロールバー ===== */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: {_BG_PRIMARY};
}}

::-webkit-scrollbar-thumb {{
    background: {_BORDER_SUBTLE};
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: {_ACCENT_GOLD};
}}

/* ===== ログインページ装飾 ===== */
.login-card {{
    background: linear-gradient(145deg, {_BG_CARD} 0%, #1a1f55 100%);
    border: 1px solid {_BORDER_SUBTLE};
    border-radius: 20px;
    padding: 2.5rem 2rem;
    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.5),
        0 0 60px rgba(212, 175, 55, 0.06);
    margin-top: 1rem;
}}

.login-logo {{
    text-align: center;
    font-size: 3.5rem;
    margin-bottom: 0.2rem;
    filter: drop-shadow(0 0 12px rgba(212, 175, 55, 0.4));
}}

.login-title {{
    text-align: center;
    font-size: 1.8rem;
    font-weight: 700;
    color: {_ACCENT_GOLD};
    letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
    text-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
}}

.login-subtitle {{
    text-align: center;
    font-size: 0.9rem;
    color: {_TEXT_SECONDARY};
    margin-bottom: 2rem;
    letter-spacing: 0.06em;
}}

.login-divider {{
    height: 1px;
    background: linear-gradient(
        90deg, transparent, {_BORDER_SUBTLE},
        {_ACCENT_GOLD}, {_BORDER_SUBTLE}, transparent);
    margin: 1.2rem 0;
    border: none;
}}

/* ===== ページ説明テキスト ===== */
.page-description {{
    color: {_TEXT_SECONDARY};
    font-size: 0.92rem;
    margin-top: -0.8rem;
    margin-bottom: 1.5rem;
    padding-left: 0.1rem;
    letter-spacing: 0.02em;
}}

/* ===== セクション見出し装飾 ===== */
.section-header {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.8rem;
}}

.section-header-icon {{
    font-size: 1.3rem;
    filter: drop-shadow(0 0 4px rgba(212, 175, 55, 0.3));
}}

.section-header-text {{
    color: {_ACCENT_SILVER};
    font-size: 1.1rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}}

/* ===== 装飾区切り線 ===== */
.fancy-divider {{
    height: 1px;
    background: linear-gradient(
        90deg, transparent, {_BORDER_SUBTLE} 20%,
        {_ACCENT_GOLD} 50%, {_BORDER_SUBTLE} 80%, transparent);
    margin: 1.5rem 0;
    border: none;
}}

/* ===== 空状態メッセージ ===== */
.empty-state {{
    text-align: center;
    padding: 3rem 1.5rem;
    color: {_TEXT_SECONDARY};
}}

.empty-state-icon {{
    font-size: 3rem;
    margin-bottom: 0.8rem;
    opacity: 0.6;
    filter: drop-shadow(0 0 8px rgba(212, 175, 55, 0.2));
}}

.empty-state-text {{
    font-size: 1rem;
    line-height: 1.6;
}}

/* ===== サイドバー装飾 ===== */
section[data-testid="stSidebar"] .sidebar-brand {{
    text-align: center;
    padding: 0.5rem 0 1rem;
}}

section[data-testid="stSidebar"] .sidebar-brand-icon {{
    font-size: 2.5rem;
    filter: drop-shadow(0 0 12px rgba(212, 175, 55, 0.5));
}}

section[data-testid="stSidebar"] .sidebar-divider {{
    height: 1px;
    background: linear-gradient(
        90deg, transparent, {_BORDER_SUBTLE},
        {_ACCENT_GOLD}, {_BORDER_SUBTLE}, transparent);
    margin: 0.5rem 0;
    border: none;
}}

/* ===== ステータスバッジ ===== */
.status-badge {{
    display: inline-block;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}}

.status-badge-ai {{
    background: rgba(212, 175, 55, 0.15);
    color: {_ACCENT_GOLD};
    border: 1px solid rgba(212, 175, 55, 0.3);
}}

.status-badge-basic {{
    background: rgba(192, 192, 192, 0.1);
    color: {_ACCENT_SILVER};
    border: 1px solid rgba(192, 192, 192, 0.2);
}}
</style>
"""


def inject_custom_theme() -> None:
    """占い・四柱推命アプリ向けのプレミアムテーマCSSを注入する。

    ミッドナイトブルー・深紫を基調とし、ゴールド・シルバーの
    アクセントを配したカスタムCSSを全ページに適用する。
    ``app.py`` のページ設定直後に1度だけ呼び出すこと。

    Note:
        ``st.markdown(unsafe_allow_html=True)`` を使用するが、
        注入するHTMLはハードコードされた固定CSSのみであり、
        外部入力は含まれないためXSSリスクはない。変更時は要レビュー。
    """
    st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)
