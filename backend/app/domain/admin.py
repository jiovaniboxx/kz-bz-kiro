"""
管理者ドメインモデル
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import re
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

@dataclass(frozen=True)
class AdminEmail:
    """管理者メールアドレス値オブジェクト"""
    value: str
    
    def __post_init__(self):
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', self.value):
            raise ValueError("無効なメールアドレスです")
    
    def __str__(self):
        return self.value

@dataclass
class AdminLoginEvent:
    """管理者ログインイベント"""
    admin_id: str
    email: str
    login_at: datetime
    ip_address: Optional[str] = None

@dataclass
class AdminLogoutEvent:
    """管理者ログアウトイベント"""
    admin_id: str
    email: str
    logout_at: datetime

@dataclass
class Admin:
    """管理者エンティティ"""
    id: str
    username: str
    email: AdminEmail
    hashed_password: str
    role: str = "admin"  # admin, staff
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.created_at:
            object.__setattr__(self, 'created_at', datetime.now())
    
    @classmethod
    def create(cls, username: str, email: str, password: str, role: str = "admin") -> "Admin":
        """新しい管理者を作成"""
        import uuid
        
        if len(password) < 8:
            raise ValueError("パスワードは8文字以上である必要があります")
        
        hashed_password = pwd_context.hash(password)
        
        return cls(
            id=str(uuid.uuid4()),
            username=username,
            email=AdminEmail(email),
            hashed_password=hashed_password,
            role=role
        )
    
    def verify_password(self, password: str) -> bool:
        """パスワード検証"""
        return pwd_context.verify(password, self.hashed_password)
    
    def login(self, ip_address: Optional[str] = None) -> AdminLoginEvent:
        """ログイン処理"""
        object.__setattr__(self, 'last_login', datetime.now())
        return AdminLoginEvent(
            admin_id=self.id,
            email=str(self.email),
            login_at=self.last_login,
            ip_address=ip_address
        )
    
    def logout(self) -> AdminLogoutEvent:
        """ログアウト処理"""
        return AdminLogoutEvent(
            admin_id=self.id,
            email=str(self.email),
            logout_at=datetime.now()
        )
    
    def change_password(self, new_password: str) -> None:
        """パスワード変更"""
        if len(new_password) < 8:
            raise ValueError("パスワードは8文字以上である必要があります")
        
        object.__setattr__(self, 'hashed_password', pwd_context.hash(new_password))
    
    def deactivate(self) -> None:
        """アカウント無効化"""
        object.__setattr__(self, 'is_active', False)
    
    def activate(self) -> None:
        """アカウント有効化"""
        object.__setattr__(self, 'is_active', True)