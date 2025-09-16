/**
 * 問い合わせ一覧コンポーネント
 */
'use client';

import React, { useEffect, useState } from 'react';
import { useContactManagement } from '@/stores/contactManagementStore';
import {
  ContactStatus,
  getStatusLabel,
  getStatusColor,
  getPreferredContactLabel,
  getLessonTypeLabel,
  getRelativeTime,
  formatDateTime,
} from '@/domain/contactManagement';

interface ContactListProps {
  onContactSelect?: (contactId: string) => void;
}

export const ContactList: React.FC<ContactListProps> = ({
  onContactSelect,
}) => {
  const {
    contacts,
    total,
    page,
    perPage,
    totalPages,
    filters,
    isLoading,
    error,
    loadContacts,
    setFilters,
    clearError,
  } = useContactManagement();

  const [searchTerm, setSearchTerm] = useState(filters.search || '');
  const [statusFilter, setStatusFilter] = useState<ContactStatus | ''>(
    (filters.status as ContactStatus) || ''
  );

  useEffect(() => {
    loadContacts();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const newFilters = {
      ...filters,
      search: searchTerm || undefined,
      page: 1,
    };
    setFilters(newFilters);
    loadContacts(newFilters);
  };

  const handleStatusFilter = (status: ContactStatus | '') => {
    setStatusFilter(status);
    const newFilters = {
      ...filters,
      status: status || undefined,
      page: 1,
    };
    setFilters(newFilters);
    loadContacts(newFilters);
  };

  const handlePageChange = (newPage: number) => {
    const newFilters = { ...filters, page: newPage };
    setFilters(newFilters);
    loadContacts(newFilters);
  };

  const handleContactClick = (contactId: string) => {
    if (onContactSelect) {
      onContactSelect(contactId);
    }
  };

  if (error) {
    return (
      <div className="rounded-md border border-red-200 bg-red-50 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-red-400"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">
              エラーが発生しました
            </h3>
            <p className="mt-1 text-sm text-red-700">{error}</p>
            <button
              onClick={clearError}
              className="mt-2 text-sm text-red-600 hover:text-red-500"
            >
              エラーを閉じる
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 検索・フィルター */}
      <div className="rounded-lg bg-white p-4 shadow">
        <form
          onSubmit={handleSearch}
          className="flex flex-col gap-4 sm:flex-row"
        >
          <div className="flex-1">
            <input
              type="text"
              placeholder="名前またはメールアドレスで検索..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <select
              value={statusFilter}
              onChange={e =>
                handleStatusFilter(e.target.value as ContactStatus | '')
              }
              className="rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全てのステータス</option>
              <option value="pending">未対応</option>
              <option value="in_progress">対応中</option>
              <option value="responded">回答済み</option>
              <option value="closed">完了</option>
            </select>
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            検索
          </button>
        </form>
      </div>

      {/* 問い合わせ一覧 */}
      <div className="overflow-hidden rounded-lg bg-white shadow">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">読み込み中...</p>
          </div>
        ) : contacts.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            問い合わせが見つかりませんでした
          </div>
        ) : (
          <>
            {/* テーブルヘッダー */}
            <div className="border-b border-gray-200 bg-gray-50 px-6 py-3">
              <div className="grid grid-cols-12 gap-4 text-xs font-medium uppercase tracking-wider text-gray-500">
                <div className="col-span-3">名前・メール</div>
                <div className="col-span-2">レッスンタイプ</div>
                <div className="col-span-2">連絡方法</div>
                <div className="col-span-2">ステータス</div>
                <div className="col-span-3">送信日時</div>
              </div>
            </div>

            {/* テーブル本体 */}
            <div className="divide-y divide-gray-200">
              {contacts.map(contact => (
                <div
                  key={contact.id}
                  onClick={() => handleContactClick(contact.id)}
                  className="cursor-pointer px-6 py-4 transition-colors hover:bg-gray-50"
                >
                  <div className="grid grid-cols-12 items-center gap-4">
                    {/* 名前・メール */}
                    <div className="col-span-3">
                      <div className="text-sm font-medium text-gray-900">
                        {contact.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {contact.email}
                      </div>
                      {contact.phone && (
                        <div className="text-xs text-gray-400">
                          📞 {contact.phone}
                        </div>
                      )}
                    </div>

                    {/* レッスンタイプ */}
                    <div className="col-span-2">
                      <span className="text-sm text-gray-900">
                        {contact.lessonType
                          ? getLessonTypeLabel(contact.lessonType)
                          : '-'}
                      </span>
                    </div>

                    {/* 連絡方法 */}
                    <div className="col-span-2">
                      <span className="text-sm text-gray-900">
                        {getPreferredContactLabel(contact.preferredContact)}
                      </span>
                    </div>

                    {/* ステータス */}
                    <div className="col-span-2">
                      <span
                        className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${getStatusColor(contact.status)}`}
                      >
                        {getStatusLabel(contact.status)}
                      </span>
                    </div>

                    {/* 送信日時 */}
                    <div className="col-span-3">
                      <div className="text-sm text-gray-900">
                        {getRelativeTime(contact.submittedAt)}
                      </div>
                      <div className="text-xs text-gray-500">
                        {formatDateTime(contact.submittedAt)}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* ページネーション */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between rounded-lg border-t border-gray-200 bg-white px-4 py-3 shadow sm:px-6">
          <div className="flex flex-1 justify-between sm:hidden">
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={page <= 1}
              className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              前へ
            </button>
            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={page >= totalPages}
              className="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              次へ
            </button>
          </div>
          <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                <span className="font-medium">{total}</span> 件中{' '}
                <span className="font-medium">{(page - 1) * perPage + 1}</span>{' '}
                -{' '}
                <span className="font-medium">
                  {Math.min(page * perPage, total)}
                </span>{' '}
                件を表示
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex -space-x-px rounded-md shadow-sm">
                <button
                  onClick={() => handlePageChange(page - 1)}
                  disabled={page <= 1}
                  className="relative inline-flex items-center rounded-l-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  前へ
                </button>
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const pageNum = Math.max(
                    1,
                    Math.min(page - 2 + i, totalPages - 4 + i)
                  );
                  return (
                    <button
                      key={pageNum}
                      onClick={() => handlePageChange(pageNum)}
                      className={`relative inline-flex items-center border px-4 py-2 text-sm font-medium ${
                        pageNum === page
                          ? 'z-10 border-blue-500 bg-blue-50 text-blue-600'
                          : 'border-gray-300 bg-white text-gray-500 hover:bg-gray-50'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                <button
                  onClick={() => handlePageChange(page + 1)}
                  disabled={page >= totalPages}
                  className="relative inline-flex items-center rounded-r-md border border-gray-300 bg-white px-2 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  次へ
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
