/**
 * 管理者ログインページ
 */
import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';
import { LoginForm } from '@/components/admin/LoginForm';

export const metadata: Metadata = {
  title: '管理者ログイン | 英会話カフェ',
  description: '英会話カフェの管理者ログインページ',
  robots: 'noindex, nofollow', // 管理者ページは検索エンジンにインデックスされないようにする
};

export default function AdminLoginPage() {
  return (
    <div className="flex min-h-screen flex-col justify-center bg-gray-50 py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h1 className="text-3xl font-extrabold text-gray-900">
            英会話カフェ
          </h1>
          <p className="mt-2 text-sm text-gray-600">管理者システム</p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <LoginForm />
      </div>

      <div className="mt-8 text-center">
        <Link href="/" className="text-sm text-blue-600 hover:text-blue-500">
          ← サイトトップに戻る
        </Link>
      </div>
    </div>
  );
}
