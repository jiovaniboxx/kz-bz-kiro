"""
Contact Service Unit Tests

Given-When-Then形式でContactServiceのテストを実装
"""

import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from app.domain.entities.contact import Contact, ContactStatus, LessonType, PreferredContact
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.value_objects.email import Email
from app.domain.value_objects.phone import Phone
from app.services.contact_service import ContactService
from app.services.email_service import MockEmailService


class TestContactServiceCreation:
    """ContactService作成のテスト"""
    
    @pytest.fixture
    def mock_contact_repository(self):
        """モックContactRepositoryを作成"""
        return AsyncMock(spec=ContactRepository)
    
    @pytest.fixture
    def mock_email_service(self):
        """モックEmailServiceを作成"""
        return MockEmailService()
    
    @pytest.fixture
    def contact_service(self, mock_contact_repository, mock_email_service):
        """ContactServiceインスタンスを作成"""
        return ContactService(mock_contact_repository, mock_email_service)
    
    @pytest.mark.asyncio
    async def test_create_contact_with_valid_data(
        self, 
        contact_service, 
        mock_contact_repository, 
        mock_email_service
    ):
        """
        Given: 有効な問い合わせデータが提供される
        When: create_contactメソッドを呼び出す
        Then: Contactが作成され、保存され、メールが送信される
        """
        # Given: 有効な問い合わせデータが提供される
        name = "田中太郎"
        email = "tanaka@example.com"
        phone = "090-1234-5678"
        lesson_type = "trial"
        preferred_contact = "email"
        message = "体験レッスンについて質問があります"
        
        # モックの設定
        saved_contact = Contact.create(
            name=name,
            email=email,
            message=message,
            lesson_type=lesson_type,
            preferred_contact=preferred_contact,
            phone=phone
        )
        mock_contact_repository.save.return_value = saved_contact
        
        # When: create_contactメソッドを呼び出す
        result = await contact_service.create_contact(
            name=name,
            email=email,
            phone=phone,
            lesson_type=lesson_type,
            preferred_contact=preferred_contact,
            message=message
        )
        
        # Then: Contactが作成され、保存される
        assert result is not None
        assert result.name == name
        assert str(result.email) == email
        assert str(result.phone) == "09012345678"  # 正規化された形式
        assert result.lesson_type == LessonType.TRIAL
        assert result.preferred_contact == PreferredContact.EMAIL
        assert result.message == message
        
        # Then: リポジトリのsaveメソッドが呼び出される
        mock_contact_repository.save.assert_called_once()
        
        # Then: メールが送信される
        assert len(mock_email_service.sent_emails) == 2
        notification_email = next(
            email for email in mock_email_service.sent_emails 
            if email["type"] == "notification"
        )
        confirmation_email = next(
            email for email in mock_email_service.sent_emails 
            if email["type"] == "confirmation"
        )
        assert notification_email["to"] == "admin@english-cafe.com"
        assert confirmation_email["to"] == email
    
    @pytest.mark.asyncio
    async def test_create_contact_without_phone(
        self, 
        contact_service, 
        mock_contact_repository, 
        mock_email_service
    ):
        """
        Given: 電話番号なしの有効な問い合わせデータが提供される
        When: create_contactメソッドを呼び出す
        Then: 電話番号なしのContactが作成される
        """
        # Given: 電話番号なしの有効な問い合わせデータが提供される
        name = "佐藤花子"
        email = "sato@example.com"
        phone = None
        lesson_type = "group"
        preferred_contact = "email"
        message = "グループレッスンに興味があります"
        
        # モックの設定
        saved_contact = Contact.create(
            name=name,
            email=email,
            message=message,
            lesson_type=lesson_type,
            preferred_contact=preferred_contact,
            phone=phone
        )
        mock_contact_repository.save.return_value = saved_contact
        
        # When: create_contactメソッドを呼び出す
        result = await contact_service.create_contact(
            name=name,
            email=email,
            phone=phone,
            lesson_type=lesson_type,
            preferred_contact=preferred_contact,
            message=message
        )
        
        # Then: 電話番号なしのContactが作成される
        assert result is not None
        assert result.name == name
        assert str(result.email) == email
        assert result.phone is None
        assert result.lesson_type == LessonType.GROUP
        
        # Then: リポジトリのsaveメソッドが呼び出される
        mock_contact_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_contact_with_invalid_email(
        self, 
        contact_service, 
        mock_contact_repository
    ):
        """
        Given: 無効なメールアドレスが提供される
        When: create_contactメソッドを呼び出す
        Then: ValueErrorが発生する
        """
        # Given: 無効なメールアドレスが提供される
        name = "山田次郎"
        invalid_email = "invalid-email"
        phone = None
        lesson_type = "private"
        preferred_contact = "email"
        message = "テストメッセージ"
        
        # When & Then: create_contactメソッドを呼び出すとValueErrorが発生する
        with pytest.raises(ValueError):
            await contact_service.create_contact(
                name=name,
                email=invalid_email,
                phone=phone,
                lesson_type=lesson_type,
                preferred_contact=preferred_contact,
                message=message
            )
        
        # Then: リポジトリのsaveメソッドは呼び出されない
        mock_contact_repository.save.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_contact_with_invalid_lesson_type(
        self, 
        contact_service, 
        mock_contact_repository
    ):
        """
        Given: 無効なレッスンタイプが提供される
        When: create_contactメソッドを呼び出す
        Then: ValueErrorが発生する
        """
        # Given: 無効なレッスンタイプが提供される
        name = "鈴木一郎"
        email = "suzuki@example.com"
        phone = None
        invalid_lesson_type = "invalid_type"
        preferred_contact = "email"
        message = "テストメッセージ"
        
        # When & Then: create_contactメソッドを呼び出すとValueErrorが発生する
        with pytest.raises(ValueError):
            await contact_service.create_contact(
                name=name,
                email=email,
                phone=phone,
                lesson_type=invalid_lesson_type,
                preferred_contact=preferred_contact,
                message=message
            )
        
        # Then: リポジトリのsaveメソッドは呼び出されない
        mock_contact_repository.save.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_contact_repository_failure(
        self, 
        contact_service, 
        mock_contact_repository, 
        mock_email_service
    ):
        """
        Given: リポジトリの保存が失敗する
        When: create_contactメソッドを呼び出す
        Then: 例外が再発生する
        """
        # Given: リポジトリの保存が失敗する
        name = "高橋美咲"
        email = "takahashi@example.com"
        phone = None
        lesson_type = "trial"
        preferred_contact = "email"
        message = "テストメッセージ"
        
        # モックの設定（例外を発生させる）
        mock_contact_repository.save.side_effect = Exception("Database error")
        
        # When & Then: create_contactメソッドを呼び出すと例外が再発生する
        with pytest.raises(Exception, match="Database error"):
            await contact_service.create_contact(
                name=name,
                email=email,
                phone=phone,
                lesson_type=lesson_type,
                preferred_contact=preferred_contact,
                message=message
            )
        
        # Then: メールは送信されない
        assert len(mock_email_service.sent_emails) == 0


