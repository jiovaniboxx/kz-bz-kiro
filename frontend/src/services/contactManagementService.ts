/**
 * 問い合わせ管理サービス（フロントエンド）
 */
import {
  ContactListResponse,
  ContactDetail,
  ContactStats,
  ContactFilters,
  UpdateContactStatusRequest,
} from '@/domain/contactManagement';
import { authService } from '@/services/authService';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ContactManagementService {
  /**
   * 問い合わせ一覧を取得
   */
  async getContacts(
    filters: ContactFilters = {}
  ): Promise<ContactListResponse> {
    const token = await authService.getValidAccessToken();
    if (!token) {
      throw new Error('認証が必要です');
    }

    const params = new URLSearchParams();
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.perPage) params.append('per_page', filters.perPage.toString());
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);

    const response = await fetch(
      `${API_BASE_URL}/api/admin/contacts?${params}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '問い合わせ一覧の取得に失敗しました');
    }

    const data = await response.json();
    return {
      contacts: data.contacts,
      total: data.total,
      page: data.page,
      perPage: data.per_page,
      totalPages: data.total_pages,
    };
  }

  /**
   * 問い合わせ詳細を取得
   */
  async getContactDetail(contactId: string): Promise<ContactDetail> {
    const token = await authService.getValidAccessToken();
    if (!token) {
      throw new Error('認証が必要です');
    }

    const response = await fetch(
      `${API_BASE_URL}/api/admin/contacts/${contactId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '問い合わせ詳細の取得に失敗しました');
    }

    const data = await response.json();
    return {
      id: data.id,
      name: data.name,
      email: data.email,
      phone: data.phone,
      message: data.message,
      lessonType: data.lesson_type,
      preferredContact: data.preferred_contact,
      status: data.status,
      submittedAt: data.submitted_at,
      updatedAt: data.updated_at,
      adminNotes: data.admin_notes,
    };
  }

  /**
   * 問い合わせのステータスを更新
   */
  async updateContactStatus(
    contactId: string,
    request: UpdateContactStatusRequest
  ): Promise<void> {
    const token = await authService.getValidAccessToken();
    if (!token) {
      throw new Error('認証が必要です');
    }

    const response = await fetch(
      `${API_BASE_URL}/api/admin/contacts/${contactId}/status`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          status: request.status,
          admin_notes: request.adminNotes,
        }),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'ステータスの更新に失敗しました');
    }
  }

  /**
   * 問い合わせ統計情報を取得
   */
  async getContactStats(): Promise<ContactStats> {
    const token = await authService.getValidAccessToken();
    if (!token) {
      throw new Error('認証が必要です');
    }

    const response = await fetch(
      `${API_BASE_URL}/api/admin/contacts/stats/summary`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '統計情報の取得に失敗しました');
    }

    const data = await response.json();
    return {
      total: data.total,
      pending: data.pending,
      inProgress: data.in_progress,
      responded: data.responded,
      closed: data.closed,
      today: data.today,
      thisWeek: data.this_week,
      thisMonth: data.this_month,
    };
  }

  /**
   * 問い合わせを削除（管理者のみ）
   */
  async deleteContact(contactId: string): Promise<void> {
    const token = await authService.getValidAccessToken();
    if (!token) {
      throw new Error('認証が必要です');
    }

    const response = await fetch(
      `${API_BASE_URL}/api/admin/contacts/${contactId}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '問い合わせの削除に失敗しました');
    }
  }

  /**
   * 問い合わせをCSVでエクスポート
   */
  async exportContactsCSV(filters: ContactFilters = {}): Promise<Blob> {
    const token = await authService.getValidAccessToken();
    if (!token) {
      throw new Error('認証が必要です');
    }

    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);

    const response = await fetch(
      `${API_BASE_URL}/api/admin/contacts/export/csv?${params}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'CSVエクスポートに失敗しました');
    }

    return await response.blob();
  }
}

// シングルトンインスタンス
export const contactManagementService = new ContactManagementService();
