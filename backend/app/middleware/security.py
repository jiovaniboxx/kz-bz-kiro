"""
Security Middleware

バックエンドセキュリティミドルウェア
"""

import re
import time
import logging
from typing import Dict, List, Optional, Set
from collections import defaultdict, deque
from datetime import datetime, timedelta

try:
    from ipaddress import ip_address, ip_network
except ImportError:
    # Fallback for older Python versions
    def ip_address(addr):
        return addr
    def ip_network(addr):
        return addr

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class SecurityHeaders:
    """セキュリティヘッダーを管理するクラス"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """セキュリティヘッダーを取得"""
        return {
            # XSS攻撃を防ぐ
            "X-XSS-Protection": "1; mode=block",
            
            # コンテンツタイプスニッフィングを防ぐ
            "X-Content-Type-Options": "nosniff",
            
            # クリックジャッキング攻撃を防ぐ
            "X-Frame-Options": "DENY",
            
            # HTTPS強制
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # リファラーポリシー
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # 権限ポリシー
            "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
            
            # コンテンツセキュリティポリシー
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self' https://english-cafe.vercel.app; "
                "frame-ancestors 'none';"
            ),
            
            # サーバー情報を隠す
            "Server": "English-Cafe-API",
            
            # キャッシュ制御
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }


class RateLimiter:
    """レート制限を実装するクラス"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, client_ip: str) -> bool:
        """リクエストが許可されるかチェック"""
        now = time.time()
        client_requests = self.requests[client_ip]
        
        # 古いリクエストを削除
        while client_requests and client_requests[0] < now - self.window_seconds:
            client_requests.popleft()
        
        # リクエスト数をチェック
        if len(client_requests) >= self.max_requests:
            return False
        
        # 新しいリクエストを記録
        client_requests.append(now)
        return True
    
    def get_remaining_requests(self, client_ip: str) -> int:
        """残りリクエスト数を取得"""
        return max(0, self.max_requests - len(self.requests[client_ip]))
    
    def get_reset_time(self, client_ip: str) -> float:
        """リセット時間を取得"""
        client_requests = self.requests[client_ip]
        if not client_requests:
            return time.time()
        return client_requests[0] + self.window_seconds


class InputValidator:
    """入力値検証クラス"""
    
    # SQLインジェクション攻撃パターン
    SQL_INJECTION_PATTERNS = [
        re.compile(r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)", re.IGNORECASE),
        re.compile(r"(--|\/\*|\*\/|;|'|\"|`)", re.IGNORECASE),
        re.compile(r"(\bOR\b|\bAND\b).*?[=<>]", re.IGNORECASE),
        re.compile(r"(INFORMATION_SCHEMA|SYSOBJECTS|SYSCOLUMNS)", re.IGNORECASE),
        re.compile(r"(\bUNION\b.*?\bSELECT\b)", re.IGNORECASE),
    ]
    
    # XSS攻撃パターン
    XSS_PATTERNS = [
        re.compile(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", re.IGNORECASE),
        re.compile(r"<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>", re.IGNORECASE),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"on\w+\s*=", re.IGNORECASE),
        re.compile(r"<img[^>]+src[^>]*>", re.IGNORECASE),
        re.compile(r"<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>", re.IGNORECASE),
        re.compile(r"<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>", re.IGNORECASE),
    ]
    
    # コマンドインジェクション攻撃パターン
    COMMAND_INJECTION_PATTERNS = [
        re.compile(r"[;&|`$(){}[\]\\]", re.IGNORECASE),
        re.compile(r"\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig)\b", re.IGNORECASE),
    ]
    
    @classmethod
    def detect_sql_injection(cls, value: str) -> bool:
        """SQLインジェクション攻撃を検出"""
        return any(pattern.search(value) for pattern in cls.SQL_INJECTION_PATTERNS)
    
    @classmethod
    def detect_xss(cls, value: str) -> bool:
        """XSS攻撃を検出"""
        return any(pattern.search(value) for pattern in cls.XSS_PATTERNS)
    
    @classmethod
    def detect_command_injection(cls, value: str) -> bool:
        """コマンドインジェクション攻撃を検出"""
        return any(pattern.search(value) for pattern in cls.COMMAND_INJECTION_PATTERNS)
    
    @classmethod
    def validate_input(cls, value: str, max_length: int = 10000) -> bool:
        """入力値を総合的に検証"""
        if not isinstance(value, str):
            return False
        
        if len(value) > max_length:
            return False
        
        if cls.detect_sql_injection(value):
            return False
        
        if cls.detect_xss(value):
            return False
        
        if cls.detect_command_injection(value):
            return False
        
        return True
    
    @classmethod
    def sanitize_input(cls, value: str) -> str:
        """入力値をサニタイズ"""
        if not isinstance(value, str):
            return str(value)
        
        # HTMLエンティティをエスケープ
        sanitized = (value
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace('"', "&quot;")
                    .replace("'", "&#x27;")
                    .replace("/", "&#x2F;"))
        
        # 制御文字を除去
        sanitized = re.sub(r'[\x00-\x1F\x7F]', '', sanitized)
        
        # 連続する空白を単一の空白に変換
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized


