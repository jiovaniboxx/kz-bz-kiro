/**
 * Security Provider Component
 *
 * セキュリティ機能を提供するプロバイダーコンポーネント
 */

'use client';

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from 'react';
import { CSRFProtection, SecurityLogger } from '@/utils/security';
import { initializeApiClient } from '@/lib/api-client';

interface SecurityContextType {
  csrfToken: string | null;
  isSecurityInitialized: boolean;
  reportSecurityEvent: (
    event: string,
    details?: Record<string, any>,
    severity?: 'low' | 'medium' | 'high' | 'critical'
  ) => void;
}

const SecurityContext = createContext<SecurityContextType | undefined>(
  undefined
);

interface SecurityProviderProps {
  children: ReactNode;
}

/**
 * セキュリティプロバイダーコンポーネント
 */
export function SecurityProvider({ children }: SecurityProviderProps) {
  const [csrfToken, setCsrfToken] = useState<string | null>(null);
  const [isSecurityInitialized, setIsSecurityInitialized] = useState(false);

  useEffect(() => {
    initializeSecurity();
  }, []);

  /**
   * セキュリティ機能を初期化
   */
  const initializeSecurity = async () => {
    try {
      // CSRFトークンを生成または取得
      let token = CSRFProtection.getToken();
      if (!token) {
        token = CSRFProtection.generateToken();
        CSRFProtection.setToken(token);
      }
      setCsrfToken(token);

      // APIクライアントを初期化
      await initializeApiClient();

      // セキュリティイベントハンドラーを設定
      setupSecurityEventHandlers();

      setIsSecurityInitialized(true);

      SecurityLogger.logSecurityEvent(
        'security_provider_initialized',
        {},
        'low'
      );
    } catch (error) {
      SecurityLogger.logSecurityEvent(
        'security_initialization_failed',
        {
          error: String(error),
        },
        'high'
      );
    }
  };

  /**
   * セキュリティイベントハンドラーを設定
   */
  const setupSecurityEventHandlers = () => {
    // ページ離脱時の処理
    const handleBeforeUnload = () => {
      SecurityLogger.logSecurityEvent(
        'page_unload',
        {
          url: window.location.href,
          duration: Date.now() - (window as any).pageLoadTime,
        },
        'low'
      );
    };

    // エラーハンドリング
    const handleError = (event: ErrorEvent) => {
      SecurityLogger.logSecurityEvent(
        'javascript_error',
        {
          message: event.message,
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
          stack: event.error?.stack,
        },
        'medium'
      );
    };

    // 未処理のPromise拒否
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      SecurityLogger.logSecurityEvent(
        'unhandled_promise_rejection',
        {
          reason: String(event.reason),
          stack: event.reason?.stack,
        },
        'medium'
      );
    };

    // コンソールエラーの監視
    const originalConsoleError = console.error;
    console.error = (...args: any[]) => {
      SecurityLogger.logSecurityEvent(
        'console_error',
        {
          arguments: args.map(arg => String(arg)),
        },
        'low'
      );
      originalConsoleError.apply(console, args);
    };

    // イベントリスナーを追加
    window.addEventListener('beforeunload', handleBeforeUnload);
    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    // ページロード時間を記録
    (window as any).pageLoadTime = Date.now();

    // クリーンアップ関数を返す
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      window.removeEventListener('error', handleError);
      window.removeEventListener(
        'unhandledrejection',
        handleUnhandledRejection
      );
      console.error = originalConsoleError;
    };
  };

  /**
   * セキュリティイベントを報告
   */
  const reportSecurityEvent = (
    event: string,
    details: Record<string, any> = {},
    severity: 'low' | 'medium' | 'high' | 'critical' = 'medium'
  ) => {
    SecurityLogger.logSecurityEvent(event, details, severity);
  };

  const contextValue: SecurityContextType = {
    csrfToken,
    isSecurityInitialized,
    reportSecurityEvent,
  };

  return (
    <SecurityContext.Provider value={contextValue}>
      {children}
    </SecurityContext.Provider>
  );
}

/**
 * セキュリティコンテキストを使用するフック
 */
export function useSecurity() {
  const context = useContext(SecurityContext);
  if (context === undefined) {
    throw new Error('useSecurity must be used within a SecurityProvider');
  }
  return context;
}

/**
 * セキュリティ状態を監視するフック
 */
export function useSecurityMonitoring() {
  const { reportSecurityEvent } = useSecurity();
  const [securityEvents, setSecurityEvents] = useState<
    Array<{
      event: string;
      timestamp: string;
      severity: string;
    }>
  >([]);

  useEffect(() => {
    // セキュリティイベントの監視を開始
    const monitoringInterval = setInterval(() => {
      // パフォーマンス監視
      if (typeof window !== 'undefined' && 'performance' in window) {
        const navigation = performance.getEntriesByType(
          'navigation'
        )[0] as PerformanceNavigationTiming;

        if (navigation) {
          const loadTime = navigation.loadEventEnd - navigation.loadEventStart;

          // 異常に遅いページロード時間を検出
          if (loadTime > 10000) {
            // 10秒以上
            reportSecurityEvent(
              'slow_page_load',
              {
                loadTime,
                url: window.location.href,
              },
              'low'
            );
          }
        }
      }

      // メモリ使用量監視
      if (
        typeof window !== 'undefined' &&
        'performance' in window &&
        'memory' in (performance as any)
      ) {
        const memory = (performance as any).memory;
        const memoryUsage = memory.usedJSHeapSize / memory.totalJSHeapSize;

        // メモリ使用量が90%を超えた場合
        if (memoryUsage > 0.9) {
          reportSecurityEvent(
            'high_memory_usage',
            {
              usedHeapSize: memory.usedJSHeapSize,
              totalHeapSize: memory.totalJSHeapSize,
              usage: memoryUsage,
            },
            'medium'
          );
        }
      }
    }, 30000); // 30秒ごと

    return () => clearInterval(monitoringInterval);
  }, [reportSecurityEvent]);

  return {
    securityEvents,
    reportSecurityEvent,
  };
}

/**
 * セキュリティ警告コンポーネント
 */
export function SecurityWarning({
  message,
  severity = 'medium',
  onDismiss,
}: {
  message: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
  onDismiss?: () => void;
}) {
  const { reportSecurityEvent } = useSecurity();

  useEffect(() => {
    reportSecurityEvent(
      'security_warning_displayed',
      {
        message,
        severity,
      },
      severity
    );
  }, [message, severity, reportSecurityEvent]);

  const severityColors = {
    low: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    medium: 'bg-orange-50 border-orange-200 text-orange-800',
    high: 'bg-red-50 border-red-200 text-red-800',
    critical: 'bg-red-100 border-red-300 text-red-900',
  };

  return (
    <div className={`border-l-4 p-4 ${severityColors[severity]}`}>
      <div className="flex">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="ml-3">
          <p className="text-sm">{message}</p>
        </div>
        {onDismiss && (
          <div className="ml-auto pl-3">
            <div className="-mx-1.5 -my-1.5">
              <button
                type="button"
                className="inline-flex rounded-md p-1.5 hover:bg-opacity-20 focus:outline-none focus:ring-2 focus:ring-offset-2"
                onClick={onDismiss}
              >
                <span className="sr-only">Dismiss</span>
                <svg
                  className="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
