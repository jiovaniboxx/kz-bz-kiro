"""
エラーハンドリングミドルウェア
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging import log_error, log_security_event, log_performance_issue, ErrorCategory

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """エラーハンドリングミドルウェア"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # リクエストIDを生成
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 開始時刻を記録
        start_time = time.time()
        
        try:
            # リクエストを処理
            response = await call_next(request)
            
            # レスポンス時間を計算
            process_time = time.time() - start_time
            
            # パフォーマンス監視
            log_performance_issue(
                endpoint=str(request.url.path),
                response_time=process_time,
                additional_data={
                    "method": request.method,
                    "status_code": response.status_code,
                    "request_id": request_id
                }
            )
            
            # レスポンスヘッダーにリクエストIDを追加
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except HTTPException as e:
            # HTTPエラーの処理
            await self._handle_http_exception(request, e, request_id)
            raise
            
        except Exception as e:
            # 予期しないエラーの処理
            return await self._handle_unexpected_error(request, e, request_id)
    
    async def _handle_http_exception(self, request: Request, exc: HTTPException, request_id: str):
        """HTTPエラーの処理"""
        # セキュリティ関連のエラーをログに記録
        if exc.status_code in [401, 403, 429]:
            severity = "HIGH" if exc.status_code == 403 else "MEDIUM"
            log_security_event(
                event_type=f"http_{exc.status_code}",
                severity=severity,
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                additional_data={
                    "path": str(request.url.path),
                    "method": request.method,
                    "request_id": request_id,
                    "detail": exc.detail
                }
            )
        
        # 4xx, 5xxエラーをログに記録
        if exc.status_code >= 400:
            category = ErrorCategory.AUTHENTICATION if exc.status_code == 401 else \
                      ErrorCategory.AUTHORIZATION if exc.status_code == 403 else \
                      ErrorCategory.VALIDATION if 400 <= exc.status_code < 500 else \
                      ErrorCategory.SYSTEM
            
            log_error(
                error=Exception(f"HTTP {exc.status_code}: {exc.detail}"),
                category=category,
                request_id=request_id,
                additional_data={
                    "path": str(request.url.path),
                    "method": request.method,
                    "status_code": exc.status_code,
                    "client_ip": self._get_client_ip(request)
                }
            )
    
    async def _handle_unexpected_error(self, request: Request, exc: Exception, request_id: str) -> JSONResponse:
        """予期しないエラーの処理"""
        # エラーをログに記録
        log_error(
            error=exc,
            category=ErrorCategory.SYSTEM,
            request_id=request_id,
            additional_data={
                "path": str(request.url.path),
                "method": request.method,
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent")
            }
        )
        
        # 本番環境では詳細なエラー情報を隠す
        import os
        is_production = os.getenv("ENVIRONMENT", "development") == "production"
        
        if is_production:
            error_detail = "内部サーバーエラーが発生しました"
        else:
            error_detail = f"{type(exc).__name__}: {str(exc)}"
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": error_detail,
                "request_id": request_id,
                "timestamp": time.time()
            },
            headers={"X-Request-ID": request_id}
        )
    
    def _get_client_ip(self, request: Request) -> str:
        """クライアントIPアドレスを取得"""
        # プロキシ経由の場合のヘッダーをチェック
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 直接接続の場合
        if request.client:
            return request.client.host
        
        return "unknown"

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """リクエストログミドルウェア"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # リクエスト情報をログに記録
        import logging
        logger = logging.getLogger("english_cafe_main")
        
        start_time = time.time()
        
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {self._get_client_ip(request)} "
            f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
        )
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        logger.info(
            f"Response: {response.status_code} "
            f"in {process_time:.3f}s "
            f"for {request.method} {request.url.path}"
        )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """クライアントIPアドレスを取得"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if request.client:
            return request.client.host
        
        return "unknown"