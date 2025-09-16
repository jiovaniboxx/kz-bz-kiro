/**
 * Videos Page
 * 動画ギャラリーページ
 */

import { Metadata } from 'next';
import Link from 'next/link';
import { VideoGallery } from '@/components/ui/VideoGallery';
import { videoSections } from '@/data/videos';
import { generatePageMetadata } from '@/utils/metadata';

export const metadata: Metadata = generatePageMetadata(
  '動画ギャラリー',
  '英会話カフェの講師紹介、レッスン風景、生徒さんの声など、様々な動画コンテンツをご覧いただけます。実際の雰囲気を感じてください。',
  '/videos',
  undefined,
  ['動画', '講師紹介動画', 'レッスン風景', '生徒の声', 'YouTube', 'カフェ紹介']
);

export default function VideosPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヒーローセクション */}
      <section className="bg-gradient-to-r from-blue-600 to-purple-600 py-16 text-white">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-4xl text-center">
            <h1 className="mb-6 text-4xl font-bold md:text-5xl">
              動画ギャラリー
            </h1>
            <p className="mb-8 text-xl text-blue-100 md:text-2xl">
              英会話カフェの魅力を動画でご紹介
            </p>
            <p className="mx-auto max-w-2xl text-lg text-blue-200">
              経験豊富な講師陣、実際のレッスン風景、生徒さんの体験談など、
              当カフェの雰囲気を動画でお楽しみください。
            </p>
          </div>
        </div>
      </section>

      {/* 動画ギャラリー */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <VideoGallery
            sections={videoSections}
            showCategories={true}
            showSearch={true}
            showFilters={true}
          />
        </div>
      </section>

      {/* CTA セクション */}
      <section className="bg-white py-16">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-4xl text-center">
            <h2 className="mb-6 text-3xl font-bold text-gray-900">
              実際のレッスンを体験してみませんか？
            </h2>
            <p className="mb-8 text-lg text-gray-600">
              動画でご覧いただいた雰囲気を、ぜひ実際に体験してください。
              無料体験レッスンも承っております。
            </p>
            <div className="flex flex-col justify-center gap-4 sm:flex-row">
              <a
                href="/contact"
                className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-8 py-3 text-base font-medium text-white transition-colors duration-200 hover:bg-blue-700"
              >
                無料体験レッスンを申し込む
              </a>
              <Link
                href="/lessons"
                className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-8 py-3 text-base font-medium text-gray-700 transition-colors duration-200 hover:bg-gray-50"
              >
                レッスン詳細を見る
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
