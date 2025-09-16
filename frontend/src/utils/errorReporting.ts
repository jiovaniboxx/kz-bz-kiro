/**
 * エラー報告ユーティリティ
 */

export interface ErrorReport {
  message: string;
  stack?: string;
  url: string;
  timestamp: string;
  userAgent: string;
  userId?: string;
  sessionId?: string;
  additionalData?: Record<string, any>;
}

export interface PerformanceReport {
  name: string;
  duration: number;
  startTime: number;
  url: string;
  timestamp: string;
}

class ErrorReporter {
  private sessionId: string;
  private userId?: string;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.setupGlobalErrorHandlers();
  }

  /**
   * セッションIDを生成
   */
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * ユーザーIDを設定
   */
  setUserId(userId: string): void {
    this.userId = userId;
  }

  /**
   * グローバルエラーハンドラーを設定
   */
  private setupGlobalErrorHandlers(): void {
    if (typeof window === 'undefined') return;

    // JavaScript エラー
    window.addEventListener('error', event => {
      this.reportError({
        message: event.message,
        stack: event.error?.stack,
        url: window.location.href,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        userId: this.userId,
        sessionId: this.sessionId,
        additionalData: {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
          type: 'javascript_error',
        },
      });
    });

    // Promise rejection エラー
    window.addEventListener('unhandledrejection', event => {
      this.reportError({
        message: event.reason?.message || 'Unhandled Promise Rejection',
        stack: event.reason?.stack,
        url: window.location.href,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        userId: this.userId,
        sessionId: this.sessionId,
        additionalData: {
          reason: event.reason,
          type: 'promise_rejection',
        },
      });
    });

    // リソース読み込みエラー
    window.addEventListener(
      'error',
      event => {
        if (event.target !== window) {
          this.reportError({
            message: 'Resource loading error',
            url: window.location.href,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            userId: this.userId,
            sessionId: this.sessionId,
            additionalData: {
              resourceUrl:
                (event.target as any)?.src || (event.target as any)?.href,
              tagName: (event.target as any)?.tagName,
              type: 'resource_error',
            },
          });
        }
      },
      true
    );
  }

  /**
   * エラーを報告
   */
  async reportError(errorReport: ErrorReport): Promise<void> {
    try {
      // ローカルストレージに保存
      this.saveErrorToLocalStorage(errorReport);

      // 本番環境では外部サービス（Sentry等）に送信
      if (process.env.NODE_ENV === 'production') {
        await this.sendToExternalService(errorReport);
      } else {
        console.error('Error Report:', errorReport);
      }
    } catch (e) {
      console.error('Failed to report error:', e);
    }
  }

  /**
   * パフォーマンス問題を報告
   */
  async reportPerformanceIssue(
    performanceReport: PerformanceReport
  ): Promise<void> {
    try {
      // 閾値を超えた場合のみ報告
      const threshold = 3000; // 3秒
      if (performanceReport.duration > threshold) {
        console.warn('Performance Issue:', performanceReport);

        // 本番環境では外部サービスに送信
        if (process.env.NODE_ENV === 'production') {
          await this.sendPerformanceToExternalService(performanceReport);
        }
      }
    } catch (e) {
      console.error('Failed to report performance issue:', e);
    }
  }

  /**
   * カスタムエラーを報告
   */
  async reportCustomError(
    message: string,
    additionalData?: Record<string, any>
  ): Promise<void> {
    const errorReport: ErrorReport = {
      message,
      url: typeof window !== 'undefined' ? window.location.href : '',
      timestamp: new Date().toISOString(),
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
      userId: this.userId,
      sessionId: this.sessionId,
      additionalData: {
        ...additionalData,
        type: 'custom_error',
      },
    };

    await this.reportError(errorReport);
  }

  /**
   * ローカルストレージにエラーを保存
   */
  private saveErrorToLocalStorage(errorReport: ErrorReport): void {
    try {
      const existingErrors = JSON.parse(
        localStorage.getItem('error_reports') || '[]'
      );
      existingErrors.push(errorReport);

      // 最新の50件のみ保持
      const recentErrors = existingErrors.slice(-50);
      localStorage.setItem('error_reports', JSON.stringify(recentErrors));
    } catch (e) {
      console.error('Failed to save error to localStorage:', e);
    }
  }

  /**
   * 外部サービスにエラーを送信
   */
  private async sendToExternalService(errorReport: ErrorReport): Promise<void> {
    // TODO: Sentry、LogRocket、Bugsnag等の実装
    // 現在はコンソールログのみ
    console.error('Would send to external service:', errorReport);
  }

  /**
   * 外部サービスにパフォーマンス情報を送信
   */
  private async sendPerformanceToExternalService(
    performanceReport: PerformanceReport
  ): Promise<void> {
    // TODO: パフォーマンス監視サービスの実装
    console.warn(
      'Would send performance data to external service:',
      performanceReport
    );
  }

  /**
   * 保存されたエラーレポートを取得
   */
  getStoredErrorReports(): ErrorReport[] {
    try {
      return JSON.parse(localStorage.getItem('error_reports') || '[]');
    } catch (e) {
      console.error('Failed to get stored error reports:', e);
      return [];
    }
  }

  /**
   * 保存されたエラーレポートをクリア
   */
  clearStoredErrorReports(): void {
    try {
      localStorage.removeItem('error_reports');
    } catch (e) {
      console.error('Failed to clear stored error reports:', e);
    }
  }
}

