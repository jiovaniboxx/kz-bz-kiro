"""
アップタイム監視サービス
"""
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import json
from pathlib import Path

from app.core.logging import log_error, log_security_event, ErrorCategory
from app.services.health_check_service import health_check_service, HealthStatus

@dataclass
class UptimeRecord:
    """アップタイム記録"""
    timestamp: datetime
    status: HealthStatus
    response_time: float
    details: Dict[str, any] = field(default_factory=dict)

@dataclass
class UptimeStats:
    """アップタイム統計"""
    uptime_percentage: float
    total_checks: int
    successful_checks: int
    failed_checks: int
    average_response_time: float
    last_downtime: Optional[datetime] = None
    longest_downtime: Optional[timedelta] = None

class UptimeMonitor:
    """アップタイム監視サービス"""
    
    def __init__(self, data_file: str = "logs/uptime.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(exist_ok=True)
        self.records: List[UptimeRecord] = []
        self.is_monitoring = False
        self.monitor_task = None
        self.load_records()
    
    def load_records(self):
        """記録をファイルから読み込み"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.records = [
                        UptimeRecord(
                            timestamp=datetime.fromisoformat(record['timestamp']),
                            status=HealthStatus(record['status']),
                            response_time=record['response_time'],
                            details=record.get('details', {})
                        )
                        for record in data
                    ]
        except Exception as e:
            log_error(
                error=e,
                category=ErrorCategory.SYSTEM,
                additional_data={"operation": "load_uptime_records"}
            )
            self.records = []
    
    def save_records(self):
        """記録をファイルに保存"""
        try:
            # 最新の1000件のみ保持
            recent_records = self.records[-1000:]
            
            data = [
                {
                    'timestamp': record.timestamp.isoformat(),
                    'status': record.status.value,
                    'response_time': record.response_time,
                    'details': record.details
                }
                for record in recent_records
            ]
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.records = recent_records
            
        except Exception as e:
            log_error(
                error=e,
                category=ErrorCategory.SYSTEM,
                additional_data={"operation": "save_uptime_records"}
            )
    
    async def start_monitoring(self, interval: int = 60):
        """監視を開始"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop(interval))
        
        log_security_event(
            event_type="uptime_monitoring_started",
            severity="INFO",
            additional_data={"interval": interval}
        )
    
    async def stop_monitoring(self):
        """監視を停止"""
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        self.save_records()
        
        log_security_event(
            event_type="uptime_monitoring_stopped",
            severity="INFO"
        )
    
    async def _monitor_loop(self, interval: int):
        """監視ループ"""
        while self.is_monitoring:
            try:
                await self._perform_check()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                log_error(
                    error=e,
                    category=ErrorCategory.SYSTEM,
                    additional_data={"operation": "uptime_monitor_loop"}
                )
                await asyncio.sleep(interval)
    
    async def _perform_check(self):
        """ヘルスチェックを実行して記録"""
        start_time = time.time()
        
        try:
            # ヘルスチェックを実行
            results = await health_check_service.run_all_checks()
            overall_status = health_check_service.get_overall_status(results)
            
            response_time = time.time() - start_time
            
            # 記録を追加
            record = UptimeRecord(
                timestamp=datetime.now(),
                status=overall_status,
                response_time=response_time,
                details={
                    'check_results': {
                        name: {
                            'status': result.status.value,
                            'message': result.message,
                            'response_time': result.response_time
                        }
                        for name, result in results.items()
                    }
                }
            )
            
            self.records.append(record)
            
            # ダウンタイムの検出
            if overall_status == HealthStatus.UNHEALTHY:
                await self._handle_downtime(record)
            
            # 定期的に保存
            if len(self.records) % 10 == 0:
                self.save_records()
                
        except Exception as e:
            # ヘルスチェック自体が失敗した場合
            record = UptimeRecord(
                timestamp=datetime.now(),
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                details={'error': str(e)}
            )
            
            self.records.append(record)
            await self._handle_downtime(record)
    
    async def _handle_downtime(self, record: UptimeRecord):
        """ダウンタイムの処理"""
        # 連続したダウンタイムかチェック
        recent_records = self.records[-5:]  # 最新5件をチェック
        consecutive_failures = sum(
            1 for r in recent_records 
            if r.status == HealthStatus.UNHEALTHY
        )
        
        if consecutive_failures >= 3:
            # 3回連続で失敗した場合はアラート
            log_security_event(
                event_type="system_downtime_detected",
                severity="CRITICAL",
                additional_data={
                    "consecutive_failures": consecutive_failures,
                    "last_error": record.details.get('error'),
                    "timestamp": record.timestamp.isoformat()
                }
            )
    
    def get_uptime_stats(self, hours: int = 24) -> UptimeStats:
        """アップタイム統計を取得"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_records = [
            record for record in self.records 
            if record.timestamp >= cutoff_time
        ]
        
        if not recent_records:
            return UptimeStats(
                uptime_percentage=0.0,
                total_checks=0,
                successful_checks=0,
                failed_checks=0,
                average_response_time=0.0
            )
        
        total_checks = len(recent_records)
        successful_checks = sum(
            1 for record in recent_records 
            if record.status in [HealthStatus.HEALTHY, HealthStatus.WARNING]
        )
        failed_checks = total_checks - successful_checks
        
        uptime_percentage = (successful_checks / total_checks) * 100 if total_checks > 0 else 0
        
        response_times = [record.response_time for record in recent_records]
        average_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # 最後のダウンタイムを検索
        last_downtime = None
        for record in reversed(recent_records):
            if record.status == HealthStatus.UNHEALTHY:
                last_downtime = record.timestamp
                break
        
        # 最長ダウンタイムを計算
        longest_downtime = self._calculate_longest_downtime(recent_records)
        
        return UptimeStats(
            uptime_percentage=uptime_percentage,
            total_checks=total_checks,
            successful_checks=successful_checks,
            failed_checks=failed_checks,
            average_response_time=average_response_time,
            last_downtime=last_downtime,
            longest_downtime=longest_downtime
        )
    
    def _calculate_longest_downtime(self, records: List[UptimeRecord]) -> Optional[timedelta]:
        """最長ダウンタイムを計算"""
        if not records:
            return None
        
        longest_downtime = timedelta(0)
        current_downtime_start = None
        
        for record in records:
            if record.status == HealthStatus.UNHEALTHY:
                if current_downtime_start is None:
                    current_downtime_start = record.timestamp
            else:
                if current_downtime_start is not None:
                    downtime_duration = record.timestamp - current_downtime_start
                    if downtime_duration > longest_downtime:
                        longest_downtime = downtime_duration
                    current_downtime_start = None
        
        # 現在もダウンタイム中の場合
        if current_downtime_start is not None:
            current_downtime = datetime.now() - current_downtime_start
            if current_downtime > longest_downtime:
                longest_downtime = current_downtime
        
        return longest_downtime if longest_downtime > timedelta(0) else None
    
    def get_recent_records(self, limit: int = 100) -> List[UptimeRecord]:
        """最近の記録を取得"""
        return self.records[-limit:] if self.records else []

# グローバルインスタンス
uptime_monitor = UptimeMonitor()