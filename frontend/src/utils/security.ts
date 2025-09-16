/**
 * Security Utilities
 *
 * フロントエンドセキュリティ関連のユーティリティ関数
 */

import DOMPurify from 'dompurify';
import type { Config } from 'dompurify';

/**
 * XSS対策: HTMLコンテンツのサニタイゼーション
 */
export class XSSProtection {
  /**
   * HTMLコンテンツをサニタイズ
   * @param html - サニタイズするHTML文字列
   * @param options - DOMPurifyオプション
   * @returns サニタイズされたHTML文字列
   */
  static sanitizeHtml(html: string, options?: Config): string {
    const defaultOptions: Config = {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li'],
      ALLOWED_ATTR: [],
      ALLOW_DATA_ATTR: false,
      FORBID_TAGS: ['script', 'object', 'embed', 'iframe', 'form', 'input'],
      FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover', 'style'],
    };

    const config = { ...defaultOptions, ...options };
    return DOMPurify.sanitize(html, config);
  }

  /**
   * テキストコンテンツをエスケープ
   * @param text - エスケープするテキスト
   * @returns エスケープされたテキスト
   */
  static escapeText(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * URLをサニタイズ
   * @param url - サニタイズするURL
   * @returns 安全なURL
   */
  static sanitizeUrl(url: string): string {
    // javascript:, data:, vbscript: などの危険なプロトコルを除去
    const dangerousProtocols = /^(javascript|data|vbscript|file|about):/i;

    if (dangerousProtocols.test(url)) {
      return '#';
    }

    // 相対URLまたはHTTP/HTTPSのみ許可
    const allowedProtocols = /^(https?:\/\/|\/|\.\/|\.\.\/)/i;

    if (!allowedProtocols.test(url)) {
      return '#';
    }

    return url;
  }

  /**
   * ファイル名をサニタイズ
   * @param filename - サニタイズするファイル名
   * @returns 安全なファイル名
   */
  static sanitizeFilename(filename: string): string {
    // 危険な文字を除去
    return filename.replace(/[<>:"/\\|?*\x00-\x1f]/g, '_');
  }
}

/**
 * CSRF対策
 */
export class CSRFProtection {
  private static readonly TOKEN_KEY = 'csrf_token';
  private static readonly TOKEN_HEADER = 'X-CSRF-Token';

  /**
   * CSRFトークンを生成
   * @returns CSRFトークン
   */
  static generateToken(): string {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join(
      ''
    );
  }

  /**
   * CSRFトークンをセッションストレージに保存
   * @param token - CSRFトークン
   */
  static setToken(token: string): void {
    if (typeof window !== 'undefined') {
      sessionStorage.setItem(this.TOKEN_KEY, token);
    }
  }

  /**
   * CSRFトークンを取得
   * @returns CSRFトークン
   */
  static getToken(): string | null {
    if (typeof window !== 'undefined') {
      return sessionStorage.getItem(this.TOKEN_KEY);
    }
    return null;
  }

  /**
   * CSRFトークンを削除
   */
  static removeToken(): void {
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem(this.TOKEN_KEY);
    }
  }

  /**
   * リクエストヘッダーにCSRFトークンを追加
   * @param headers - 既存のヘッダー
   * @returns CSRFトークンが追加されたヘッダー
   */
  static addTokenToHeaders(
    headers: Record<string, string> = {}
  ): Record<string, string> {
    const token = this.getToken();
    if (token) {
      headers[this.TOKEN_HEADER] = token;
    }
    return headers;
  }

  /**
   * フォームにCSRFトークンを追加
   * @param formData - フォームデータ
   * @returns CSRFトークンが追加されたフォームデータ
   */
  static addTokenToFormData(formData: FormData): FormData {
    const token = this.getToken();
    if (token) {
      formData.append('csrf_token', token);
    }
    return formData;
  }
}

/**
 * 入力値検証とサニタイゼーション
 */
export class InputValidation {
  /**
   * 文字列の長さを検証
   * @param value - 検証する値
   * @param minLength - 最小長
   * @param maxLength - 最大長
   * @returns 検証結果
   */
  static validateLength(
    value: string,
    minLength: number,
    maxLength: number
  ): boolean {
    return value.length >= minLength && value.length <= maxLength;
  }

  /**
   * 英数字のみかチェック
   * @param value - 検証する値
   * @returns 検証結果
   */
  static isAlphanumeric(value: string): boolean {
    return /^[a-zA-Z0-9]+$/.test(value);
  }

  /**
   * SQLインジェクション攻撃パターンを検出
   * @param value - 検証する値
   * @returns 危険なパターンが検出された場合true
   */
  static detectSQLInjection(value: string): boolean {
    const sqlPatterns = [
      /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)/i,
      /(--|\/\*|\*\/|;|'|"|`)/,
      /(\bOR\b|\bAND\b).*?[=<>]/i,
      /(INFORMATION_SCHEMA|SYSOBJECTS|SYSCOLUMNS)/i,
    ];

    return sqlPatterns.some(pattern => pattern.test(value));
  }

  /**
   * XSS攻撃パターンを検出
   * @param value - 検証する値
   * @returns 危険なパターンが検出された場合true
   */
  static detectXSS(value: string): boolean {
    const xssPatterns = [
      /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
      /<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi,
      /javascript:/i,
      /on\w+\s*=/i,
      /<img[^>]+src[^>]*>/gi,
      /<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi,
      /<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>/gi,
    ];

    return xssPatterns.some(pattern => pattern.test(value));
  }

  /**
   * 入力値を安全にサニタイズ
   * @param value - サニタイズする値
   * @returns サニタイズされた値
   */
  static sanitizeInput(value: string): string {
    // HTMLエンティティをエスケープ
    let sanitized = value
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;');

    // 制御文字を除去
    sanitized = sanitized.replace(/[\x00-\x1F\x7F]/g, '');

    // 連続する空白を単一の空白に変換
    sanitized = sanitized.replace(/\s+/g, ' ').trim();

    return sanitized;
  }
}

/**
 * セキュアなストレージ操作
 */
export class SecureStorage {
  /**
   * データを暗号化してローカルストレージに保存
   * @param key - キー
   * @param value - 値
   * @param encrypt - 暗号化するかどうか
   */
  static setItem(key: string, value: string, encrypt: boolean = false): void {
    if (typeof window === 'undefined') return;

    try {
      const sanitizedKey = InputValidation.sanitizeInput(key);
      let sanitizedValue = InputValidation.sanitizeInput(value);

      if (encrypt) {
        // 簡易的な暗号化（本格的な実装では専用ライブラリを使用）
        sanitizedValue = btoa(sanitizedValue);
      }

      localStorage.setItem(sanitizedKey, sanitizedValue);
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    }
  }

  /**
   * ローカルストレージからデータを取得して復号化
   * @param key - キー
   * @param decrypt - 復号化するかどうか
   * @returns 値
   */
  static getItem(key: string, decrypt: boolean = false): string | null {
    if (typeof window === 'undefined') return null;

    try {
      const sanitizedKey = InputValidation.sanitizeInput(key);
      let value = localStorage.getItem(sanitizedKey);

      if (value && decrypt) {
        // 簡易的な復号化
        value = atob(value);
      }

      return value;
    } catch (error) {
      console.error('Failed to read from localStorage:', error);
      return null;
    }
  }

  /**
   * ローカルストレージからデータを削除
   * @param key - キー
   */
  static removeItem(key: string): void {
    if (typeof window === 'undefined') return;

    try {
      const sanitizedKey = InputValidation.sanitizeInput(key);
      localStorage.removeItem(sanitizedKey);
    } catch (error) {
      console.error('Failed to remove from localStorage:', error);
    }
  }

  /**
   * ローカルストレージをクリア
   */
  static clear(): void {
    if (typeof window === 'undefined') return;

    try {
      localStorage.clear();
    } catch (error) {
      console.error('Failed to clear localStorage:', error);
    }
  }
}

/**
 * セキュアなHTTPクライアント
 */
export class SecureHttpClient {
  private static readonly DEFAULT_TIMEOUT = 30000; // 30秒

  /**
   * セキュアなFetchリクエスト
   * @param url - リクエストURL
   * @param options - Fetchオプション
   * @returns レスポンス
   */
  static async secureFetch(
    url: string,
    options: RequestInit = {}
  ): Promise<Response> {
    // URLをサニタイズ
    const sanitizedUrl = XSSProtection.sanitizeUrl(url);

    if (sanitizedUrl === '#') {
      throw new Error('Invalid URL provided');
    }

    // デフォルトヘッダーを設定
    const defaultHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    };

    // CSRFトークンを追加
    const headers = CSRFProtection.addTokenToHeaders({
      ...defaultHeaders,
      ...(options.headers as Record<string, string>),
    });

    // セキュリティ設定
    const secureOptions: RequestInit = {
      ...options,
      headers,
      credentials: 'same-origin', // CSRF攻撃を防ぐ
      mode: 'cors',
      cache: 'no-cache',
    };

    // タイムアウト設定
    const controller = new AbortController();
    const timeoutId = setTimeout(
      () => controller.abort(),
      this.DEFAULT_TIMEOUT
    );

    try {
      const response = await fetch(sanitizedUrl, {
        ...secureOptions,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // レスポンスヘッダーのセキュリティチェック
      this.validateResponseHeaders(response);

      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  /**
   * レスポンスヘッダーのセキュリティ検証
   * @param response - レスポンス
   */
  private static validateResponseHeaders(response: Response): void {
    const contentType = response.headers.get('Content-Type');

    // Content-Typeが期待される形式かチェック
    if (
      contentType &&
      !contentType.includes('application/json') &&
      !contentType.includes('text/html') &&
      !contentType.includes('text/plain')
    ) {
      console.warn('Unexpected Content-Type:', contentType);
    }

    // セキュリティヘッダーの存在確認
    const securityHeaders = [
      'X-Content-Type-Options',
      'X-Frame-Options',
      'X-XSS-Protection',
    ];

    securityHeaders.forEach(header => {
      if (!response.headers.get(header)) {
        console.warn(`Missing security header: ${header}`);
      }
    });
  }
}

/**
 * パスワード強度チェック
 */
export class PasswordSecurity {
  /**
   * パスワード強度を評価
   * @param password - パスワード
   * @returns 強度スコア（0-4）
   */
  static evaluateStrength(password: string): number {
    let score = 0;

    // 長さチェック
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;

    // 文字種チェック
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;

    return Math.min(score, 4);
  }

  /**
   * 一般的な脆弱なパスワードかチェック
   * @param password - パスワード
   * @returns 脆弱な場合true
   */
  static isCommonPassword(password: string): boolean {
    const commonPasswords = [
      'password',
      '123456',
      '123456789',
      'qwerty',
      'abc123',
      'password123',
      'admin',
      'letmein',
      'welcome',
      'monkey',
      'dragon',
      'master',
      'shadow',
      'football',
      'baseball',
    ];

    return commonPasswords.includes(password.toLowerCase());
  }

  /**
   * パスワード要件を満たしているかチェック
   * @param password - パスワード
   * @returns 要件を満たしている場合true
   */
  static meetsRequirements(password: string): boolean {
    return (
      password.length >= 8 &&
      /[a-z]/.test(password) &&
      /[A-Z]/.test(password) &&
      /[0-9]/.test(password) &&
      /[^a-zA-Z0-9]/.test(password) &&
      !this.isCommonPassword(password)
    );
  }
}

/**
 * セキュリティイベントログ
 */
export class SecurityLogger {
  /**
   * セキュリティイベントをログに記録
   * @param event - イベント名
   * @param details - 詳細情報
   * @param severity - 重要度
   */
  static logSecurityEvent(
    event: string,
    details: Record<string, any> = {},
    severity: 'low' | 'medium' | 'high' | 'critical' = 'medium'
  ): void {
    const logEntry = {
      timestamp: new Date().toISOString(),
      event: InputValidation.sanitizeInput(event),
      severity,
      details: this.sanitizeLogDetails(details),
      userAgent:
        typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
      url: typeof window !== 'undefined' ? window.location.href : 'unknown',
    };

    // 本番環境では外部ログサービスに送信
    if (process.env.NODE_ENV === 'production') {
      this.sendToLogService(logEntry);
    } else {
      console.warn('Security Event:', logEntry);
    }
  }

  /**
   * ログ詳細情報をサニタイズ
   * @param details - 詳細情報
   * @returns サニタイズされた詳細情報
   */
  private static sanitizeLogDetails(
    details: Record<string, any>
  ): Record<string, any> {
    const sanitized: Record<string, any> = {};

    for (const [key, value] of Object.entries(details)) {
      const sanitizedKey = InputValidation.sanitizeInput(key);

      if (typeof value === 'string') {
        sanitized[sanitizedKey] = InputValidation.sanitizeInput(value);
      } else if (typeof value === 'object' && value !== null) {
        sanitized[sanitizedKey] = JSON.stringify(value);
      } else {
        sanitized[sanitizedKey] = String(value);
      }
    }

    return sanitized;
  }

  /**
   * ログサービスに送信
   * @param logEntry - ログエントリ
   */
  private static async sendToLogService(logEntry: any): Promise<void> {
    try {
      // 実際の実装では適切なログサービスのAPIを使用
      await fetch('/api/security-logs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(logEntry),
      });
    } catch (error) {
      console.error('Failed to send security log:', error);
    }
  }
}
