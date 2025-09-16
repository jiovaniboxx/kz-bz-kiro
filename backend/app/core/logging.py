"""
ログ設定とエラー監視
"""
import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
import json
import traceback
from enum import Enum

class LogLevel(Enum):
    """ログレベル"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ErrorCategory(Enum):
    """エラーカテゴリ"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    SYSTEM = "system"
    BUSINESS_LOGIC = "business_logic"
    UNKNOWN = "unknown"

class ErrorLogger:
    """エラーログ記録クラス"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self._setup_loggers()
    
    def _setup_loggers(self):
        """ログ設定を初期化"""
        # メインログファイル
        self.main_logger = logging.getLogger("english_cafe_main")
        self.main_logger.setLevel(logging.INFO)
        
        # エラーログファイル
        self.error_logger = logging.getLogger("english_cafe_error")
        self.error_logger.setLevel(logging.ERROR)
        
        # セキュリティログファイル
        self.security_logger = logging.getLogger("english_cafe_security")
        self.security_logger.setLevel(logging.WARNING)
        
        # フォーマッター
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # ファイルハンドラー
        main_handler = logging.FileHandler(self.log_dir / "main.log")
        main_handler.setFormatter(formatter)
        self.main_logger.addHandler(main_handler)
        
        error_handler = logging.FileHandler(self.log_dir / "error.log")
        error_handler.setFormatter(formatter)
        self.error_logger.addHandler(error_handler)
        
        security_handler = logging.FileHandler(self.log_dir / "security.log")
        security_handler.setFormatter(formatter)
        self.security_logger.addHandler(security_handler)
        
        # コンソール出力（開発環境）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.main_logger.addHandler(console_handler)
    
    def log_error(
        self,
        error: Exception,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """エラーをログに記録"""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "category": category.value,
            "user_id": user_id,
            "request_id": request_id,
            "traceback": traceback.format_exc(),
            "additional_data": additional_data or {}
        }
        
        # JSONログとして記録
        self.error_logger.error(json.dumps(error_data, ensure_ascii=False))
        
        # 重要なエラーの場合は即座に通知
        if category in [ErrorCategory.SYSTEM, ErrorCategory.DATABASE]:
            self._send_critical_alert(error_data)
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """セキュリティイベントをログに記録"""
        security_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "additional_data": additional_data or {}
        }
        
        self.security_logger.warning(json.dumps(security_data, ensure_ascii=False))
        
        # 高リスクイベントの場合は即座に通知
        if severity in ["HIGH", "CRITICAL"]:
            self._send_security_alert(security_data)
    
    def log_performance_issue(
        self,
        endpoint: str,
        response_time: float,
        threshold: float = 5.0,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """パフォーマンス問題をログに記録"""
        if response_time > threshold:
            performance_data = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "slow_response",
                "endpoint": endpoint,
                "response_time": response_time,
                "threshold": threshold,
                "additional_data": additional_data or {}
            }
            
            self.main_logger.warning(json.dumps(performance_data, ensure_ascii=False))
    
    def _send_critical_alert(self, error_data: Dict[str, Any]):
        """重要なエラーのアラート送信（将来実装）"""
        # TODO: Slack、メール、SMS等での通知実装
        print(f"CRITICAL ALERT: {error_data['error_type']} - {error_data['error_message']}")
    
    def _send_security_alert(self, security_data: Dict[str, Any]):
        """セキュリティアラートの送信（将来実装）"""
        # TODO: セキュリティチームへの通知実装
        print(f"SECURITY ALERT: {security_data['event_type']} - {security_data['severity']}")

# グローバルエラーログインスタンス
error_logger = ErrorLogger()

def log_error(
    error: Exception,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    additional_data: Optional[Dict[str, Any]] = None
):
    """エラーログ記録のヘルパー関数"""
    error_logger.log_error(error, category, user_id, request_id, additional_data)

def log_security_event(
    event_type: str,
    severity: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    additional_data: Optional[Dict[str, Any]] = None
):
    """セキュリティイベントログ記録のヘルパー関数"""
    error_logger.log_security_event(
        event_type, severity, user_id, ip_address, user_agent, additional_data
    )

def log_performance_issue(
    endpoint: str,
    response_time: float,
    threshold: float = 5.0,
    additional_data: Optional[Dict[str, Any]] = None
):
    """パフォーマンス問題ログ記録のヘルパー関数"""
    error_logger.log_performance_issue(endpoint, response_time, threshold, additional_data)