"""
Database Models Unit Tests
"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.contact import ContactModel
from app.domain.entities.contact import Contact, ContactStatus, LessonType, PreferredContact
from app.domain.value_objects.email import Email
from app.domain.value_objects.phone import Phone


class TestContactModel:
    """ContactModelのテスト"""
    
    async def test_contact_model_creation(self, async_session: AsyncSession):
        """ContactModel作成のテスト"""
        contact_model = ContactModel(
            name="田中太郎",
            email="tanaka@example.com",
            message="テストメッセージ",
            phone="09012345678",
            lesson_type="trial",
            preferred_contact="email",
            status="pending"
        )
        
        async_session.add(contact_model)
        await async_session.commit()
        await async_session.refresh(contact_model)
        
        assert contact_model.id is not None
        assert contact_model.name == "田中太郎"
        assert contact_model.email == "tanaka@example.com"
        assert contact_model.message == "テストメッセージ"
        assert contact_model.phone == "09012345678"
        assert contact_model.lesson_type == "trial"
        assert contact_model.preferred_contact == "email"
        assert contact_model.status == "pending"
        assert isinstance(contact_model.created_at, datetime)
        assert isinstance(contact_model.updated_at, datetime)
    
    async def test_contact_model_without_phone(self, async_session: AsyncSession):
        """電話番号なしのContactModel作成テスト"""
        contact_model = ContactModel(
            name="佐藤花子",
            email="sato@example.com",
            message="電話番号なしのテスト",
            lesson_type="group",
            preferred_contact="email",
            status="pending"
        )
        
        async_session.add(contact_model)
        await async_session.commit()
        await async_session.refresh(contact_model)
        
        assert contact_model.phone is None
        assert contact_model.name == "佐藤花子"
    
    async def test_contact_model_to_domain_entity(self, async_session: AsyncSession):
        """ContactModelからドメインエンティティへの変換テスト"""
        contact_model = ContactModel(
            name="山田次郎",
            email="yamada@example.com",
            message="ドメイン変換テスト",
            phone="08012345678",
            lesson_type="private",
            preferred_contact="phone",
            status="responded"
        )
        
        async_session.add(contact_model)
        await async_session.commit()
        await async_session.refresh(contact_model)
        
        # ドメインエンティティに変換
        domain_contact = Contact(
            id=contact_model.id,
            name=contact_model.name,
            email=Email.create(contact_model.email),
            message=contact_model.message,
            phone=Phone.create(contact_model.phone) if contact_model.phone else None,
            lesson_type=LessonType(contact_model.lesson_type),
            preferred_contact=PreferredContact(contact_model.preferred_contact),
            status=ContactStatus(contact_model.status),
            created_at=contact_model.created_at,
            updated_at=contact_model.updated_at
        )
        
        assert domain_contact.id == contact_model.id
        assert domain_contact.name == contact_model.name
        assert str(domain_contact.email) == contact_model.email
        assert domain_contact.message == contact_model.message
        assert str(domain_contact.phone) == contact_model.phone
        assert domain_contact.lesson_type.value == contact_model.lesson_type
        assert domain_contact.preferred_contact.value == contact_model.preferred_contact
        assert domain_contact.status.value == contact_model.status
    
    async def test_contact_model_update(self, async_session: AsyncSession):
        """ContactModel更新のテスト"""
        contact_model = ContactModel(
            name="更新テスト",
            email="update@example.com",
            message="更新前のメッセージ",
            status="pending"
        )
        
        async_session.add(contact_model)
        await async_session.commit()
        await async_session.refresh(contact_model)
        
        original_updated_at = contact_model.updated_at
        
        # 更新
        contact_model.status = "responded"
        contact_model.message = "更新後のメッセージ"
        
        await async_session.commit()
        await async_session.refresh(contact_model)
        
        assert contact_model.status == "responded"
        assert contact_model.message == "更新後のメッセージ"
        assert contact_model.updated_at > original_updated_at
    
    async def test_contact_model_query(self, async_session: AsyncSession):
        """ContactModelクエリのテスト"""
        # テストデータ作成
        contacts = [
            ContactModel(
                name=f"テストユーザー{i}",
                email=f"test{i}@example.com",
                message=f"テストメッセージ{i}",
                status="pending" if i % 2 == 0 else "responded"
            )
            for i in range(5)
        ]
        
        for contact in contacts:
            async_session.add(contact)
        await async_session.commit()
        
        # 全件取得
        from sqlalchemy import select
        result = await async_session.execute(select(ContactModel))
        all_contacts = result.scalars().all()
        assert len(all_contacts) == 5
        
        # ステータス別取得
        result = await async_session.execute(
            select(ContactModel).where(ContactModel.status == "pending")
        )
        pending_contacts = result.scalars().all()
        assert len(pending_contacts) == 3  # 0, 2, 4
        
        # メールアドレスで検索
        result = await async_session.execute(
            select(ContactModel).where(ContactModel.email == "test1@example.com")
        )
        specific_contact = result.scalar_one_or_none()
        assert specific_contact is not None
        assert specific_contact.name == "テストユーザー1"