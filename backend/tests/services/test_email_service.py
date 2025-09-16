"""
Email Service Unit Tests

Given-When-Then形式でEmailServiceのテストを実装
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import smtplib
from email.mime.multipart import MIMEMultipart

from app.domain.entities.contact import Contact, LessonType, PreferredContact
from app.domain.value_objects.email import Email
from app.domain.value_objects.phone import Phone
from app.services.email_service import SMTPEmailService, MockEmailService


class TestSMTPEmailService:
    """SMTPEmailServiceのテスト"""
    
    @pytest.fixture
    def smtp_email_service(self):
        """SMTPEmailServiceインスタンスを作成"""
        return SMTPEmailService(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="test@example.com",
            smtp_password="password",
            from_email="noreply@english-cafe.com",
            admin_email="admin@english-cafe.com"
        )
    
    @pytest.fixture
    def sample_contact(self):
        """テスト用のContactを作成"""
        return Contact.create(
            name="田中太郎",
            email="tanaka@example.com",
            message="体験レッスンについて質問があります",
            lesson_type="trial",
            preferred_contact="email",
            phone="090-1234-5678"
        )
    
    @pytest.mark.asyncio
    async def test_send_contact_notification_success(
        self, 
        smtp_email_service, 
        sample_contact
    ):
        """
        Given: 有効なContactが提供される
        When: send_contact_notificationメソッドを呼び出す
        Then: 管理者に通知メールが送信される
        """
        # Given: 有効なContactが提供される（sample_contactフィクスチャ）
        
        # SMTPサーバーをモック化
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # When: send_contact_notificationメソッドを呼び出す
            result = await smtp_email_service.send_contact_notification(sample_contact)
            
            # Then: 管理者に通知メールが送信される
            assert result is True
            
            # Then: SMTPサーバーが正しく呼び出される
            mock_smtp.assert_called_once_with("smtp.example.com", 587)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("test@example.com", "password")
            mock_server.send_message.assert_called_once()
            
            # Then: 送信されたメッセージの内容を確認
            sent_message = mock_server.send_message.call_args[0][0]
            assert sent_message['To'] == "admin@english-cafe.com"
            assert sent_message['From'] == "noreply@english-cafe.com"
            assert "新しいお問い合わせ" in sent_message['Subject']
            assert "田中太郎" in sent_message['Subject']
    
    @pytest.mark.asyncio
    async def test_send_contact_notification_smtp_failure(
        self, 
        smtp_email_service, 
        sample_contact
    ):
        """
        Given: SMTPサーバーが利用できない状況が存在する
        When: send_contact_notificationメソッドを呼び出す
        Then: Falseが返される
        """
        # Given: SMTPサーバーが利用できない状況が存在する
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = smtplib.SMTPException("Connection failed")
            
            # When: send_contact_notificationメソッドを呼び出す
            result = await smtp_email_service.send_contact_notification(sample_contact)
            
            # Then: Falseが返される
            assert result is False
    
    @pytest.mark.asyncio
    async def test_send_contact_confirmation_success(
        self, 
        smtp_email_service, 
        sample_contact
    ):
        """
        Given: 有効なContactが提供される
        When: send_contact_confirmationメソッドを呼び出す
        Then: 顧客に確認メールが送信される
        """
        # Given: 有効なContactが提供される（sample_contactフィクスチャ）
        
        # SMTPサーバーをモック化
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # When: send_contact_confirmationメソッドを呼び出す
            result = await smtp_email_service.send_contact_confirmation(sample_contact)
            
            # Then: 顧客に確認メールが送信される
            assert result is True
            
            # Then: SMTPサーバーが正しく呼び出される
            mock_smtp.assert_called_once_with("smtp.example.com", 587)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("test@example.com", "password")
            mock_server.send_message.assert_called_once()
            
            # Then: 送信されたメッセージの内容を確認
            sent_message = mock_server.send_message.call_args[0][0]
            assert sent_message['To'] == "tanaka@example.com"
            assert sent_message['From'] == "noreply@english-cafe.com"
            assert "お問い合わせありがとうございます" in sent_message['Subject']
    
    @pytest.mark.asyncio
    async def test_send_contact_confirmation_smtp_failure(
        self, 
        smtp_email_service, 
        sample_contact
    ):
        """
        Given: SMTPサーバーでエラーが発生する状況が存在する
        When: send_contact_confirmationメソッドを呼び出す
        Then: Falseが返される
        """
        # Given: SMTPサーバーでエラーが発生する状況が存在する
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            mock_server.send_message.side_effect = smtplib.SMTPException("Send failed")
            
            # When: send_contact_confirmationメソッドを呼び出す
            result = await smtp_email_service.send_contact_confirmation(sample_contact)
            
            # Then: Falseが返される
            assert result is False
    
    def test_create_notification_body_with_phone(self, smtp_email_service):
        """
        Given: 電話番号付きのContactが提供される
        When: _create_notification_bodyメソッドを呼び出す
        Then: 電話番号を含む通知メール本文が作成される
        """
        # Given: 電話番号付きのContactが提供される
        contact = Contact.create(
            name="佐藤花子",
            email="sato@example.com",
            message="グループレッスンについて詳しく知りたいです",
            lesson_type="group",
            preferred_contact="phone",
            phone="080-9876-5432"
        )
        
        # When: _create_notification_bodyメソッドを呼び出す
        body = smtp_email_service._create_notification_body(contact)
        
        # Then: 電話番号を含む通知メール本文が作成される
        assert "佐藤花子" in body
        assert "sato@example.com" in body
        assert "080-9876-5432" in body
        assert "グループレッスン" in body
        assert "電話" in body
        assert "グループレッスンについて詳しく知りたいです" in body
        assert str(contact.id) in body
    
    def test_create_notification_body_without_phone(self, smtp_email_service):
        """
        Given: 電話番号なしのContactが提供される
        When: _create_notification_bodyメソッドを呼び出す
        Then: 電話番号を含まない通知メール本文が作成される
        """
        # Given: 電話番号なしのContactが提供される
        contact = Contact.create(
            name="山田次郎",
            email="yamada@example.com",
            message="プライベートレッスンの料金について",
            lesson_type="private",
            preferred_contact="email",
            phone=None
        )
        
        # When: _create_notification_bodyメソッドを呼び出す
        body = smtp_email_service._create_notification_body(contact)
        
        # Then: 電話番号を含まない通知メール本文が作成される
        assert "山田次郎" in body
        assert "yamada@example.com" in body
        assert "電話番号:" not in body
        assert "プライベートレッスン" in body
        assert "メール" in body
        assert "プライベートレッスンの料金について" in body
    
    def test_create_confirmation_body(self, smtp_email_service):
        """
        Given: Contactが提供される
        When: _create_confirmation_bodyメソッドを呼び出す
        Then: 適切な確認メール本文が作成される
        """
        # Given: Contactが提供される
        contact = Contact.create(
            name="鈴木一郎",
            email="suzuki@example.com",
            message="オンラインレッスンに興味があります",
            lesson_type="trial",
            preferred_contact="email"
        )
        
        # When: _create_confirmation_bodyメソッドを呼び出す
        body = smtp_email_service._create_confirmation_body(contact)
        
        # Then: 適切な確認メール本文が作成される
        assert "鈴木一郎 様" in body
        assert "体験レッスン" in body
        assert "オンラインレッスンに興味があります" in body
        assert "2営業日以内" in body
        assert "英会話カフェ" in body
        assert "03-1234-5678" in body
        assert "info@english-cafe.com" in body


class TestMockEmailService:
    """MockEmailServiceのテスト"""
    
    @pytest.fixture
    def mock_email_service(self):
        """MockEmailServiceインスタンスを作成"""
        return MockEmailService()
    
    @pytest.fixture
    def sample_contact(self):
        """テスト用のContactを作成"""
        return Contact.create(
            name="高橋美咲",
            email="takahashi@example.com",
            message="ビジネス英語について",
            lesson_type="private",
            preferred_contact="email",
            phone="070-1111-2222"
        )
    
    @pytest.mark.asyncio
    async def test_send_contact_notification_mock(
        self, 
        mock_email_service, 
        sample_contact
    ):
        """
        Given: MockEmailServiceとContactが提供される
        When: send_contact_notificationメソッドを呼び出す
        Then: モック通知メールが記録される
        """
        # Given: MockEmailServiceとContactが提供される（フィクスチャ）
        
        # When: send_contact_notificationメソッドを呼び出す
        result = await mock_email_service.send_contact_notification(sample_contact)
        
        # Then: モック通知メールが記録される
        assert result is True
        assert len(mock_email_service.sent_emails) == 1
        
        sent_email = mock_email_service.sent_emails[0]
        assert sent_email["type"] == "notification"
        assert sent_email["contact_id"] == str(sample_contact.id)
        assert sent_email["to"] == "admin@english-cafe.com"
    
    @pytest.mark.asyncio
    async def test_send_contact_confirmation_mock(
        self, 
        mock_email_service, 
        sample_contact
    ):
        """
        Given: MockEmailServiceとContactが提供される
        When: send_contact_confirmationメソッドを呼び出す
        Then: モック確認メールが記録される
        """
        # Given: MockEmailServiceとContactが提供される（フィクスチャ）
        
        # When: send_contact_confirmationメソッドを呼び出す
        result = await mock_email_service.send_contact_confirmation(sample_contact)
        
        # Then: モック確認メールが記録される
        assert result is True
        assert len(mock_email_service.sent_emails) == 1
        
        sent_email = mock_email_service.sent_emails[0]
        assert sent_email["type"] == "confirmation"
        assert sent_email["contact_id"] == str(sample_contact.id)
        assert sent_email["to"] == "takahashi@example.com"
    
    @pytest.mark.asyncio
    async def test_multiple_email_sending_mock(
        self, 
        mock_email_service, 
        sample_contact
    ):
        """
        Given: MockEmailServiceとContactが提供される
        When: 複数のメール送信メソッドを呼び出す
        Then: 全てのメールが記録される
        """
        # Given: MockEmailServiceとContactが提供される（フィクスチャ）
        
        # When: 複数のメール送信メソッドを呼び出す
        notification_result = await mock_email_service.send_contact_notification(sample_contact)
        confirmation_result = await mock_email_service.send_contact_confirmation(sample_contact)
        
        # Then: 全てのメールが記録される
        assert notification_result is True
        assert confirmation_result is True
        assert len(mock_email_service.sent_emails) == 2
        
        # Then: 通知メールが記録されている
        notification_email = next(
            email for email in mock_email_service.sent_emails 
            if email["type"] == "notification"
        )
        assert notification_email["contact_id"] == str(sample_contact.id)
        assert notification_email["to"] == "admin@english-cafe.com"
        
        # Then: 確認メールが記録されている
        confirmation_email = next(
            email for email in mock_email_service.sent_emails 
            if email["type"] == "confirmation"
        )
        assert confirmation_email["contact_id"] == str(sample_contact.id)
        assert confirmation_email["to"] == "takahashi@example.com"
    
    def test_mock_email_service_initialization(self):
        """
        Given: MockEmailServiceを初期化する
        When: インスタンスを作成する
        Then: 空のメールリストで初期化される
        """
        # Given & When: MockEmailServiceを初期化する
        service = MockEmailService()
        
        # Then: 空のメールリストで初期化される
        assert isinstance(service.sent_emails, list)
        assert len(service.sent_emails) == 0


class TestEmailServiceEdgeCases:
    """EmailServiceエッジケースのテスト"""
    
    @pytest.fixture
    def smtp_email_service(self):
        """SMTPEmailServiceインスタンスを作成"""
        return SMTPEmailService(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="test@example.com",
            smtp_password="password",
            from_email="noreply@english-cafe.com",
            admin_email="admin@english-cafe.com"
        )
    
    def test_create_notification_body_with_special_characters(self, smtp_email_service):
        """
        Given: 特殊文字を含むContactが提供される
        When: _create_notification_bodyメソッドを呼び出す
        Then: 特殊文字が適切に処理された本文が作成される
        """
        # Given: 特殊文字を含むContactが提供される
        contact = Contact.create(
            name="田中 太郎（Mr.）",
            email="tanaka+test@example.com",
            message="こんにちは！\n英語のレッスンについて質問があります。\n\n詳細を教えてください。",
            lesson_type="trial",
            preferred_contact="email",
            phone="090-1234-5678"
        )
        
        # When: _create_notification_bodyメソッドを呼び出す
        body = smtp_email_service._create_notification_body(contact)
        
        # Then: 特殊文字が適切に処理された本文が作成される
        assert "田中 太郎（Mr.）" in body
        assert "tanaka+test@example.com" in body
        assert "こんにちは！" in body
        assert "詳細を教えてください。" in body
    
    def test_create_confirmation_body_with_long_message(self, smtp_email_service):
        """
        Given: 長いメッセージを含むContactが提供される
        When: _create_confirmation_bodyメソッドを呼び出す
        Then: 長いメッセージが適切に処理された本文が作成される
        """
        # Given: 長いメッセージを含むContactが提供される
        long_message = "あ" * 1000  # 1000文字の長いメッセージ
        contact = Contact.create(
            name="長文太郎",
            email="longtext@example.com",
            message=long_message,
            lesson_type="group",
            preferred_contact="email"
        )
        
        # When: _create_confirmation_bodyメソッドを呼び出す
        body = smtp_email_service._create_confirmation_body(contact)
        
        # Then: 長いメッセージが適切に処理された本文が作成される
        assert "長文太郎 様" in body
        assert long_message in body
        assert len(body) > 1000  # 長いメッセージが含まれている
    
    @pytest.mark.asyncio
    async def test_send_email_with_authentication_failure(self, smtp_email_service):
        """
        Given: SMTP認証が失敗する状況が存在する
        When: メール送信を試行する
        Then: Falseが返される
        """
        # Given: SMTP認証が失敗する状況が存在する
        contact = Contact.create(
            name="認証失敗",
            email="auth@example.com",
            message="認証テスト",
            lesson_type="trial",
            preferred_contact="email"
        )
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")
            
            # When: メール送信を試行する
            result = await smtp_email_service.send_contact_notification(contact)
            
            # Then: Falseが返される
            assert result is False
    
    @pytest.mark.asyncio
    async def test_send_email_with_network_timeout(self, smtp_email_service):
        """
        Given: ネットワークタイムアウトが発生する状況が存在する
        When: メール送信を試行する
        Then: Falseが返される
        """
        # Given: ネットワークタイムアウトが発生する状況が存在する
        contact = Contact.create(
            name="タイムアウト",
            email="timeout@example.com",
            message="タイムアウトテスト",
            lesson_type="private",
            preferred_contact="email"
        )
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = TimeoutError("Network timeout")
            
            # When: メール送信を試行する
            result = await smtp_email_service.send_contact_confirmation(contact)
            
            # Then: Falseが返される
            assert result is False