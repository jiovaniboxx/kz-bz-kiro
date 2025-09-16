"""
Contact Entity Unit Tests

Given-When-Then形式でContactエンティティのテストを実装
"""

import pytest
from datetime import datetime, UTC
from uuid import UUID, uuid4

from app.domain.entities.contact import (
    Contact,
    LessonType,
    PreferredContact,
    ContactStatus
)
from app.domain.events.contact_events import (
    ContactCreated,
    ContactUpdated,
    ContactProcessed
)
from app.domain.value_objects.email import Email
from app.domain.value_objects.phone import Phone


class TestContactCreation:
    """Contact作成のテスト"""
    
    def test_create_contact_with_valid_data(self):
        """
        Given: 有効な問い合わせデータが提供される
        When: Contactエンティティを作成する
        Then: 正しいContactエンティティが作成され、ContactCreatedイベントが発行される
        """
        # Given: 有効な問い合わせデータが提供される
        name = "田中太郎"
        email = "tanaka@example.com"
        message = "英会話レッスンについて質問があります"
        lesson_type = "trial"
        preferred_contact = "email"
        phone = "090-1234-5678"
        
        # When: Contactエンティティを作成する
        contact = Contact.create(
            name=name,
            email=email,
            message=message,
            lesson_type=lesson_type,
            preferred_contact=preferred_contact,
            phone=phone
        )
        
        # Then: 正しいContactエンティティが作成される
        assert isinstance(contact.id, UUID)
        assert contact.name == name
        assert str(contact.email) == email
        assert str(contact.phone) == "09012345678"  # 正規化された形式
        assert contact.message == message
        assert contact.lesson_type == LessonType.TRIAL
        assert contact.preferred_contact == PreferredContact.EMAIL
        assert contact.status == ContactStatus.PENDING
        assert isinstance(contact.created_at, datetime)
        assert isinstance(contact.updated_at, datetime)
        
        # Then: ContactCreatedイベントが発行される
        events = contact.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ContactCreated)
        assert events[0].contact_id == contact.id
        assert events[0].name == name
        assert events[0].email == email
    
    def test_create_contact_without_phone(self):
        """
        Given: 電話番号なしの有効な問い合わせデータが提供される
        When: Contactエンティティを作成する
        Then: 電話番号なしのContactエンティティが作成される
        """
        # Given: 電話番号なしの有効な問い合わせデータが提供される
        name = "佐藤花子"
        email = "sato@example.com"
        message = "グループレッスンに興味があります"
        lesson_type = "group"
        preferred_contact = "email"
        
        # When: Contactエンティティを作成する
        contact = Contact.create(
            name=name,
            email=email,
            message=message,
            lesson_type=lesson_type,
            preferred_contact=preferred_contact,
            phone=None
        )
        
        # Then: 電話番号なしのContactエンティティが作成される
        assert contact.name == name
        assert str(contact.email) == email
        assert contact.phone is None
        assert contact.lesson_type == LessonType.GROUP
        assert contact.preferred_contact == PreferredContact.EMAIL
    
    def test_create_contact_with_invalid_email(self):
        """
        Given: 無効なメールアドレスが提供される
        When: Contactエンティティを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: 無効なメールアドレスが提供される
        name = "山田次郎"
        invalid_email = "invalid-email"
        message = "テストメッセージ"
        lesson_type = "private"
        preferred_contact = "email"
        
        # When & Then: Contactエンティティを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="無効なメールアドレス形式です"):
            Contact.create(
                name=name,
                email=invalid_email,
                message=message,
                lesson_type=lesson_type,
                preferred_contact=preferred_contact
            )
    
    def test_create_contact_with_empty_name(self):
        """
        Given: 空の名前が提供される
        When: Contactエンティティを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: 空の名前が提供される
        empty_name = ""
        email = "test@example.com"
        message = "テストメッセージ"
        lesson_type = "trial"
        preferred_contact = "email"
        
        # When & Then: Contactエンティティを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="名前は必須です"):
            Contact.create(
                name=empty_name,
                email=email,
                message=message,
                lesson_type=lesson_type,
                preferred_contact=preferred_contact
            )
    
    def test_create_contact_with_invalid_lesson_type(self):
        """
        Given: 無効なレッスンタイプが提供される
        When: Contactエンティティを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: 無効なレッスンタイプが提供される
        name = "鈴木一郎"
        email = "suzuki@example.com"
        message = "テストメッセージ"
        invalid_lesson_type = "invalid_type"
        preferred_contact = "email"
        
        # When & Then: Contactエンティティを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="無効なレッスンタイプです"):
            Contact.create(
                name=name,
                email=email,
                message=message,
                lesson_type=invalid_lesson_type,
                preferred_contact=preferred_contact
            )


class TestContactStatusUpdate:
    """Contactステータス更新のテスト"""
    
    def test_update_status_to_processing(self):
        """
        Given: 未処理状態のContactが存在する
        When: ステータスを処理中に更新する
        Then: ステータスが更新され、ContactUpdatedイベントが発行される
        """
        # Given: 未処理状態のContactが存在する
        contact = Contact.create(
            name="田中太郎",
            email="tanaka@example.com",
            message="テストメッセージ",
            lesson_type="trial",
            preferred_contact="email"
        )
        contact.clear_domain_events()  # 作成イベントをクリア
        original_updated_at = contact.updated_at
        
        # When: ステータスを処理中に更新する
        contact.update_status(ContactStatus.PROCESSING)
        
        # Then: ステータスが更新される
        assert contact.status == ContactStatus.PROCESSING
        assert contact.updated_at > original_updated_at
        
        # Then: ContactUpdatedイベントが発行される
        events = contact.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ContactUpdated)
        assert events[0].contact_id == contact.id
        assert events[0].updated_fields['status']['old'] == ContactStatus.PENDING.value
        assert events[0].updated_fields['status']['new'] == ContactStatus.PROCESSING.value
    
    def test_update_status_to_completed(self):
        """
        Given: 処理中状態のContactが存在する
        When: ステータスを完了に更新する
        Then: ステータスが更新され、ContactUpdatedイベントが発行される
        """
        # Given: 処理中状態のContactが存在する
        contact = Contact.create(
            name="佐藤花子",
            email="sato@example.com",
            message="テストメッセージ",
            lesson_type="group",
            preferred_contact="email"
        )
        contact.update_status(ContactStatus.PROCESSING)
        contact.clear_domain_events()  # 既存イベントをクリア
        
        # When: ステータスを完了に更新する
        contact.update_status(ContactStatus.COMPLETED)
        
        # Then: ステータスが更新される
        assert contact.status == ContactStatus.COMPLETED
        
        # Then: ContactUpdatedイベントが発行される
        events = contact.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ContactUpdated)
        assert events[0].updated_fields['status']['old'] == ContactStatus.PROCESSING.value
        assert events[0].updated_fields['status']['new'] == ContactStatus.COMPLETED.value


class TestContactProcessing:
    """Contact処理のテスト"""
    
    def test_process_contact_with_notes(self):
        """
        Given: 未処理状態のContactが存在する
        When: 処理メモ付きで問い合わせを処理する
        Then: 処理済み状態になり、ContactProcessedイベントが発行される
        """
        # Given: 未処理状態のContactが存在する
        contact = Contact.create(
            name="山田次郎",
            email="yamada@example.com",
            message="プライベートレッスンについて",
            lesson_type="private",
            preferred_contact="phone",
            phone="080-9876-5432"
        )
        contact.clear_domain_events()  # 作成イベントをクリア
        
        # When: 処理メモ付きで問い合わせを処理する
        processed_by = "staff@example.com"
        notes = "顧客に詳細資料を送付済み"
        contact.process(processed_by, notes)
        
        # Then: 処理済み状態になる
        assert contact.status == ContactStatus.COMPLETED
        assert contact.processed_by == processed_by
        assert contact.processing_notes == notes
        assert contact.processed_at is not None
        assert isinstance(contact.processed_at, datetime)
        
        # Then: ContactProcessedイベントが発行される
        events = contact.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ContactProcessed)
        assert events[0].contact_id == contact.id
        assert events[0].processed_by == processed_by
        assert events[0].processing_notes == notes
    
    def test_process_contact_without_notes(self):
        """
        Given: 未処理状態のContactが存在する
        When: 処理メモなしで問い合わせを処理する
        Then: 処理済み状態になり、処理メモはNoneになる
        """
        # Given: 未処理状態のContactが存在する
        contact = Contact.create(
            name="鈴木一郎",
            email="suzuki@example.com",
            message="オンラインレッスンについて",
            lesson_type="online",
            preferred_contact="email"
        )
        contact.clear_domain_events()  # 作成イベントをクリア
        
        # When: 処理メモなしで問い合わせを処理する
        processed_by = "admin@example.com"
        contact.process(processed_by)
        
        # Then: 処理済み状態になり、処理メモはNoneになる
        assert contact.status == ContactStatus.COMPLETED
        assert contact.processed_by == processed_by
        assert contact.processing_notes is None
        assert contact.processed_at is not None


class TestContactInfoUpdate:
    """Contact情報更新のテスト"""
    
    def test_update_contact_name(self):
        """
        Given: Contactが存在する
        When: 名前を更新する
        Then: 名前が更新され、ContactUpdatedイベントが発行される
        """
        # Given: Contactが存在する
        contact = Contact.create(
            name="田中太郎",
            email="tanaka@example.com",
            message="テストメッセージ",
            lesson_type="trial",
            preferred_contact="email"
        )
        contact.clear_domain_events()  # 作成イベントをクリア
        old_name = contact.name
        
        # When: 名前を更新する
        new_name = "田中花子"
        contact.update_contact_info(name=new_name)
        
        # Then: 名前が更新される
        assert contact.name == new_name
        
        # Then: ContactUpdatedイベントが発行される
        events = contact.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ContactUpdated)
        assert events[0].updated_fields['name']['old'] == old_name
        assert events[0].updated_fields['name']['new'] == new_name
    
    def test_update_contact_email(self):
        """
        Given: Contactが存在する
        When: メールアドレスを更新する
        Then: メールアドレスが更新され、ContactUpdatedイベントが発行される
        """
        # Given: Contactが存在する
        contact = Contact.create(
            name="佐藤花子",
            email="sato@example.com",
            message="テストメッセージ",
            lesson_type="group",
            preferred_contact="email"
        )
        contact.clear_domain_events()  # 作成イベントをクリア
        old_email = str(contact.email)
        
        # When: メールアドレスを更新する
        new_email = "sato.hanako@example.com"
        contact.update_contact_info(email=new_email)
        
        # Then: メールアドレスが更新される
        assert str(contact.email) == new_email
        
        # Then: ContactUpdatedイベントが発行される
        events = contact.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ContactUpdated)
        assert events[0].updated_fields['email']['old'] == old_email
        assert events[0].updated_fields['email']['new'] == new_email
    
    def test_update_contact_multiple_fields(self):
        """
        Given: Contactが存在する
        When: 複数のフィールドを同時に更新する
        Then: 全てのフィールドが更新され、1つのContactUpdatedイベントが発行される
        """
        # Given: Contactが存在する
        contact = Contact.create(
            name="山田次郎",
            email="yamada@example.com",
            message="元のメッセージ",
            lesson_type="private",
            preferred_contact="email",
            phone="090-1111-2222"
        )
        contact.clear_domain_events()  # 作成イベントをクリア
        
        # When: 複数のフィールドを同時に更新する
        new_name = "山田太郎"
        new_email = "yamada.taro@example.com"
        new_message = "更新されたメッセージ"
        contact.update_contact_info(
            name=new_name,
            email=new_email,
            message=new_message
        )
        
        # Then: 全てのフィールドが更新される
        assert contact.name == new_name
        assert str(contact.email) == new_email
        assert contact.message == new_message
        
        # Then: 1つのContactUpdatedイベントが発行される
        events = contact.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ContactUpdated)
        assert 'name' in events[0].updated_fields
        assert 'email' in events[0].updated_fields
        assert 'message' in events[0].updated_fields
    
    def test_update_contact_with_same_values(self):
        """
        Given: Contactが存在する
        When: 同じ値で更新しようとする
        Then: 何も変更されず、イベントも発行されない
        """
        # Given: Contactが存在する
        contact = Contact.create(
            name="鈴木一郎",
            email="suzuki@example.com",
            message="テストメッセージ",
            lesson_type="trial",
            preferred_contact="email"
        )
        contact.clear_domain_events()  # 作成イベントをクリア
        original_updated_at = contact.updated_at
        
        # When: 同じ値で更新しようとする
        contact.update_contact_info(
            name=contact.name,
            email=str(contact.email),
            message=contact.message
        )
        
        # Then: 何も変更されず、イベントも発行されない
        assert contact.updated_at == original_updated_at
        events = contact.get_domain_events()
        assert len(events) == 0


class TestContactBusinessLogic:
    """Contactビジネスロジックのテスト"""
    
    def test_is_pending_when_status_is_pending(self):
        """
        Given: 未処理状態のContactが存在する
        When: is_pending()を呼び出す
        Then: Trueが返される
        """
        # Given: 未処理状態のContactが存在する
        contact = Contact.create(
            name="田中太郎",
            email="tanaka@example.com",
            message="テストメッセージ",
            lesson_type="trial",
            preferred_contact="email"
        )
        
        # When & Then: is_pending()を呼び出すとTrueが返される
        assert contact.is_pending() is True
    
    def test_is_pending_when_status_is_not_pending(self):
        """
        Given: 処理中状態のContactが存在する
        When: is_pending()を呼び出す
        Then: Falseが返される
        """
        # Given: 処理中状態のContactが存在する
        contact = Contact.create(
            name="佐藤花子",
            email="sato@example.com",
            message="テストメッセージ",
            lesson_type="group",
            preferred_contact="email"
        )
        contact.update_status(ContactStatus.PROCESSING)
        
        # When & Then: is_pending()を呼び出すとFalseが返される
        assert contact.is_pending() is False
    
    def test_is_completed_when_status_is_completed(self):
        """
        Given: 完了状態のContactが存在する
        When: is_completed()を呼び出す
        Then: Trueが返される
        """
        # Given: 完了状態のContactが存在する
        contact = Contact.create(
            name="山田次郎",
            email="yamada@example.com",
            message="テストメッセージ",
            lesson_type="private",
            preferred_contact="email"
        )
        contact.process("staff@example.com")
        
        # When & Then: is_completed()を呼び出すとTrueが返される
        assert contact.is_completed() is True
    
    def test_can_be_processed_when_pending(self):
        """
        Given: 未処理状態のContactが存在する
        When: can_be_processed()を呼び出す
        Then: Trueが返される
        """
        # Given: 未処理状態のContactが存在する
        contact = Contact.create(
            name="鈴木一郎",
            email="suzuki@example.com",
            message="テストメッセージ",
            lesson_type="online",
            preferred_contact="email"
        )
        
        # When & Then: can_be_processed()を呼び出すとTrueが返される
        assert contact.can_be_processed() is True
    
    def test_can_be_processed_when_processing(self):
        """
        Given: 処理中状態のContactが存在する
        When: can_be_processed()を呼び出す
        Then: Trueが返される
        """
        # Given: 処理中状態のContactが存在する
        contact = Contact.create(
            name="高橋美咲",
            email="takahashi@example.com",
            message="テストメッセージ",
            lesson_type="trial",
            preferred_contact="email"
        )
        contact.update_status(ContactStatus.PROCESSING)
        
        # When & Then: can_be_processed()を呼び出すとTrueが返される
        assert contact.can_be_processed() is True
    
    def test_can_be_processed_when_completed(self):
        """
        Given: 完了状態のContactが存在する
        When: can_be_processed()を呼び出す
        Then: Falseが返される
        """
        # Given: 完了状態のContactが存在する
        contact = Contact.create(
            name="伊藤健太",
            email="ito@example.com",
            message="テストメッセージ",
            lesson_type="group",
            preferred_contact="email"
        )
        contact.process("admin@example.com")
        
        # When & Then: can_be_processed()を呼び出すとFalseが返される
        assert contact.can_be_processed() is False


class TestContactDomainEvents:
    """Contactドメインイベントのテスト"""
    
    def test_domain_events_accumulation(self):
        """
        Given: Contactが存在する
        When: 複数の操作を実行する
        Then: 全てのドメインイベントが蓄積される
        """
        # Given: Contactが存在する
        contact = Contact.create(
            name="渡辺直子",
            email="watanabe@example.com",
            message="テストメッセージ",
            lesson_type="trial",
            preferred_contact="email"
        )
        
        # When: 複数の操作を実行する
        contact.update_status(ContactStatus.PROCESSING)
        contact.update_contact_info(name="渡辺花子")
        contact.process("staff@example.com", "処理完了")
        
        # Then: 全てのドメインイベントが蓄積される
        events = contact.get_domain_events()
        assert len(events) == 4  # Created, Updated(status), Updated(name), Processed
        
        event_types = [type(event).__name__ for event in events]
        assert "ContactCreated" in event_types
        assert "ContactUpdated" in event_types
        assert "ContactProcessed" in event_types
    
    def test_clear_domain_events(self):
        """
        Given: ドメインイベントを持つContactが存在する
        When: clear_domain_events()を呼び出す
        Then: 全てのドメインイベントがクリアされる
        """
        # Given: ドメインイベントを持つContactが存在する
        contact = Contact.create(
            name="中村雅子",
            email="nakamura@example.com",
            message="テストメッセージ",
            lesson_type="group",
            preferred_contact="email"
        )
        contact.update_status(ContactStatus.PROCESSING)
        
        # 初期状態でイベントが存在することを確認
        assert len(contact.get_domain_events()) > 0
        
        # When: clear_domain_events()を呼び出す
        contact.clear_domain_events()
        
        # Then: 全てのドメインイベントがクリアされる
        assert len(contact.get_domain_events()) == 0


class TestContactStringRepresentation:
    """Contact文字列表現のテスト"""
    
    def test_str_representation(self):
        """
        Given: Contactが存在する
        When: str()で文字列化する
        Then: 適切な文字列表現が返される
        """
        # Given: Contactが存在する
        contact = Contact.create(
            name="小林健一",
            email="kobayashi@example.com",
            message="テストメッセージ",
            lesson_type="private",
            preferred_contact="email"
        )
        
        # When: str()で文字列化する
        str_repr = str(contact)
        
        # Then: 適切な文字列表現が返される
        assert "Contact(" in str_repr
        assert str(contact.id) in str_repr
        assert "小林健一" in str_repr
        assert "pending" in str_repr
    
    def test_repr_representation(self):
        """
        Given: Contactが存在する
        When: repr()でデバッグ用文字列化する
        Then: 適切なデバッグ用文字列表現が返される
        """
        # Given: Contactが存在する
        contact = Contact.create(
            name="加藤美香",
            email="kato@example.com",
            message="テストメッセージ",
            lesson_type="online",
            preferred_contact="email"
        )
        
        # When: repr()でデバッグ用文字列化する
        repr_str = repr(contact)
        
        # Then: 適切なデバッグ用文字列表現が返される
        assert "Contact(" in repr_str
        assert str(contact.id) in repr_str
        assert "加藤美香" in repr_str
        assert "kato@example.com" in repr_str
        assert "pending" in repr_str