"""
Phone Value Object Unit Tests

Given-When-Then形式でPhone値オブジェクトのテストを実装
"""

import pytest

from app.domain.value_objects.phone import Phone


class TestPhoneCreation:
    """Phone作成のテスト"""
    
    def test_create_phone_with_mobile_number(self):
        """
        Given: 有効な携帯電話番号が提供される
        When: Phoneオブジェクトを作成する
        Then: 正しいPhoneオブジェクトが作成される
        """
        # Given: 有効な携帯電話番号が提供される
        mobile_number = "090-1234-5678"
        
        # When: Phoneオブジェクトを作成する
        phone = Phone.create(mobile_number)
        
        # Then: 正しいPhoneオブジェクトが作成される
        assert isinstance(phone, Phone)
        assert phone.value == "09012345678"  # 正規化された形式
        assert str(phone) == "09012345678"
    
    def test_create_phone_with_landline_number(self):
        """
        Given: 有効な固定電話番号が提供される
        When: Phoneオブジェクトを作成する
        Then: 正しいPhoneオブジェクトが作成される
        """
        # Given: 有効な固定電話番号が提供される
        landline_number = "03-1234-5678"
        
        # When: Phoneオブジェクトを作成する
        phone = Phone.create(landline_number)
        
        # Then: 正しいPhoneオブジェクトが作成される
        assert phone.value == "0312345678"  # 正規化された形式
        assert str(phone) == "0312345678"
    
    def test_create_phone_with_ip_phone_number(self):
        """
        Given: 有効なIP電話番号が提供される
        When: Phoneオブジェクトを作成する
        Then: 正しいPhoneオブジェクトが作成される
        """
        # Given: 有効なIP電話番号が提供される
        ip_phone_number = "050-1234-5678"
        
        # When: Phoneオブジェクトを作成する
        phone = Phone.create(ip_phone_number)
        
        # Then: 正しいPhoneオブジェクトが作成される
        assert phone.value == "05012345678"  # 正規化された形式
        assert str(phone) == "05012345678"
    
    def test_create_phone_with_toll_free_number(self):
        """
        Given: 有効なフリーダイヤル番号が提供される
        When: Phoneオブジェクトを作成する
        Then: 正しいPhoneオブジェクトが作成される
        """
        # Given: 有効なフリーダイヤル番号が提供される
        toll_free_number = "0120-123-456"
        
        # When: Phoneオブジェクトを作成する
        phone = Phone.create(toll_free_number)
        
        # Then: 正しいPhoneオブジェクトが作成される
        assert phone.value == "0120123456"  # 正規化された形式
        assert str(phone) == "0120123456"


class TestPhoneNormalization:
    """Phone正規化のテスト"""
    
    def test_normalize_phone_with_hyphens(self):
        """
        Given: ハイフンを含む電話番号が提供される
        When: Phoneオブジェクトを作成する
        Then: ハイフンが除去された正規化された番号が作成される
        """
        # Given: ハイフンを含む電話番号が提供される
        phone_with_hyphens = "090-1234-5678"
        
        # When: Phoneオブジェクトを作成する
        phone = Phone.create(phone_with_hyphens)
        
        # Then: ハイフンが除去された正規化された番号が作成される
        assert phone.value == "09012345678"
    
    def test_normalize_phone_with_spaces(self):
        """
        Given: スペースを含む電話番号が提供される
        When: Phoneオブジェクトを作成する
        Then: スペースが除去された正規化された番号が作成される
        """
        # Given: スペースを含む電話番号が提供される
        phone_with_spaces = "090 1234 5678"
        
        # When: Phoneオブジェクトを作成する
        phone = Phone.create(phone_with_spaces)
        
        # Then: スペースが除去された正規化された番号が作成される
        assert phone.value == "09012345678"
    
    def test_normalize_phone_with_parentheses(self):
        """
        Given: 括弧を含む電話番号が提供される
        When: Phoneオブジェクトを作成する
        Then: 括弧が除去された正規化された番号が作成される
        """
        # Given: 括弧を含む電話番号が提供される
        phone_with_parentheses = "(090) 1234-5678"
        
        # When: Phoneオブジェクトを作成する
        phone = Phone.create(phone_with_parentheses)
        
        # Then: 括弧が除去された正規化された番号が作成される
        assert phone.value == "09012345678"
    
    def test_normalize_phone_with_international_prefix_plus81(self):
        """
        Given: +81で始まる国際番号が提供される
        When: Phoneオブジェクトを作成する
        Then: 0で始まる国内番号に正規化される
        """
        # Given: +81で始まる国際番号が提供される
        international_phone = "+81-90-1234-5678"
        
        # When: Phoneオブジェクトを作成する
        phone = Phone.create(international_phone)
        
        # Then: 0で始まる国内番号に正規化される
        assert phone.value == "09012345678"
    
    def test_normalize_phone_with_international_prefix_81(self):
        """
        Given: 81で始まる国際番号が提供される
        When: Phoneオブジェクトを作成する
        Then: 0で始まる国内番号に正規化される
        """
        # Given: 81で始まる国際番号が提供される
        international_phone = "81-90-1234-5678"
        
        # When: Phoneオブジェクトを作成する
        phone = Phone.create(international_phone)
        
        # Then: 0で始まる国内番号に正規化される
        assert phone.value == "09012345678"
    
    def test_normalize_phone_with_mixed_formatting(self):
        """
        Given: 複数の書式が混在する電話番号が提供される
        When: Phoneオブジェクトを作成する
        Then: 全ての書式が除去された正規化された番号が作成される
        """
        # Given: 複数の書式が混在する電話番号が提供される
        mixed_format_phone = " +81-(090) 1234-5678 "
        
        # When: Phoneオブジェクトを作成する
        phone = Phone.create(mixed_format_phone)
        
        # Then: 全ての書式が除去された正規化された番号が作成される
        assert phone.value == "09012345678"


