"""
API Security

APIセキュリティ機能
"""

import jwt
import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from functools import wraps

from fastapi import HTTPException, Request, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

logger = logging.getLogger(__name__)


class JWTManager:
    """JWT管理クラス"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """アクセストークンを作成"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """リフレッシュトークンを作成"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """トークンを検証"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # トークンタイプを確認
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """アクセストークンをリフレッシュ"""
        payload = self.verify_token(refresh_token, "refresh")
        
        # 新しいアクセストークンを作成
        new_token_data = {
            "sub": payload.get("sub"),
            "user_id": payload.get("user_id"),
            "role": payload.get("role"),
        }
        
        return self.create_access_token(new_token_data)


class PasswordManager:
    """パスワード管理クラス"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"])
    
    def hash_password(self, password: str) -> str:
        """パスワードをハッシュ化"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """パスワードを検証"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def generate_secure_password(self, length: int = 12) -> str:
        """セキュアなパスワードを生成"""
        import string
        
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(characters) for _ in range(length))
        
        # パスワード強度を確認
        if self.check_password_strength(password):
            return password
        else:
            # 強度が不十分な場合は再生成
            return self.generate_secure_password(length)
    
    def check_password_strength(self, password: str) -> bool:
        """パスワード強度をチェック"""
        import re
        
        # 最小長
        if len(password) < 8:
            return False
        
        # 大文字を含む
        if not re.search(r'[A-Z]', password):
            return False
        
        # 小文字を含む
        if not re.search(r'[a-z]', password):
            return False
        
        # 数字を含む
        if not re.search(r'\d', password):
            return False
        
        # 特殊文字を含む
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        return True


