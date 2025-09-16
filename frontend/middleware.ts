/**
 * Next.js Middleware
 *
 * 基本的なセキュリティヘッダーを適用
 */

import { NextRequest, NextResponse } from 'next/server';

export async function middleware(request: NextRequest) {
  // 開発環境では基本的なセキュリティヘッダーのみ適用
  const response = NextResponse.next();

  // 基本的なセキュリティヘッダーを設定
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'SAMEORIGIN'); // 開発環境では緩く設定
  response.headers.set('X-XSS-Protection', '1; mode=block');

  return response;
}

// ミドルウェアを適用するパスを設定
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
