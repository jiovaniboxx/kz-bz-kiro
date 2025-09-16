/**
 * 管理者ダッシュボードページ
 */
'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/stores/authStore';
import { useContactManagement } from '@/stores/contactManagementStore';
import { ContactStats } from '@/components/admin/ContactStats';
import { getRelativeTime } from '@/domain/contactManagement';

export default function AdminDashboardPage() {
  const { admin, logout } = useAuth();
  const { contacts, loadContacts } = useContactManagement();

  useEffect(() => {
    // 最新の問い合わせを5件取得
    loadContacts({ page: 1, perPage: 5 });
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('ログアウトエラー:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* ヘッダー */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              管理者ダッシュボード
            </h1>
            <p className="mt-1 text-sm text-gray-600">
              ようこそ、{admin?.username}さん
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">
              ロール: {admin?.role === 'admin' ? '管理者' : 'スタッフ'}
            </span>
            <button
              onClick={handleLogout}
              className="text-sm text-red-600 hover:text-red-500"
            >
              ログアウト
            </button>
          </div>
        </div>

        {/* 統計情報 */}
        <div className="mb-8">
          <h2 className="mb-4 text-lg font-medium text-gray-900">統計情報</h2>
          <ContactStats />
        </div>

        {/* クイックアクション */}
        <div className="mb-8">
          <h2 className="mb-4 text-lg font-medium text-gray-900">
            クイックアクション
          </h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Link
              href="/admin/contacts"
              className="rounded-lg bg-white p-6 shadow transition-shadow hover:shadow-md"
            >
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="flex h-8 w-8 items-center justify-center rounded-md bg-blue-500">
                    <span className="text-sm text-white">📧</span>
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-sm font-medium text-gray-900">
                    問い合わせ管理
                  </h3>
                  <p className="text-sm text-gray-500">
                    問い合わせの確認・対応
                  </p>
                </div>
              </div>
            </Link>

            {admin?.role === 'admin' && (
              <Link
                href="/admin/users"
                className="rounded-lg bg-white p-6 shadow transition-shadow hover:shadow-md"
              >
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="flex h-8 w-8 items-center justify-center rounded-md bg-green-500">
                      <span className="text-sm text-white">👥</span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-sm font-medium text-gray-900">
                      ユーザー管理
                    </h3>
                    <p className="text-sm text-gray-500">
                      管理者・スタッフの管理
                    </p>
                  </div>
                </div>
              </Link>
            )}

            <Link
              href="/admin/settings"
              className="rounded-lg bg-white p-6 shadow transition-shadow hover:shadow-md"
            >
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="flex h-8 w-8 items-center justify-center rounded-md bg-gray-500">
                    <span className="text-sm text-white">⚙️</span>
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-sm font-medium text-gray-900">設定</h3>
                  <p className="text-sm text-gray-500">システム設定の管理</p>
                </div>
              </div>
            </Link>
          </div>
        </div>

        {/* 最新の問い合わせ */}
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-medium text-gray-900">
              最新の問い合わせ
            </h2>
            <Link
              href="/admin/contacts"
              className="text-sm text-blue-600 hover:text-blue-500"
            >
              すべて見る →
            </Link>
          </div>
          <div className="overflow-hidden rounded-lg bg-white shadow">
            {contacts.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                問い合わせがありません
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {contacts.slice(0, 5).map(contact => (
                  <div key={contact.id} className="p-4 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h3 className="text-sm font-medium text-gray-900">
                            {contact.name}
                          </h3>
                          <span
                            className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                              contact.status === 'pending'
                                ? 'bg-yellow-100 text-yellow-800'
                                : contact.status === 'in_progress'
                                  ? 'bg-blue-100 text-blue-800'
                                  : contact.status === 'responded'
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {contact.status === 'pending'
                              ? '未対応'
                              : contact.status === 'in_progress'
                                ? '対応中'
                                : contact.status === 'responded'
                                  ? '回答済み'
                                  : '完了'}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600">{contact.email}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-500">
                          {getRelativeTime(contact.submittedAt)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