class IPWhitelist:
    """IP許可リスト管理クラス"""
    
    def __init__(self, whitelist: Optional[List[str]] = None):
        self.whitelist = whitelist or []
        self.networks = []
        
        for ip_str in self.whitelist:
            try:
                if '/' in ip_str:
                    self.networks.append(ip_network(ip_str))
                else:
                    self.networks.append(ip_network(f"{ip_str}/32"))
            except ValueError:
                logger.warning(f"Invalid IP address in whitelist: {ip_str}")
    
    def is_allowed(self, client_ip: str) -> bool:
        """IPアドレスが許可されているかチェック"""
        if not self.networks:
            return True  # ホワイトリストが空の場合は全て許可
        
        try:
            client_addr = ip_address(client_ip)
            return any(client_addr in network for network in self.networks)
        except ValueError:
            return False


class SecurityEventLogger:
    """セキュリティイベントログクラス"""
    
    @staticmethod
    def log_security_event(
        event_type: str,
        client_ip: str,
        user_agent: str = "",
        details: Optional[Dict] = None,
        severity: str = "medium"
    ):
        """セキュリティイベントをログに記録"""
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "severity": severity,
            "details": details or {},
        }
        
        if severity in ["high", "critical"]:
            logger.error(f"Security Event: {event_data}")
        elif severity == "medium":
            logger.warning(f"Security Event: {event_data}")
        else:
            logger.info(f"Security Event: {event_data}")


class SecurityMiddleware(BaseHTTPMiddleware):
    """メインセキュリティミドルウェア"""
    
    def __init__(
        self,
        app,
        rate_limiter: Optional[RateLimiter] = None,
        ip_whitelist: Optional[IPWhitelist] = None,
        enable_security_headers: bool = True,
        enable_input_validation: bool = True,
    ):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.ip_whitelist = ip_whitelist
        self.enable_security_headers = enable_security_headers
        self.enable_input_validation = enable_input_validation
        self.security_headers = SecurityHeaders.get_security_headers()
    
    async def dispatch(self, request: Request, call_next):
        """リクエストを処理"""
        start_time = time.time()
        client_ip = self.get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        try:
            # 1. IP許可リストチェック
            if self.ip_whitelist and not self.ip_whitelist.is_allowed(client_ip):
                SecurityEventLogger.log_security_event(
                    "ip_blocked",
                    client_ip,
                    user_agent,
                    {"path": str(request.url.path)},
                    "medium"
                )
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Access denied"}
                )
            
            # 2. レート制限チェック
            if not self.rate_limiter.is_allowed(client_ip):
                SecurityEventLogger.log_security_event(
                    "rate_limit_exceeded",
                    client_ip,
                    user_agent,
                    {
                        "path": str(request.url.path),
                        "method": request.method,
                    },
                    "medium"
                )
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests"},
                    headers={
                        "Retry-After": str(int(self.rate_limiter.get_reset_time(client_ip) - time.time())),
                        "X-RateLimit-Limit": str(self.rate_limiter.max_requests),
                        "X-RateLimit-Remaining": str(self.rate_limiter.get_remaining_requests(client_ip)),
                    }
                )
            
            # 3. 入力値検証
            if self.enable_input_validation:
                validation_result = await self.validate_request(request, client_ip, user_agent)
                if validation_result:
                    return validation_result
            
            # 4. リクエストを処理
            response = await call_next(request)
            
            # 5. セキュリティヘッダーを追加
            if self.enable_security_headers:
                for header, value in self.security_headers.items():
                    response.headers[header] = value
            
            # 6. レスポンス時間をログ
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # 異常に遅いレスポンスをログ
            if process_time > 5.0:  # 5秒以上
                SecurityEventLogger.log_security_event(
                    "slow_response",
                    client_ip,
                    user_agent,
                    {
                        "path": str(request.url.path),
                        "method": request.method,
                        "process_time": process_time,
                    },
                    "low"
                )
            
            return response
            
        except Exception as e:
            SecurityEventLogger.log_security_event(
                "middleware_error",
                client_ip,
                user_agent,
                {
                    "path": str(request.url.path),
                    "method": request.method,
                    "error": str(e),
                },
                "high"
            )
            raise
    
    def get_client_ip(self, request: Request) -> str:
        """クライアントIPアドレスを取得"""
        # プロキシ経由の場合のIPアドレスを取得
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def validate_request(self, request: Request, client_ip: str, user_agent: str) -> Optional[JSONResponse]:
        """リクエストを検証"""
        # URLパラメータを検証
        for key, value in request.query_params.items():
            if not InputValidator.validate_input(value):
                SecurityEventLogger.log_security_event(
                    "malicious_query_parameter",
                    client_ip,
                    user_agent,
                    {
                        "path": str(request.url.path),
                        "parameter": key,
                        "value": value[:100],  # 最初の100文字のみログ
                    },
                    "high"
                )
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid request parameters"}
                )
        
        # リクエストボディを検証（POSTリクエストの場合）
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode("utf-8")
                    if not InputValidator.validate_input(body_str):
                        SecurityEventLogger.log_security_event(
                            "malicious_request_body",
                            client_ip,
                            user_agent,
                            {
                                "path": str(request.url.path),
                                "method": request.method,
                                "body_preview": body_str[:200],  # 最初の200文字のみログ
                            },
                            "high"
                        )
                        return JSONResponse(
                            status_code=400,
                            content={"detail": "Invalid request body"}
                        )
            except UnicodeDecodeError:
                SecurityEventLogger.log_security_event(
                    "invalid_request_encoding",
                    client_ip,
                    user_agent,
                    {
                        "path": str(request.url.path),
                        "method": request.method,
                    },
                    "medium"
                )
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid request encoding"}
                )
        
        return None


