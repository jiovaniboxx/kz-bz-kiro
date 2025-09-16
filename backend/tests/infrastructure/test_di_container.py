"""
Dependency Injection Container Unit Tests
"""

import pytest
from unittest.mock import AsyncMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.di.container import Container
from app.services.contact_service import ContactService
from app.services.email_service import EmailService
from app.infrastructure.repositories.sqlalchemy_contact_repository import SQLAlchemyContactRepository
from app.infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus
from app.infrastructure.event_bus.event_bus import EventBus


class TestContainer:
    """Containerのテスト"""
    
    def test_container_initialization(self):
        """コンテナ初期化のテスト"""
        container = Container()
        
        assert container is not None
        assert hasattr(container, '_services')
    
    async def test_setup_database_services(self):
        """データベースサービス設定のテスト"""
        container = Container()
        mock_session = AsyncMock(spec=AsyncSession)
        
        await container.setup_database_services(mock_session)
        
        # リポジトリが設定されているか確認
        contact_repo = container.contact_repository()
        assert isinstance(contact_repo, SQLAlchemyContactRepository)
    
    async def test_get_contact_service(self):
        """ContactService取得のテスト"""
        container = Container()
        mock_session = AsyncMock(spec=AsyncSession)
        
        await container.setup_database_services(mock_session)
        
        contact_service = container.contact_service()
        assert isinstance(contact_service, ContactService)
        
        # 同じインスタンスが返されることを確認（シングルトン）
        contact_service2 = container.contact_service()
        assert contact_service is contact_service2
    
    async def test_get_email_service(self):
        """EmailService取得のテスト"""
        container = Container()
        mock_session = AsyncMock(spec=AsyncSession)
        
        # データベースサービスをセットアップしてからEmailServiceを取得
        await container.setup_database_services(mock_session)
        
        email_service = container.email_service()
        assert isinstance(email_service, EmailService)
        
        # 同じインスタンスが返されることを確認（シングルトン）
        email_service2 = container.email_service()
        assert email_service is email_service2
    
    async def test_get_event_bus(self):
        """EventBus取得のテスト"""
        container = Container()
        
        event_bus = container.get(EventBus)
        assert isinstance(event_bus, InMemoryEventBus)
        
        # 同じインスタンスが返されることを確認（シングルトン）
        event_bus2 = container.get(EventBus)
        assert event_bus is event_bus2
    
    async def test_get_contact_repository(self):
        """ContactRepository取得のテスト"""
        container = Container()
        mock_session = AsyncMock(spec=AsyncSession)
        
        await container.setup_database_services(mock_session)
        
        contact_repo = container.contact_repository()
        assert isinstance(contact_repo, SQLAlchemyContactRepository)
        
        # 同じインスタンスが返されることを確認（シングルトン）
        contact_repo2 = container.contact_repository()
        assert contact_repo is contact_repo2
    
    async def test_service_dependencies(self):
        """サービス間の依存関係のテスト"""
        container = Container()
        mock_session = AsyncMock(spec=AsyncSession)
        
        await container.setup_database_services(mock_session)
        
        contact_service = container.contact_service()
        
        # ContactServiceが正しい依存関係を持っているか確認
        assert hasattr(contact_service, 'contact_repository')
        assert hasattr(contact_service, 'email_service')
        
        # 依存関係が正しいインスタンスか確認
        assert contact_service.contact_repository == container.contact_repository()
        assert contact_service.email_service == container.email_service()
    
    def test_container_register_and_get(self):
        """コンテナ登録・取得のテスト"""
        container = Container()
        
        # モックサービスを登録
        mock_email_service = Mock(spec=EmailService)
        container.register(EmailService, mock_email_service)
        
        # 登録されたサービスが取得できることを確認
        assert container.get(EmailService) == mock_email_service
        assert container.is_registered(EmailService) is True
    
    def test_container_service_not_found(self):
        """未登録サービス取得のテスト"""
        container = Container()
        
        # 未登録のサービスタイプ
        class UnknownService:
            pass
        
        # KeyErrorが発生することを確認
        with pytest.raises(KeyError):
            container.get(UnknownService)
        
        assert container.is_registered(UnknownService) is False