class TestContactServiceRetrieval:
    """ContactService取得のテスト"""
    
    @pytest.fixture
    def mock_contact_repository(self):
        """モックContactRepositoryを作成"""
        return AsyncMock(spec=ContactRepository)
    
    @pytest.fixture
    def mock_email_service(self):
        """モックEmailServiceを作成"""
        return MockEmailService()
    
    @pytest.fixture
    def contact_service(self, mock_contact_repository, mock_email_service):
        """ContactServiceインスタンスを作成"""
        return ContactService(mock_contact_repository, mock_email_service)
    
    @pytest.mark.asyncio
    async def test_get_contact_by_id_existing_contact(
        self, 
        contact_service, 
        mock_contact_repository
    ):
        """
        Given: 存在するContactのIDが提供される
        When: get_contact_by_idメソッドを呼び出す
        Then: 対応するContactが返される
        """
        # Given: 存在するContactのIDが提供される
        contact_id = uuid4()
        existing_contact = Contact.create(
            name="伊藤健太",
            email="ito@example.com",
            message="テストメッセージ",
            lesson_type="group",
            preferred_contact="email"
        )
        existing_contact.id = contact_id
        
        # モックの設定
        mock_contact_repository.find_by_id.return_value = existing_contact
        
        # When: get_contact_by_idメソッドを呼び出す
        result = await contact_service.get_contact_by_id(contact_id)
        
        # Then: 対応するContactが返される
        assert result is not None
        assert result.id == contact_id
        assert result.name == "伊藤健太"
        
        # Then: リポジトリのfind_by_idメソッドが呼び出される
        mock_contact_repository.find_by_id.assert_called_once_with(contact_id)
    
    @pytest.mark.asyncio
    async def test_get_contact_by_id_nonexistent_contact(
        self, 
        contact_service, 
        mock_contact_repository
    ):
        """
        Given: 存在しないContactのIDが提供される
        When: get_contact_by_idメソッドを呼び出す
        Then: Noneが返される
        """
        # Given: 存在しないContactのIDが提供される
        nonexistent_id = uuid4()
        
        # モックの設定
        mock_contact_repository.find_by_id.return_value = None
        
        # When: get_contact_by_idメソッドを呼び出す
        result = await contact_service.get_contact_by_id(nonexistent_id)
        
        # Then: Noneが返される
        assert result is None
        
        # Then: リポジトリのfind_by_idメソッドが呼び出される
        mock_contact_repository.find_by_id.assert_called_once_with(nonexistent_id)
    
    @pytest.mark.asyncio
    async def test_get_contact_by_id_repository_failure(
        self, 
        contact_service, 
        mock_contact_repository
    ):
        """
        Given: リポジトリの取得が失敗する
        When: get_contact_by_idメソッドを呼び出す
        Then: 例外が再発生する
        """
        # Given: リポジトリの取得が失敗する
        contact_id = uuid4()
        
        # モックの設定（例外を発生させる）
        mock_contact_repository.find_by_id.side_effect = Exception("Database connection error")
        
        # When & Then: get_contact_by_idメソッドを呼び出すと例外が再発生する
        with pytest.raises(Exception, match="Database connection error"):
            await contact_service.get_contact_by_id(contact_id)


