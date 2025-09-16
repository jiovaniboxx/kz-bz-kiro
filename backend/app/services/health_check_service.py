"""
ヘルスチェックサービス
"""
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.logging import log_error, ErrorCategory

class HealthStatus(Enum):
    """ヘルス状態"""
    HEALTHY = "healthy"
    WARNING = "warning"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class HealthCheckResult:
    """ヘルスチェック結果"""
    name: str
    status: HealthStatus
    response_time: float
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class HealthCheckService:
    """ヘルスチェックサービス"""
    
    def __init__(self):
        self.checks = {}
        self.last_results = {}
        self.setup_default_checks()
    
    def setup_default_checks(self):
        """デフォルトのヘルスチェックを設定"""
        self.register_check("database", self.check_database)
        self.register_check("disk_space", self.check_disk_space)
        self.register_check("memory", self.check_memory)
        self.register_check("external_apis", self.check_external_apis)
    
    def register_check(self, name: str, check_function):
        """ヘルスチェック関数を登録"""
        self.checks[name] = check_function
    
    async def run_all_checks(self, db_session: AsyncSession = None) -> Dict[str, HealthCheckResult]:
        """全てのヘルスチェックを実行"""
        results = {}
        
        for name, check_function in self.checks.items():
            try:
                start_time = time.time()
                
                if name == "database" and db_session:
                    result = await check_function(db_session)
                else:
                    result = await check_function()
                
                response_time = time.time() - start_time
                result.response_time = response_time
                
                results[name] = result
                self.last_results[name] = result
                
            except Exception as e:
                log_error(
                    error=e,
                    category=ErrorCategory.SYSTEM,
                    additional_data={"health_check": name}
                )
                
                results[name] = HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    response_time=0,
                    message=f"Health check failed: {str(e)}"
                )
        
        return results
    
    async def check_database(self, db_session: AsyncSession) -> HealthCheckResult:
        """データベース接続チェック"""
        try:
            # 簡単なクエリを実行
            result = await db_session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            
            if row and row.test == 1:
                return HealthCheckResult(
                    name="database",
                    status=HealthStatus.HEALTHY,
                    response_time=0,
                    message="Database connection successful"
                )
            else:
                return HealthCheckResult(
                    name="database",
                    status=HealthStatus.UNHEALTHY,
                    response_time=0,
                    message="Database query returned unexpected result"
                )
                
        except Exception as e:
            return HealthCheckResult(
                name="database",
                status=HealthStatus.UNHEALTHY,
                response_time=0,
                message=f"Database connection failed: {str(e)}"
            )
    
    async def check_disk_space(self) -> HealthCheckResult:
        """ディスク容量チェック"""
        try:
            import psutil
            
            disk_usage = psutil.disk_usage('/')
            usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            if usage_percent > 95:
                status = HealthStatus.UNHEALTHY
                message = f"Disk usage critical: {usage_percent:.1f}%"
            elif usage_percent > 85:
                status = HealthStatus.WARNING
                message = f"Disk usage high: {usage_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {usage_percent:.1f}%"
            
            return HealthCheckResult(
                name="disk_space",
                status=status,
                response_time=0,
                message=message,
                details={
                    "usage_percent": usage_percent,
                    "free_gb": disk_usage.free / (1024**3),
                    "total_gb": disk_usage.total / (1024**3)
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="disk_space",
                status=HealthStatus.UNKNOWN,
                response_time=0,
                message=f"Disk check failed: {str(e)}"
            )
    
    async def check_memory(self) -> HealthCheckResult:
        """メモリ使用量チェック"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            if usage_percent > 95:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage critical: {usage_percent:.1f}%"
            elif usage_percent > 85:
                status = HealthStatus.WARNING
                message = f"Memory usage high: {usage_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {usage_percent:.1f}%"
            
            return HealthCheckResult(
                name="memory",
                status=status,
                response_time=0,
                message=message,
                details={
                    "usage_percent": usage_percent,
                    "available_gb": memory.available / (1024**3),
                    "total_gb": memory.total / (1024**3)
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="memory",
                status=HealthStatus.UNKNOWN,
                response_time=0,
                message=f"Memory check failed: {str(e)}"
            )
    
    async def check_external_apis(self) -> HealthCheckResult:
        """外部API接続チェック"""
        try:
            # 将来的に外部APIが追加された場合のチェック
            # 現在は基本的なインターネット接続チェック
            
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Google DNS への接続テスト
                async with session.get('https://dns.google/resolve?name=example.com&type=A') as response:
                    if response.status == 200:
                        return HealthCheckResult(
                            name="external_apis",
                            status=HealthStatus.HEALTHY,
                            response_time=0,
                            message="External connectivity OK"
                        )
                    else:
                        return HealthCheckResult(
                            name="external_apis",
                            status=HealthStatus.WARNING,
                            response_time=0,
                            message=f"External API returned status {response.status}"
                        )
                        
        except asyncio.TimeoutError:
            return HealthCheckResult(
                name="external_apis",
                status=HealthStatus.WARNING,
                response_time=0,
                message="External API timeout"
            )
        except Exception as e:
            return HealthCheckResult(
                name="external_apis",
                status=HealthStatus.WARNING,
                response_time=0,
                message=f"External API check failed: {str(e)}"
            )
    
    def get_overall_status(self, results: Dict[str, HealthCheckResult]) -> HealthStatus:
        """全体的なヘルス状態を判定"""
        if not results:
            return HealthStatus.UNKNOWN
        
        statuses = [result.status for result in results.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.WARNING

# グローバルインスタンス
health_check_service = HealthCheckService()