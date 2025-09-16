"""
Contact API Endpoints Unit Tests

Given-When-Then形式でContact APIエンドポイントのテストを実装
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from httpx import AsyncClient

from app.domain.entities.contact import Contact, ContactStatus, LessonType, PreferredContact
from app.services.contact_service import ContactService


class TestContactCreateEndpoint:
    """Contact作成エンドポイントのテスト"""
    
    @pytest.mark.asyncio
    async def test_create_contact_with_valid_data(self, client: AsyncClient):
        """
        Given: 有効な問い合わせデータが提供される
        When: POST /contacts/ エンドポイントを呼び出す
        Then: 201ステータスで問い合わせが作成される
        """
        # Given: 有効な問い合わせデータが提供される
        valid_contact_data = {
            "name": "田中太郎",
            "email": "tanaka@example.com",
            "phone": "090-1234-5678",
            "lesson_type": "trial",
            "preferred_contact": "email",
            "message": "体験レッスンについて質問があります"
        }
        
        # ContactServiceをモック化
        with patch('app.api.endpoints.contact.get_contact_service') as mock_get_service:
            mock_service = AsyncMock(spec=ContactService)
            mock_contact = Contact.create(
                name=valid_contact_data["name"],
                email=valid_contact_data["email"],
                message=valid_contact_data["message"],
                lesson_type=valid_contact_data["lesson_type"],
                preferred_contact=valid_contact_data["preferred_contact"],
                phone=valid_contact_data["phone"]
            )
            mock_service.create_contact.return_value = mock_contact
            mock_get_service.return_value = mock_service
            
            # When: POST /api/v1/contacts/ エンドポイントを呼び出す
            response = await client.post("/api/v1/contacts/", json=valid_contact_data)
            
            # Then: 201ステータスで問い合わせが作成される
            assert response.status_code == 201
            
            response_data = response.json()
            assert response_data["message"] == "お問い合わせを受け付けました。"
            assert "contact_id" in response_data
            assert response_data["contact_id"] == str(mock_contact.id)
            
            # Then: ContactServiceのcreate_contactが呼び出される
            mock_service.create_contact.assert_called_once_with(
                name=valid_contact_data["name"],
                email=valid_contact_data["email"],
                phone=valid_contact_data["phone"],
                lesson_type=valid_contact_data["lesson_type"],
                preferred_contact=valid_contact_data["preferred_contact"],
                message=valid_contact_data["message"]
            )
    
    @pytest.mark.asyncio
    async def test_create_contact_without_phone(self, client: AsyncClient):
        """
        Given: 電話番号なしの有効な問い合わせデータが提供される
        When: POST /contacts/ エンドポイントを呼び出す
        Then: 201ステータスで問い合わせが作成される
        """
        # Given: 電話番号なしの有効な問い合わせデータが提供される
        contact_data_without_phone = {
            "name": "佐藤花子",
            "email": "sato@example.com",
            "lesson_type": "group",
            "preferred_contact": "email",
            "message": "グループレッスンに興味があります"
        }
        
        # ContactServiceをモック化
        with patch('app.api.endpoints.contact.get_contact_service') as mock_get_service:
            mock_service = AsyncMock(spec=ContactService)
            mock_contact = Contact.create(
                name=contact_data_without_phone["name"],
                email=contact_data_without_phone["email"],
                message=contact_data_without_phone["message"],
                lesson_type=contact_data_without_phone["lesson_type"],
                preferred_contact=contact_data_without_phone["preferred_contact"],
                phone=None
            )
            mock_service.create_contact.return_value = mock_contact
            mock_get_service.return_value = mock_service
            
            # When: POST /api/v1/contacts/ エンドポイントを呼び出す
            response = await client.post("/api/v1/contacts/", json=contact_data_without_phone)
            
            # Then: 201ステータスで問い合わせが作成される
            assert response.status_code == 201
            
            response_data = response.json()
            assert response_data["message"] == "お問い合わせを受け付けました。"
            assert "contact_id" in response_data
            
            # Then: ContactServiceのcreate_contactが電話番号Noneで呼び出される
            mock_service.create_contact.assert_called_once_with(
                name=contact_data_without_phone["name"],
                email=contact_data_without_phone["email"],
                phone=None,
                lesson_type=contact_data_without_phone["lesson_type"],
                preferred_contact=contact_data_without_phone["preferred_contact"],
                message=contact_data_without_phone["message"]
            )
    
    @pytest.mark.asyncio
    async def test_create_contact_with_missing_required_fields(self, client: AsyncClient):
        """
        Given: 必須フィールドが不足している問い合わせデータが提供される
        When: POST /contacts/ エンドポイントを呼び出す
        Then: 422ステータスでバリデーションエラーが返される
        """
        # Given: 必須フィールドが不足している問い合わせデータが提供される
        incomplete_data = {
            "name": "山田次郎",
            # email, lesson_type, preferred_contact, messageが不足
        }
        
        # When: POST /api/v1/contacts/ エンドポイントを呼び出す
        response = await client.post("/api/v1/contacts/", json=incomplete_data)
        
        # Then: 422ステータスでバリデーションエラーが返される
        assert response.status_code == 422
        
        response_data = response.json()
        assert "detail" in response_data
        
        # Then: 不足しているフィールドのエラーが含まれる
        error_fields = [error["loc"][-1] for error in response_data["detail"]]
        assert "email" in error_fields
        assert "lesson_type" in error_fields
        assert "preferred_contact" in error_fields
        assert "message" in error_fields
    
    @pytest.mark.asyncio
    async def test_create_contact_with_invalid_email(self, client: AsyncClient):
        """
        Given: 無効なメールアドレスを含む問い合わせデータが提供される
        When: POST /contacts/ エンドポイントを呼び出す
        Then: 422ステータスでバリデーションエラーが返される
        """
        # Given: 無効なメールアドレスを含む問い合わせデータが提供される
        invalid_email_data = {
            "name": "鈴木一郎",
            "email": "invalid-email",
            "lesson_type": "private",
            "preferred_contact": "email",
            "message": "テストメッセージ"
        }
        
        # When: POST /api/v1/contacts/ エンドポイントを呼び出す
        response = await client.post("/api/v1/contacts/", json=invalid_email_data)
        
        # Then: 422ステータスでバリデーションエラーが返される
        assert response.status_code == 422
        
        response_data = response.json()
        assert "detail" in response_data
        
        # Then: メールアドレスのバリデーションエラーが含まれる
        email_errors = [
            error for error in response_data["detail"] 
            if error["loc"][-1] == "email"
        ]
        assert len(email_errors) > 0
    
    @pytest.mark.asyncio
    async def test_create_contact_with_invalid_lesson_type(self, client: AsyncClient):
        """
        Given: 無効なレッスンタイプを含む問い合わせデータが提供される
        When: POST /contacts/ エンドポイントを呼び出す
        Then: 422ステータスでバリデーションエラーが返される
        """
        # Given: 無効なレッスンタイプを含む問い合わせデータが提供される
        invalid_lesson_type_data = {
            "name": "高橋美咲",
            "email": "takahashi@example.com",
            "lesson_type": "invalid_type",
            "preferred_contact": "email",
            "message": "テストメッセージ"
        }
        
        # When: POST /api/v1/contacts/ エンドポイントを呼び出す
        response = await client.post("/api/v1/contacts/", json=invalid_lesson_type_data)
        
        # Then: 422ステータスでバリデーションエラーが返される
        assert response.status_code == 422
        
        response_data = response.json()
        assert "detail" in response_data
        
        # Then: レッスンタイプのバリデーションエラーが含まれる
        lesson_type_errors = [
            error for error in response_data["detail"] 
            if error["loc"][-1] == "lesson_type"
        ]
        assert len(lesson_type_errors) > 0
    
    @pytest.mark.asyncio
    async def test_create_contact_with_too_long_name(self, client: AsyncClient):
        """
        Given: 長すぎる名前を含む問い合わせデータが提供される
        When: POST /contacts/ エンドポイントを呼び出す
        Then: 422ステータスでバリデーションエラーが返される
        """
        # Given: 長すぎる名前を含む問い合わせデータが提供される
        long_name_data = {
            "name": "あ" * 101,  # 101文字（制限は100文字）
            "email": "longname@example.com",
            "lesson_type": "trial",
            "preferred_contact": "email",
            "message": "テストメッセージ"
        }
        
        # When: POST /api/v1/contacts/ エンドポイントを呼び出す
        response = await client.post("/api/v1/contacts/", json=long_name_data)
        
        # Then: 422ステータスでバリデーションエラーが返される
        assert response.status_code == 422
        
        response_data = response.json()
        assert "detail" in response_data
        
        # Then: 名前の長さのバリデーションエラーが含まれる
        name_errors = [
            error for error in response_data["detail"] 
            if error["loc"][-1] == "name"
        ]
        assert len(name_errors) > 0
    
    @pytest.mark.asyncio
    async def test_create_contact_with_too_long_message(self, client: AsyncClient):
        """
        Given: 長すぎるメッセージを含む問い合わせデータが提供される
        When: POST /contacts/ エンドポイントを呼び出す
        Then: 422ステータスでバリデーションエラーが返される
        """
        # Given: 長すぎるメッセージを含む問い合わせデータが提供される
        long_message_data = {
            "name": "伊藤健太",
            "email": "ito@example.com",
            "lesson_type": "group",
            "preferred_contact": "email",
            "message": "あ" * 1001  # 1001文字（制限は1000文字）
        }
        
        # When: POST /api/v1/contacts/ エンドポイントを呼び出す
        response = await client.post("/api/v1/contacts/", json=long_message_data)
        
        # Then: 422ステータスでバリデーションエラーが返される
        assert response.status_code == 422
        
        response_data = response.json()
        assert "detail" in response_data
        
        # Then: メッセージの長さのバリデーションエラーが含まれる
        message_errors = [
            error for error in response_data["detail"] 
            if error["loc"][-1] == "message"
        ]
        assert len(message_errors) > 0
    
    @pytest.mark.asyncio
    async def test_create_contact_service_value_error(self, client: AsyncClient):
        """
        Given: ContactServiceがValueErrorを発生させる状況が存在する
        When: POST /contacts/ エンドポイントを呼び出す
        Then: 400ステータスでエラーメッセージが返される
        """
        # Given: ContactServiceがValueErrorを発生させる状況が存在する
        valid_contact_data = {
            "name": "渡辺直子",
            "email": "watanabe@example.com",
            "lesson_type": "trial",
            "preferred_contact": "email",
            "message": "テストメッセージ"
        }
        
        # ContactServiceをモック化（ValueErrorを発生させる）
        with patch('app.api.endpoints.contact.get_contact_service') as mock_get_service:
            mock_service = AsyncMock(spec=ContactService)
            mock_service.create_contact.side_effect = ValueError("無効なメールアドレス形式です")
            mock_get_service.return_value = mock_service
            
            # When: POST /api/v1/contacts/ エンドポイントを呼び出す
            response = await client.post("/api/v1/contacts/", json=valid_contact_data)
            
            # Then: 400ステータスでエラーメッセージが返される
            assert response.status_code == 400
            
            response_data = response.json()
            assert "detail" in response_data
            assert "入力データが無効です" in response_data["detail"]
            assert "無効なメールアドレス形式です" in response_data["detail"]
    
    @pytest.mark.asyncio
    async def test_create_contact_service_general_error(self, client: AsyncClient):
        """
        Given: ContactServiceが一般的な例外を発生させる状況が存在する
        When: POST /contacts/ エンドポイントを呼び出す
        Then: 500ステータスでエラーメッセージが返される
        """
        # Given: ContactServiceが一般的な例外を発生させる状況が存在する
        valid_contact_data = {
            "name": "中村雅子",
            "email": "nakamura@example.com",
            "lesson_type": "private",
            "preferred_contact": "email",
            "message": "テストメッセージ"
        }
        
        # ContactServiceをモック化（一般的な例外を発生させる）
        with patch('app.api.endpoints.contact.get_contact_service') as mock_get_service:
            mock_service = AsyncMock(spec=ContactService)
            mock_service.create_contact.side_effect = Exception("Database connection error")
            mock_get_service.return_value = mock_service
            
            # When: POST /api/v1/contacts/ エンドポイントを呼び出す
            response = await client.post("/api/v1/contacts/", json=valid_contact_data)
            
            # Then: 500ステータスでエラーメッセージが返される
            assert response.status_code == 500
            
            response_data = response.json()
            assert "detail" in response_data
            assert "問い合わせの作成に失敗しました" in response_data["detail"]


class TestContactGetEndpoint:
    """Contact取得エンドポイントのテスト"""
    
    @pytest.mark.asyncio
    async def test_get_contact_existing_contact(self, client: AsyncClient):
        """
        Given: 存在するContactのIDが提供される
        When: GET /contacts/{contact_id} エンドポイントを呼び出す
        Then: 200ステータスでContactの詳細が返される
        """
        # Given: 存在するContactのIDが提供される
        contact_id = uuid4()
        existing_contact = Contact.create(
            name="小林健一",
            email="kobayashi@example.com",
            message="オンラインレッスンについて",
            lesson_type="online",
            preferred_contact="email",
            phone="070-1111-2222"
        )
        existing_contact.id = contact_id
        
        # ContactServiceをモック化
        with patch('app.api.endpoints.contact.get_contact_service') as mock_get_service:
            mock_service = AsyncMock(spec=ContactService)
            mock_service.get_contact_by_id.return_value = existing_contact
            mock_get_service.return_value = mock_service
            
            # When: GET /api/v1/contacts/{contact_id} エンドポイントを呼び出す
            response = await client.get(f"/api/v1/contacts/{contact_id}")
            
            # Then: 200ステータスでContactの詳細が返される
            assert response.status_code == 200
            
            response_data = response.json()
            assert response_data["id"] == str(contact_id)
            assert response_data["name"] == "小林健一"
            assert response_data["email"] == "kobayashi@example.com"
            assert response_data["phone"] == "07011112222"  # 正規化された形式
            assert response_data["lesson_type"] == "online"
            assert response_data["preferred_contact"] == "email"
            assert response_data["message"] == "オンラインレッスンについて"
            assert response_data["status"] == "pending"
            assert "created_at" in response_data
            
            # Then: ContactServiceのget_contact_by_idが呼び出される
            mock_service.get_contact_by_id.assert_called_once_with(contact_id)
    
    @pytest.mark.asyncio
    async def test_get_contact_without_phone(self, client: AsyncClient):
        """
        Given: 電話番号なしの存在するContactのIDが提供される
        When: GET /contacts/{contact_id} エンドポイントを呼び出す
        Then: 200ステータスでContactの詳細が返される（電話番号はnull）
        """
        # Given: 電話番号なしの存在するContactのIDが提供される
        contact_id = uuid4()
        existing_contact = Contact.create(
            name="加藤美香",
            email="kato@example.com",
            message="グループレッスンについて",
            lesson_type="group",
            preferred_contact="email",
            phone=None
        )
        existing_contact.id = contact_id
        
        # ContactServiceをモック化
        with patch('app.api.endpoints.contact.get_contact_service') as mock_get_service:
            mock_service = AsyncMock(spec=ContactService)
            mock_service.get_contact_by_id.return_value = existing_contact
            mock_get_service.return_value = mock_service
            
            # When: GET /api/v1/contacts/{contact_id} エンドポイントを呼び出す
            response = await client.get(f"/api/v1/contacts/{contact_id}")
            
            # Then: 200ステータスでContactの詳細が返される（電話番号はnull）
            assert response.status_code == 200
            
            response_data = response.json()
            assert response_data["id"] == str(contact_id)
            assert response_data["name"] == "加藤美香"
            assert response_data["email"] == "kato@example.com"
            assert response_data["phone"] is None
            assert response_data["lesson_type"] == "group"
            assert response_data["preferred_contact"] == "email"
            assert response_data["message"] == "グループレッスンについて"
    
    @pytest.mark.asyncio
    async def test_get_contact_nonexistent_contact(self, client: AsyncClient):
        """
        Given: 存在しないContactのIDが提供される
        When: GET /contacts/{contact_id} エンドポイントを呼び出す
        Then: 404ステータスでエラーメッセージが返される
        """
        # Given: 存在しないContactのIDが提供される
        nonexistent_id = uuid4()
        
        # ContactServiceをモック化（Noneを返す）
        with patch('app.api.endpoints.contact.get_contact_service') as mock_get_service:
            mock_service = AsyncMock(spec=ContactService)
            mock_service.get_contact_by_id.return_value = None
            mock_get_service.return_value = mock_service
            
            # When: GET /api/v1/contacts/{contact_id} エンドポイントを呼び出す
            response = await client.get(f"/api/v1/contacts/{nonexistent_id}")
            
            # Then: 404ステータスでエラーメッセージが返される
            assert response.status_code == 404
            
            response_data = response.json()
            assert "detail" in response_data
            assert "指定された問い合わせが見つかりません" in response_data["detail"]
            
            # Then: ContactServiceのget_contact_by_idが呼び出される
            mock_service.get_contact_by_id.assert_called_once_with(nonexistent_id)
    
    @pytest.mark.asyncio
    async def test_get_contact_invalid_uuid(self, client: AsyncClient):
        """
        Given: 無効なUUID形式のIDが提供される
        When: GET /contacts/{contact_id} エンドポイントを呼び出す
        Then: 422ステータスでバリデーションエラーが返される
        """
        # Given: 無効なUUID形式のIDが提供される
        invalid_id = "invalid-uuid"
        
        # When: GET /api/v1/contacts/{contact_id} エンドポイントを呼び出す
        response = await client.get(f"/api/v1/contacts/{invalid_id}")
        
        # Then: 422ステータスでバリデーションエラーが返される
        assert response.status_code == 422
        
        response_data = response.json()
        assert "detail" in response_data
        
        # Then: UUIDのバリデーションエラーが含まれる
        uuid_errors = [
            error for error in response_data["detail"] 
            if "contact_id" in str(error["loc"])
        ]
        assert len(uuid_errors) > 0
    
    @pytest.mark.asyncio
    async def test_get_contact_service_error(self, client: AsyncClient):
        """
        Given: ContactServiceが例外を発生させる状況が存在する
        When: GET /contacts/{contact_id} エンドポイントを呼び出す
        Then: 500ステータスでエラーメッセージが返される
        """
        # Given: ContactServiceが例外を発生させる状況が存在する
        contact_id = uuid4()
        
        # ContactServiceをモック化（例外を発生させる）
        with patch('app.api.endpoints.contact.get_contact_service') as mock_get_service:
            mock_service = AsyncMock(spec=ContactService)
            mock_service.get_contact_by_id.side_effect = Exception("Database connection error")
            mock_get_service.return_value = mock_service
            
            # When: GET /api/v1/contacts/{contact_id} エンドポイントを呼び出す
            response = await client.get(f"/api/v1/contacts/{contact_id}")
            
            # Then: 500ステータスでエラーメッセージが返される
            assert response.status_code == 500
            
            response_data = response.json()
            assert "detail" in response_data
            assert "問い合わせの取得に失敗しました" in response_data["detail"]


class TestContactEndpointsEdgeCases:
    """Contact APIエンドポイントのエッジケースのテスト"""
    
    @pytest.mark.asyncio
    async def test_create_contact_with_special_characters(self, client: AsyncClient):
        """
        Given: 特殊文字を含む問い合わせデータが提供される
        When: POST /contacts/ エンドポイントを呼び出す
        Then: 201ステータスで問い合わせが作成される
        """
        # Given: 特殊文字を含む問い合わせデータが提供される
        special_char_data = {
            "name": "田中 太郎（Mr.）",
            "email": "tanaka+test@example.com",
            "phone": "090-1234-5678",
            "lesson_type": "trial",
            "preferred_contact": "email",
            "message": "こんにちは！\n英語のレッスンについて質問があります。\n\n詳細を教えてください。"
        }
        
        # ContactServiceをモック化
        with patch('app.api.endpoints.contact.get_contact_service') as mock_get_service:
            mock_service = AsyncMock(spec=ContactService)
            mock_contact = Contact.create(
                name=special_char_data["name"],
                email=special_char_data["email"],
                message=special_char_data["message"],
                lesson_type=special_char_data["lesson_type"],
                preferred_contact=special_char_data["preferred_contact"],
                phone=special_char_data["phone"]
            )
            mock_service.create_contact.return_value = mock_contact
            mock_get_service.return_value = mock_service
            
            # When: POST /api/v1/contacts/ エンドポイントを呼び出す
            response = await client.post("/api/v1/contacts/", json=special_char_data)
            
            # Then: 201ステータスで問い合わせが作成される
            assert response.status_code == 201
            
            response_data = response.json()
            assert response_data["message"] == "お問い合わせを受け付けました。"
            assert "contact_id" in response_data
    
    @pytest.mark.asyncio
    async def test_create_contact_with_maximum_length_fields(self, client: AsyncClient):
        """
        Given: 最大長のフィールドを含む問い合わせデータが提供される
        When: POST /contacts/ エンドポイントを呼び出す
        Then: 201ステータスで問い合わせが作成される
        """
        # Given: 最大長のフィールドを含む問い合わせデータが提供される
        max_length_data = {
            "name": "あ" * 100,  # 最大長100文字
            "email": "maxlength@example.com",
            "phone": "090-1234-5678",  # 有効な電話番号
            "lesson_type": "private",
            "preferred_contact": "email",
            "message": "あ" * 1000  # 最大長1000文字
        }
        
        # ContactServiceをモック化
        with patch('app.api.endpoints.contact.get_contact_service') as mock_get_service:
            mock_service = AsyncMock(spec=ContactService)
            mock_contact = Contact.create(
                name=max_length_data["name"],
                email=max_length_data["email"],
                message=max_length_data["message"],
                lesson_type=max_length_data["lesson_type"],
                preferred_contact=max_length_data["preferred_contact"],
                phone=max_length_data["phone"]
            )
            mock_service.create_contact.return_value = mock_contact
            mock_get_service.return_value = mock_service
            
            # When: POST /api/v1/contacts/ エンドポイントを呼び出す
            response = await client.post("/api/v1/contacts/", json=max_length_data)
            
            # Then: 201ステータスで問い合わせが作成される
            assert response.status_code == 201
            
            response_data = response.json()
            assert response_data["message"] == "お問い合わせを受け付けました。"
            assert "contact_id" in response_data
    
    @pytest.mark.asyncio
    async def test_create_contact_with_all_lesson_types(self, client: AsyncClient):
        """
        Given: 全てのレッスンタイプが順次提供される
        When: POST /contacts/ エンドポイントを呼び出す
        Then: 全てのレッスンタイプで201ステータスで問い合わせが作成される
        """
        # Given: 全てのレッスンタイプが順次提供される
        lesson_types = ["group", "private", "online", "trial"]
        
        for lesson_type in lesson_types:
            contact_data = {
                "name": f"テスト{lesson_type}",
                "email": f"{lesson_type}@example.com",
                "lesson_type": lesson_type,
                "preferred_contact": "email",
                "message": f"{lesson_type}レッスンについて"
            }
            
            # ContactServiceをモック化
            with patch('app.api.endpoints.contact.get_contact_service') as mock_get_service:
                mock_service = AsyncMock(spec=ContactService)
                mock_contact = Contact.create(
                    name=contact_data["name"],
                    email=contact_data["email"],
                    message=contact_data["message"],
                    lesson_type=contact_data["lesson_type"],
                    preferred_contact=contact_data["preferred_contact"]
                )
                mock_service.create_contact.return_value = mock_contact
                mock_get_service.return_value = mock_service
                
                # When: POST /api/v1/contacts/ エンドポイントを呼び出す
                response = await client.post("/api/v1/contacts/", json=contact_data)
                
                # Then: 201ステータスで問い合わせが作成される
                assert response.status_code == 201, f"Failed for lesson_type: {lesson_type}"
                
                response_data = response.json()
                assert response_data["message"] == "お問い合わせを受け付けました。"
                assert "contact_id" in response_data
    
    @pytest.mark.asyncio
    async def test_create_contact_with_all_preferred_contacts(self, client: AsyncClient):
        """
        Given: 全ての希望連絡方法が順次提供される
        When: POST /contacts/ エンドポイントを呼び出す
        Then: 全ての希望連絡方法で201ステータスで問い合わせが作成される
        """
        # Given: 全ての希望連絡方法が順次提供される
        preferred_contacts = ["email", "phone", "either"]
        
        for preferred_contact in preferred_contacts:
            contact_data = {
                "name": f"テスト{preferred_contact}",
                "email": f"{preferred_contact}@example.com",
                "lesson_type": "trial",
                "preferred_contact": preferred_contact,
                "message": f"{preferred_contact}での連絡希望"
            }
            
            # ContactServiceをモック化
            with patch('app.api.endpoints.contact.get_contact_service') as mock_get_service:
                mock_service = AsyncMock(spec=ContactService)
                mock_contact = Contact.create(
                    name=contact_data["name"],
                    email=contact_data["email"],
                    message=contact_data["message"],
                    lesson_type=contact_data["lesson_type"],
                    preferred_contact=contact_data["preferred_contact"]
                )
                mock_service.create_contact.return_value = mock_contact
                mock_get_service.return_value = mock_service
                
                # When: POST /api/v1/contacts/ エンドポイントを呼び出す
                response = await client.post("/api/v1/contacts/", json=contact_data)
                
                # Then: 201ステータスで問い合わせが作成される
                assert response.status_code == 201, f"Failed for preferred_contact: {preferred_contact}"
                
                response_data = response.json()
                assert response_data["message"] == "お問い合わせを受け付けました。"
                assert "contact_id" in response_data