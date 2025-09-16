/**
 * Security Middleware
 *
 * Next.jsアプリケーション用のセキュリティミドルウェア
 */

import { NextRequest, NextResponse } from 'next/server';
import { SecurityLogger, InputValidation } from '@/utils/security';

/**
 * セキュリティヘッダーを設定するミドルウェア
 */
export function securityHeadersMiddleware(request: NextRequest) {
  const response = NextResponse.next();

  // セキュリティヘッダーを設定
  const securityHeaders = {
    // XSS攻撃を防ぐ
    'X-XSS-Protection': '1; mode=block',

    // コンテンツタイプスニッフィングを防ぐ
    'X-Content-Type-Options': 'nosniff',

    // クリックジャッキング攻撃を防ぐ
    'X-Frame-Options': 'DENY',

    // HTTPS強制（本番環境のみ）
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',

    // リファラーポリシー
    'Referrer-Policy': 'strict-origin-when-cross-origin',

    // 権限ポリシー
    'Permissions-Policy':
      'camera=(), microphone=(), geolocation=(), payment=()',

    // コンテンツセキュリティポリシー
    'Content-Security-Policy': [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com https://www.google-analytics.com",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "font-src 'self' https://fonts.gstatic.com",
      "img-src 'self' data: https: blob:",
      "media-src 'self' https:",
      "object-src 'none'",
      "frame-src 'self' https://www.youtube.com https://www.google.com",
      "connect-src 'self' https://english-cafe-backend.onrender.com https://www.google-analytics.com",
      "worker-src 'self' blob:",
      "child-src 'self'",
      "form-action 'self'",
      "base-uri 'self'",
      "manifest-src 'self'",
      'upgrade-insecure-requests',
    ].join('; '),
  };

  // 本番環境でのみ適用するヘッダー
  if (process.env.NODE_ENV === 'production') {
    Object.entries(securityHeaders).forEach(([key, value]) => {
      response.headers.set(key, value);
    });
  } else {
    // 開発環境では一部のヘッダーのみ適用
    const devHeaders = {
      'X-XSS-Protection': securityHeaders['X-XSS-Protection'],
      'X-Content-Type-Options': securityHeaders['X-Content-Type-Options'],
      'X-Frame-Options': securityHeaders['X-Frame-Options'],
    };

    Object.entries(devHeaders).forEach(([key, value]) => {
      response.headers.set(key, value);
    });
  }

  return response;
}

/**
 * レート制限ミドルウェア
 */
export class RateLimitMiddleware {
  private static requests = new Map<
    string,
    { count: number; resetTime: number }
  >();
  private static readonly WINDOW_SIZE = 15 * 60 * 1000; // 15分
  private static readonly MAX_REQUESTS = 100; // 15分間に100リクエスト

  static check(request: NextRequest): NextResponse | null {
    const clientIP = this.getClientIP(request);
    const now = Date.now();

    // 古いエントリをクリーンアップ
    this.cleanup(now);

    const clientData = this.requests.get(clientIP);

    if (!clientData) {
      // 新しいクライアント
      this.requests.set(clientIP, {
        count: 1,
        resetTime: now + this.WINDOW_SIZE,
      });
      return null;
    }

    if (now > clientData.resetTime) {
      // ウィンドウをリセット
      this.requests.set(clientIP, {
        count: 1,
        resetTime: now + this.WINDOW_SIZE,
      });
      return null;
    }

    if (clientData.count >= this.MAX_REQUESTS) {
      // レート制限に達した
      SecurityLogger.logSecurityEvent(
        'rate_limit_exceeded',
        {
          clientIP,
          requestCount: clientData.count,
          path: request.nextUrl.pathname,
        },
        'medium'
      );

      return new NextResponse('Too Many Requests', {
        status: 429,
        headers: {
          'Retry-After': String(Math.ceil((clientData.resetTime - now) / 1000)),
          'X-RateLimit-Limit': String(this.MAX_REQUESTS),
          'X-RateLimit-Remaining': '0',
          'X-RateLimit-Reset': String(clientData.resetTime),
        },
      });
    }

    // リクエスト数を増加
    clientData.count++;

    return null;
  }

  public static getClientIP(request: NextRequest): string {
    const forwarded = request.headers.get('x-forwarded-for');
    const realIP = request.headers.get('x-real-ip');

    if (forwarded) {
      return forwarded.split(',')[0].trim();
    }

    if (realIP) {
      return realIP;
    }

    // Next.js 15では request.ip が削除されたため、ヘッダーから取得
    return request.headers.get('x-real-ip') || 
           request.headers.get('x-client-ip') || 
           'unknown';
  }

  private static cleanup(now: number): void {
    Array.from(this.requests.entries()).forEach(([ip, data]) => {
      if (now > data.resetTime) {
        this.requests.delete(ip);
      }
    });
  }
}

/**
 * 入力値検証ミドルウェア
 */
