/**
 * 404 Not Found ページ
 */
import React from 'react';
import Link from 'next/link';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'ページが見つかりません | 英会話カフェ',
  description: 'お探しのページは見つかりませんでした。',
};

export default function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col justify-center bg-gray-50 py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white px-4 py-8 shadow sm:rounded-lg sm:px-10">
          <div className="text-center">
            {/* 404アイコン */}
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-yellow-100">
              <svg
                className="h-6 w-6 text-yellow-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 20.5a7.962 7.962 0 01-5.657-2.343m0 0L3.515 15.33A9.015 9.015 0 0112 2.25a9.015 9.015 0 018.485 13.08l-2.828 2.827z"
                />
              </svg>
            </div>

            <h1 className="mt-6 text-3xl font-bold text-gray-900">404</h1>

            <h2 className="mt-2 text-xl font-semibold text-gray-700">
              ページが見つかりません
            </h2>

            <p className="mt-2 text-sm text-gray-600">
              お探しのページは存在しないか、移動された可能性があります。
            </p>

            {/* ナビゲーションリンク */}
            <div className="mt-6 space-y-3">
              <Link
                href="/"
                className="flex w-full justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                ホームに戻る
              </Link>

              <div className="flex space-x-2">
                <Link
                  href="/teachers"
                  className="flex flex-1 justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  講師紹介
                </Link>
                <Link
                  href="/lessons"
                  className="flex flex-1 justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  レッスン
                </Link>
              </div>

              <Link
                href="/contact"
                className="flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                お問い合わせ
              </Link>
            </div>

            {/* 検索候補 */}
            <div className="mt-6">
              <h3 className="mb-2 text-sm font-medium text-gray-900">
                こちらのページもご覧ください:
              </h3>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>
                  <Link
                    href="/about"
                    className="text-blue-600 hover:text-blue-500"
                  >
                    カフェについて
                  </Link>
                </li>
                <li>
                  <Link
                    href="/access"
                    className="text-blue-600 hover:text-blue-500"
                  >
                    アクセス情報
                  </Link>
                </li>
                <li>
                  <Link
                    href="/faq"
                    className="text-blue-600 hover:text-blue-500"
                  >
                    よくある質問
                  </Link>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
