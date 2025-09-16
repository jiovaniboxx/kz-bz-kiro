/**
 * 認証状態管理ストア
 */
import { create } from 'zustand';
import {
  Admin,
  LoginCredentials,
  ChangePasswordRequest,
  CreateAdminRequest,
} from '@/domain/admin';
import { authService } from '@/services/authService';
import { eventBus } from '@/utils/eventBus';

interface AuthState {
  // 状態
  admin: Admin | null;
  isLoading: boolean;
  error: string | null;
  isInitialized: boolean;

  // アクション
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  getCurrentAdmin: () => Promise<void>;
  changePassword: (request: ChangePasswordRequest) => Promise<void>;
  createAdmin: (request: CreateAdminRequest) => Promise<Admin>;
  clearError: () => void;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  // 初期状態
  admin: null,
  isLoading: false,
  error: null,
  isInitialized: false,

  // ログイン
  login: async (credentials: LoginCredentials) => {
    set({ isLoading: true, error: null });

    try {
      const response = await authService.login(credentials);
      set({ admin: response.admin, isLoading: false });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'ログインに失敗しました';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  // ログアウト
  logout: async () => {
    set({ isLoading: true });

    try {
      await authService.logout();
      set({ admin: null, isLoading: false, error: null });
    } catch (error) {
      console.error('ログアウトエラー:', error);
      // ログアウトは失敗してもローカル状態はクリアする
      set({ admin: null, isLoading: false, error: null });
    }
  },

  // 現在の管理者情報を取得
  getCurrentAdmin: async () => {
    if (!authService.isAuthenticated()) {
      set({ admin: null, isInitialized: true });
      return;
    }

    set({ isLoading: true });

    try {
      const admin = await authService.getCurrentAdmin();
      set({ admin, isLoading: false, isInitialized: true });
    } catch (error) {
      console.error('管理者情報取得エラー:', error);
      set({ admin: null, isLoading: false, isInitialized: true });
    }
  },

  // パスワード変更
  changePassword: async (request: ChangePasswordRequest) => {
    set({ isLoading: true, error: null });

    try {
      await authService.changePassword(request);
      set({ isLoading: false });
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : 'パスワードの変更に失敗しました';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  // 管理者作成
  createAdmin: async (request: CreateAdminRequest) => {
    set({ isLoading: true, error: null });

    try {
      const newAdmin = await authService.createAdmin(request);
      set({ isLoading: false });
      return newAdmin;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : '管理者の作成に失敗しました';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  // エラークリア
  clearError: () => {
    set({ error: null });
  },

  // 初期化
  initialize: async () => {
    await get().getCurrentAdmin();
  },
}));

// イベントリスナーの設定
if (typeof window !== 'undefined') {
  // ログインイベント
  eventBus.on('ADMIN_LOGIN', payload => {
    console.log('管理者ログイン:', payload);
  });

  // ログアウトイベント
  eventBus.on('ADMIN_LOGOUT', payload => {
    console.log('管理者ログアウト:', payload);
  });

  // トークンリフレッシュイベント
  eventBus.on('ADMIN_TOKEN_REFRESH', payload => {
    console.log('トークンリフレッシュ:', payload);
  });
}

// 認証状態の便利なセレクター
export const useAuth = () => {
  const store = useAuthStore();

  return {
    ...store,
    isAuthenticated: !!store.admin,
    isAdmin: store.admin?.role === 'admin',
    isStaff: store.admin?.role === 'staff',
  };
};
