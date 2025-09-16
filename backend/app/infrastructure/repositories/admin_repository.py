"""
管理者リポジトリ実装
"""

from typing import Optional
from app.domain.admin import Admin, AdminEmail


class AdminRepository:
    """管理者リポジトリ"""
    
    def __init__(self):
        # テスト用のインメモリストレージ
        self._admins = {}
        
        # デフォルト管理者を作成
        default_admin = Admin.create(
            username="admin",
            email="admin@test.com",
            password="testpassword123",
            role="admin"
        )
        self._admins[default_admin.id] = default_admin
    
    async def find_by_id(self, admin_id: str) -> Optional[Admin]:
        """IDで管理者を検索"""
        return self._admins.get(admin_id)
    
    async def find_by_username(self, username: str) -> Optional[Admin]:
        """ユーザー名で管理者を検索"""
        for admin in self._admins.values():
            if admin.username == username:
                return admin
        return None
    
    async def find_by_email(self, email: str) -> Optional[Admin]:
        """メールアドレスで管理者を検索"""
        for admin in self._admins.values():
            if str(admin.email) == email:
                return admin
        return None
    
    async def save(self, admin: Admin) -> Admin:
        """管理者を保存"""
        self._admins[admin.id] = admin
        return admin
    
    async def delete(self, admin_id: str) -> bool:
        """管理者を削除"""
        if admin_id in self._admins:
            del self._admins[admin_id]
            return True
        return False