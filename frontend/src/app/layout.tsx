import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { ErrorReportingProvider } from '@/components/ErrorReportingProvider';

const inter = Inter({
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'English Cafe - 英会話カフェ',
  description:
    '東京の英会話カフェで、ネイティブ講師と楽しく英会話を学びませんか？',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <ErrorReportingProvider>{children}</ErrorReportingProvider>
      </body>
    </html>
  );
}