export class InputValidationMiddleware {
  static async validate(request: NextRequest): Promise<NextResponse | null> {
    // POSTリクエストのボディを検証
    if (request.method === 'POST') {
      try {
        const body = await request.text();

        if (body) {
          // SQLインジェクション攻撃を検出
          if (InputValidation.detectSQLInjection(body)) {
            SecurityLogger.logSecurityEvent(
              'sql_injection_attempt',
              {
                path: request.nextUrl.pathname,
                method: request.method,
                userAgent: request.headers.get('user-agent'),
              },
              'high'
            );

            return new NextResponse('Bad Request', { status: 400 });
          }

          // XSS攻撃を検出
          if (InputValidation.detectXSS(body)) {
            SecurityLogger.logSecurityEvent(
              'xss_attempt',
              {
                path: request.nextUrl.pathname,
                method: request.method,
                userAgent: request.headers.get('user-agent'),
              },
              'high'
            );

            return new NextResponse('Bad Request', { status: 400 });
          }
        }
      } catch (error) {
        // ボディの解析に失敗した場合
        SecurityLogger.logSecurityEvent(
          'malformed_request_body',
          {
            path: request.nextUrl.pathname,
            method: request.method,
            error: String(error),
          },
          'medium'
        );

        return new NextResponse('Bad Request', { status: 400 });
      }
    }

    // URLパラメータを検証
    const searchParams = request.nextUrl.searchParams;
    for (const [key, value] of Array.from(searchParams.entries())) {
      if (
        InputValidation.detectSQLInjection(value) ||
        InputValidation.detectXSS(value)
      ) {
        SecurityLogger.logSecurityEvent(
          'malicious_url_parameter',
          {
            path: request.nextUrl.pathname,
            parameter: key,
            userAgent: request.headers.get('user-agent'),
          },
          'medium'
        );

        return new NextResponse('Bad Request', { status: 400 });
      }
    }

    return null;
  }
}

/**
 * ボット検出ミドルウェア
 */
export class BotDetectionMiddleware {
  private static readonly SUSPICIOUS_USER_AGENTS = [
    /bot/i,
    /crawler/i,
    /spider/i,
    /scraper/i,
    /curl/i,
    /wget/i,
    /python/i,
    /java/i,
    /go-http-client/i,
  ];

  private static readonly ALLOWED_BOTS = [
    /googlebot/i,
    /bingbot/i,
    /slurp/i, // Yahoo
    /duckduckbot/i,
    /facebookexternalhit/i,
    /twitterbot/i,
    /linkedinbot/i,
  ];

  static check(request: NextRequest): NextResponse | null {
    const userAgent = request.headers.get('user-agent') || '';

    // 許可されたボットは通す
    if (this.ALLOWED_BOTS.some(pattern => pattern.test(userAgent))) {
      return null;
    }

    // 疑わしいユーザーエージェントをチェック
    if (this.SUSPICIOUS_USER_AGENTS.some(pattern => pattern.test(userAgent))) {
      SecurityLogger.logSecurityEvent(
        'suspicious_bot_detected',
        {
          userAgent,
          path: request.nextUrl.pathname,
          ip: RateLimitMiddleware.getClientIP(request),
        },
        'low'
      );

      // 疑わしいボットには遅延を追加
      return new NextResponse('Please wait...', {
        status: 429,
        headers: {
          'Retry-After': '60',
        },
      });
    }

    // ユーザーエージェントが空または短すぎる場合
    if (!userAgent || userAgent.length < 10) {
      SecurityLogger.logSecurityEvent(
        'missing_or_short_user_agent',
        {
          userAgent,
          path: request.nextUrl.pathname,
          ip: RateLimitMiddleware.getClientIP(request),
        },
        'low'
      );

      return new NextResponse('Bad Request', { status: 400 });
    }

    return null;
  }
}

/**
 * 地理的制限ミドルウェア（オプション）
 */
export class GeoBlockingMiddleware {
  private static readonly BLOCKED_COUNTRIES: string[] = [
    // 必要に応じて国コードを追加
    // 'CN', 'RU', 'KP'
  ];

  static check(request: NextRequest): NextResponse | null {
    // Next.js 15では request.geo が削除されたため、ヘッダーから取得
    const country = request.headers.get('cf-ipcountry') || 
                   request.headers.get('x-vercel-ip-country');

    if (country && this.BLOCKED_COUNTRIES.includes(country)) {
      SecurityLogger.logSecurityEvent(
        'geo_blocked_request',
        {
          country,
          path: request.nextUrl.pathname,
          ip: RateLimitMiddleware.getClientIP(request),
        },
        'medium'
      );

      return new NextResponse('Access Denied', { status: 403 });
    }

    return null;
  }
}

/**
 * メインセキュリティミドルウェア
 */
export function securityMiddleware(request: NextRequest) {
  // 1. セキュリティヘッダーを設定
  let response = securityHeadersMiddleware(request);

  // 2. レート制限をチェック
  const rateLimitResponse = RateLimitMiddleware.check(request);
  if (rateLimitResponse) {
    return rateLimitResponse;
  }

  // 3. ボット検出
  const botResponse = BotDetectionMiddleware.check(request);
  if (botResponse) {
    return botResponse;
  }

  // 4. 地理的制限（環境変数で制御）
  if (process.env.ENABLE_GEO_BLOCKING === 'true') {
    const geoResponse = GeoBlockingMiddleware.check(request);
    if (geoResponse) {
      return geoResponse;
    }
  }

  // 5. 入力値検証（非同期処理のため別途実装）

  return response;
}

/**
 * 非同期セキュリティチェック
 */
export async function asyncSecurityChecks(
  request: NextRequest
): Promise<NextResponse | null> {
  // 入力値検証
  const validationResponse = await InputValidationMiddleware.validate(request);
  if (validationResponse) {
    return validationResponse;
  }

  return null;
}
