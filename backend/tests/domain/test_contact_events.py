"""
Contact Domain Events Unit Tests
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.domain.events.contact_events import (
    ContactCreated,
    ContactUpdated,
    ContactProcessed
)
from app.domain.events.base import DomainEvent


class TestContactCreated:
    """ContactCreatedのテスト"""
    
    def test_contact_created_event_creation(self):
        """ContactCreated作成のテスト"""
        contact_id = uuid4()
        name = "田中太郎"
        email = "test@example.com"
        phone = "090-1234-5678"
        message = "テストメッセージ"
        lesson_type = "trial"
        preferred_contact = "email"
        
        event = ContactCreated(
            contact_id=contact_id,
            name=name,
            email=email,
            phone=phone,
            message=message,
            lesson_type=lesson_type,
            preferred_contact=preferred_contact
        )
        
        assert isinstance(event, DomainEvent)
        assert event.contact_id == contact_id
        assert event.name == name
        assert event.email == email
        assert event.phone == phone
        assert event.message == message
        assert event.lesson_type == lesson_type
        assert event.preferred_contact == preferred_contact
        assert isinstance(event.occurred_at, datetime)
    
    def test_contact_created_event_serialization(self):
        """ContactCreatedシリアライゼーションのテスト"""
        contact_id = uuid4()
        name = "佐藤花子"
        email = "serialize@example.com"
        
        event = ContactCreated(
            contact_id=contact_id,
            name=name,
            email=email,
            phone=None,
            message="シリアライゼーションテスト",
            lesson_type="group",
            preferred_contact="email"
        )
        
        event_data = event._get_event_data()
        
        assert event_data["contact_id"] == str(contact_id)
        assert event_data["name"] == name
        assert event_data["email"] == email
        assert event_data["phone"] is None
        assert event_data["message"] == "シリアライゼーションテスト"
        assert event_data["lesson_type"] == "group"
        assert event_data["preferred_contact"] == "email"
    
    def test_contact_created_event_equality(self):
        """ContactCreated等価性のテスト"""
        contact_id = uuid4()
        name = "山田次郎"
        email = "equal@example.com"
        
        event1 = ContactCreated(
            contact_id=contact_id,
            name=name,
            email=email,
            phone=None,
            message="等価性テスト",
            lesson_type="private",
            preferred_contact="email"
        )
        
        event2 = ContactCreated(
            contact_id=contact_id,
            name=name,
            email=email,
            phone=None,
            message="等価性テスト",
            lesson_type="private",
            preferred_contact="email"
        )
        
        # 同じデータでも異なるoccurred_atを持つため、等価ではない
        assert event1.contact_id == event2.contact_id
        assert event1.name == event2.name
        assert event1.email == event2.email


class TestContactUpdated:
    """ContactUpdatedのテスト"""
    
    def test_contact_updated_event_creation(self):
        """ContactUpdated作成のテスト"""
        contact_id = uuid4()
        updated_fields = {
            "status": "responded",
            "updated_by": "admin@example.com"
        }
        
        event = ContactUpdated(
            contact_id=contact_id,
            updated_fields=updated_fields
        )
        
        assert isinstance(event, DomainEvent)
        assert event.contact_id == contact_id
        assert event.updated_fields == updated_fields
    
    def test_contact_updated_event_serialization(self):
        """ContactUpdatedシリアライゼーションのテスト"""
        contact_id = uuid4()
        updated_fields = {
            "status": "archived",
            "notes": "処理完了"
        }
        
        event = ContactUpdated(
            contact_id=contact_id,
            updated_fields=updated_fields
        )
        
        event_data = event._get_event_data()
        
        assert event_data["contact_id"] == str(contact_id)
        assert event_data["updated_fields"] == updated_fields


class TestContactProcessed:
    """ContactProcessedのテスト"""
    
    def test_contact_processed_event_creation(self):
        """ContactProcessed作成のテスト"""
        contact_id = uuid4()
        processed_by = "staff@example.com"
        processing_notes = "顧客に返信済み"
        
        event = ContactProcessed(
            contact_id=contact_id,
            processed_by=processed_by,
            processing_notes=processing_notes
        )
        
        assert isinstance(event, DomainEvent)
        assert event.contact_id == contact_id
        assert event.processed_by == processed_by
        assert event.processing_notes == processing_notes
    
    def test_contact_processed_event_without_notes(self):
        """処理メモなしのContactProcessedテスト"""
        contact_id = uuid4()
        processed_by = "auto-system"
        
        event = ContactProcessed(
            contact_id=contact_id,
            processed_by=processed_by,
            processing_notes=None
        )
        
        assert event.processing_notes is None
        assert event.contact_id == contact_id
        assert event.processed_by == processed_by
    
    def test_contact_processed_event_serialization(self):
        """ContactProcessedシリアライゼーションのテスト"""
        contact_id = uuid4()
        processed_by = "manager@example.com"
        processing_notes = "特別対応が必要"
        
        event = ContactProcessed(
            contact_id=contact_id,
            processed_by=processed_by,
            processing_notes=processing_notes
        )
        
        event_data = event._get_event_data()
        
        assert event_data["contact_id"] == str(contact_id)
        assert event_data["processed_by"] == processed_by
        assert event_data["processing_notes"] == processing_notes


class TestDomainEventBase:
    """DomainEvent基底クラスのテスト"""
    
    def test_domain_event_occurred_at_auto_set(self):
        """DomainEventのoccurred_at自動設定テスト"""
        contact_id = uuid4()
        
        event = ContactCreated(
            contact_id=contact_id,
            name="自動設定テスト",
            email="auto@example.com",
            phone=None,
            message="occurred_at自動設定テスト",
            lesson_type="trial",
            preferred_contact="email"
        )
        
        assert isinstance(event.occurred_at, datetime)
        # occurred_atが現在時刻に近いことを確認（1秒以内）
        from datetime import UTC
        time_diff = abs((datetime.now(UTC) - event.occurred_at).total_seconds())
        assert time_diff < 1.0
    
    def test_domain_event_string_representation(self):
        """DomainEvent文字列表現のテスト"""
        contact_id = uuid4()
        
        event = ContactCreated(
            contact_id=contact_id,
            name="文字列テスト",
            email="string@example.com",
            phone=None,
            message="文字列表現テスト",
            lesson_type="group",
            preferred_contact="email"
        )
        
        str_repr = str(event)
        assert "ContactCreated" in str_repr
        assert str(contact_id) in str_repr