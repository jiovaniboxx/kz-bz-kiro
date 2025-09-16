"""
Contact Integration Tests

Given-When-Then形式で問い合わせフローの統合テストを実装
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.contact import Contact, ContactStatus
from app.infrastructure.repositories.sqlalchemy_contact_repository import SQLAlchemyContactRepository


class TestContactIntegrationFlow:
    """問い合わせフローの統合テスト"""
    
    @pytest.mark.asyncio
    async def test_complete_contact_submission_flow(
        self, 
        client: AsyncClient, 
        async_session: AsyncSession
    ):
        """
        Given: 有効な問い合わせデータが提供される
        When: 問い合わせ作成APIを呼び出す
        Then: 問い合わせが作成され、データベースに保存され、取得できる
        """
        # Given: 有効な問い合わせデータが提供される
        contact_data = {
            "name": "統合テスト太郎",
            "email": "integration@example.com",
            "phone": "090-1111-2222",
            "lesson_type": "trial",
            "preferred_contact": "email",
            "message": "統合テストのメッセージです"
        }
        
        # When: 問い合わせ作成APIを呼び出す
        create_response = await client.post("/api/v1/contacts/", json=contact_data)
        
        # Then: 問い合わせが作成される
        assert create_response.status_code == 201
        create_data = create_response.json()
        assert create_data["message"] == "お問い合わせを受け付けました。"
        contact_id = create_data["contact_id"]
        
        # Then: 作成された問い合わせを取得できる
        get_response = await client.get(f"/api/v1/contacts/{contact_id}")
        assert get_response.status_code == 200
        
        get_data = get_response.json()
        assert get_data["id"] == contact_id
        assert get_data["name"] == contact_data["name"]
        assert get_data["email"] == contact_data["email"]
        assert get_data["phone"] == "09011112222"  # 正規化された形式
        assert get_data["lesson_type"] == contact_data["lesson_type"]
        assert get_data["preferred_contact"] == contact_data["preferred_contact"]
        assert get_data["message"] == contact_data["message"]
        assert get_data["status"] == "pending"
        assert "created_at" in get_data
        
        # Then: データベースに直接アクセスして確認
        repository = SQLAlchemyContactRepository(async_session)
        saved_contact = await repository.find_by_email("integration@example.com")
        assert saved_contact is not None
        assert saved_contact.name == contact_data["name"]
        assert str(saved_contact.email) == contact_data["email"]
        assert saved_contact.status == ContactStatus.PENDING
    
    @pytest.mark.asyncio
    async def test_contact_submission_without_phone(
        self, 
        client: AsyncClient, 
        async_session: AsyncSession
    ):
        """
        Given: 電話番号なしの有効な問い合わせデータが提供される
        When: 問い合わせ作成APIを呼び出す
        Then: 問い合わせが作成され、電話番号はnullで保存される
        """
        # Given: 電話番号なしの有効な問い合わせデータが提供される
        contact_data = {
            "name": "電話なし太郎",
            "email": "nophone@example.com",
            "lesson_type": "group",
            "preferred_contact": "email",
            "message": "電話番号なしのテストです"
        }
        
        # When: 問い合わせ作成APIを呼び出す
        create_response = await client.post("/api/v1/contacts/", json=contact_data)
        
        # Then: 問い合わせが作成される
        assert create_response.status_code == 201
        contact_id = create_response.json()["contact_id"]
        
        # Then: 作成された問い合わせを取得して電話番号がnullであることを確認
        get_response = await client.get(f"/api/v1/contacts/{contact_id}")
        assert get_response.status_code == 200
        
        get_data = get_response.json()
        assert get_data["phone"] is None
        
        # Then: データベースに直接アクセスして確認
        repository = SQLAlchemyContactRepository(async_session)
        saved_contact = await repository.find_by_email("nophone@example.com")
        assert saved_contact is not None
        assert saved_contact.phone is None
    
    @pytest.mark.asyncio
    async def test_contact_validation_error_flow(self, client: AsyncClient):
        """
        Given: 無効なデータが提供される
        When: 問い合わせ作成APIを呼び出す
        Then: バリデーションエラーが返され、データベースには保存されない
        """
        # Given: 無効なデータが提供される
        invalid_data = {
            "name": "",  # 空の名前
            "email": "invalid-email",  # 無効なメール
            "lesson_type": "invalid_type",  # 無効なレッスンタイプ
            "preferred_contact": "email",
            "message": ""  # 空のメッセージ
        }
        
        # When: 問い合わせ作成APIを呼び出す
        response = await client.post("/api/v1/contacts/", json=invalid_data)
        
        # Then: バリデーションエラーが返される
        assert response.status_code == 422
        
        error_data = response.json()
        assert "detail" in error_data
        
        # Then: エラーの詳細を確認
        errors = error_data["detail"]
        error_fields = [error["loc"][-1] for error in errors]
        assert "name" in error_fields
        assert "email" in error_fields
        assert "lesson_type" in error_fields
        assert "message" in error_fields
    
    @pytest.mark.asyncio
    async def test_nonexistent_contact_retrieval(self, client: AsyncClient):
        """
        Given: 存在しない問い合わせIDが提供される
        When: 問い合わせ取得APIを呼び出す
        Then: 404エラーが返される
        """
        # Given: 存在しない問い合わせIDが提供される
        nonexistent_id = "12345678-1234-1234-1234-123456789012"
        
        # When: 問い合わせ取得APIを呼び出す
        response = await client.get(f"/api/v1/contacts/{nonexistent_id}")
        
        # Then: 404エラーが返される
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data
        assert "指定された問い合わせが見つかりません" in error_data["detail"]


class TestContactDatabaseIntegration:
    """問い合わせデータベース統合テスト"""
    
    @pytest.mark.asyncio
    async def test_contact_repository_integration(self, async_session: AsyncSession):
        """
        Given: ContactRepositoryとデータベースセッションが提供される
        When: Contactエンティティを保存・取得する
        Then: 正しくデータベースに保存され、取得できる
        """
        # Given: ContactRepositoryとデータベースセッションが提供される
        repository = SQLAlchemyContactRepository(async_session)
        
        # Given: 新しいContactエンティティを作成
        contact = Contact.create(
            name="リポジトリテスト",
            email="repository@example.com",
            message="リポジトリ統合テスト",
            lesson_type="private",
            preferred_contact="phone",
            phone="080-3333-4444"
        )
        
        # When: Contactエンティティを保存する
        saved_contact = await repository.save(contact)
        
        # Then: 正しく保存される
        assert saved_contact.id == contact.id
        assert saved_contact.name == contact.name
        assert str(saved_contact.email) == str(contact.email)
        assert saved_contact.status == ContactStatus.PENDING
        
        # When: 保存されたContactを取得する
        retrieved_contact = await repository.find_by_id(contact.id)
        
        # Then: 正しく取得できる
        assert retrieved_contact is not None
        assert retrieved_contact.id == contact.id
        assert retrieved_contact.name == contact.name
        assert str(retrieved_contact.email) == str(contact.email)
        assert str(retrieved_contact.phone) == str(contact.phone)
        assert retrieved_contact.message == contact.message
        assert retrieved_contact.lesson_type == contact.lesson_type
        assert retrieved_contact.preferred_contact == contact.preferred_contact
    
    @pytest.mark.asyncio
    async def test_contact_email_search_integration(self, async_session: AsyncSession):
        """
        Given: 複数のContactがデータベースに保存されている
        When: メールアドレスで検索する
        Then: 正しいContactが取得される
        """
        # Given: 複数のContactがデータベースに保存されている
        repository = SQLAlchemyContactRepository(async_session)
        
        contact1 = Contact.create(
            name="検索テスト1",
            email="search1@example.com",
            message="検索テスト1",
            lesson_type="trial",
            preferred_contact="email"
        )
        
        contact2 = Contact.create(
            name="検索テスト2",
            email="search2@example.com",
            message="検索テスト2",
            lesson_type="group",
            preferred_contact="email"
        )
        
        await repository.save(contact1)
        await repository.save(contact2)
        
        # When: メールアドレスで検索する
        found_contact1 = await repository.find_by_email("search1@example.com")
        found_contact2 = await repository.find_by_email("search2@example.com")
        not_found = await repository.find_by_email("notfound@example.com")
        
        # Then: 正しいContactが取得される
        assert found_contact1 is not None
        assert found_contact1.name == "検索テスト1"
        assert str(found_contact1.email) == "search1@example.com"
        
        assert found_contact2 is not None
        assert found_contact2.name == "検索テスト2"
        assert str(found_contact2.email) == "search2@example.com"
        
        assert not_found is None
    
    @pytest.mark.asyncio
    async def test_contact_update_integration(self, async_session: AsyncSession):
        """
        Given: 保存されたContactが存在する
        When: Contactのステータスを更新する
        Then: 更新が正しくデータベースに反映される
        """
        # Given: 保存されたContactが存在する
        repository = SQLAlchemyContactRepository(async_session)
        
        contact = Contact.create(
            name="更新テスト",
            email="update@example.com",
            message="更新テスト",
            lesson_type="online",
            preferred_contact="email"
        )
        
        saved_contact = await repository.save(contact)
        original_updated_at = saved_contact.updated_at
        
        # When: Contactのステータスを更新する
        saved_contact.update_status(ContactStatus.PROCESSING)
        updated_contact = await repository.save(saved_contact)
        
        # Then: 更新が正しくデータベースに反映される
        assert updated_contact.status == ContactStatus.PROCESSING
        assert updated_contact.updated_at > original_updated_at
        
        # Then: データベースから再取得して確認
        retrieved_contact = await repository.find_by_id(contact.id)
        assert retrieved_contact is not None
        assert retrieved_contact.status == ContactStatus.PROCESSING
        assert retrieved_contact.updated_at > original_updated_at


class TestContactServiceIntegration:
    """ContactService統合テスト"""
    
    @pytest.mark.asyncio
    async def test_contact_service_full_flow(self, async_session: AsyncSession):
        """
        Given: ContactServiceとその依存関係が提供される
        When: ContactServiceを通じて問い合わせを作成・取得する
        Then: 全ての処理が正しく実行される
        """
        # Given: ContactServiceとその依存関係が提供される
        from app.infrastructure.di.container import get_container
        
        container = get_container()
        await container.setup_database_services(async_session)
        contact_service = container.contact_service()
        
        # When: ContactServiceを通じて問い合わせを作成する
        created_contact = await contact_service.create_contact(
            name="サービステスト",
            email="service@example.com",
            phone="070-5555-6666",
            lesson_type="trial",
            preferred_contact="email",
            message="サービス統合テスト"
        )
        
        # Then: 問い合わせが正しく作成される
        assert created_contact is not None
        assert created_contact.name == "サービステスト"
        assert str(created_contact.email) == "service@example.com"
        assert str(created_contact.phone) == "07055556666"
        assert created_contact.status == ContactStatus.PENDING
        
        # When: ContactServiceを通じて問い合わせを取得する
        retrieved_contact = await contact_service.get_contact_by_id(created_contact.id)
        
        # Then: 正しく取得できる
        assert retrieved_contact is not None
        assert retrieved_contact.id == created_contact.id
        assert retrieved_contact.name == created_contact.name
        assert str(retrieved_contact.email) == str(created_contact.email)
        
        # When: ContactServiceを通じてステータスを更新する
        updated_contact = await contact_service.update_contact_status(
            contact_id=created_contact.id,
            status=ContactStatus.COMPLETED,
            processed_by="test@example.com",
            processing_notes="テスト完了"
        )
        
        # Then: ステータスが正しく更新される
        assert updated_contact is not None
        assert updated_contact.status == ContactStatus.COMPLETED
        assert updated_contact.processed_by == "test@example.com"
        assert updated_contact.processing_notes == "テスト完了"
        assert updated_contact.processed_at is not None


class TestContactAPIErrorHandling:
    """Contact API エラーハンドリング統合テスト"""
    
    @pytest.mark.asyncio
    async def test_api_error_handling_integration(self, client: AsyncClient):
        """
        Given: 様々なエラー条件が存在する
        When: APIエンドポイントを呼び出す
        Then: 適切なエラーレスポンスが返される
        """
        # Given & When & Then: 無効なUUIDでアクセス
        response = await client.get("/api/v1/contacts/invalid-uuid")
        assert response.status_code == 422
        
        # Given & When & Then: 空のJSONでPOST
        response = await client.post("/api/v1/contacts/", json={})
        assert response.status_code == 422
        
        # Given & When & Then: 不正なJSONでPOST
        response = await client.post(
            "/api/v1/contacts/", 
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
        # Given & When & Then: 存在しないエンドポイントにアクセス
        response = await client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_api_cors_integration(self, client: AsyncClient):
        """
        Given: CORSが設定されたAPIが存在する
        When: OPTIONSリクエストを送信する
        Then: 適切なCORSヘッダーが返される
        """
        # Given & When: OPTIONSリクエストを送信する
        response = await client.options(
            "/api/v1/contacts/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        # Then: 適切なCORSヘッダーが返される
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers