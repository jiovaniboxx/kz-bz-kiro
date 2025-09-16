import type { Metadata } from 'next';
import { Inter, Noto_Sans_JP } from 'next/font/google';
import './globals.css';
import Layout from '@/components/layout/Layout';
import { EventProvider } from '@/providers/EventProvider';
import { PerformanceProvider } from '@/providers/PerformanceProvider';
import { ToastContainer } from '@/components/ui/Toast';
import { generatePageMetadata, StructuredData, generateOrganizationSchema, generateLocalBusinessSchema } from '@/utils/metadata';
import { GoogleAnalytics } from '@/components/analytics/GoogleAnalytics';

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
});

const notoSansJP = Noto_Sans_JP({
  subsets: ['latin'],
  variable: '--font-noto-sans-jp',
});

export const metadata: Metadata = generatePageMetadata(
  'ネイティブ講師との楽しい英会話レッスン',
  '東京の英会話カフェで、ネイティブ講師と楽しく英会話を学びませんか？初心者から上級者まで、あなたのレベルに合わせたレッスンを提供します。',
  '',
  undefined,
  ['体験レッスン', 'ビジネス英語', 'TOEIC', '初心者歓迎']
);

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja" className={`${inter.variable} ${notoSansJP.variable}`}>
      <head>
        <StructuredData data={generateOrganizationSchema()} />
        <StructuredData data={generateLocalBusinessSchema()} />
      </head>
      <body className={inter.className}>
        <GoogleAnalytics measurementId={process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID || ''} />
        <PerformanceProvider>
          <EventProvider>
            <Layout>{children}</Layout>
            <ToastContainer />
          </EventProvider>
        </PerformanceProvider>
      </body>
    </html>
  );
}
