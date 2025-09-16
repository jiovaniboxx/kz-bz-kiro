"""
監視・ヘルスチェックAPI
"""
import time
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db_session
from app.services.auth_service import get_current_admin
from app.domain.admin import Admin
from app.services.health_check_service import health_check_service
from app.services.uptime_monitor import uptime_monitor
from app.services.alert_service import alert_service, AlertChannel

router = APIRouter(prefix="/api/monitoring", tags=["監視"])

# レスポンスモデル
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    uptime: float
    checks: Dict[str, Any]

class SystemMetricsResponse(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int
    timestamp: str

class ErrorLogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    category: str
    request_id: str

class ErrorLogsResponse(BaseModel):
    logs: List[ErrorLogEntry]
    total: int
    page: int
    per_page: int

# アプリケーション開始時刻
app_start_time = time.time()

@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: AsyncSession = Depends(get_db_session)):
    """ヘルスチェック"""
    # 新しいヘルスチェックサービスを使用
    results = await health_check_service.run_all_checks(db)
    overall_status = health_check_service.get_overall_status(results)
    
    # レスポンス形式に変換
    checks = {}
    for name, result in results.items():
        checks[name] = {
            "status": result.status.value,
            "response_time": f"{result.response_time:.3f}s",
            "message": result.message
        }
        if result.details:
            checks[name].update(result.details)
    
    return HealthCheckResponse(
        status=overall_status.value,
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        uptime=time.time() - app_start_time,
        checks=checks
    )