class APIKeyManager:
    """APIキー管理クラス"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.api_keys: Dict[str, Dict[str, Any]] = {}
    
    def generate_api_key(
        self,
        user_id: str,
        name: str,
        permissions: List[str],
        expires_at: Optional[datetime] = None
    ) -> str:
        """APIキーを生成"""
        # ランダムなAPIキーを生成
        api_key = secrets.token_urlsafe(32)
        
        # APIキー情報を保存
        self.api_keys[api_key] = {
            "user_id": user_id,
            "name": name,
            "permissions": permissions,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "last_used": None,
            "usage_count": 0,
        }
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """APIキーを検証"""
        key_info = self.api_keys.get(api_key)
        
        if not key_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        # 有効期限をチェック
        if key_info["expires_at"] and datetime.utcnow() > key_info["expires_at"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired"
            )
        
        # 使用回数を更新
        key_info["last_used"] = datetime.utcnow()
        key_info["usage_count"] += 1
        
        return key_info
    
    def revoke_api_key(self, api_key: str) -> bool:
        """APIキーを無効化"""
        if api_key in self.api_keys:
            del self.api_keys[api_key]
            return True
        return False
    
    def list_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """ユーザーのAPIキー一覧を取得"""
        user_keys = []
        for api_key, key_info in self.api_keys.items():
            if key_info["user_id"] == user_id:
                # APIキー自体は返さない（セキュリティのため）
                safe_info = key_info.copy()
                safe_info["api_key"] = api_key[:8] + "..." + api_key[-4:]
                user_keys.append(safe_info)
        
        return user_keys


class RoleBasedAccessControl:
    """ロールベースアクセス制御"""
    
    def __init__(self):
        self.roles: Dict[str, List[str]] = {
            "admin": ["*"],  # 全権限
            "manager": [
                "contacts:read",
                "contacts:write",
                "contacts:update",
                "users:read",
            ],
            "user": [
                "contacts:read",
                "profile:read",
                "profile:update",
            ],
            "guest": [
                "contacts:create",
            ],
        }
    
    def has_permission(self, user_role: str, required_permission: str) -> bool:
        """権限をチェック"""
        role_permissions = self.roles.get(user_role, [])
        
        # 全権限を持つ場合
        if "*" in role_permissions:
            return True
        
        # 特定の権限をチェック
        return required_permission in role_permissions
    
    def require_permission(self, permission: str):
        """権限を要求するデコレータ"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # リクエストからユーザー情報を取得
                request = kwargs.get("request") or args[0] if args else None
                if not request or not hasattr(request.state, "user"):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                user_role = request.state.user.get("role", "guest")
                
                if not self.has_permission(user_role, permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator


class SecurityAuditLogger:
    """セキュリティ監査ログ"""
    
    @staticmethod
    def log_authentication_attempt(
        user_id: Optional[str],
        success: bool,
        client_ip: str,
        user_agent: str,
        method: str = "password"
    ):
        """認証試行をログ"""
        log_data = {
            "event": "authentication_attempt",
            "user_id": user_id,
            "success": success,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "method": method,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if success:
            logger.info(f"Authentication success: {log_data}")
        else:
            logger.warning(f"Authentication failed: {log_data}")
    
    @staticmethod
    def log_authorization_failure(
        user_id: str,
        required_permission: str,
        client_ip: str,
        endpoint: str
    ):
        """認可失敗をログ"""
        log_data = {
            "event": "authorization_failure",
            "user_id": user_id,
            "required_permission": required_permission,
            "client_ip": client_ip,
            "endpoint": endpoint,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.warning(f"Authorization failed: {log_data}")
    
    @staticmethod
    def log_api_key_usage(
        api_key_id: str,
        user_id: str,
        endpoint: str,
        client_ip: str,
        success: bool
    ):
        """APIキー使用をログ"""
        log_data = {
            "event": "api_key_usage",
            "api_key_id": api_key_id,
            "user_id": user_id,
            "endpoint": endpoint,
            "client_ip": client_ip,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"API key usage: {log_data}")


class SecurityDependencies:
    """セキュリティ依存関数"""
    
    def __init__(self, jwt_manager: JWTManager, rbac: RoleBasedAccessControl):
        self.jwt_manager = jwt_manager
        self.rbac = rbac
        self.security = HTTPBearer()
    
    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        request: Request = None
    ) -> Dict[str, Any]:
        """現在のユーザーを取得"""
        try:
            payload = self.jwt_manager.verify_token(credentials.credentials)
            user_data = {
                "user_id": payload.get("user_id"),
                "email": payload.get("sub"),
                "role": payload.get("role", "guest"),
            }
            
            # リクエストにユーザー情報を設定
            if request:
                request.state.user = user_data
            
            return user_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    
    def require_role(self, required_role: str):
        """特定のロールを要求"""
        async def role_checker(
            current_user: Dict[str, Any] = Depends(self.get_current_user)
        ) -> Dict[str, Any]:
            user_role = current_user.get("role", "guest")
            
            if user_role != required_role and user_role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{required_role}' required"
                )
            
            return current_user
        
        return role_checker
    
    def require_permission(self, permission: str):
        """特定の権限を要求"""
        async def permission_checker(
            current_user: Dict[str, Any] = Depends(self.get_current_user),
            request: Request = None
        ) -> Dict[str, Any]:
            user_role = current_user.get("role", "guest")
            
            if not self.rbac.has_permission(user_role, permission):
                # 認可失敗をログ
                SecurityAuditLogger.log_authorization_failure(
                    current_user.get("user_id", "unknown"),
                    permission,
                    request.client.host if request and request.client else "unknown",
                    str(request.url.path) if request else "unknown"
                )
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return current_user
        
        return permission_checker


class CSRFProtection:
    """CSRF保護"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def generate_csrf_token(self, session_id: str) -> str:
        """CSRFトークンを生成"""
        import hmac
        import hashlib
        
        timestamp = str(int(datetime.utcnow().timestamp()))
        nonce = secrets.token_hex(16)
        
        message = f"{session_id}:{timestamp}:{nonce}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}:{nonce}:{signature}"
    
    def validate_csrf_token(
        self,
        token: str,
        session_id: str,
        max_age: int = 3600
    ) -> bool:
        """CSRFトークンを検証"""
        import hmac
        import hashlib
        
        try:
            timestamp_str, nonce, signature = token.split(":", 2)
            timestamp = int(timestamp_str)
            
            # トークンの有効期限をチェック
            if datetime.utcnow().timestamp() - timestamp > max_age:
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
    
    def csrf_protect(self):
        """CSRF保護デコレータ"""
        async def csrf_dependency(request: Request):
            if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                csrf_token = request.headers.get("X-CSRF-Token")
                session_id = request.headers.get("X-Session-ID", "default")
                
                if not csrf_token or not self.validate_csrf_token(csrf_token, session_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="CSRF token validation failed"
                    )
            
            return True
        
        return csrf_dependency


# セキュリティ設定のファクトリ関数
def create_security_dependencies(
    secret_key: str,
    algorithm: str = "HS256"
) -> SecurityDependencies:
    """セキュリティ依存関数を作成"""
    jwt_manager = JWTManager(secret_key, algorithm)
    rbac = RoleBasedAccessControl()
    
    return SecurityDependencies(jwt_manager, rbac)