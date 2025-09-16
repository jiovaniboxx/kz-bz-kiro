"""
Database Security

データベースセキュリティ機能
"""

import logging
import hashlib
import secrets
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy import text, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import ClauseElement

logger = logging.getLogger(__name__)


class QuerySanitizer:
    """SQLクエリサニタイザー"""
    
    # 危険なSQL文のパターン
    DANGEROUS_PATTERNS = [
        r'\b(DROP|DELETE|TRUNCATE|ALTER|CREATE|EXEC|EXECUTE)\b',
        r'--',
        r'/\*.*?\*/',
        r';.*?;',
        r'\bUNION\b.*?\bSELECT\b',
        r'\bINSERT\b.*?\bINTO\b',
        r'\bUPDATE\b.*?\bSET\b',
    ]
    
    @classmethod
    def is_safe_query(cls, query: str) -> bool:
        """クエリが安全かどうかを判定"""
        import re
        
        query_upper = query.upper()
        
        # 危険なパターンをチェック
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, query_upper, re.IGNORECASE):
                logger.warning(f"Dangerous SQL pattern detected: {pattern}")
                return False
        
        return True
    
    @classmethod
    def sanitize_query_params(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """クエリパラメータをサニタイズ"""
        sanitized = {}
        
        for key, value in params.items():
            if isinstance(value, str):
                # SQLインジェクション攻撃パターンを除去
                sanitized_value = value.replace("'", "''")  # シングルクォートをエスケープ
                sanitized_value = sanitized_value.replace(";", "")  # セミコロンを除去
                sanitized_value = sanitized_value.replace("--", "")  # コメントを除去
                sanitized[key] = sanitized_value
            else:
                sanitized[key] = value
        
        return sanitized


class DatabaseAuditor:
    """データベース監査機能"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def log_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        operation_type: str = "SELECT"
    ):
        """クエリ実行をログに記録"""
        audit_data = {
            "timestamp": datetime.utcnow(),
            "query": query[:1000],  # 最初の1000文字のみ記録
            "params": str(params)[:500] if params else None,
            "user_id": user_id,
            "client_ip": client_ip,
            "operation_type": operation_type,
        }
        
        logger.info(f"Database Query Audit: {audit_data}")
    
    def log_data_access(
        self,
        table_name: str,
        record_id: Optional[Union[str, int]] = None,
        operation: str = "READ",
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        sensitive_data: bool = False
    ):
        """データアクセスをログに記録"""
        audit_data = {
            "timestamp": datetime.utcnow(),
            "table_name": table_name,
            "record_id": record_id,
            "operation": operation,
            "user_id": user_id,
            "client_ip": client_ip,
            "sensitive_data": sensitive_data,
        }
        
        if sensitive_data or operation in ["CREATE", "UPDATE", "DELETE"]:
            logger.warning(f"Sensitive Data Access: {audit_data}")
        else:
            logger.info(f"Data Access: {audit_data}")


class DataEncryption:
    """データ暗号化機能"""
    
    def __init__(self, encryption_key: str):
        self.encryption_key = encryption_key.encode()
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """機密データを暗号化"""
        from cryptography.fernet import Fernet
        
        # 暗号化キーからFernetキーを生成
        key = hashlib.sha256(self.encryption_key).digest()
        fernet_key = Fernet.generate_key()  # 実際の実装では固定キーを使用
        fernet = Fernet(fernet_key)
        
        encrypted_data = fernet.encrypt(data.encode())
        return encrypted_data.decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """機密データを復号化"""
        from cryptography.fernet import Fernet
        
        # 暗号化キーからFernetキーを生成
        key = hashlib.sha256(self.encryption_key).digest()
        fernet_key = Fernet.generate_key()  # 実際の実装では固定キーを使用
        fernet = Fernet(fernet_key)
        
        decrypted_data = fernet.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """パスワードをハッシュ化"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # PBKDF2を使用してパスワードをハッシュ化
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000  # 100,000回の反復
        )
        
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """パスワードを検証"""
        computed_hash, _ = self.hash_password(password, salt)
        return secrets.compare_digest(password_hash, computed_hash)


class DatabaseConnectionSecurity:
    """データベース接続セキュリティ"""
    
    @staticmethod
    def validate_connection_string(connection_string: str) -> bool:
        """接続文字列を検証"""
        # SSL/TLS接続を強制
        if "sslmode" not in connection_string.lower():
            logger.warning("Database connection without SSL detected")
            return False
        
        # パスワードが平文で含まれていないかチェック
        if "password=" in connection_string.lower():
            logger.warning("Plain text password in connection string")
            return False
        
        return True
    
    @staticmethod
    def setup_connection_security(engine: Engine):
        """データベース接続のセキュリティを設定"""
        
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """SQLite用のセキュリティ設定"""
            if "sqlite" in str(engine.url):
                cursor = dbapi_connection.cursor()
                # 外部キー制約を有効化
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        
        @event.listens_for(engine, "before_cursor_execute")
        def log_queries(conn, cursor, statement, parameters, context, executemany):
            """クエリ実行前のログ"""
            if not QuerySanitizer.is_safe_query(statement):
                logger.error(f"Potentially dangerous query blocked: {statement}")
                raise ValueError("Dangerous query detected")
            
            logger.debug(f"Executing query: {statement[:200]}...")


