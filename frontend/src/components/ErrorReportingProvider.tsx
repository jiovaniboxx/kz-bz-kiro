/**
 * エラー報告プロバイダー
 */
'use client';

import React, { useEffect } from 'react';
import { errorReporter } from '@/utils/errorReporting';

interface ErrorReportingProviderProps {
  children: React.ReactNode;
}

export const ErrorReportingProvider: React.FC<ErrorReportingProviderProps> = ({
  children,
}) => {
  useEffect(() => {
    // エラー報告システムの初期化は既にerrorReporter内で行われている

    // 認証状態が変わった場合にユーザーIDを設定
    const handleAuthChange = () => {
      // 認証ストアからユーザー情報を取得してセット
      // 実装は認証システムに依存
    };

    // 開発環境でのデバッグ情報
    if (process.env.NODE_ENV === 'development') {
      console.log('Error reporting system initialized');

      // 開発環境でのテスト用グローバル関数
      (window as any).testErrorReporting = () => {
        errorReporter.reportCustomError('Test error from console', {
          test: true,
          timestamp: new Date().toISOString(),
        });
      };

      (window as any).getErrorReports = () => {
        return errorReporter.getStoredErrorReports();
      };

      (window as any).clearErrorReports = () => {
        errorReporter.clearStoredErrorReports();
      };
    }

    return () => {
      // クリーンアップ処理
    };
  }, []);

  return <>{children}</>;
};
