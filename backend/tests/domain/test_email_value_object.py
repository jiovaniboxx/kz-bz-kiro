"""
Email Value Object Unit Tests

Given-When-Then形式でEmail値オブジェクトのテストを実装
"""

import pytest

from app.domain.value_objects.email import Email


class TestEmailCreation:
    """Email作成のテスト"""
    
    def test_create_email_with_valid_address(self):
        """
        Given: 有効なメールアドレスが提供される
        When: Emailオブジェクトを作成する
        Then: 正しいEmailオブジェクトが作成される
        """
        # Given: 有効なメールアドレスが提供される
        valid_email = "test@example.com"
        
        # When: Emailオブジェクトを作成する
        email = Email.create(valid_email)
        
        # Then: 正しいEmailオブジェクトが作成される
        assert isinstance(email, Email)
        assert email.value == valid_email
        assert str(email) == valid_email
    
    def test_create_email_with_uppercase_letters(self):
        """
        Given: 大文字を含むメールアドレスが提供される
        When: Emailオブジェクトを作成する
        Then: 小文字に正規化されたEmailオブジェクトが作成される
        """
        # Given: 大文字を含むメールアドレスが提供される
        uppercase_email = "Test.User@EXAMPLE.COM"
        
        # When: Emailオブジェクトを作成する
        email = Email.create(uppercase_email)
        
        # Then: 小文字に正規化されたEmailオブジェクトが作成される
        assert email.value == "test.user@example.com"
        assert str(email) == "test.user@example.com"
    
    def test_create_email_with_whitespace(self):
        """
        Given: 前後に空白を含むメールアドレスが提供される
        When: Emailオブジェクトを作成する
        Then: 空白が除去されたEmailオブジェクトが作成される
        """
        # Given: 前後に空白を含むメールアドレスが提供される
        email_with_whitespace = "  user@example.com  "
        
        # When: Emailオブジェクトを作成する
        email = Email.create(email_with_whitespace)
        
        # Then: 空白が除去されたEmailオブジェクトが作成される
        assert email.value == "user@example.com"
        assert str(email) == "user@example.com"
    
    def test_create_email_with_plus_sign(self):
        """
        Given: プラス記号を含む有効なメールアドレスが提供される
        When: Emailオブジェクトを作成する
        Then: 正しいEmailオブジェクトが作成される
        """
        # Given: プラス記号を含む有効なメールアドレスが提供される
        email_with_plus = "user+tag@example.com"
        
        # When: Emailオブジェクトを作成する
        email = Email.create(email_with_plus)
        
        # Then: 正しいEmailオブジェクトが作成される
        assert email.value == email_with_plus
        assert str(email) == email_with_plus
    
    def test_create_email_with_dots_and_hyphens(self):
        """
        Given: ドットとハイフンを含む有効なメールアドレスが提供される
        When: Emailオブジェクトを作成する
        Then: 正しいEmailオブジェクトが作成される
        """
        # Given: ドットとハイフンを含む有効なメールアドレスが提供される
        complex_email = "first.last-name@sub-domain.example.co.jp"
        
        # When: Emailオブジェクトを作成する
        email = Email.create(complex_email)
        
        # Then: 正しいEmailオブジェクトが作成される
        assert email.value == complex_email
        assert str(email) == complex_email


