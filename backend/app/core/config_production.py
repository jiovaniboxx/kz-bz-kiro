"""
Production Configuration

本番環境用の設定ファイル
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator


class ProductionSettings(BaseSettings):
    """本番環境設定"""
    
    # Application
    app_name: str = "English Cafe API"
    environment: str = "production"
    debug: bool = False
    
    # Database
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    
    # Security
    secret_key: str
    allowed_hosts: List[str] = ["english-cafe-backend.onrender.com"]
    cors_origins: List[str] = [
        "https://english-cafe.vercel.app",
        "https://english-cafe.com"
    ]
    
    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    smtp_from_email: str
    smtp_use_tls: bool = True
    
    # Admin
    admin_email: str
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    
    # Render specific
    port: int = int(os.getenv("PORT", "8000"))
    render_external_hostname: Optional[str] = None
    render_external_url: Optional[str] = None
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("allowed_hosts", pre=True)
    def assemble_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("database_url", pre=True)
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL is required in production")
        if not v.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must be a PostgreSQL URL")
        return v
    
    @validator("secret_key", pre=True)
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    class Config:
        env_file = ".env.production"
        case_sensitive = False


# Database configuration for production
class DatabaseConfig:
    """本番環境用データベース設定"""
    
    @staticmethod
    def get_database_config(settings: ProductionSettings) -> dict:
        """データベース設定を取得"""
        return {
            "url": settings.database_url,
            "pool_size": settings.database_pool_size,
            "max_overflow": settings.database_max_overflow,
            "pool_timeout": settings.database_pool_timeout,
            "pool_recycle": settings.database_pool_recycle,
            "pool_pre_ping": True,  # 接続の健全性チェック
            "echo": False,  # 本番環境ではSQLログを無効化
        }


# Logging configuration for production
class LoggingConfig:
    """本番環境用ログ設定"""
    
    @staticmethod
    def get_logging_config(settings: ProductionSettings) -> dict:
        """ログ設定を取得"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": settings.log_format,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "json": {
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "level": settings.log_level,
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "/tmp/app.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "formatter": "json",
                    "level": settings.log_level,
                },
            },
            "loggers": {
                "": {
                    "handlers": ["console", "file"],
                    "level": settings.log_level,
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                },
                "sqlalchemy": {
                    "handlers": ["console"],
                    "level": "WARNING",
                    "propagate": False,
                },
            },
        }


# Security configuration for production
class SecurityConfig:
    """本番環境用セキュリティ設定"""
    
    @staticmethod
    def get_security_headers() -> dict:
        """セキュリティヘッダーを取得"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self' https://english-cafe.vercel.app; "
                "frame-ancestors 'none';"
            ),
        }


# Health check configuration
class HealthCheckConfig:
    """ヘルスチェック設定"""
    
    @staticmethod
    def get_health_check_config() -> dict:
        """ヘルスチェック設定を取得"""
        return {
            "checks": [
                "database",
                "email",
                "disk_space",
                "memory",
            ],
            "timeout": 30,
            "interval": 60,
        }


# Performance configuration
class PerformanceConfig:
    """パフォーマンス設定"""
    
    @staticmethod
    def get_performance_config() -> dict:
        """パフォーマンス設定を取得"""
        return {
            "workers": 1,  # Renderの無料プランでは1ワーカー
            "worker_class": "uvicorn.workers.UvicornWorker",
            "worker_connections": 1000,
            "max_requests": 1000,
            "max_requests_jitter": 100,
            "timeout": 30,
            "keepalive": 2,
            "preload_app": True,
        }


# Create settings instance
settings = ProductionSettings()

# Export configurations
database_config = DatabaseConfig.get_database_config(settings)
logging_config = LoggingConfig.get_logging_config(settings)
security_headers = SecurityConfig.get_security_headers()
health_check_config = HealthCheckConfig.get_health_check_config()
performance_config = PerformanceConfig.get_performance_config()