@router.get("/health/simple")
async def simple_health_check():
    """シンプルなヘルスチェック（ロードバランサー用）"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@router.get("/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics(admin: Admin = Depends(get_current_admin)):
    """システムメトリクス取得（管理者のみ）"""
    try:
        # CPU使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # メモリ使用率
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # ディスク使用率
        disk = psutil.disk_usage('/')
        disk_usage = (disk.used / disk.total) * 100
        
        # アクティブな接続数（概算）
        active_connections = len(psutil.net_connections())
        
        return SystemMetricsResponse(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            active_connections=active_connections,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"メトリクス取得に失敗しました: {str(e)}"
        )

@router.get("/logs/errors", response_model=ErrorLogsResponse)
async def get_error_logs(
    page: int = 1,
    per_page: int = 50,
    level: str = None,
    admin: Admin = Depends(get_current_admin)
):
    """エラーログ取得（管理者のみ）"""
    try:
        import json
        from pathlib import Path
        
        log_file = Path("logs/error.log")
        if not log_file.exists():
            return ErrorLogsResponse(logs=[], total=0, page=page, per_page=per_page)
        
        # ログファイルを読み込み
        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    # ログエントリをパース
                    parts = line.strip().split(' - ', 3)
                    if len(parts) >= 4:
                        timestamp = parts[0]
                        log_level = parts[2]
                        message = parts[3]
                        
                        # JSONメッセージの場合はパース
                        try:
                            json_data = json.loads(message)
                            category = json_data.get('category', 'unknown')
                            request_id = json_data.get('request_id', '')
                            message = json_data.get('error_message', message)
                        except:
                            category = 'unknown'
                            request_id = ''
                        
                        # レベルフィルター
                        if level and log_level.upper() != level.upper():
                            continue
                        
                        logs.append(ErrorLogEntry(
                            timestamp=timestamp,
                            level=log_level,
                            message=message,
                            category=category,
                            request_id=request_id
                        ))
                except Exception:
                    continue
        
        # 最新順にソート
        logs.reverse()
        
        # ページネーション
        total = len(logs)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_logs = logs[start:end]
        
        return ErrorLogsResponse(
            logs=paginated_logs,
            total=total,
            page=page,
            per_page=per_page
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"エラーログの取得に失敗しました: {str(e)}"
        )

@router.post("/alerts/test")
async def test_alert(admin: Admin = Depends(get_current_admin)):
    """アラート機能のテスト（管理者のみ）"""
    if admin.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です"
        )
    
    try:
        from app.core.logging import log_error, ErrorCategory
        
        # テストエラーを生成
        test_error = Exception("これはアラート機能のテストエラーです")
        log_error(
            error=test_error,
            category=ErrorCategory.SYSTEM,
            user_id=admin.id,
            additional_data={
                "test": True,
                "triggered_by": admin.username
            }
        )
        
        return {
            "message": "テストアラートを送信しました",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"テストアラートの送信に失敗しました: {str(e)}"
        )

@router.get("/uptime")
async def get_uptime_stats(
    hours: int = 24,
    admin: Admin = Depends(get_current_admin)
):
    """アップタイム統計取得（管理者のみ）"""
    try:
        stats = uptime_monitor.get_uptime_stats(hours)
        recent_records = uptime_monitor.get_recent_records(50)
        
        return {
            "uptime_percentage": stats.uptime_percentage,
            "total_checks": stats.total_checks,
            "successful_checks": stats.successful_checks,
            "failed_checks": stats.failed_checks,
            "average_response_time": stats.average_response_time,
            "last_downtime": stats.last_downtime.isoformat() if stats.last_downtime else None,
            "longest_downtime_minutes": stats.longest_downtime.total_seconds() / 60 if stats.longest_downtime else None,
            "recent_records": [
                {
                    "timestamp": record.timestamp.isoformat(),
                    "status": record.status.value,
                    "response_time": record.response_time
                }
                for record in recent_records
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"アップタイム統計の取得に失敗しました: {str(e)}"
        )

@router.get("/alerts")
async def get_alerts(admin: Admin = Depends(get_current_admin)):
    """アラート一覧取得（管理者のみ）"""
    try:
        active_alerts = alert_service.get_active_alerts()
        alert_history = alert_service.get_alert_history(24)
        
        return {
            "active_alerts": [
                {
                    "id": alert.id,
                    "rule_name": alert.rule_name,
                    "severity": alert.severity.value,
                    "title": alert.title,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "resolved": alert.resolved,
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
                }
                for alert in active_alerts
            ],
            "recent_history": [
                {
                    "id": alert.id,
                    "rule_name": alert.rule_name,
                    "severity": alert.severity.value,
                    "title": alert.title,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "resolved": alert.resolved,
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
                }
                for alert in alert_history
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"アラート一覧の取得に失敗しました: {str(e)}"
        )

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    admin: Admin = Depends(get_current_admin)
):
    """アラートを解決（管理者のみ）"""
    try:
        success = await alert_service.resolve_alert(alert_id)
        if success:
            return {"message": "アラートを解決しました", "alert_id": alert_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="アラートが見つかりません"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"アラートの解決に失敗しました: {str(e)}"
        )

@router.post("/monitoring/start")
async def start_monitoring(admin: Admin = Depends(get_current_admin)):
    """監視を開始（管理者のみ）"""
    if admin.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です"
        )
    
    try:
        await uptime_monitor.start_monitoring(interval=60)
        return {"message": "監視を開始しました"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"監視の開始に失敗しました: {str(e)}"
        )

@router.post("/monitoring/stop")
async def stop_monitoring(admin: Admin = Depends(get_current_admin)):
    """監視を停止（管理者のみ）"""
    if admin.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です"
        )
    
    try:
        await uptime_monitor.stop_monitoring()
        return {"message": "監視を停止しました"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"監視の停止に失敗しました: {str(e)}"
        )

@router.post("/alerts/test/{channel}")
async def test_alert_channel(
    channel: str,
    admin: Admin = Depends(get_current_admin)
):
    """アラート通知チャンネルのテスト（管理者のみ）"""
    if admin.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です"
        )
    
    try:
        channel_enum = AlertChannel(channel)
        success = await alert_service.test_alert(channel_enum)
        
        if success:
            return {
                "message": f"{channel}チャンネルのテストアラートを送信しました",
                "channel": channel
            }
        else:
            return {
                "message": f"{channel}チャンネルのテストに失敗しました",
                "channel": channel
            }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"無効なチャンネル: {channel}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"テストアラートの送信に失敗しました: {str(e)}"
        )

@router.get("/status")
async def get_application_status():
    """アプリケーション状態取得"""
    return {
        "application": "英会話カフェ API",
        "version": "1.0.0",
        "status": "running",
        "uptime": time.time() - app_start_time,
        "timestamp": datetime.now().isoformat(),
        "environment": "development"  # 環境変数から取得するように変更予定
    }