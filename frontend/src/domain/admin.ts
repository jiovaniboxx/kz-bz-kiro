/**
 * 管理者ドメインモデル（フロントエンド）
 */

export interface Admin {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'staff';
  isActive: boolean;
  createdAt: string;
  lastLogin: string | null;
}

export interface LoginCredentials {
  usernameOrEmail: string;
  password: string;
}

export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
  admin: Admin;
}

export interface RefreshTokenResponse {
  accessToken: string;
  tokenType: string;
  expiresIn: number;
}

export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
}

export interface CreateAdminRequest {
  username: string;
  email: string;
  password: string;
  role: 'admin' | 'staff';
}

// 認証イベント
export interface AdminLoginEvent {
  type: 'ADMIN_LOGIN';
  payload: {
    admin: Admin;
    loginAt: Date;
  };
}

export interface AdminLogoutEvent {
  type: 'ADMIN_LOGOUT';
  payload: {
    adminId: string;
    logoutAt: Date;
  };
}

export interface AdminTokenRefreshEvent {
  type: 'ADMIN_TOKEN_REFRESH';
  payload: {
    adminId: string;
    refreshAt: Date;
  };
}

export type AdminEvent =
  | AdminLoginEvent
  | AdminLogoutEvent
  | AdminTokenRefreshEvent;

// バリデーション関数
export const validateLoginCredentials = (
  credentials: LoginCredentials
): string[] => {
  const errors: string[] = [];

  if (!credentials.usernameOrEmail.trim()) {
    errors.push('ユーザー名またはメールアドレスは必須です');
  }

  if (!credentials.password.trim()) {
    errors.push('パスワードは必須です');
  }

  return errors;
};

export const validateChangePassword = (
  request: ChangePasswordRequest
): string[] => {
  const errors: string[] = [];

  if (!request.currentPassword.trim()) {
    errors.push('現在のパスワードは必須です');
  }

  if (!request.newPassword.trim()) {
    errors.push('新しいパスワードは必須です');
  } else if (request.newPassword.length < 8) {
    errors.push('新しいパスワードは8文字以上である必要があります');
  }

  return errors;
};

export const validateCreateAdmin = (request: CreateAdminRequest): string[] => {
  const errors: string[] = [];

  if (!request.username.trim()) {
    errors.push('ユーザー名は必須です');
  }

  if (!request.email.trim()) {
    errors.push('メールアドレスは必須です');
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(request.email)) {
    errors.push('有効なメールアドレスを入力してください');
  }

  if (!request.password.trim()) {
    errors.push('パスワードは必須です');
  } else if (request.password.length < 8) {
    errors.push('パスワードは8文字以上である必要があります');
  }

  if (!['admin', 'staff'].includes(request.role)) {
    errors.push('ロールはadminまたはstaffである必要があります');
  }

  return errors;
};
