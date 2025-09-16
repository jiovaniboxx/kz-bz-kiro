/**
 * Dynamic Import Utilities
 * 動的インポートのユーティリティ関数
 */

import dynamic from 'next/dynamic';
import React, { ComponentType } from 'react';

// 高階関数：任意のコンポーネントを動的インポート化
export function createDynamicComponent<P extends object>(
  importFn: () => Promise<{ default: ComponentType<P> }>,
  options: {
    loading?: () => React.ReactElement | null;
    ssr?: boolean;
  } = {}
) {
  return dynamic(importFn, {
    loading:
      options.loading || (() => React.createElement('div', null, 'Loading...')),
    ssr: options.ssr ?? false,
  });
}

// プリロード関数
export const preloadComponent = (importFn: () => Promise<any>) => {
  if (typeof window !== 'undefined') {
    // ブラウザ環境でのみ実行
    importFn();
  }
};

// 重要なコンポーネントのプリロード
export const preloadCriticalComponents = () => {
  // 基本的なプリロード処理
  console.log('Preloading critical components...');
};
