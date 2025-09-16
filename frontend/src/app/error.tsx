/**
 * グローバルエラーページ
 */
'use client';

import React, { useEffect } from 'react';

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function ErrorPage({ error, reset }: ErrorPageProps) {
  useEffect(() => {
    // エラーをログに記録
    console.error('Application error:', error);

    // 将来的にはエラー監視サービス（Sentry等）に送信
    if (typeof window !== 'undefined') {
      // エラー情報をローカルストレージに保存（デバッグ用）
      const errorLog = {
        message: error.message,
        stack: error.stack,
        digest: error.digest,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent,
      };

      try {
        const existingLogs = JSON.parse(
          localStorage.getItem('error_logs') || '[]'
        );
        existingLogs.push(errorLog);
        // 最新の10件のみ保持
        const recentLogs = existingLogs.slice(-10);
        localStorage.setItem('error_logs', JSON.stringify(recentLogs));
      } catch (e) {
        console.error('Failed to save error log:', e);
      }
    }
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col justify-center bg-gray-50 py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white px-4 py-8 shadow sm:rounded-lg sm:px-10">
          <div className="text-center">
            {/* エラーアイコン */}
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
              <svg
                className="h-6 w-6 text-red-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                />
              </svg>
            </div>

            <h2 className="mt-6 text-2xl font-bold text-gray-900">
              エラーが発生しました
            </h2>

            <p className="mt-2 text-sm text-gray-600">
              申し訳ございません。予期しないエラーが発生しました。
            </p>

            {/* 開発環境でのみエラー詳細を表示 */}
            {process.env.NODE_ENV === 'development' && (
              <div className="mt-4 rounded-md bg-gray-100 p-4 text-left">
                <h3 className="mb-2 text-sm font-medium text-gray-900">
                  エラー詳細（開発環境のみ）:
                </h3>
                <p className="break-all font-mono text-xs text-gray-700">
                  {error.message}
                </p>
                {error.digest && (
                  <p className="mt-1 text-xs text-gray-500">
                    Digest: {error.digest}
                  </p>
                )}
              </div>
            )}

            {/* アクションボタン */}
            <div className="mt-6 space-y-3">
              <button
                onClick={reset}
                className="flex w-full justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                再試行
              </button>

              <button
                onClick={() => (window.location.href = '/')}
                className="flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                ホームに戻る
              </button>
            </div>

            {/* サポート情報 */}
            <div className="mt-6 text-center">
              <p className="text-xs text-gray-500">
                問題が続く場合は、
                <a
                  href="/contact"
                  className="ml-1 text-blue-600 hover:text-blue-500"
                >
                  お問い合わせ
                </a>
                ください。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
