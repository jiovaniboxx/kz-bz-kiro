"""
イベントバス実装
アプリケーション内でのイベント駆動アーキテクチャをサポート
"""

from typing import Dict, List, Callable, Any
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Event:
    """イベントベースクラス"""
    
    def __init__(self, event_type: str, data: Dict[str, Any] = None):
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = datetime.now()
        self.event_id = f"{event_type}_{self.timestamp.timestamp()}"


class EventBus:
    """イベントバス実装"""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._async_handlers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable):
        """イベントハンドラーを登録"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Handler registered for event type: {event_type}")
    
    def subscribe_async(self, event_type: str, handler: Callable):
        """非同期イベントハンドラーを登録"""
        if event_type not in self._async_handlers:
            self._async_handlers[event_type] = []
        self._async_handlers[event_type].append(handler)
        logger.info(f"Async handler registered for event type: {event_type}")
    
    def publish(self, event: Event):
        """イベントを発行（同期）"""
        logger.info(f"Publishing event: {event.event_type}")
        
        # 同期ハンドラーを実行
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")
    
    async def publish_async(self, event: Event):
        """イベントを発行（非同期）"""
        logger.info(f"Publishing async event: {event.event_type}")
        
        # 非同期ハンドラーを実行
        if event.event_type in self._async_handlers:
            tasks = []
            for handler in self._async_handlers[event.event_type]:
                try:
                    task = asyncio.create_task(handler(event))
                    tasks.append(task)
                except Exception as e:
                    logger.error(f"Error creating task for event handler: {e}")
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """イベントハンドラーの登録を解除"""
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logger.info(f"Handler unregistered for event type: {event_type}")
    
    def unsubscribe_async(self, event_type: str, handler: Callable):
        """非同期イベントハンドラーの登録を解除"""
        if event_type in self._async_handlers and handler in self._async_handlers[event_type]:
            self._async_handlers[event_type].remove(handler)
            logger.info(f"Async handler unregistered for event type: {event_type}")


# グローバルイベントバスインスタンス
event_bus = EventBus()


# 便利な関数
def publish_event(event_type: str, data: Dict[str, Any] = None):
    """イベントを発行する便利関数"""
    event = Event(event_type, data)
    event_bus.publish(event)


async def publish_event_async(event_type: str, data: Dict[str, Any] = None):
    """非同期でイベントを発行する便利関数"""
    event = Event(event_type, data)
    await event_bus.publish_async(event)


# 定義済みイベントタイプ
class EventTypes:
    """アプリケーションで使用するイベントタイプ定数"""
    
    # 問い合わせ関連
    CONTACT_CREATED = "contact_created"
    CONTACT_UPDATED = "contact_updated"
    CONTACT_STATUS_CHANGED = "contact_status_changed"
    
    # 認証関連
    USER_LOGGED_IN = "user_logged_in"
    USER_LOGGED_OUT = "user_logged_out"
    LOGIN_FAILED = "login_failed"
    
    # システム関連
    SYSTEM_ERROR = "system_error"
    SYSTEM_WARNING = "system_warning"
    HEALTH_CHECK_FAILED = "health_check_failed"
    
    # 監視関連
    PERFORMANCE_ALERT = "performance_alert"
    SECURITY_ALERT = "security_alert"
    UPTIME_ALERT = "uptime_alert"