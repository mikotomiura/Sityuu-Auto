"""テキスト処理ユーティリティ。"""

import re


def strip_mentor_section(ai_text: str) -> str:
    """AI鑑定テキストからメンター向けセクション（## 5.）を除去する。

    エクスポート時に相談者向けレポートを生成する際に使用する。

    Args:
        ai_text: AI生成の鑑定テキスト。

    Returns:
        メンター向けセクションを除去したテキスト。
    """
    # "## 5." で始まるセクションから次の "## " または末尾までを除去
    pattern = r"\n*## 5\..*?(?=\n## |\Z)"
    return re.sub(pattern, "", ai_text, flags=re.DOTALL).rstrip()
