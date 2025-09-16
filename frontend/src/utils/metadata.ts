/**
 * SEO Metadata Utilities
 * SEO最適化のためのメタデータユーティリティ
 */

import { Metadata } from 'next';

// サイト基本情報
export const SITE_CONFIG = {
  name: '英会話カフェ',
  description:
    '東京の英会話カフェで、ネイティブ講師と楽しく英会話を学びませんか？初心者から上級者まで、あなたのレベルに合わせたレッスンを提供します。',
  url: 'https://english-cafe.com', // 実際のドメインに変更
  ogImage: '/og-image.jpg',
  keywords: [
    '英会話',
    'カフェ',
    'ネイティブ講師',
    '東京',
    '英語学習',
    'レッスン',
    '初心者',
    'ビジネス英語',
    'TOEIC',
    '体験レッスン',
  ],
  author: '英会話カフェ',
  creator: '英会話カフェ',
  publisher: '英会話カフェ',
  locale: 'ja_JP',
  type: 'website',
} as const;

// 構造化データ（JSON-LD）
export const generateOrganizationSchema = () => ({
  '@context': 'https://schema.org',
  '@type': 'EducationalOrganization',
  name: SITE_CONFIG.name,
  description: SITE_CONFIG.description,
  url: SITE_CONFIG.url,
  logo: `${SITE_CONFIG.url}/logo.png`,
  image: `${SITE_CONFIG.url}${SITE_CONFIG.ogImage}`,
  address: {
    '@type': 'PostalAddress',
    streetAddress: '神宮前1-2-3 英会話カフェビル 2F',
    addressLocality: '渋谷区',
    addressRegion: '東京都',
    postalCode: '150-0001',
    addressCountry: 'JP',
  },
  contactPoint: {
    '@type': 'ContactPoint',
    telephone: '+81-3-1234-5678',
    contactType: 'customer service',
    availableLanguage: ['Japanese', 'English'],
  },
  openingHours: ['Mo-Fr 10:00-22:00', 'Sa-Su 10:00-20:00'],
  priceRange: '¥2500-¥5000',
  paymentAccepted: ['Cash', 'Credit Card'],
  currenciesAccepted: 'JPY',
});

// ページ別メタデータ生成
export const generatePageMetadata = (
  title: string,
  description: string,
  path: string = '',
  image?: string,
  keywords?: string[]
): Metadata => {
  const fullTitle = `${title} | ${SITE_CONFIG.name}`;
  const url = `${SITE_CONFIG.url}${path}`;
  const ogImage = image || SITE_CONFIG.ogImage;
  const allKeywords = [...SITE_CONFIG.keywords, ...(keywords || [])];

  return {
    title: fullTitle,
    description,
    keywords: allKeywords.join(', '),
    authors: [{ name: SITE_CONFIG.author }],
    creator: SITE_CONFIG.creator,
    publisher: SITE_CONFIG.publisher,
    metadataBase: new URL(SITE_CONFIG.url),
    alternates: {
      canonical: url,
    },
    openGraph: {
      title: fullTitle,
      description,
      url,
      siteName: SITE_CONFIG.name,
      images: [
        {
          url: ogImage,
          width: 1200,
          height: 630,
          alt: title,
        },
      ],
      locale: SITE_CONFIG.locale,
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title: fullTitle,
      description,
      images: [ogImage],
      creator: '@english_cafe_tokyo', // 実際のTwitterアカウントに変更
    },
    robots: {
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        'max-video-preview': -1,
        'max-image-preview': 'large',
        'max-snippet': -1,
      },
    },
    verification: {
      google:
        process.env.NEXT_PUBLIC_GOOGLE_VERIFICATION ||
        'your-google-verification-code',
    },
  };
};

// 構造化データをJSON文字列として生成
export function generateStructuredDataScript(data: object): string {
  return JSON.stringify(data, null, 2);
}