class TestContactServiceStatusUpdate:
    """ContactServiceステータス更新のテスト"""
    
    @pytest.fixture
    def mock_contact_repository(self):
        """モックContactRepositoryを作成"""
        return AsyncMock(spec=ContactRepository)
    
    @pytest.fixture
    def mock_email_service(self):
        """モックEmailServiceを作成"""
        return MockEmailService()
    
    @pytest.fixture
    def contact_service(self, mock_contact_repository, mock_email_service):
        """ContactServiceインスタンスを作成"""
        return ContactService(mock_contact_repository, mock_email_service)
    
    @pytest.mark.asyncio
    async def test_update_contact_status_to_processing(
        self, 
        contact_service, 
        mock_contact_repository
    ):
        """
        Given: 未処理状態のContactが存在する
        When: ステータスを処理中に更新する
        Then: ステータスが更新され、保存される
        """
        # Given: 未処理状態のContactが存在する
        contact_id = uuid4()
        existing_contact = Contact.create(
            name="渡辺直子",
            email="watanabe@example.com",
            message="テストメッセージ",
            lesson_type="trial",
            preferred_contact="email"
        )
        existing_contact.id = contact_id
        
        # モックの設定
        mock_contact_repository.find_by_id.return_value = existing_contact
        mock_contact_repository.save.return_value = existing_contact
        
        # When: ステータスを処理中に更新する
        result = await contact_service.update_contact_status(
            contact_id=contact_id,
            status=ContactStatus.PROCESSING
        )
        
        # Then: ステータスが更新される
        assert result is not None
        assert result.status == ContactStatus.PROCESSING
        
        # Then: リポジトリのメソッドが呼び出される
        mock_contact_repository.find_by_id.assert_called_once_with(contact_id)
        mock_contact_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_contact_status_to_completed_with_processor(
        self, 
        contact_service, 
        mock_contact_repository
    ):
        """
        Given: 処理中状態のContactが存在する
        When: ステータスを完了に更新し、処理者情報を提供する
        Then: ステータスが完了に更新され、処理者情報が設定される
        """
        # Given: 処理中状態のContactが存在する
        contact_id = uuid4()
        existing_contact = Contact.create(
            name="中村雅子",
            email="nakamura@example.com",
            message="テストメッセージ",
            lesson_type="group",
            preferred_contact="email"
        )
        existing_contact.id = contact_id
        existing_contact.update_status(ContactStatus.PROCESSING)
        
        # モックの設定
        mock_contact_repository.find_by_id.return_value = existing_contact
        mock_contact_repository.save.return_value = existing_contact
        
        # When: ステータスを完了に更新し、処理者情報を提供する
        processed_by = "staff@example.com"
        processing_notes = "顧客に詳細資料を送付済み"
        result = await contact_service.update_contact_status(
            contact_id=contact_id,
            status=ContactStatus.COMPLETED,
            processed_by=processed_by,
            processing_notes=processing_notes
        )
        
        # Then: ステータスが完了に更新され、処理者情報が設定される
        assert result is not None
        assert result.status == ContactStatus.COMPLETED
        assert result.processed_by == processed_by
        assert result.processing_notes == processing_notes
        assert result.processed_at is not None
        
        # Then: リポジトリのメソッドが呼び出される
        mock_contact_repository.find_by_id.assert_called_once_with(contact_id)
        mock_contact_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_contact_status_nonexistent_contact(
        self, 
        contact_service, 
        mock_contact_repository
    ):
        """
        Given: 存在しないContactのIDが提供される
        When: ステータスを更新しようとする
        Then: Noneが返される
        """
        # Given: 存在しないContactのIDが提供される
        nonexistent_id = uuid4()
        
        # モックの設定
        mock_contact_repository.find_by_id.return_value = None
        
        # When: ステータスを更新しようとする
        result = await contact_service.update_contact_status(
            contact_id=nonexistent_id,
            status=ContactStatus.PROCESSING
        )
        
        # Then: Noneが返される
        assert result is None
        
        # Then: find_by_idは呼び出されるが、saveは呼び出されない
        mock_contact_repository.find_by_id.assert_called_once_with(nonexistent_id)
        mock_contact_repository.save.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_update_contact_status_repository_failure(
        self, 
        contact_service, 
        mock_contact_repository
    ):
        """
        Given: リポジトリの保存が失敗する
        When: ステータスを更新しようとする
        Then: 例外が再発生する
        """
        # Given: リポジトリの保存が失敗する
        contact_id = uuid4()
        existing_contact = Contact.create(
            name="小林健一",
            email="kobayashi@example.com",
            message="テストメッセージ",
            lesson_type="private",
            preferred_contact="email"
        )
        existing_contact.id = contact_id
        
        # モックの設定
        mock_contact_repository.find_by_id.return_value = existing_contact
        mock_contact_repository.save.side_effect = Exception("Database update error")
        
        # When & Then: ステータスを更新しようとすると例外が再発生する
        with pytest.raises(Exception, match="Database update error"):
            await contact_service.update_contact_status(
                contact_id=contact_id,
                status=ContactStatus.PROCESSING
            )