class TestPhoneValidation:
    """Phoneバリデーションのテスト"""
    
    def test_create_phone_with_empty_string(self):
        """
        Given: 空文字列が提供される
        When: Phoneオブジェクトを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: 空文字列が提供される
        empty_phone = ""
        
        # When & Then: Phoneオブジェクトを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="電話番号は必須です"):
            Phone.create(empty_phone)
    
    def test_create_phone_with_invalid_format(self):
        """
        Given: 無効な形式の電話番号が提供される
        When: Phoneオブジェクトを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: 無効な形式の電話番号が提供される
        invalid_phone = "123-456-789"
        
        # When & Then: Phoneオブジェクトを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="無効な電話番号形式です"):
            Phone.create(invalid_phone)
    
    def test_create_phone_with_too_short_number(self):
        """
        Given: 短すぎる電話番号が提供される
        When: Phoneオブジェクトを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: 短すぎる電話番号が提供される
        short_phone = "090-123"
        
        # When & Then: Phoneオブジェクトを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="無効な電話番号形式です"):
            Phone.create(short_phone)
    
    def test_create_phone_with_too_long_number(self):
        """
        Given: 長すぎる電話番号が提供される
        When: Phoneオブジェクトを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: 長すぎる電話番号が提供される
        long_phone = "090-1234-5678-9012"
        
        # When & Then: Phoneオブジェクトを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="無効な電話番号形式です"):
            Phone.create(long_phone)
    
    def test_create_phone_with_invalid_prefix(self):
        """
        Given: 無効なプレフィックスの電話番号が提供される
        When: Phoneオブジェクトを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: 無効なプレフィックスの電話番号が提供される
        invalid_prefix_phone = "010-1234-5678"  # 010は無効なプレフィックス
        
        # When & Then: Phoneオブジェクトを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="無効な電話番号形式です"):
            Phone.create(invalid_prefix_phone)
    
    def test_create_phone_with_letters(self):
        """
        Given: 文字を含む電話番号が提供される
        When: Phoneオブジェクトを作成しようとする
        Then: ValueErrorが発生する
        """
        # Given: 文字を含む電話番号が提供される
        phone_with_letters = "090-ABCD-5678"
        
        # When & Then: Phoneオブジェクトを作成しようとするとValueErrorが発生する
        with pytest.raises(ValueError, match="無効な電話番号形式です"):
            Phone.create(phone_with_letters)


class TestPhoneOptionalCreation:
    """Phoneオプショナル作成のテスト"""
    
    def test_create_optional_phone_with_valid_number(self):
        """
        Given: 有効な電話番号が提供される
        When: create_optionalでPhoneオブジェクトを作成する
        Then: 正しいPhoneオブジェクトが返される
        """
        # Given: 有効な電話番号が提供される
        valid_phone = "090-1234-5678"
        
        # When: create_optionalでPhoneオブジェクトを作成する
        phone = Phone.create_optional(valid_phone)
        
        # Then: 正しいPhoneオブジェクトが返される
        assert phone is not None
        assert isinstance(phone, Phone)
        assert phone.value == "09012345678"
    
    def test_create_optional_phone_with_none(self):
        """
        Given: Noneが提供される
        When: create_optionalでPhoneオブジェクトを作成する
        Then: Noneが返される
        """
        # Given: Noneが提供される
        none_phone = None
        
        # When: create_optionalでPhoneオブジェクトを作成する
        phone = Phone.create_optional(none_phone)
        
        # Then: Noneが返される
        assert phone is None
    
    def test_create_optional_phone_with_empty_string(self):
        """
        Given: 空文字列が提供される
        When: create_optionalでPhoneオブジェクトを作成する
        Then: Noneが返される
        """
        # Given: 空文字列が提供される
        empty_phone = ""
        
        # When: create_optionalでPhoneオブジェクトを作成する
        phone = Phone.create_optional(empty_phone)
        
        # Then: Noneが返される
        assert phone is None
    
    def test_create_optional_phone_with_whitespace_only(self):
        """
        Given: 空白のみの文字列が提供される
        When: create_optionalでPhoneオブジェクトを作成する
        Then: Noneが返される
        """
        # Given: 空白のみの文字列が提供される
        whitespace_phone = "   "
        
        # When: create_optionalでPhoneオブジェクトを作成する
        phone = Phone.create_optional(whitespace_phone)
        
        # Then: Noneが返される
        assert phone is None


class TestPhoneFormatting:
    """Phoneフォーマットのテスト"""
    
    def test_formatted_mobile_number_090(self):
        """
        Given: 090で始まる携帯電話番号のPhoneオブジェクトが存在する
        When: formatted()メソッドを呼び出す
        Then: ハイフン区切りの形式で返される
        """
        # Given: 090で始まる携帯電話番号のPhoneオブジェクトが存在する
        phone = Phone.create("09012345678")
        
        # When: formatted()メソッドを呼び出す
        formatted = phone.formatted()
        
        # Then: ハイフン区切りの形式で返される
        assert formatted == "090-1234-5678"
    
    def test_formatted_mobile_number_080(self):
        """
        Given: 080で始まる携帯電話番号のPhoneオブジェクトが存在する
        When: formatted()メソッドを呼び出す
        Then: ハイフン区切りの形式で返される
        """
        # Given: 080で始まる携帯電話番号のPhoneオブジェクトが存在する
        phone = Phone.create("08087654321")
        
        # When: formatted()メソッドを呼び出す
        formatted = phone.formatted()
        
        # Then: ハイフン区切りの形式で返される
        assert formatted == "080-8765-4321"
    
    def test_formatted_mobile_number_070(self):
        """
        Given: 070で始まる携帯電話番号のPhoneオブジェクトが存在する
        When: formatted()メソッドを呼び出す
        Then: ハイフン区切りの形式で返される
        """
        # Given: 070で始まる携帯電話番号のPhoneオブジェクトが存在する
        phone = Phone.create("07011112222")
        
        # When: formatted()メソッドを呼び出す
        formatted = phone.formatted()
        
        # Then: ハイフン区切りの形式で返される
        assert formatted == "070-1111-2222"
    
    def test_formatted_ip_phone_number(self):
        """
        Given: 050で始まるIP電話番号のPhoneオブジェクトが存在する
        When: formatted()メソッドを呼び出す
        Then: ハイフン区切りの形式で返される
        """
        # Given: 050で始まるIP電話番号のPhoneオブジェクトが存在する
        phone = Phone.create("05012345678")
        
        # When: formatted()メソッドを呼び出す
        formatted = phone.formatted()
        
        # Then: ハイフン区切りの形式で返される
        assert formatted == "050-1234-5678"
    
    def test_formatted_toll_free_0120(self):
        """
        Given: 0120で始まるフリーダイヤル番号のPhoneオブジェクトが存在する
        When: formatted()メソッドを呼び出す
        Then: ハイフン区切りの形式で返される
        """
        # Given: 0120で始まるフリーダイヤル番号のPhoneオブジェクトが存在する
        phone = Phone.create("0120123456")
        
        # When: formatted()メソッドを呼び出す
        formatted = phone.formatted()
        
        # Then: ハイフン区切りの形式で返される
        assert formatted == "0120-123-456"
    
    def test_formatted_toll_free_0800(self):
        """
        Given: 0800で始まるフリーダイヤル番号のPhoneオブジェクトが存在する
        When: formatted()メソッドを呼び出す
        Then: ハイフン区切りの形式で返される
        """
        # Given: 0800で始まるフリーダイヤル番号のPhoneオブジェクトが存在する
        phone = Phone.create("08001234567")
        
        # When: formatted()メソッドを呼び出す
        formatted = phone.formatted()
        
        # Then: ハイフン区切りの形式で返される
        assert formatted == "0800-123-4567"
    
    def test_formatted_landline_tokyo_03(self):
        """
        Given: 03で始まる東京の固定電話番号のPhoneオブジェクトが存在する
        When: formatted()メソッドを呼び出す
        Then: 2桁市外局番の形式で返される
        """
        # Given: 03で始まる東京の固定電話番号のPhoneオブジェクトが存在する
        phone = Phone.create("0312345678")
        
        # When: formatted()メソッドを呼び出す
        formatted = phone.formatted()
        
        # Then: 2桁市外局番の形式で返される
        assert formatted == "03-1234-5678"
    
    def test_formatted_landline_osaka_06(self):
        """
        Given: 06で始まる大阪の固定電話番号のPhoneオブジェクトが存在する
        When: formatted()メソッドを呼び出す
        Then: 2桁市外局番の形式で返される
        """
        # Given: 06で始まる大阪の固定電話番号のPhoneオブジェクトが存在する
        phone = Phone.create("0687654321")
        
        # When: formatted()メソッドを呼び出す
        formatted = phone.formatted()
        
        # Then: 2桁市外局番の形式で返される
        assert formatted == "06-8765-4321"
    
    def test_formatted_landline_other_3digit(self):
        """
        Given: 3桁市外局番の固定電話番号のPhoneオブジェクトが存在する
        When: formatted()メソッドを呼び出す
        Then: 3桁市外局番の形式で返される
        """
        # Given: 3桁市外局番の固定電話番号のPhoneオブジェクトが存在する
        phone = Phone.create("0451234567")
        
        # When: formatted()メソッドを呼び出す
        formatted = phone.formatted()
        
        # Then: 3桁市外局番の形式で返される
        assert formatted == "045-123-4567"
    
    def test_formatted_landline_4digit(self):
        """
        Given: 4桁市外局番の固定電話番号のPhoneオブジェクトが存在する
        When: formatted()メソッドを呼び出す
        Then: 4桁市外局番の形式で返される
        """
        # Given: 4桁市外局番の固定電話番号のPhoneオブジェクトが存在する
        phone = Phone.create("04291234567")
        
        # When: formatted()メソッドを呼び出す
        formatted = phone.formatted()
        
        # Then: 4桁市外局番の形式で返される
        assert formatted == "0429-123-4567"


class TestPhoneEquality:
    """Phone等価性のテスト"""
    
    def test_phone_equality_with_same_number(self):
        """
        Given: 同じ電話番号を持つ2つのPhoneオブジェクトが存在する
        When: 等価性を比較する
        Then: 等価であると判定される
        """
        # Given: 同じ電話番号を持つ2つのPhoneオブジェクトが存在する
        phone1 = Phone.create("090-1234-5678")
        phone2 = Phone.create("09012345678")
        
        # When & Then: 等価性を比較すると等価であると判定される
        assert phone1 == phone2
        assert hash(phone1) == hash(phone2)
    
    def test_phone_inequality_with_different_number(self):
        """
        Given: 異なる電話番号を持つ2つのPhoneオブジェクトが存在する
        When: 等価性を比較する
        Then: 等価でないと判定される
        """
        # Given: 異なる電話番号を持つ2つのPhoneオブジェクトが存在する
        phone1 = Phone.create("090-1234-5678")
        phone2 = Phone.create("080-8765-4321")
        
        # When & Then: 等価性を比較すると等価でないと判定される
        assert phone1 != phone2
        assert hash(phone1) != hash(phone2)


class TestPhoneImmutability:
    """Phone不変性のテスト"""
    
    def test_phone_is_immutable(self):
        """
        Given: Phoneオブジェクトが存在する
        When: valueを変更しようとする
        Then: AttributeErrorが発生する（frozen=Trueのため）
        """
        # Given: Phoneオブジェクトが存在する
        phone = Phone.create("090-1234-5678")
        
        # When & Then: valueを変更しようとするとAttributeErrorが発生する
        with pytest.raises(AttributeError):
            phone.value = "08087654321"


class TestPhoneStringRepresentation:
    """Phone文字列表現のテスト"""
    
    def test_str_representation(self):
        """
        Given: Phoneオブジェクトが存在する
        When: str()で文字列化する
        Then: 正規化された電話番号文字列が返される
        """
        # Given: Phoneオブジェクトが存在する
        phone = Phone.create("090-1234-5678")
        
        # When: str()で文字列化する
        str_repr = str(phone)
        
        # Then: 正規化された電話番号文字列が返される
        assert str_repr == "09012345678"
    
    def test_repr_representation(self):
        """
        Given: Phoneオブジェクトが存在する
        When: repr()でデバッグ用文字列化する
        Then: 適切なデバッグ用文字列表現が返される
        """
        # Given: Phoneオブジェクトが存在する
        phone = Phone.create("090-1234-5678")
        
        # When: repr()でデバッグ用文字列化する
        repr_str = repr(phone)
        
        # Then: 適切なデバッグ用文字列表現が返される
        assert repr_str == "Phone('09012345678')"