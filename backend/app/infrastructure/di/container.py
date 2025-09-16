"""
依存性注入コンテナ
"""

from app.services.auth_service import AuthService
from app.infrastructure.repositories.admin_repository import AdminRepository
from app.utils.event_bus import event_bus


class DIContainer:
    """依存性注入コンテナ"""
    
    def __init__(self):
        self._admin_repository = None
        self._auth_service = None
    
    def get_admin_repository(self) -> AdminRepository:
        """管理者リポジトリを取得"""
        if self._admin_repository is None:
            self._admin_repository = AdminRepository()
        return self._admin_repository
    
    def get_auth_service(self) -> AuthService:
        """認証サービスを取得"""
        if self._auth_service is None:
            self._auth_service = AuthService(
                admin_repository=self.get_admin_repository(),
                event_bus=event_bus
            )
        return self._auth_service


# グローバルコンテナインスタンス
container = DIContainer()