class TestContactServiceEmailFailure:
    """ContactServiceメール送信失敗のテスト"""
    
    @pytest.fixture
    def mock_contact_repository(self):
        """モックContactRepositoryを作成"""
        return AsyncMock(spec=ContactRepository)
    
    @pytest.fixture
    def failing_email_service(self):
        """失敗するEmailServiceを作成"""
        email_service = AsyncMock()
        email_service.send_contact_notification.side_effect = Exception("SMTP error")
        email_service.send_contact_confirmation.side_effect = Exception("SMTP error")
        return email_service
    
    @pytest.fixture
    def contact_service(self, mock_contact_repository, failing_email_service):
        """ContactServiceインスタンスを作成"""
        return ContactService(mock_contact_repository, failing_email_service)
    
    @pytest.mark.asyncio
    async def test_create_contact_email_failure_does_not_prevent_creation(
        self, 
        contact_service, 
        mock_contact_repository, 
        failing_email_service
    ):
        """
        Given: メール送信が失敗する環境が存在する
        When: create_contactメソッドを呼び出す
        Then: Contactは作成されるが、メール送信エラーは無視される
        """
        # Given: メール送信が失敗する環境が存在する
        name = "加藤美香"
        email = "kato@example.com"
        phone = None
        lesson_type = "online"
        preferred_contact = "email"
        message = "オンラインレッスンについて"
        
        # モックの設定
        saved_contact = Contact.create(
            name=name,
            email=email,
            message=message,
            lesson_type=lesson_type,
            preferred_contact=preferred_contact,
            phone=phone
        )
        mock_contact_repository.save.return_value = saved_contact
        
        # When: create_contactメソッドを呼び出す
        result = await contact_service.create_contact(
            name=name,
            email=email,
            phone=phone,
            lesson_type=lesson_type,
            preferred_contact=preferred_contact,
            message=message
        )
        
        # Then: Contactは作成される
        assert result is not None
        assert result.name == name
        assert str(result.email) == email
        
        # Then: リポジトリのsaveメソッドが呼び出される
        mock_contact_repository.save.assert_called_once()
        
        # Then: メール送信が試行される（失敗するが例外は発生しない）
        failing_email_service.send_contact_notification.assert_called_once()
        failing_email_service.send_contact_confirmation.assert_called_once()