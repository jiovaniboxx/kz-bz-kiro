/**
 * 問い合わせ詳細コンポーネント
 */
'use client';

import React, { useState } from 'react';
import { useContactManagement } from '@/stores/contactManagementStore';
import {
  ContactStatus,
  getStatusLabel,
  getStatusColor,
  getPreferredContactLabel,
  getLessonTypeLabel,
  formatDateTime,
  UpdateContactStatusRequest,
  validateUpdateContactStatus,
} from '@/domain/contactManagement';

interface ContactDetailProps {
  contactId: string;
  onClose?: () => void;
  onStatusUpdate?: () => void;
}

export const ContactDetail: React.FC<ContactDetailProps> = ({
  contactId,
  onClose,
  onStatusUpdate,
}) => {
  const {
    selectedContact,
    isLoading,
    isUpdating,
    error,
    loadContactDetail,
    updateContactStatus,
    clearError,
  } = useContactManagement();

  const [isEditing, setIsEditing] = useState(false);
  const [newStatus, setNewStatus] = useState<ContactStatus>('pending');
  const [adminNotes, setAdminNotes] = useState('');
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  React.useEffect(() => {
    loadContactDetail(contactId);
  }, [contactId]);

  React.useEffect(() => {
    if (selectedContact) {
      setNewStatus(selectedContact.status);
      setAdminNotes(selectedContact.adminNotes || '');
    }
  }, [selectedContact]);

  const handleStatusUpdate = async (e: React.FormEvent) => {
    e.preventDefault();

    const request: UpdateContactStatusRequest = {
      status: newStatus,
      adminNotes: adminNotes.trim() || undefined,
    };

    const errors = validateUpdateContactStatus(request);
    if (errors.length > 0) {
      setValidationErrors(errors);
      return;
    }

    setValidationErrors([]);

    try {
      await updateContactStatus(contactId, request);
      setIsEditing(false);
      if (onStatusUpdate) {
        onStatusUpdate();
      }
    } catch (error) {
      // エラーはストアで管理される
    }
  };

  const handleCancelEdit = () => {
    if (selectedContact) {
      setNewStatus(selectedContact.status);
      setAdminNotes(selectedContact.adminNotes || '');
    }
    setIsEditing(false);
    setValidationErrors([]);
  };

  if (isLoading) {
    return (
      <div className="rounded-lg bg-white p-6 shadow">
        <div className="animate-pulse">
          <div className="mb-4 h-4 w-1/4 rounded bg-gray-200"></div>
          <div className="space-y-3">
            <div className="h-4 rounded bg-gray-200"></div>
            <div className="h-4 w-5/6 rounded bg-gray-200"></div>
            <div className="h-4 w-4/6 rounded bg-gray-200"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!selectedContact) {
    return (
      <div className="rounded-lg bg-white p-6 shadow">
        <p className="text-gray-500">問い合わせが見つかりません</p>
      </div>
    );
  }

  const allErrors = [...validationErrors, ...(error ? [error] : [])];

  return (
    <div className="rounded-lg bg-white shadow">
      {/* ヘッダー */}
      <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
        <h2 className="text-lg font-medium text-gray-900">問い合わせ詳細</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>

      <div className="space-y-6 p-6">
        {/* エラー表示 */}
        {allErrors.length > 0 && (
          <div className="rounded-md border border-red-200 bg-red-50 p-3">
            <ul className="space-y-1 text-sm text-red-600">
              {allErrors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
            <button
              onClick={clearError}
              className="mt-2 text-sm text-red-600 hover:text-red-500"
            >
              エラーを閉じる
            </button>
          </div>
        )}

        {/* 基本情報 */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div>
            <h3 className="mb-2 text-sm font-medium text-gray-500">
              お客様情報
            </h3>
            <div className="space-y-2">
              <div>
                <span className="text-sm font-medium text-gray-900">
                  {selectedContact.name}
                </span>
              </div>
              <div>
                <span className="text-sm text-gray-600">
                  {selectedContact.email}
                </span>
              </div>
              {selectedContact.phone && (
                <div>
                  <span className="text-sm text-gray-600">
                    📞 {selectedContact.phone}
                  </span>
                </div>
              )}
            </div>
          </div>

          <div>
            <h3 className="mb-2 text-sm font-medium text-gray-500">
              問い合わせ情報
            </h3>
            <div className="space-y-2">
              <div>
                <span className="text-xs text-gray-500">レッスンタイプ: </span>
                <span className="text-sm text-gray-900">
                  {selectedContact.lessonType
                    ? getLessonTypeLabel(selectedContact.lessonType)
                    : '-'}
                </span>
              </div>
              <div>
                <span className="text-xs text-gray-500">希望連絡方法: </span>
                <span className="text-sm text-gray-900">
                  {getPreferredContactLabel(selectedContact.preferredContact)}
                </span>
              </div>
              <div>
                <span className="text-xs text-gray-500">送信日時: </span>
                <span className="text-sm text-gray-900">
                  {formatDateTime(selectedContact.submittedAt)}
                </span>
              </div>
              {selectedContact.updatedAt && (
                <div>
                  <span className="text-xs text-gray-500">更新日時: </span>
                  <span className="text-sm text-gray-900">
                    {formatDateTime(selectedContact.updatedAt)}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* メッセージ */}
        <div>
          <h3 className="mb-2 text-sm font-medium text-gray-500">メッセージ</h3>
          <div className="rounded-md bg-gray-50 p-4">
            <p className="whitespace-pre-wrap text-sm text-gray-900">
              {selectedContact.message}
            </p>
          </div>
        </div>

        {/* ステータス管理 */}
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-500">
              ステータス管理
            </h3>
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="text-sm text-blue-600 hover:text-blue-500"
              >
                編集
              </button>
            )}
          </div>

          {isEditing ? (
            <form onSubmit={handleStatusUpdate} className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  ステータス
                </label>
                <select
                  value={newStatus}
                  onChange={e => setNewStatus(e.target.value as ContactStatus)}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUpdating}
                >
                  <option value="pending">未対応</option>
                  <option value="in_progress">対応中</option>
                  <option value="responded">回答済み</option>
                  <option value="closed">完了</option>
                </select>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  管理者メモ
                </label>
                <textarea
                  value={adminNotes}
                  onChange={e => setAdminNotes(e.target.value)}
                  rows={4}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="対応内容や備考を入力..."
                  disabled={isUpdating}
                />
              </div>

              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={isUpdating}
                  className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {isUpdating ? '更新中...' : '更新'}
                </button>
                <button
                  type="button"
                  onClick={handleCancelEdit}
                  disabled={isUpdating}
                  className="rounded-md border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  キャンセル
                </button>
              </div>
            </form>
          ) : (
            <div className="space-y-3">
              <div>
                <span className="text-xs text-gray-500">
                  現在のステータス:{' '}
                </span>
                <span
                  className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${getStatusColor(selectedContact.status)}`}
                >
                  {getStatusLabel(selectedContact.status)}
                </span>
              </div>
              {selectedContact.adminNotes && (
                <div>
                  <span className="text-xs text-gray-500">管理者メモ:</span>
                  <div className="mt-1 rounded-md bg-gray-50 p-3">
                    <p className="whitespace-pre-wrap text-sm text-gray-900">
                      {selectedContact.adminNotes}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