class TestEmailValidation:
    """Emailバリデーションのテスト"""
    
    def test_create_email_with_empty_string(self):
        """
        Given: 空文字列が提供される
        When: Emailオブジェクトを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: 空文字列が提供される
        empty_email = ""
        
        # When & Then: Emailオブジェクトを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="メールアドレスは必須です"):
            Email.create(empty_email)
    
    def test_create_email_without_at_symbol(self):
        """
        Given: @記号がないメールアドレスが提供される
        When: Emailオブジェクトを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: @記号がないメールアドレスが提供される
        invalid_email = "userexample.com"
        
        # When & Then: Emailオブジェクトを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="無効なメールアドレス形式です"):
            Email.create(invalid_email)
    
    def test_create_email_without_domain(self):
        """
        Given: ドメイン部分がないメールアドレスが提供される
        When: Emailオブジェクトを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: ドメイン部分がないメールアドレスが提供される
        invalid_email = "user@"
        
        # When & Then: Emailオブジェクトを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="無効なメールアドレス形式です"):
            Email.create(invalid_email)
    
    def test_create_email_without_local_part(self):
        """
        Given: ローカル部分がないメールアドレスが提供される
        When: Emailオブジェクトを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: ローカル部分がないメールアドレスが提供される
        invalid_email = "@example.com"
        
        # When & Then: Emailオブジェクトを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="無効なメールアドレス形式です"):
            Email.create(invalid_email)
    
    def test_create_email_without_tld(self):
        """
        Given: トップレベルドメインがないメールアドレスが提供される
        When: Emailオブジェクトを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: トップレベルドメインがないメールアドレスが提供される
        invalid_email = "user@example"
        
        # When & Then: Emailオブジェクトを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="無効なメールアドレス形式です"):
            Email.create(invalid_email)
    
    def test_create_email_with_multiple_at_symbols(self):
        """
        Given: 複数の@記号を含むメールアドレスが提供される
        When: Emailオブジェクトを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: 複数の@記号を含むメールアドレスが提供される
        invalid_email = "user@@example.com"
        
        # When & Then: Emailオブジェクトを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="無効なメールアドレス形式です"):
            Email.create(invalid_email)
    
    def test_create_email_with_spaces_in_middle(self):
        """
        Given: 中間にスペースを含むメールアドレスが提供される
        When: Emailオブジェクトを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: 中間にスペースを含むメールアドレスが提供される
        invalid_email = "user name@example.com"
        
        # When & Then: Emailオブジェクトを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="無効なメールアドレス形式です"):
            Email.create(invalid_email)


class TestEmailProperties:
    """Emailプロパティのテスト"""
    
    def test_domain_property(self):
        """
        Given: Emailオブジェクトが存在する
        When: domainプロパティにアクセスする
        Then: 正しいドメイン部分が返される
        """
        # Given: Emailオブジェクトが存在する
        email = Email.create("user@example.com")
        
        # When: domainプロパティにアクセスする
        domain = email.domain
        
        # Then: 正しいドメイン部分が返される
        assert domain == "example.com"
    
    def test_local_part_property(self):
        """
        Given: Emailオブジェクトが存在する
        When: local_partプロパティにアクセスする
        Then: 正しいローカル部分が返される
        """
        # Given: Emailオブジェクトが存在する
        email = Email.create("user@example.com")
        
        # When: local_partプロパティにアクセスする
        local_part = email.local_part
        
        # Then: 正しいローカル部分が返される
        assert local_part == "user"
    
    def test_domain_property_with_subdomain(self):
        """
        Given: サブドメインを含むEmailオブジェクトが存在する
        When: domainプロパティにアクセスする
        Then: サブドメインを含む完全なドメイン部分が返される
        """
        # Given: サブドメインを含むEmailオブジェクトが存在する
        email = Email.create("user@mail.example.com")
        
        # When: domainプロパティにアクセスする
        domain = email.domain
        
        # Then: サブドメインを含む完全なドメイン部分が返される
        assert domain == "mail.example.com"
    
    def test_local_part_property_with_plus(self):
        """
        Given: プラス記号を含むEmailオブジェクトが存在する
        When: local_partプロパティにアクセスする
        Then: プラス記号を含む完全なローカル部分が返される
        """
        # Given: プラス記号を含むEmailオブジェクトが存在する
        email = Email.create("user+tag@example.com")
        
        # When: local_partプロパティにアクセスする
        local_part = email.local_part
        
        # Then: プラス記号を含む完全なローカル部分が返される
        assert local_part == "user+tag"


class TestEmailEquality:
    """Email等価性のテスト"""
    
    def test_email_equality_with_same_address(self):
        """
        Given: 同じメールアドレスを持つ2つのEmailオブジェクトが存在する
        When: 等価性を比較する
        Then: 等価であると判定される
        """
        # Given: 同じメールアドレスを持つ2つのEmailオブジェクトが存在する
        email1 = Email.create("test@example.com")
        email2 = Email.create("test@example.com")
        
        # When & Then: 等価性を比較すると等価であると判定される
        assert email1 == email2
        assert hash(email1) == hash(email2)
    
    def test_email_equality_with_different_case(self):
        """
        Given: 大文字小文字が異なる同じメールアドレスを持つ2つのEmailオブジェクトが存在する
        When: 等価性を比較する
        Then: 等価であると判定される（正規化により）
        """
        # Given: 大文字小文字が異なる同じメールアドレスを持つ2つのEmailオブジェクトが存在する
        email1 = Email.create("Test@Example.Com")
        email2 = Email.create("test@example.com")
        
        # When & Then: 等価性を比較すると等価であると判定される
        assert email1 == email2
        assert hash(email1) == hash(email2)
    
    def test_email_inequality_with_different_address(self):
        """
        Given: 異なるメールアドレスを持つ2つのEmailオブジェクトが存在する
        When: 等価性を比較する
        Then: 等価でないと判定される
        """
        # Given: 異なるメールアドレスを持つ2つのEmailオブジェクトが存在する
        email1 = Email.create("user1@example.com")
        email2 = Email.create("user2@example.com")
        
        # When & Then: 等価性を比較すると等価でないと判定される
        assert email1 != email2
        assert hash(email1) != hash(email2)


class TestEmailImmutability:
    """Email不変性のテスト"""
    
    def test_email_is_immutable(self):
        """
        Given: Emailオブジェクトが存在する
        When: valueを変更しようとする
        Then: AttributeErrorが発生する（frozen=Trueのため）
        """
        # Given: Emailオブジェクトが存在する
        email = Email.create("test@example.com")
        
        # When & Then: valueを変更しようとするとAttributeErrorが発生する
        with pytest.raises(AttributeError):
            email.value = "changed@example.com"


class TestEmailStringRepresentation:
    """Email文字列表現のテスト"""
    
    def test_str_representation(self):
        """
        Given: Emailオブジェクトが存在する
        When: str()で文字列化する
        Then: メールアドレス文字列が返される
        """
        # Given: Emailオブジェクトが存在する
        email_address = "user@example.com"
        email = Email.create(email_address)
        
        # When: str()で文字列化する
        str_repr = str(email)
        
        # Then: メールアドレス文字列が返される
        assert str_repr == email_address
    
    def test_repr_representation(self):
        """
        Given: Emailオブジェクトが存在する
        When: repr()でデバッグ用文字列化する
        Then: 適切なデバッグ用文字列表現が返される
        """
        # Given: Emailオブジェクトが存在する
        email_address = "debug@example.com"
        email = Email.create(email_address)
        
        # When: repr()でデバッグ用文字列化する
        repr_str = repr(email)
        
        # Then: 適切なデバッグ用文字列表現が返される
        assert repr_str == f"Email('{email_address}')"


class TestEmailEdgeCases:
    """Emailエッジケースのテスト"""
    
    def test_create_email_with_international_domain(self):
        """
        Given: 国際化ドメインを含むメールアドレスが提供される
        When: Emailオブジェクトを作成する
        Then: 正しいEmailオブジェクトが作成される
        """
        # Given: 国際化ドメインを含むメールアドレスが提供される
        international_email = "user@example.co.jp"
        
        # When: Emailオブジェクトを作成する
        email = Email.create(international_email)
        
        # Then: 正しいEmailオブジェクトが作成される
        assert email.value == international_email
        assert email.domain == "example.co.jp"
    
    def test_create_email_with_long_domain(self):
        """
        Given: 長いドメイン名を含むメールアドレスが提供される
        When: Emailオブジェクトを作成する
        Then: 正しいEmailオブジェクトが作成される
        """
        # Given: 長いドメイン名を含むメールアドレスが提供される
        long_domain_email = "user@very-long-subdomain.example-domain.com"
        
        # When: Emailオブジェクトを作成する
        email = Email.create(long_domain_email)
        
        # Then: 正しいEmailオブジェクトが作成される
        assert email.value == long_domain_email
        assert email.domain == "very-long-subdomain.example-domain.com"
    
    def test_create_email_with_numbers_in_local_part(self):
        """
        Given: ローカル部分に数字を含むメールアドレスが提供される
        When: Emailオブジェクトを作成する
        Then: 正しいEmailオブジェクトが作成される
        """
        # Given: ローカル部分に数字を含むメールアドレスが提供される
        numeric_email = "user123@example.com"
        
        # When: Emailオブジェクトを作成する
        email = Email.create(numeric_email)
        
        # Then: 正しいEmailオブジェクトが作成される
        assert email.value == numeric_email
        assert email.local_part == "user123"