/**
 * Hero Section Component
 * メインページのヒーローセクション
 */

'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Button, Container } from '@/components/ui';
import { cn } from '@/utils/cn';

interface HeroSectionProps {
  className?: string;
}

const heroImages = [
  {
    src: '/images/hero/cafe-interior-1.jpg',
    alt: '英会話カフェの温かい雰囲気の店内',
    fallback:
      'https://images.unsplash.com/photo-1554118811-1e0d58224f24?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
  },
  {
    src: '/images/hero/lesson-scene-1.jpg',
    alt: 'ネイティブ講師との楽しいレッスン風景',
    fallback:
      'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
  },
  {
    src: '/images/hero/students-conversation.jpg',
    alt: '生徒同士の英会話練習',
    fallback:
      'https://images.unsplash.com/photo-1543269664-647b4d4d8d8c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
  },
];

const features = [
  {
    icon: '🌟',
    title: 'ネイティブ講師',
    description: '経験豊富なネイティブスピーカーが指導',
  },
  {
    icon: '☕',
    title: 'カフェスタイル',
    description: 'リラックスした雰囲気で自然な英会話',
  },
  {
    icon: '👥',
    title: '少人数制',
    description: '一人ひとりに合わせた丁寧な指導',
  },
  {
    icon: '📈',
    title: '実践重視',
    description: '日常で使える実用的な英語力を習得',
  },
];

export function HeroSection({ className }: HeroSectionProps) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isLoaded, setIsLoaded] = useState(false);

  // 画像のスライドショー
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex(prev => (prev + 1) % heroImages.length);
    }, 5000); // 5秒ごとに切り替え

    return () => clearInterval(interval);
  }, []);

  // 初期ロード完了
  useEffect(() => {
    const timer = setTimeout(() => setIsLoaded(true), 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <section
      className={cn(
        'relative overflow-hidden bg-gradient-to-br from-primary-50 to-white',
        className
      )}
    >
      {/* 背景画像 */}
      <div className="absolute inset-0 z-0">
        {heroImages.map((image, index) => (
          <div
            key={index}
            className={cn(
              'absolute inset-0 transition-opacity duration-1000',
              index === currentImageIndex ? 'opacity-30' : 'opacity-0'
            )}
          >
            <Image
              src={image.fallback} // 本番では image.src を使用
              alt={image.alt}
              fill
              className="object-cover"
              priority={index === 0}
              onError={(e: React.SyntheticEvent<HTMLImageElement, Event>) => {
                // フォールバック画像に切り替え
                const target = e.target as HTMLImageElement;
                target.src = image.fallback;
              }}
            />
          </div>
        ))}
        {/* オーバーレイ */}
        <div className="absolute inset-0 bg-white/70" />
      </div>

      <Container className="relative z-10">
        <div className="py-20 lg:py-32">
          <div className="grid items-center gap-12 lg:grid-cols-2">
            {/* メインコンテンツ */}
            <div
              className={cn(
                'transform text-center transition-all duration-1000 lg:text-left',
                isLoaded
                  ? 'translate-y-0 opacity-100'
                  : 'translate-y-8 opacity-0'
              )}
            >
              <h1 className="mb-6 text-4xl font-bold leading-tight text-gray-900 md:text-5xl lg:text-6xl">
                <span className="block">英会話を</span>
                <span className="block text-primary-600">もっと身近に</span>
                <span className="block">もっと楽しく</span>
              </h1>

              <p className="mb-8 text-lg leading-relaxed text-gray-600 md:text-xl">
                ネイティブ講師とのカジュアルな会話で、
                <br className="hidden sm:block" />
                自然な英語力を身につけませんか？
                <br className="hidden sm:block" />
                初心者から上級者まで、あなたのペースで学べます。
              </p>

              {/* CTA ボタン */}
              <div className="mb-12 flex flex-col justify-center gap-4 sm:flex-row lg:justify-start">
                <Button size="lg" className="px-8 py-4 text-lg" asChild>
                  <Link href="/contact">無料体験レッスンを予約</Link>
                </Button>

                <Button
                  variant="outline"
                  size="lg"
                  className="px-8 py-4 text-lg"
                  asChild
                >
                  <Link href="/lessons">レッスン詳細を見る</Link>
                </Button>
              </div>

              {/* 特徴 */}
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                {features.map((feature, index) => (
                  <div
                    key={index}
                    className={cn(
                      'transform rounded-lg bg-white/80 p-4 text-center shadow-sm backdrop-blur-sm transition-all duration-700',
                      isLoaded
                        ? 'translate-y-0 opacity-100'
                        : 'translate-y-4 opacity-0'
                    )}
                  >
                    <div className="mb-2 text-2xl">{feature.icon}</div>
                    <h3 className="mb-1 text-sm font-semibold text-gray-900">
                      {feature.title}
                    </h3>
                    <p className="text-xs leading-tight text-gray-600">
                      {feature.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* サイド画像/動画エリア */}
            <div
              className={cn(
                'relative transform transition-all delay-500 duration-1000',
                isLoaded
                  ? 'translate-x-0 opacity-100'
                  : 'translate-x-8 opacity-0'
              )}
            >
              <div className="relative aspect-[4/3] overflow-hidden rounded-2xl shadow-2xl">
                <Image
                  src="https://images.unsplash.com/photo-1521737604893-d14cc237f11d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
                  alt="英会話カフェでの楽しいレッスン風景"
                  fill
                  className="object-cover"
                  priority
                />

                {/* 再生ボタンオーバーレイ（将来のYouTube動画用） */}
                <div className="group absolute inset-0 flex cursor-pointer items-center justify-center bg-black/20 transition-colors hover:bg-black/30">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white/90 shadow-lg transition-transform group-hover:scale-110">
                    <svg
                      className="ml-1 h-6 w-6 text-primary-600"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M8 5v14l11-7z" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* 装飾要素 */}
              <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-primary-100 opacity-60" />
              <div className="absolute -bottom-6 -left-6 h-32 w-32 rounded-full bg-secondary-100 opacity-40" />
            </div>
          </div>
        </div>
      </Container>

      {/* スクロールインジケーター */}
      <div className="absolute bottom-8 left-1/2 z-10 -translate-x-1/2 transform">
        <div className="flex animate-bounce flex-col items-center text-gray-600">
          <span className="mb-2 text-sm">もっと見る</span>
          <svg
            className="h-6 w-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 14l-7 7m0 0l-7-7m7 7V3"
            />
          </svg>
        </div>
      </div>

      {/* 画像インジケーター */}
      <div className="absolute bottom-20 right-8 z-10 flex space-x-2">
        {heroImages.map((_, index) => (
          <button
            key={index}
            className={cn(
              'h-2 w-2 rounded-full transition-all duration-300',
              index === currentImageIndex
                ? 'w-8 bg-primary-600'
                : 'bg-white/60 hover:bg-white/80'
            )}
            onClick={() => setCurrentImageIndex(index)}
            aria-label={`画像 ${index + 1} を表示`}
          />
        ))}
      </div>
    </section>
  );
}
