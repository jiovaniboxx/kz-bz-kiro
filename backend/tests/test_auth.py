"""
認証機能のテスト
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.domain.admin import Admin
from app.infrastructure.repositories.admin_repository import AdminRepository
from app.services.auth_service import AuthService
from app.utils.event_bus import EventBus

class TestAuthAPI:
    """認証API テスト"""
    
    @pytest.fixture
    async def test_admin(self, db_session: AsyncSession):
        """テスト用管理者を作成"""
        admin_repository = AdminRepository(db_session)
        admin = Admin.create("testadmin", "test@example.com", "testpassword123")
        return await admin_repository.save(admin)
    
    @pytest.mark.asyncio
    async def test_login_success(self, test_admin: Admin):
        """ログイン成功テスト"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/login", json={
                "username_or_email": "testadmin",
                "password": "testpassword123"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["admin"]["username"] == "testadmin"
    
    @pytest.mark.asyncio
    async def test_login_with_email(self, test_admin: Admin):
        """メールアドレスでのログインテスト"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/login", json={
                "username_or_email": "test@example.com",
                "password": "testpassword123"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["admin"]["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, test_admin: Admin):
        """無効なパスワードでのログインテスト"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/login", json={
                "username_or_email": "testadmin",
                "password": "wrongpassword"
            })
        
        assert response.status_code == 401
        assert "ユーザー名またはパスワードが正しくありません" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self):
        """存在しないユーザーでのログインテスト"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/login", json={
                "username_or_email": "nonexistent",
                "password": "password123"
            })
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_admin(self, test_admin: Admin):
        """現在の管理者情報取得テスト"""
        # まずログインしてトークンを取得
        async with AsyncClient(app=app, base_url="http://test") as client:
            login_response = await client.post("/api/auth/login", json={
                "username_or_email": "testadmin",
                "password": "testpassword123"
            })
            token = login_response.json()["access_token"]
            
            # 管理者情報を取得
            response = await client.get("/api/auth/me", headers={
                "Authorization": f"Bearer {token}"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testadmin"
        assert data["email"] == "test@example.com"
        assert data["role"] == "admin"
    
    @pytest.mark.asyncio
    async def test_get_current_admin_invalid_token(self):
        """無効なトークンでの管理者情報取得テスト"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/auth/me", headers={
                "Authorization": "Bearer invalid_token"
            })
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, test_admin: Admin):
        """トークンリフレッシュテスト"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # ログインしてリフレッシュトークンを取得
            login_response = await client.post("/api/auth/login", json={
                "username_or_email": "testadmin",
                "password": "testpassword123"
            })
            refresh_token = login_response.json()["refresh_token"]
            
            # トークンをリフレッシュ
            response = await client.post("/api/auth/refresh", json={
                "refresh_token": refresh_token
            })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_change_password(self, test_admin: Admin):
        """パスワード変更テスト"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # ログインしてトークンを取得
            login_response = await client.post("/api/auth/login", json={
                "username_or_email": "testadmin",
                "password": "testpassword123"
            })
            token = login_response.json()["access_token"]
            
            # パスワード変更
            response = await client.post("/api/auth/change-password", 
                json={
                    "current_password": "testpassword123",
                    "new_password": "newpassword123"
                },
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 200
        assert "パスワードを変更しました" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_create_admin(self, test_admin: Admin):
        """管理者作成テスト"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # ログインしてトークンを取得
            login_response = await client.post("/api/auth/login", json={
                "username_or_email": "testadmin",
                "password": "testpassword123"
            })
            token = login_response.json()["access_token"]
            
            # 新しい管理者を作成
            response = await client.post("/api/auth/create-admin",
                json={
                    "username": "newadmin",
                    "email": "newadmin@example.com",
                    "password": "newpassword123",
                    "role": "staff"
                },
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newadmin"
        assert data["email"] == "newadmin@example.com"
        assert data["role"] == "staff"
    
    @pytest.mark.asyncio
    async def test_logout(self, test_admin: Admin):
        """ログアウトテスト"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # ログインしてトークンを取得
            login_response = await client.post("/api/auth/login", json={
                "username_or_email": "testadmin",
                "password": "testpassword123"
            })
            token = login_response.json()["access_token"]
            
            # ログアウト
            response = await client.post("/api/auth/logout",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 200
        assert "ログアウトしました" in response.json()["message"]

class TestAuthService:
    """認証サービス テスト"""
    
    @pytest.fixture
    def auth_service(self, db_session: AsyncSession):
        """AuthServiceのフィクスチャ"""
        admin_repository = AdminRepository(db_session)
        event_bus = EventBus()
        return AuthService(admin_repository, event_bus)
    
    @pytest.mark.asyncio
    async def test_create_admin(self, auth_service: AuthService):
        """管理者作成テスト"""
        admin = await auth_service.create_admin(
            "testuser", "test@example.com", "password123"
        )
        
        assert admin.username == "testuser"
        assert str(admin.email) == "test@example.com"
        assert admin.role == "admin"
        assert admin.is_active is True
    
    @pytest.mark.asyncio
    async def test_create_admin_duplicate_username(self, auth_service: AuthService):
        """重複ユーザー名での管理者作成テスト"""
        # 最初の管理者を作成
        await auth_service.create_admin("testuser", "test1@example.com", "password123")
        
        # 同じユーザー名で作成を試行
        with pytest.raises(ValueError, match="このユーザー名は既に使用されています"):
            await auth_service.create_admin("testuser", "test2@example.com", "password123")
    
    @pytest.mark.asyncio
    async def test_authenticate_admin(self, auth_service: AuthService):
        """管理者認証テスト"""
        # 管理者を作成
        await auth_service.create_admin("testuser", "test@example.com", "password123")
        
        # 認証テスト
        result = await auth_service.authenticate_admin("testuser", "password123")
        
        assert result is not None
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["admin"]["username"] == "testuser"
    
    @pytest.mark.asyncio
    async def test_authenticate_admin_invalid_password(self, auth_service: AuthService):
        """無効なパスワードでの認証テスト"""
        # 管理者を作成
        await auth_service.create_admin("testuser", "test@example.com", "password123")
        
        # 無効なパスワードで認証
        result = await auth_service.authenticate_admin("testuser", "wrongpassword")
        
        assert result is None

class TestAdminDomain:
    """管理者ドメインモデル テスト"""
    
    def test_create_admin(self):
        """管理者作成テスト"""
        admin = Admin.create("testuser", "test@example.com", "password123")
        
        assert admin.username == "testuser"
        assert str(admin.email) == "test@example.com"
        assert admin.role == "admin"
        assert admin.is_active is True
        assert admin.created_at is not None
    
    def test_create_admin_invalid_email(self):
        """無効なメールアドレスでの管理者作成テスト"""
        with pytest.raises(ValueError, match="無効なメールアドレスです"):
            Admin.create("testuser", "invalid-email", "password123")
    
    def test_create_admin_short_password(self):
        """短いパスワードでの管理者作成テスト"""
        with pytest.raises(ValueError, match="パスワードは8文字以上である必要があります"):
            Admin.create("testuser", "test@example.com", "short")
    
    def test_verify_password(self):
        """パスワード検証テスト"""
        admin = Admin.create("testuser", "test@example.com", "password123")
        
        assert admin.verify_password("password123") is True
        assert admin.verify_password("wrongpassword") is False
    
    def test_change_password(self):
        """パスワード変更テスト"""
        admin = Admin.create("testuser", "test@example.com", "password123")
        old_hash = admin.hashed_password
        
        admin.change_password("newpassword123")
        
        assert admin.hashed_password != old_hash
        assert admin.verify_password("newpassword123") is True
        assert admin.verify_password("password123") is False
    
    def test_login_event(self):
        """ログインイベントテスト"""
        admin = Admin.create("testuser", "test@example.com", "password123")
        
        event = admin.login("192.168.1.1")
        
        assert event.admin_id == admin.id
        assert event.email == "test@example.com"
        assert event.ip_address == "192.168.1.1"
        assert admin.last_login is not None
    
    def test_logout_event(self):
        """ログアウトイベントテスト"""
        admin = Admin.create("testuser", "test@example.com", "password123")
        
        event = admin.logout()
        
        assert event.admin_id == admin.id
        assert event.email == "test@example.com"
        assert event.logout_at is not None