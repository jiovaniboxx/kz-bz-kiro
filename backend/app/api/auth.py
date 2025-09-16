"""
認証API エンドポイント
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import AuthService, security
from app.infrastructure.repositories.admin_repository import AdminRepository
from app.domain.admin import Admin
from app.core.database import get_db_session
from app.utils.event_bus import get_event_bus

router = APIRouter(prefix="/api/auth", tags=["認証"])

# リクエスト/レスポンスモデル
class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    admin: Dict[str, Any]

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class CreateAdminRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "admin"

class AdminResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str
    last_login: str | None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class MessageResponse(BaseModel):
    message: str

# 依存関数
async def get_auth_service(
    db: AsyncSession = Depends(get_db_session),
    event_bus = Depends(get_event_bus)
) -> AuthService:
    """AuthServiceの依存注入"""
    admin_repository = AdminRepository(db)
    return AuthService(admin_repository, event_bus)

async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Admin:
    """現在の管理者を取得"""
    return await auth_service.get_current_admin(credentials)

# エンドポイント
@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """管理者ログイン"""
    client_ip = request.client.host if request.client else None
    
    result = await auth_service.authenticate_admin(
        login_data.username_or_email,
        login_data.password,
        client_ip
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません"
        )
    
    return LoginResponse(**result)

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """トークンリフレッシュ"""
    result = await auth_service.refresh_token(refresh_data.refresh_token)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なリフレッシュトークンです"
        )
    
    return RefreshTokenResponse(**result)

@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_admin: Admin = Depends(get_current_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """管理者ログアウト"""
    await auth_service.logout_admin(current_admin.id)
    return MessageResponse(message="ログアウトしました")

@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(current_admin: Admin = Depends(get_current_admin)):
    """現在の管理者情報を取得"""
    return AdminResponse(
        id=current_admin.id,
        username=current_admin.username,
        email=str(current_admin.email),
        role=current_admin.role,
        is_active=current_admin.is_active,
        created_at=current_admin.created_at.isoformat() if current_admin.created_at else "",
        last_login=current_admin.last_login.isoformat() if current_admin.last_login else None
    )

@router.post("/create-admin", response_model=AdminResponse)
async def create_admin(
    admin_data: CreateAdminRequest,
    current_admin: Admin = Depends(get_current_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """新しい管理者を作成（管理者のみ）"""
    if current_admin.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です"
        )
    
    try:
        new_admin = await auth_service.create_admin(
            admin_data.username,
            admin_data.email,
            admin_data.password,
            admin_data.role
        )
        
        return AdminResponse(
            id=new_admin.id,
            username=new_admin.username,
            email=str(new_admin.email),
            role=new_admin.role,
            is_active=new_admin.is_active,
            created_at=new_admin.created_at.isoformat() if new_admin.created_at else "",
            last_login=None
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_admin: Admin = Depends(get_current_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """パスワード変更"""
    success = await auth_service.change_password(
        current_admin.id,
        password_data.current_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="現在のパスワードが正しくありません"
        )
    
    return MessageResponse(message="パスワードを変更しました")