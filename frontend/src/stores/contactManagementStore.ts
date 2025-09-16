/**
 * 問い合わせ管理状態管理ストア
 */
import { create } from 'zustand';
import {
  ContactListItem,
  ContactDetail,
  ContactStats,
  ContactFilters,
  UpdateContactStatusRequest,
  ContactStatus,
} from '@/domain/contactManagement';
import { contactManagementService } from '@/services/contactManagementService';

interface ContactManagementState {
  // 問い合わせ一覧
  contacts: ContactListItem[];
  total: number;
  page: number;
  perPage: number;
  totalPages: number;

  // 問い合わせ詳細
  selectedContact: ContactDetail | null;

  // 統計情報
  stats: ContactStats | null;

  // フィルター
  filters: ContactFilters;

  // 状態
  isLoading: boolean;
  isUpdating: boolean;
  error: string | null;

  // アクション
  loadContacts: (filters?: ContactFilters) => Promise<void>;
  loadContactDetail: (contactId: string) => Promise<void>;
  loadStats: () => Promise<void>;
  updateContactStatus: (
    contactId: string,
    request: UpdateContactStatusRequest
  ) => Promise<void>;
  deleteContact: (contactId: string) => Promise<void>;
  setFilters: (filters: ContactFilters) => void;
  clearError: () => void;
  clearSelectedContact: () => void;
}

export const useContactManagementStore = create<ContactManagementState>(
  (set, get) => ({
    // 初期状態
    contacts: [],
    total: 0,
    page: 1,
    perPage: 20,
    totalPages: 0,
    selectedContact: null,
    stats: null,
    filters: { page: 1, perPage: 20 },
    isLoading: false,
    isUpdating: false,
    error: null,

    // 問い合わせ一覧を読み込み
    loadContacts: async (filters?: ContactFilters) => {
      set({ isLoading: true, error: null });

      try {
        const currentFilters = filters || get().filters;
        const response =
          await contactManagementService.getContacts(currentFilters);

        set({
          contacts: response.contacts,
          total: response.total,
          page: response.page,
          perPage: response.perPage,
          totalPages: response.totalPages,
          filters: currentFilters,
          isLoading: false,
        });
      } catch (error) {
        const errorMessage =
          error instanceof Error
            ? error.message
            : '問い合わせ一覧の取得に失敗しました';
        set({ error: errorMessage, isLoading: false });
      }
    },

    // 問い合わせ詳細を読み込み
    loadContactDetail: async (contactId: string) => {
      set({ isLoading: true, error: null });

      try {
        const contact =
          await contactManagementService.getContactDetail(contactId);
        set({ selectedContact: contact, isLoading: false });
      } catch (error) {
        const errorMessage =
          error instanceof Error
            ? error.message
            : '問い合わせ詳細の取得に失敗しました';
        set({ error: errorMessage, isLoading: false });
      }
    },

    // 統計情報を読み込み
    loadStats: async () => {
      try {
        const stats = await contactManagementService.getContactStats();
        set({ stats });
      } catch (error) {
        console.error('統計情報の取得に失敗しました:', error);
      }
    },

    // 問い合わせのステータスを更新
    updateContactStatus: async (
      contactId: string,
      request: UpdateContactStatusRequest
    ) => {
      set({ isUpdating: true, error: null });

      try {
        await contactManagementService.updateContactStatus(contactId, request);

        // 一覧を更新
        const currentState = get();
        const updatedContacts = currentState.contacts.map(contact =>
          contact.id === contactId
            ? {
                ...contact,
                status: request.status,
                updatedAt: new Date().toISOString(),
              }
            : contact
        );

        // 詳細も更新
        const updatedSelectedContact =
          currentState.selectedContact?.id === contactId
            ? {
                ...currentState.selectedContact,
                status: request.status,
                adminNotes: request.adminNotes,
                updatedAt: new Date().toISOString(),
              }
            : currentState.selectedContact;

        set({
          contacts: updatedContacts,
          selectedContact: updatedSelectedContact,
          isUpdating: false,
        });

        // 統計情報を再読み込み
        get().loadStats();
      } catch (error) {
        const errorMessage =
          error instanceof Error
            ? error.message
            : 'ステータスの更新に失敗しました';
        set({ error: errorMessage, isUpdating: false });
        throw error;
      }
    },

    // 問い合わせを削除
    deleteContact: async (contactId: string) => {
      set({ isUpdating: true, error: null });

      try {
        await contactManagementService.deleteContact(contactId);

        // 一覧から削除
        const currentState = get();
        const updatedContacts = currentState.contacts.filter(
          contact => contact.id !== contactId
        );

        set({
          contacts: updatedContacts,
          total: currentState.total - 1,
          selectedContact:
            currentState.selectedContact?.id === contactId
              ? null
              : currentState.selectedContact,
          isUpdating: false,
        });

        // 統計情報を再読み込み
        get().loadStats();
      } catch (error) {
        const errorMessage =
          error instanceof Error
            ? error.message
            : '問い合わせの削除に失敗しました';
        set({ error: errorMessage, isUpdating: false });
        throw error;
      }
    },

    // フィルターを設定
    setFilters: (filters: ContactFilters) => {
      const currentFilters = get().filters;
      const newFilters = { ...currentFilters, ...filters };
      set({ filters: newFilters });
    },

    // エラーをクリア
    clearError: () => {
      set({ error: null });
    },

    // 選択された問い合わせをクリア
    clearSelectedContact: () => {
      set({ selectedContact: null });
    },
  })
);

// 便利なセレクター
export const useContactManagement = () => {
  const store = useContactManagementStore();

  return {
    ...store,
    hasContacts: store.contacts.length > 0,
    hasPendingContacts: store.stats ? store.stats.pending > 0 : false,
    hasNextPage: store.page < store.totalPages,
    hasPrevPage: store.page > 1,
  };
};
