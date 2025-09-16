/**
 * 問い合わせ管理ページ
 */
'use client';

import React, { useState } from 'react';
import { ContactList } from '@/components/admin/ContactList';
import { ContactDetail } from '@/components/admin/ContactDetail';
import { ContactStats } from '@/components/admin/ContactStats';

export default function AdminContactsPage() {
  const [selectedContactId, setSelectedContactId] = useState<string | null>(
    null
  );
  const [activeTab, setActiveTab] = useState<'list' | 'stats'>('list');

  const handleContactSelect = (contactId: string) => {
    setSelectedContactId(contactId);
  };

  const handleCloseDetail = () => {
    setSelectedContactId(null);
  };

  const handleStatusUpdate = () => {
    // 必要に応じて一覧を再読み込み
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* ヘッダー */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">問い合わせ管理</h1>
          <p className="mt-1 text-sm text-gray-600">
            お客様からの問い合わせを管理・対応できます
          </p>
        </div>

        {/* タブナビゲーション */}
        <div className="mb-6">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('list')}
              className={`border-b-2 px-1 py-2 text-sm font-medium ${
                activeTab === 'list'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              }`}
            >
              問い合わせ一覧
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={`border-b-2 px-1 py-2 text-sm font-medium ${
                activeTab === 'stats'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              }`}
            >
              統計情報
            </button>
          </nav>
        </div>

        {/* コンテンツ */}
        {activeTab === 'list' ? (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* 問い合わせ一覧 */}
            <div
              className={selectedContactId ? 'lg:col-span-2' : 'lg:col-span-3'}
            >
              <ContactList onContactSelect={handleContactSelect} />
            </div>

            {/* 問い合わせ詳細 */}
            {selectedContactId && (
              <div className="lg:col-span-1">
                <ContactDetail
                  contactId={selectedContactId}
                  onClose={handleCloseDetail}
                  onStatusUpdate={handleStatusUpdate}
                />
              </div>
            )}
          </div>
        ) : (
          <ContactStats />
        )}
      </div>
    </div>
  );
}
