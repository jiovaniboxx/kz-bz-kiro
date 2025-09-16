/**
 * 問い合わせ管理ドメインモデル（フロントエンド）
 */

export interface ContactListItem {
  id: string;
  name: string;
  email: string;
  phone?: string;
  lessonType?: string;
  preferredContact: string;
  status: ContactStatus;
  submittedAt: string;
  updatedAt?: string;
}

export interface ContactDetail {
  id: string;
  name: string;
  email: string;
  phone?: string;
  message: string;
  lessonType?: string;
  preferredContact: string;
  status: ContactStatus;
  submittedAt: string;
  updatedAt?: string;
  adminNotes?: string;
}

export interface ContactListResponse {
  contacts: ContactListItem[];
  total: number;
  page: number;
  perPage: number;
  totalPages: number;
}

export interface ContactStats {
  total: number;
  pending: number;
  inProgress: number;
  responded: number;
  closed: number;
  today: number;
  thisWeek: number;
  thisMonth: number;
}

export type ContactStatus = 'pending' | 'in_progress' | 'responded' | 'closed';

export interface UpdateContactStatusRequest {
  status: ContactStatus;
  adminNotes?: string;
}

export interface ContactFilters {
  status?: ContactStatus;
  search?: string;
  page?: number;
  perPage?: number;
}

// ステータス表示用の設定
export const ContactStatusConfig = {
  pending: {
    label: '未対応',
    color: 'bg-yellow-100 text-yellow-800',
    icon: '⏳',
  },
  in_progress: {
    label: '対応中',
    color: 'bg-blue-100 text-blue-800',
    icon: '🔄',
  },
  responded: {
    label: '回答済み',
    color: 'bg-green-100 text-green-800',
    icon: '✅',
  },
  closed: {
    label: '完了',
    color: 'bg-gray-100 text-gray-800',
    icon: '🔒',
  },
} as const;

// 連絡方法の表示設定
export const PreferredContactConfig = {
  email: { label: 'メール', icon: '📧' },
  phone: { label: '電話', icon: '📞' },
  line: { label: 'LINE', icon: '💬' },
  facebook: { label: 'Facebook', icon: '📘' },
  instagram: { label: 'Instagram', icon: '📷' },
} as const;

// レッスンタイプの表示設定
export const LessonTypeConfig = {
  group: { label: 'グループレッスン', icon: '👥' },
  private: { label: 'プライベートレッスン', icon: '👤' },
  trial: { label: '体験レッスン', icon: '🎯' },
  other: { label: 'その他', icon: '❓' },
} as const;

// バリデーション関数
export const validateUpdateContactStatus = (
  request: UpdateContactStatusRequest
): string[] => {
  const errors: string[] = [];

  const validStatuses: ContactStatus[] = [
    'pending',
    'in_progress',
    'responded',
    'closed',
  ];
  if (!validStatuses.includes(request.status)) {
    errors.push('無効なステータスです');
  }

  return errors;
};

// ユーティリティ関数
export const getStatusLabel = (status: ContactStatus): string => {
  return ContactStatusConfig[status]?.label || status;
};

export const getStatusColor = (status: ContactStatus): string => {
  return ContactStatusConfig[status]?.color || 'bg-gray-100 text-gray-800';
};

export const getPreferredContactLabel = (preferredContact: string): string => {
  return (
    PreferredContactConfig[
      preferredContact as keyof typeof PreferredContactConfig
    ]?.label || preferredContact
  );
};

export const getLessonTypeLabel = (lessonType: string): string => {
  return (
    LessonTypeConfig[lessonType as keyof typeof LessonTypeConfig]?.label ||
    lessonType
  );
};

export const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const getRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffHours / 24);

  if (diffHours < 1) {
    return '1時間以内';
  } else if (diffHours < 24) {
    return `${diffHours}時間前`;
  } else if (diffDays < 7) {
    return `${diffDays}日前`;
  } else {
    return formatDateTime(dateString);
  }
};
