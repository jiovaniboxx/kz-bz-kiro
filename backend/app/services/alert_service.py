"""
アラートサービス
"""
import asyncio
import smtplib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import json
from pathlib import Path

from app.core.logging import log_error, ErrorCategory

class AlertSeverity(Enum):
    """アラート重要度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertChannel(Enum):
    """アラート通知チャンネル"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"

@dataclass
class AlertRule:
    """アラートルール"""
    name: str
    condition: str
    severity: AlertSeverity
    channels: List[AlertChannel]
    cooldown_minutes: int = 30
    enabled: bool = True

@dataclass
class Alert:
    """アラート"""
    id: str
    rule_name: str
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

class AlertService:
    """アラートサービス"""
    
    def __init__(self, config_file: str = "logs/alert_config.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(exist_ok=True)
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.last_alert_times: Dict[str, datetime] = {}
        self.load_config()
        self.setup_default_rules()
    
    def load_config(self):
        """設定を読み込み"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.rules = {
                        name: AlertRule(
                            name=rule['name'],
                            condition=rule['condition'],
                            severity=AlertSeverity(rule['severity']),
                            channels=[AlertChannel(ch) for ch in rule['channels']],
                            cooldown_minutes=rule.get('cooldown_minutes', 30),
                            enabled=rule.get('enabled', True)
                        )
                        for name, rule in config.get('rules', {}).items()
                    }
        except Exception as e:
            log_error(
                error=e,
                category=ErrorCategory.SYSTEM,
                additional_data={"operation": "load_alert_config"}
            )
    
    def save_config(self):
        """設定を保存"""
        try:
            config = {
                'rules': {
                    name: {
                        'name': rule.name,
                        'condition': rule.condition,
                        'severity': rule.severity.value,
                        'channels': [ch.value for ch in rule.channels],
                        'cooldown_minutes': rule.cooldown_minutes,
                        'enabled': rule.enabled
                    }
                    for name, rule in self.rules.items()
                }
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            log_error(
                error=e,
                category=ErrorCategory.SYSTEM,
                additional_data={"operation": "save_alert_config"}
            )
    
    def setup_default_rules(self):
        """デフォルトのアラートルールを設定"""
        default_rules = [
            AlertRule(
                name="system_down",
                condition="system_status == 'unhealthy'",
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=15
            ),
            AlertRule(
                name="high_cpu_usage",
                condition="cpu_usage > 90",
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=30
            ),
            AlertRule(
                name="high_memory_usage",
                condition="memory_usage > 90",
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=30
            ),
            AlertRule(
                name="disk_space_low",
                condition="disk_usage > 95",
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=60
            ),
            AlertRule(
                name="database_connection_failed",
                condition="database_status == 'unhealthy'",
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=10
            ),
            AlertRule(
                name="consecutive_errors",
                condition="consecutive_errors >= 5",
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL],
                cooldown_minutes=20
            )
        ]
        
        for rule in default_rules:
            if rule.name not in self.rules:
                self.rules[rule.name] = rule
        
        self.save_config()
    
    async def trigger_alert(
        self,
        rule_name: str,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Alert]:
        """アラートをトリガー"""
        rule = self.rules.get(rule_name)
        if not rule or not rule.enabled:
            return None
        
        # クールダウンチェック
        last_alert_time = self.last_alert_times.get(rule_name)
        if last_alert_time:
            time_since_last = datetime.now() - last_alert_time
            if time_since_last < timedelta(minutes=rule.cooldown_minutes):
                return None
        
        # アラートを作成
        alert_id = f"{rule_name}_{int(datetime.now().timestamp())}"
        alert = Alert(
            id=alert_id,
            rule_name=rule_name,
            severity=rule.severity,
            title=title,
            message=message,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        # アクティブアラートに追加
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        self.last_alert_times[rule_name] = alert.timestamp
        
        # 通知を送信
        await self._send_notifications(alert, rule)
        
        return alert
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """アラートを解決"""
        alert = self.active_alerts.get(alert_id)
        if not alert:
            return False
        
        alert.resolved = True
        alert.resolved_at = datetime.now()
        
        # アクティブアラートから削除
        del self.active_alerts[alert_id]
        
        return True
    
    async def _send_notifications(self, alert: Alert, rule: AlertRule):
        """通知を送信"""
        for channel in rule.channels:
            try:
                if channel == AlertChannel.EMAIL:
                    await self._send_email_notification(alert)
                elif channel == AlertChannel.SLACK:
                    await self._send_slack_notification(alert)
                elif channel == AlertChannel.WEBHOOK:
                    await self._send_webhook_notification(alert)
                # SMS は将来実装
                
            except Exception as e:
                log_error(
                    error=e,
                    category=ErrorCategory.SYSTEM,
                    additional_data={
                        "operation": "send_alert_notification",
                        "channel": channel.value,
                        "alert_id": alert.id
                    }
                )
    
    async def _send_email_notification(self, alert: Alert):
        """メール通知を送信"""
        # 環境変数から設定を取得（実装時に追加）
        smtp_server = "smtp.gmail.com"  # 設定から取得
        smtp_port = 587
        smtp_username = "your-email@gmail.com"  # 設定から取得
        smtp_password = "your-app-password"  # 設定から取得
        recipient_emails = ["admin@example.com"]  # 設定から取得
        
        try:
            # メール作成
            msg = MimeMultipart()
            msg['From'] = smtp_username
            msg['To'] = ", ".join(recipient_emails)
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            body = f"""
アラートが発生しました。

重要度: {alert.severity.value.upper()}
タイトル: {alert.title}
メッセージ: {alert.message}
発生時刻: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
ルール: {alert.rule_name}

詳細情報:
{json.dumps(alert.metadata, ensure_ascii=False, indent=2) if alert.metadata else 'なし'}

このメールは自動送信されています。
            """
            
            msg.attach(MimeText(body, 'plain', 'utf-8'))
            
            # SMTP送信（開発環境では実際に送信しない）
            import os
            if os.getenv("ENVIRONMENT") == "production":
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
                server.quit()
            else:
                print(f"[DEV] Email notification would be sent: {alert.title}")
                
        except Exception as e:
            raise Exception(f"Failed to send email notification: {str(e)}")
    
    async def _send_slack_notification(self, alert: Alert):
        """Slack通知を送信"""
        # Slack Webhook URL（設定から取得）
        webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
        
        try:
            import aiohttp
            
            color_map = {
                AlertSeverity.LOW: "#36a64f",      # green
                AlertSeverity.MEDIUM: "#ff9500",   # orange
                AlertSeverity.HIGH: "#ff0000",     # red
                AlertSeverity.CRITICAL: "#8B0000"  # dark red
            }
            
            payload = {
                "attachments": [
                    {
                        "color": color_map.get(alert.severity, "#808080"),
                        "title": alert.title,
                        "text": alert.message,
                        "fields": [
                            {
                                "title": "重要度",
                                "value": alert.severity.value.upper(),
                                "short": True
                            },
                            {
                                "title": "発生時刻",
                                "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                                "short": True
                            }
                        ],
                        "footer": "英会話カフェ監視システム",
                        "ts": int(alert.timestamp.timestamp())
                    }
                ]
            }
            
            # 開発環境では実際に送信しない
            import os
            if os.getenv("ENVIRONMENT") == "production":
                async with aiohttp.ClientSession() as session:
                    async with session.post(webhook_url, json=payload) as response:
                        if response.status != 200:
                            raise Exception(f"Slack API returned status {response.status}")
            else:
                print(f"[DEV] Slack notification would be sent: {alert.title}")
                
        except Exception as e:
            raise Exception(f"Failed to send Slack notification: {str(e)}")
    
    async def _send_webhook_notification(self, alert: Alert):
        """Webhook通知を送信"""
        webhook_url = "https://your-webhook-endpoint.com/alerts"  # 設定から取得
        
        try:
            import aiohttp
            
            payload = {
                "alert_id": alert.id,
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "title": alert.title,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "metadata": alert.metadata
            }
            
            # 開発環境では実際に送信しない
            import os
            if os.getenv("ENVIRONMENT") == "production":
                async with aiohttp.ClientSession() as session:
                    async with session.post(webhook_url, json=payload) as response:
                        if response.status not in [200, 201, 202]:
                            raise Exception(f"Webhook returned status {response.status}")
            else:
                print(f"[DEV] Webhook notification would be sent: {alert.title}")
                
        except Exception as e:
            raise Exception(f"Failed to send webhook notification: {str(e)}")
    
    def get_active_alerts(self) -> List[Alert]:
        """アクティブなアラートを取得"""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """アラート履歴を取得"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]
    
    async def test_alert(self, channel: AlertChannel = AlertChannel.EMAIL) -> bool:
        """テストアラートを送信"""
        test_alert = Alert(
            id="test_alert",
            rule_name="test",
            severity=AlertSeverity.LOW,
            title="テストアラート",
            message="これはアラート機能のテストです。",
            timestamp=datetime.now(),
            metadata={"test": True}
        )
        
        try:
            if channel == AlertChannel.EMAIL:
                await self._send_email_notification(test_alert)
            elif channel == AlertChannel.SLACK:
                await self._send_slack_notification(test_alert)
            elif channel == AlertChannel.WEBHOOK:
                await self._send_webhook_notification(test_alert)
            
            return True
        except Exception as e:
            log_error(
                error=e,
                category=ErrorCategory.SYSTEM,
                additional_data={"operation": "test_alert", "channel": channel.value}
            )
            return False

# グローバルインスタンス
alert_service = AlertService()