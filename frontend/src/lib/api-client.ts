/**
 * Secure API Client
 *
 * セキュリティ機能を備えたAPIクライアント
 */

import {
  SecureHttpClient,
  CSRFProtection,
  SecurityLogger,
} from '@/utils/security';

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

export interface ApiError {
  message: string;
  status: number;
  details?: any;
}

/**
 * セキュアなAPIクライアント
 */
export class ApiClient {
  private baseUrl: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_URL || '';
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    };
  }

  /**
   * GETリクエスト
   */
  async get<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    const url = this.buildUrl(endpoint, params);

    try {
      const response = await SecureHttpClient.secureFetch(url, {
        method: 'GET',
        headers: this.defaultHeaders,
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      throw this.handleError(error, 'GET', endpoint);
    }
  }

  /**
   * POSTリクエスト
   */
  async post<T>(endpoint: string, data?: any): Promise<T> {
    const url = this.buildUrl(endpoint);

    try {
      const response = await SecureHttpClient.secureFetch(url, {
        method: 'POST',
        headers: this.defaultHeaders,
        body: data ? JSON.stringify(data) : undefined,
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      throw this.handleError(error, 'POST', endpoint);
    }
  }

  /**
   * PUTリクエスト
   */
  async put<T>(endpoint: string, data?: any): Promise<T> {
    const url = this.buildUrl(endpoint);

    try {
      const response = await SecureHttpClient.secureFetch(url, {
        method: 'PUT',
        headers: this.defaultHeaders,
        body: data ? JSON.stringify(data) : undefined,
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      throw this.handleError(error, 'PUT', endpoint);
    }
  }

  /**
   * DELETEリクエスト
   */
  async delete<T>(endpoint: string): Promise<T> {
    const url = this.buildUrl(endpoint);

    try {
      const response = await SecureHttpClient.secureFetch(url, {
        method: 'DELETE',
        headers: this.defaultHeaders,
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      throw this.handleError(error, 'DELETE', endpoint);
    }
  }

  /**
   * フォームデータ送信
   */
  async postForm<T>(endpoint: string, formData: FormData): Promise<T> {
    const url = this.buildUrl(endpoint);

    // CSRFトークンを追加
    CSRFProtection.addTokenToFormData(formData);

    try {
      const response = await SecureHttpClient.secureFetch(url, {
        method: 'POST',
        body: formData,
        // FormDataの場合はContent-Typeを設定しない（ブラウザが自動設定）
        headers: {
          ...this.defaultHeaders,
          'Content-Type': undefined,
        } as any,
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      throw this.handleError(error, 'POST_FORM', endpoint);
    }
  }

  /**
   * URLを構築
   */
  private buildUrl(endpoint: string, params?: Record<string, string>): string {
    let url = `${this.baseUrl}${endpoint}`;

    if (params) {
      const searchParams = new URLSearchParams(params);
      url += `?${searchParams.toString()}`;
    }

    return url;
  }

  /**
   * レスポンスを処理
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('Content-Type');

    if (!response.ok) {
      let errorData: any;

      try {
        if (contentType?.includes('application/json')) {
          errorData = await response.json();
        } else {
          errorData = { message: await response.text() };
        }
      } catch {
        errorData = { message: 'Unknown error occurred' };
      }

      throw new ApiError(
        errorData.message || errorData.detail || 'Request failed',
        response.status,
        errorData
      );
    }

    try {
      if (contentType?.includes('application/json')) {
        return await response.json();
      } else {
        return (await response.text()) as unknown as T;
      }
    } catch (error) {
      SecurityLogger.logSecurityEvent(
        'response_parsing_error',
        {
          contentType,
          status: response.status,
          error: String(error),
        },
        'medium'
      );

      throw new ApiError('Failed to parse response', response.status, error);
    }
  }

  /**
   * エラーを処理
   */
  private handleError(error: any, method: string, endpoint: string): ApiError {
    if (error instanceof ApiError) {
      return error;
    }

    // ネットワークエラーやその他のエラー
    SecurityLogger.logSecurityEvent(
      'api_request_error',
      {
        method,
        endpoint,
        error: String(error),
      },
      'medium'
    );

    if (error.name === 'AbortError') {
      return new ApiError('Request timeout', 408, error);
    }

    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return new ApiError('Network error', 0, error);
    }

    return new ApiError(
      error.message || 'Unknown error occurred',
      error.status || 500,
      error
    );
  }

  /**
   * CSRFトークンを初期化
   */
  async initializeCSRF(): Promise<void> {
    try {
      // サーバーからCSRFトークンを取得
      const response = await fetch(`${this.baseUrl}/csrf-token`, {
        method: 'GET',
        credentials: 'same-origin',
      });

      if (response.ok) {
        const data = await response.json();
        if (data.csrf_token) {
          CSRFProtection.setToken(data.csrf_token);
        }
      }
    } catch (error) {
      // CSRFトークンの取得に失敗した場合は新しいトークンを生成
      const token = CSRFProtection.generateToken();
      CSRFProtection.setToken(token);

      SecurityLogger.logSecurityEvent(
        'csrf_token_generation_fallback',
        {
          error: String(error),
        },
        'low'
      );
    }
  }

  /**
   * ヘルスチェック
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = (await this.get('/health')) as { status?: string };
      return response && response.status === 'healthy';
    } catch {
      return false;
    }
  }
}

/**
 * カスタムAPIエラークラス
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * デフォルトAPIクライアントインスタンス
 */
export const apiClient = new ApiClient();

/**
 * Contact API
 */
export const contactApi = {
  /**
   * 問い合わせを作成
   */
  async create(contactData: {
    name: string;
    email: string;
    phone?: string;
    lesson_type: string;
    preferred_contact: string;
    message: string;
  }): Promise<{ contact_id: string; message: string }> {
    return apiClient.post('/api/v1/contacts/', contactData);
  },

  /**
   * 問い合わせを取得
   */
  async get(contactId: string): Promise<any> {
    return apiClient.get(`/api/v1/contacts/${contactId}`);
  },

  /**
   * 問い合わせ一覧を取得
   */
  async list(params?: {
    limit?: number;
    offset?: number;
    status?: string;
  }): Promise<any[]> {
    return apiClient.get('/api/v1/contacts/', params as Record<string, string>);
  },
};

/**
 * Health API
 */
export const healthApi = {
  /**
   * ヘルスチェック
   */
  async check(): Promise<{
    status: string;
    timestamp: string;
    version: string;
    database?: string;
  }> {
    return apiClient.get('/health');
  },
};

/**
 * APIクライアントの初期化
 */
export async function initializeApiClient(): Promise<void> {
  try {
    // CSRFトークンを初期化
    await apiClient.initializeCSRF();

    // ヘルスチェックを実行
    const isHealthy = await apiClient.healthCheck();

    if (!isHealthy) {
      SecurityLogger.logSecurityEvent('api_health_check_failed', {}, 'medium');
    }
  } catch (error) {
    SecurityLogger.logSecurityEvent(
      'api_client_initialization_failed',
      {
        error: String(error),
      },
      'medium'
    );
  }
}