class CSRFProtection:
    """CSRF攻撃保護クラス"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def generate_token(self, session_id: str) -> str:
        """CSRFトークンを生成"""
        import hmac
        import hashlib
        import secrets
        
        timestamp = str(int(time.time()))
        nonce = secrets.token_hex(16)
        
        message = f"{session_id}:{timestamp}:{nonce}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}:{nonce}:{signature}"
    
    def validate_token(self, token: str, session_id: str, max_age: int = 3600) -> bool:
        """CSRFトークンを検証"""
        import hmac
        import hashlib
        
        try:
            timestamp_str, nonce, signature = token.split(":", 2)
            timestamp = int(timestamp_str)
            
            # トークンの有効期限をチェック
            if time.time() - timestamp > max_age:
                return False
            
            # 署名を検証
            message = f"{session_id}:{timestamp_str}:{nonce}"
            expected_signature = hmac.new(
                self.secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except (ValueError, IndexError):
            return False


class BotDetection:
    """ボット検出クラス"""
    
    SUSPICIOUS_USER_AGENTS = [
        re.compile(r"bot", re.IGNORECASE),
        re.compile(r"crawler", re.IGNORECASE),
        re.compile(r"spider", re.IGNORECASE),
        re.compile(r"scraper", re.IGNORECASE),
        re.compile(r"curl", re.IGNORECASE),
        re.compile(r"wget", re.IGNORECASE),
        re.compile(r"python", re.IGNORECASE),
        re.compile(r"java", re.IGNORECASE),
        re.compile(r"go-http-client", re.IGNORECASE),
    ]
    
    ALLOWED_BOTS = [
        re.compile(r"googlebot", re.IGNORECASE),
        re.compile(r"bingbot", re.IGNORECASE),
        re.compile(r"slurp", re.IGNORECASE),  # Yahoo
        re.compile(r"duckduckbot", re.IGNORECASE),
        re.compile(r"facebookexternalhit", re.IGNORECASE),
        re.compile(r"twitterbot", re.IGNORECASE),
        re.compile(r"linkedinbot", re.IGNORECASE),
    ]
    
    @classmethod
    def is_suspicious_bot(cls, user_agent: str) -> bool:
        """疑わしいボットかどうかを判定"""
        if not user_agent or len(user_agent) < 10:
            return True
        
        # 許可されたボットは通す
        if any(pattern.search(user_agent) for pattern in cls.ALLOWED_BOTS):
            return False
        
        # 疑わしいパターンをチェック
        return any(pattern.search(user_agent) for pattern in cls.SUSPICIOUS_USER_AGENTS)


# セキュリティミドルウェアのファクトリ関数
def create_security_middleware(
    rate_limit_requests: int = 100,
    rate_limit_window: int = 3600,
    ip_whitelist: Optional[List[str]] = None,
    enable_security_headers: bool = True,
    enable_input_validation: bool = True,
) -> SecurityMiddleware:
    """セキュリティミドルウェアを作成"""
    rate_limiter = RateLimiter(rate_limit_requests, rate_limit_window)
    ip_whitelist_obj = IPWhitelist(ip_whitelist) if ip_whitelist else None
    
    return SecurityMiddleware(
        app=None,  # アプリケーションで設定
        rate_limiter=rate_limiter,
        ip_whitelist=ip_whitelist_obj,
        enable_security_headers=enable_security_headers,
        enable_input_validation=enable_input_validation,
    )