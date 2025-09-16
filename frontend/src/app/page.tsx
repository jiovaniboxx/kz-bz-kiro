import React from 'react';
import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="mb-4 text-4xl font-bold text-gray-900">
            English Cafe
          </h1>
          <p className="mb-8 text-xl text-gray-600">
            アットホームな雰囲気で英語を学ぼう
          </p>

          <div className="mx-auto max-w-md rounded-lg bg-white p-8 shadow-md">
            <h2 className="mb-4 text-2xl font-semibold">ようこそ</h2>
            <p className="mb-4 text-gray-700">
              英会話カフェで楽しく英語を学びませんか？
            </p>

            <div className="space-y-2">
              <p className="text-sm text-gray-500">✅ ネイティブ講師</p>
              <p className="text-sm text-gray-500">✅ カフェスタイル</p>
              <p className="text-sm text-gray-500">✅ 少人数制</p>
              <p className="text-sm text-gray-500">✅ 実践重視</p>
            </div>

            <div className="mt-6 space-y-4">
              <Link
                href="/contact"
                className="inline-block rounded bg-blue-600 px-6 py-3 text-white transition-colors hover:bg-blue-700"
              >
                無料体験レッスンを予約
              </Link>
              
              <div>
                <Link
                  href="/lessons"
                  className="inline-block rounded bg-gray-600 px-6 py-3 text-white transition-colors hover:bg-gray-700"
                >
                  レッスン詳細を見る
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Docker Compose テスト用リンク */}
      <div className="bg-gray-100 py-4">
        <div className="container mx-auto px-4 text-center">
          <Link
            href="/api-test"
            className="inline-block rounded bg-blue-600 px-4 py-2 text-sm text-white transition-colors hover:bg-blue-700"
          >
            API接続テスト
          </Link>
        </div>
      </div>
    </main>
  );
}
