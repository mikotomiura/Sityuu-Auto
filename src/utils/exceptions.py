"""カスタム例外クラス定義。"""


class FortuneAppError(Exception):
    """アプリケーション基底例外。"""


class FortuneCalculationError(FortuneAppError):
    """命式算出エラー。"""


class AIServiceError(FortuneAppError):
    """AI連携エラー。"""


class AIServiceConfigError(AIServiceError):
    """AI連携設定エラー（APIキー未設定・認証失敗など）。"""


class DatabaseError(FortuneAppError):
    """DB操作エラー。"""


class PDFExportError(FortuneAppError):
    """PDFエクスポートエラー。"""
