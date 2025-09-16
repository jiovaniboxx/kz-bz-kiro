/**
 * 認証サービス（フロントエンド）
 */
import {
  Admin,
  LoginCredentials,
  LoginResponse,
  RefreshTokenResponse,
  ChangePasswordRequest,
  CreateAdminRequest,
  AdminLoginEvent,
  AdminLogoutEvent,
  AdminTokenRefreshEvent,
} from '@/domain/admin';
import { eventBus } from '@/utils/eventBus';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class AuthService {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private tokenExpiresAt: Date | null = null;

  constructor() {
    // ブラウザ環境でのみローカルストレージから復元
    if (typeof window !== 'undefined') {
      this.loadTokensFromStorage();
    }
  }

  /**
   * ログイン
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username_or_email: credentials.usernameOrEmail,
        password: credentials.password,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'ログインに失敗しました');
    }

    const data = await response.json();
    const loginResponse: LoginResponse = {
      accessToken: data.access_token,
      refreshToken: data.refresh_token,
      tokenType: data.token_type,
      expiresIn: data.expires_in,
      admin: data.admin,
    };

    // トークンを保存
    this.setTokens(
      loginResponse.accessToken,
      loginResponse.refreshToken,
      loginResponse.expiresIn
    );

    // ログインイベント発行
    const loginEvent: AdminLoginEvent = {
      type: 'ADMIN_LOGIN',
      payload: {
        admin: loginResponse.admin,
        loginAt: new Date(),
      },
    };
    eventBus.emit(loginEvent.type, loginEvent.payload);

    return loginResponse;
  }

  /**
   * ログアウト
   */
  async logout(): Promise<void> {
    const currentAdmin = await this.getCurrentAdmin();

    try {
      // サーバーにログアウト通知
      await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
      });
    } catch (error) {
      console.warn('ログアウト通知の送信に失敗しました:', error);
    }

    // ローカルのトークンをクリア
    this.clearTokens();

    // ログアウトイベント発行
    if (currentAdmin) {
      const logoutEvent: AdminLogoutEvent = {
        type: 'ADMIN_LOGOUT',
        payload: {
          adminId: currentAdmin.id,
          logoutAt: new Date(),
        },
      };
      eventBus.emit(logoutEvent.type, logoutEvent.payload);
    }
  }

  /**
   * トークンリフレッシュ
   */
  async refreshAccessToken(): Promise<string> {
    if (!this.refreshToken) {
      throw new Error('リフレッシュトークンがありません');
    }

    const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh_token: this.refreshToken,
      }),
    });

    if (!response.ok) {
      this.clearTokens();
      throw new Error('トークンのリフレッシュに失敗しました');
    }

    const data: RefreshTokenResponse = await response.json();

    // 新しいアクセストークンを保存
    this.setTokens(data.accessToken, this.refreshToken, data.expiresIn);

    // リフレッシュイベント発行
    const currentAdmin = await this.getCurrentAdmin();
    if (currentAdmin) {
      const refreshEvent: AdminTokenRefreshEvent = {
        type: 'ADMIN_TOKEN_REFRESH',
        payload: {
          adminId: currentAdmin.id,
          refreshAt: new Date(),
        },
      };
      eventBus.emit(refreshEvent.type, refreshEvent.payload);
    }

    return data.accessToken;
  }

  /**
   * 現在の管理者情報を取得
   */
  async getCurrentAdmin(): Promise<Admin | null> {
    const token = await this.getValidAccessToken();
    if (!token) {
      return null;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          this.clearTokens();
        }
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error('管理者情報の取得に失敗しました:', error);
      return null;
    }
  }

  /**
   * パスワード変更
   */
  async changePassword(request: ChangePasswordRequest): Promise<void> {
    const token = await this.getValidAccessToken();
    if (!token) {
      throw new Error('認証が必要です');
    }

    const response = await fetch(`${API_BASE_URL}/api/auth/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        current_password: request.currentPassword,
        new_password: request.newPassword,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'パスワードの変更に失敗しました');
    }
  }

  /**
   * 新しい管理者を作成
   */
  async createAdmin(request: CreateAdminRequest): Promise<Admin> {
    const token = await this.getValidAccessToken();
    if (!token) {
      throw new Error('認証が必要です');
    }

    const response = await fetch(`${API_BASE_URL}/api/auth/create-admin`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '管理者の作成に失敗しました');
    }

    return await response.json();
  }

  /**
   * 認証状態を確認
   */
  isAuthenticated(): boolean {
    return this.accessToken !== null && this.isTokenValid();
  }

  /**
   * 有効なアクセストークンを取得（必要に応じてリフレッシュ）
   */
  async getValidAccessToken(): Promise<string | null> {
    if (!this.accessToken) {
      return null;
    }

    // トークンが期限切れの場合はリフレッシュを試行
    if (!this.isTokenValid() && this.refreshToken) {
      try {
        return await this.refreshAccessToken();
      } catch (error) {
        console.error('トークンリフレッシュに失敗しました:', error);
        return null;
      }
    }

    return this.accessToken;
  }

  /**
   * トークンの有効性を確認
   */
  private isTokenValid(): boolean {
    if (!this.tokenExpiresAt) {
      return false;
    }

    // 5分のマージンを持たせる
    const margin = 5 * 60 * 1000; // 5分をミリ秒で
    return new Date().getTime() < this.tokenExpiresAt.getTime() - margin;
  }

  /**
   * トークンを設定
   */
  private setTokens(
    accessToken: string,
    refreshToken: string,
    expiresIn: number
  ): void {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    this.tokenExpiresAt = new Date(Date.now() + expiresIn * 1000);

    // ローカルストレージに保存
    if (typeof window !== 'undefined') {
      localStorage.setItem('admin_access_token', accessToken);
      localStorage.setItem('admin_refresh_token', refreshToken);
      localStorage.setItem(
        'admin_token_expires_at',
        this.tokenExpiresAt.toISOString()
      );
    }
  }

  /**
   * トークンをクリア
   */
  private clearTokens(): void {
    this.accessToken = null;
    this.refreshToken = null;
    this.tokenExpiresAt = null;

    // ローカルストレージからも削除
    if (typeof window !== 'undefined') {
      localStorage.removeItem('admin_access_token');
      localStorage.removeItem('admin_refresh_token');
      localStorage.removeItem('admin_token_expires_at');
    }
  }

  /**
   * ローカルストレージからトークンを復元
   */
  private loadTokensFromStorage(): void {
    if (typeof window === 'undefined') {
      return;
    }

    const accessToken = localStorage.getItem('admin_access_token');
    const refreshToken = localStorage.getItem('admin_refresh_token');
    const expiresAt = localStorage.getItem('admin_token_expires_at');

    if (accessToken && refreshToken && expiresAt) {
      this.accessToken = accessToken;
      this.refreshToken = refreshToken;
      this.tokenExpiresAt = new Date(expiresAt);
    }
  }
}

// シングルトンインスタンス
export const authService = new AuthService();
