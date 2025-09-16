import React from 'react';
import Link from 'next/link';

export default function ApiTestPage() {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="mb-4 text-4xl font-bold text-gray-900">
            API接続テスト
          </h1>
          <p className="mb-8 text-xl text-gray-600">
            Docker Composeでの動作確認用のページです
          </p>

          <div className="mx-auto max-w-md rounded-lg bg-white p-8 shadow-md">
            <h2 className="mb-4 text-2xl font-semibold">動作確認</h2>
            <p className="mb-4 text-gray-700">
              フロントエンドとバックエンドの接続をテストします。
            </p>

            <div className="space-y-2">
              <p className="text-sm text-gray-500">✅ Next.js 14</p>
              <p className="text-sm text-gray-500">✅ Tailwind CSS</p>
              <p className="text-sm text-gray-500">✅ TypeScript</p>
              <p className="text-sm text-gray-500">✅ Docker Compose</p>
            </div>

            <div className="mt-6 space-y-4">
              <a
                href="/api/health"
                className="inline-block rounded bg-blue-600 px-4 py-2 text-white transition-colors hover:bg-blue-700"
              >
                API接続テスト
              </a>
              
              <div className="mt-4">
                <Link
                  href="/"
                  className="inline-block rounded bg-gray-600 px-4 py-2 text-white transition-colors hover:bg-gray-700"
                >
                  ホームに戻る
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}