// パフォーマンス監視
export class PerformanceMonitor {
  /**
   * ページ読み込み時間を測定
   */
  static measurePageLoad(): void {
    if (typeof window === 'undefined') return;

    window.addEventListener('load', () => {
      const navigation = performance.getEntriesByType(
        'navigation'
      )[0] as PerformanceNavigationTiming;

      const loadTime = navigation.loadEventEnd - navigation.fetchStart;
      const domContentLoaded =
        navigation.domContentLoadedEventEnd - navigation.fetchStart;

      errorReporter.reportPerformanceIssue({
        name: 'page_load',
        duration: loadTime,
        startTime: navigation.fetchStart,
        url: window.location.href,
        timestamp: new Date().toISOString(),
      });

      // Core Web Vitals の測定
      this.measureCoreWebVitals();
    });
  }

  /**
   * Core Web Vitals を測定
   */
  static measureCoreWebVitals(): void {
    // LCP (Largest Contentful Paint)
    new PerformanceObserver(entryList => {
      const entries = entryList.getEntries();
      const lastEntry = entries[entries.length - 1];

      if (lastEntry.startTime > 2500) {
        // 2.5秒を超える場合
        errorReporter.reportPerformanceIssue({
          name: 'lcp',
          duration: lastEntry.startTime,
          startTime: 0,
          url: window.location.href,
          timestamp: new Date().toISOString(),
        });
      }
    }).observe({ entryTypes: ['largest-contentful-paint'] });

    // FID (First Input Delay)
    new PerformanceObserver(entryList => {
      const entries = entryList.getEntries();
      entries.forEach((entry: any) => {
        if (entry.processingStart - entry.startTime > 100) {
          // 100ms を超える場合
          errorReporter.reportPerformanceIssue({
            name: 'fid',
            duration: entry.processingStart - entry.startTime,
            startTime: entry.startTime,
            url: window.location.href,
            timestamp: new Date().toISOString(),
          });
        }
      });
    }).observe({ entryTypes: ['first-input'] });
  }

  /**
   * API呼び出し時間を測定
   */
  static async measureApiCall<T>(
    name: string,
    apiCall: () => Promise<T>
  ): Promise<T> {
    const startTime = performance.now();

    try {
      const result = await apiCall();
      const duration = performance.now() - startTime;

      if (duration > 5000) {
        // 5秒を超える場合
        errorReporter.reportPerformanceIssue({
          name: `api_${name}`,
          duration,
          startTime,
          url: typeof window !== 'undefined' ? window.location.href : '',
          timestamp: new Date().toISOString(),
        });
      }

      return result;
    } catch (error) {
      const duration = performance.now() - startTime;

      // API エラーも報告
      errorReporter.reportCustomError(`API Error: ${name}`, {
        duration,
        error: error instanceof Error ? error.message : 'Unknown error',
      });

      throw error;
    }
  }
}

// グローバルインスタンス
export const errorReporter = new ErrorReporter();

// 初期化
if (typeof window !== 'undefined') {
  PerformanceMonitor.measurePageLoad();
}
