"""
認証サービス
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.admin import Admin, AdminEmail
    from app.infrastructure.repositories.admin_repository import AdminRepository
    from app.utils.event_bus import EventBus

# JWT設定
SECRET_KEY = "your-secret-key-change-in-production"  # 本番環境では環境変数から取得
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()

class AuthService:
    """認証サービス"""
    
    def __init__(self, admin_repository: "AdminRepository", event_bus: "EventBus"):
        self.admin_repository = admin_repository
        self.event_bus = event_bus
    
    async def authenticate_admin(self, username_or_email: str, password: str, ip_address: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """管理者認証"""
        # ユーザー名またはメールアドレスで検索
        admin = await self.admin_repository.find_by_username(username_or_email)
        if not admin:
            admin = await self.admin_repository.find_by_email(username_or_email)
        
        if not admin or not admin.is_active:
            return None
        
        if not admin.verify_password(password):
            return None
        
        # ログインイベント発行
        login_event = admin.login(ip_address)
        await self.event_bus.publish(login_event)
        
        # 管理者情報を更新（最終ログイン時刻）
        await self.admin_repository.save(admin)
        
        # JWTトークン生成
        access_token = self._create_access_token({"sub": admin.id, "username": admin.username, "role": admin.role})
        refresh_token = self._create_refresh_token({"sub": admin.id})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "admin": {
                "id": admin.id,
                "username": admin.username,
                "email": str(admin.email),
                "role": admin.role
            }
        }
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """リフレッシュトークンで新しいアクセストークンを生成"""
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            admin_id: str = payload.get("sub")
            if admin_id is None:
                return None
        except JWTError:
            return None
        
        admin = await self.admin_repository.find_by_id(admin_id)
        if not admin or not admin.is_active:
            return None
        
        # 新しいアクセストークン生成
        access_token = self._create_access_token({"sub": admin.id, "username": admin.username, "role": admin.role})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    async def get_current_admin(self, credentials: HTTPAuthorizationCredentials) -> "Admin":
        """現在の管理者を取得"""
        token = credentials.credentials
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            admin_id: str = payload.get("sub")
            if admin_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="無効なトークンです",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無効なトークンです",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        admin = await self.admin_repository.find_by_id(admin_id)
        if not admin or not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="管理者が見つかりません",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return admin
    
    async def create_admin(self, username: str, email: str, password: str, role: str = "admin") -> "Admin":
        """新しい管理者を作成"""
        # 既存チェック
        existing_username = await self.admin_repository.find_by_username(username)
        if existing_username:
            raise ValueError("このユーザー名は既に使用されています")
        
        existing_email = await self.admin_repository.find_by_email(email)
        if existing_email:
            raise ValueError("このメールアドレスは既に使用されています")
        
        # 管理者作成
        admin = Admin.create(username, email, password, role)
        return await self.admin_repository.save(admin)
    
    async def change_password(self, admin_id: str, current_password: str, new_password: str) -> bool:
        """パスワード変更"""
        admin = await self.admin_repository.find_by_id(admin_id)
        if not admin:
            return False
        
        if not admin.verify_password(current_password):
            return False
        
        admin.change_password(new_password)
        await self.admin_repository.save(admin)
        return True
    
    async def logout_admin(self, admin_id: str) -> None:
        """管理者ログアウト"""
        admin = await self.admin_repository.find_by_id(admin_id)
        if admin:
            logout_event = admin.logout()
            await self.event_bus.publish(logout_event)
    
    def _create_access_token(self, data: Dict[str, Any]) -> str:
        """アクセストークン生成"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def _create_refresh_token(self, data: Dict[str, Any]) -> str:
        """リフレッシュトークン生成"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 依存関数
async def get_current_admin(credentials: HTTPAuthorizationCredentials = security) -> "Admin":
    """現在の管理者を取得する依存関数"""
    # この関数は実際のAPIエンドポイントで使用される際に、
    # AuthServiceのインスタンスを注入する必要があります
    pass

def require_admin_role(required_role: str = "admin"):
    """管理者ロール要求デコレータ"""
    def decorator(admin: "Admin"):
        if admin.role != required_role and admin.role != "admin":  # adminは全権限
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="権限が不足しています"
            )
        return admin
    return decorator