class DataMasking:
    """データマスキング機能"""
    
    @staticmethod
    def mask_email(email: str) -> str:
        """メールアドレスをマスク"""
        if "@" not in email:
            return email
        
        local, domain = email.split("@", 1)
        if len(local) <= 2:
            masked_local = "*" * len(local)
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """電話番号をマスク"""
        if len(phone) <= 4:
            return "*" * len(phone)
        
        return phone[:2] + "*" * (len(phone) - 4) + phone[-2:]
    
    @staticmethod
    def mask_name(name: str) -> str:
        """名前をマスク"""
        if len(name) <= 1:
            return "*"
        elif len(name) <= 3:
            return name[0] + "*" * (len(name) - 1)
        else:
            return name[0] + "*" * (len(name) - 2) + name[-1]
    
    @classmethod
    def mask_sensitive_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """機密データをマスク"""
        masked_data = data.copy()
        
        # メールアドレスをマスク
        if "email" in masked_data:
            masked_data["email"] = cls.mask_email(str(masked_data["email"]))
        
        # 電話番号をマスク
        if "phone" in masked_data:
            masked_data["phone"] = cls.mask_phone(str(masked_data["phone"]))
        
        # 名前をマスク
        if "name" in masked_data:
            masked_data["name"] = cls.mask_name(str(masked_data["name"]))
        
        return masked_data


class DatabaseBackupSecurity:
    """データベースバックアップセキュリティ"""
    
    def __init__(self, encryption_key: str):
        self.encryption = DataEncryption(encryption_key)
    
    def create_secure_backup(self, session: Session, tables: List[str]) -> Dict[str, Any]:
        """セキュアなバックアップを作成"""
        backup_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "tables": {},
            "checksum": None,
        }
        
        for table_name in tables:
            try:
                # テーブルデータを取得
                result = session.execute(text(f"SELECT * FROM {table_name}"))
                rows = result.fetchall()
                
                # データをシリアライズ
                table_data = []
                for row in rows:
                    row_dict = dict(row._mapping)
                    # 機密データをマスク
                    masked_row = DataMasking.mask_sensitive_data(row_dict)
                    table_data.append(masked_row)
                
                backup_data["tables"][table_name] = table_data
                
            except Exception as e:
                logger.error(f"Failed to backup table {table_name}: {e}")
                backup_data["tables"][table_name] = {"error": str(e)}
        
        # チェックサムを計算
        import json
        backup_json = json.dumps(backup_data["tables"], sort_keys=True)
        backup_data["checksum"] = hashlib.sha256(backup_json.encode()).hexdigest()
        
        return backup_data
    
    def verify_backup_integrity(self, backup_data: Dict[str, Any]) -> bool:
        """バックアップの整合性を検証"""
        import json
        
        stored_checksum = backup_data.get("checksum")
        if not stored_checksum:
            return False
        
        # チェックサムを再計算
        backup_json = json.dumps(backup_data["tables"], sort_keys=True)
        calculated_checksum = hashlib.sha256(backup_json.encode()).hexdigest()
        
        return secrets.compare_digest(stored_checksum, calculated_checksum)


class DatabaseSecurityManager:
    """データベースセキュリティ管理クラス"""
    
    def __init__(
        self,
        session: Session,
        encryption_key: str,
        enable_auditing: bool = True,
        enable_query_validation: bool = True,
    ):
        self.session = session
        self.encryption = DataEncryption(encryption_key)
        self.auditor = DatabaseAuditor(session) if enable_auditing else None
        self.enable_query_validation = enable_query_validation
    
    def execute_secure_query(
        self,
        query: Union[str, ClauseElement],
        params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
    ) -> Any:
        """セキュアなクエリ実行"""
        
        # クエリ文字列を取得
        if isinstance(query, str):
            query_str = query
        else:
            query_str = str(query.compile(compile_kwargs={"literal_binds": True}))
        
        # クエリ検証
        if self.enable_query_validation and not QuerySanitizer.is_safe_query(query_str):
            raise ValueError("Dangerous query detected")
        
        # パラメータサニタイズ
        if params:
            params = QuerySanitizer.sanitize_query_params(params)
        
        # 監査ログ
        if self.auditor:
            operation_type = query_str.strip().split()[0].upper()
            self.auditor.log_query(query_str, params, user_id, client_ip, operation_type)
        
        # クエリ実行
        try:
            if isinstance(query, str):
                result = self.session.execute(text(query), params or {})
            else:
                result = self.session.execute(query, params or {})
            
            return result
            
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise
    
    def log_data_access(
        self,
        table_name: str,
        record_id: Optional[Union[str, int]] = None,
        operation: str = "READ",
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        sensitive_data: bool = False,
    ):
        """データアクセスをログ"""
        if self.auditor:
            self.auditor.log_data_access(
                table_name, record_id, operation, user_id, client_ip, sensitive_data
            )
    
    def encrypt_field(self, data: str) -> str:
        """フィールドデータを暗号化"""
        return self.encryption.encrypt_sensitive_data(data)
    
    def decrypt_field(self, encrypted_data: str) -> str:
        """フィールドデータを復号化"""
        return self.encryption.decrypt_sensitive_data(encrypted_data)
    
    def hash_password(self, password: str) -> tuple[str, str]:
        """パスワードをハッシュ化"""
        return self.encryption.hash_password(password)
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """パスワードを検証"""
        return self.encryption.verify_password(password, password_hash, salt)


# セキュリティ設定のファクトリ関数
def setup_database_security(
    engine: Engine,
    encryption_key: str,
    enable_connection_security: bool = True,
    enable_query_logging: bool = True,
) -> None:
    """データベースセキュリティを設定"""
    
    if enable_connection_security:
        DatabaseConnectionSecurity.setup_connection_security(engine)
    
    if enable_query_logging:
        @event.listens_for(engine, "before_cursor_execute")
        def log_queries(conn, cursor, statement, parameters, context, executemany):
            logger.debug(f"Executing query: {statement[:200]}...")
    
    logger.info("Database security setup completed")