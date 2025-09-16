# Vercelデプロイメントガイド

## 概要

このドキュメントでは、English Cafe WebサイトのフロントエンドをVercelにデプロイする手順を説明します。

## 前提条件

- Vercelアカウントの作成
- GitHubリポジトリの準備
- 必要な環境変数の準備

## デプロイ手順

### 1. Vercelプロジェクトの作成

1. [Vercel Dashboard](https://vercel.com/dashboard)にアクセス
2. "New Project"をクリック
3. GitHubリポジトリを選択
4. プロジェクト設定を行う

### 2. プロジェクト設定

#### Framework Preset

- **Framework**: Next.js
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Install Command**: `npm install`

#### 環境変数の設定

以下の環境変数をVercel Dashboardで設定してください：

```bash
# 必須環境変数
NEXT_PUBLIC_API_URL=https://english-cafe-backend.onrender.com
NEXT_PUBLIC_SITE_URL=https://english-cafe.vercel.app

# Google Services（取得後に設定）
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
NEXT_PUBLIC_GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

### 3. ドメイン設定

#### カスタムドメインの設定（オプション）

1. Vercel Dashboardでプロジェクトを選択
2. "Settings" → "Domains"に移動
3. カスタムドメインを追加
4. DNS設定を更新

#### SSL証明書

- Vercelが自動的にSSL証明書を発行・更新
- Let's Encryptを使用

### 4. デプロイメント設定

#### 自動デプロイ

- `main`ブランチへのプッシュで本番環境に自動デプロイ
- プルリクエストでプレビュー環境を自動作成

#### ブランチ設定

```bash
# 本番環境
Production Branch: main

# プレビュー環境
Preview Branches: develop, feature/*
```

## 環境変数詳細

### 必須環境変数

| 変数名                 | 説明                 | 例                                          |
| ---------------------- | -------------------- | ------------------------------------------- |
| `NEXT_PUBLIC_API_URL`  | バックエンドAPIのURL | `https://english-cafe-backend.onrender.com` |
| `NEXT_PUBLIC_SITE_URL` | フロントエンドのURL  | `https://english-cafe.vercel.app`           |

### オプション環境変数

| 変数名                            | 説明                | 例                                 |
| --------------------------------- | ------------------- | ---------------------------------- |
| `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` | Google Maps API Key | `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXX` |
| `NEXT_PUBLIC_GOOGLE_ANALYTICS_ID` | Google Analytics ID | `G-XXXXXXXXXX`                     |

## パフォーマンス最適化

### 自動最適化機能

- **画像最適化**: Next.js Image Optimization
- **コード分割**: 自動的なチャンク分割
- **CDN**: Vercel Edge Network
- **キャッシュ**: 静的アセットの自動キャッシュ

### カスタム最適化

```javascript
// next.config.js での設定
module.exports = {
  // 画像最適化
  images: {
    domains: ['english-cafe-backend.onrender.com'],
    formats: ['image/webp', 'image/avif'],
  },

  // コンパイラ最適化
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
};
```

## セキュリティ設定

### セキュリティヘッダー

`vercel.json`で以下のセキュリティヘッダーを設定：

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

### CORS設定

APIエンドポイント用のCORS設定：

```json
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "https://english-cafe.vercel.app"
        }
      ]
    }
  ]
}
```

## 監視とログ

### Vercel Analytics

1. Vercel Dashboardで"Analytics"を有効化
2. パフォーマンスメトリクスの監視
3. Core Web Vitalsの追跡

### エラー監視

```javascript
// pages/_app.tsx
export function reportWebVitals(metric) {
  // カスタムアナリティクスに送信
  console.log(metric);
}
```

## トラブルシューティング

### よくある問題

#### 1. ビルドエラー

```bash
# 依存関係の問題
npm install --legacy-peer-deps

# TypeScriptエラー
npm run type-check
```

#### 2. 環境変数が反映されない

- 環境変数名が`NEXT_PUBLIC_`で始まっているか確認
- Vercel Dashboardで正しく設定されているか確認
- デプロイ後に再ビルドが必要

#### 3. 画像が表示されない

- `next.config.js`の`images.domains`に追加
- 画像URLが正しいか確認

### デバッグ方法

```bash
# ローカルでの本番ビルドテスト
npm run build
npm run start

# Vercelログの確認
vercel logs [deployment-url]
```

## CI/CD設定

### GitHub Actions（オプション）

```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

## バックアップとロールバック

### デプロイメント履歴

- Vercel Dashboardで過去のデプロイメントを確認
- ワンクリックでロールバック可能

### データベース連携

- バックエンドAPIとの連携確認
- データベースマイグレーションとの同期

## スケーリング

### 自動スケーリング

- Vercelが自動的にトラフィックに応じてスケール
- Edge Functionsによる地理的分散

### パフォーマンス監視

```javascript
// Web Vitalsの監視
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getFCP(console.log);
getLCP(console.log);
getTTFB(console.log);
```

## サポートとメンテナンス

### 定期メンテナンス

- 依存関係の更新
- セキュリティパッチの適用
- パフォーマンス最適化の見直し

### 監視項目

- アップタイム
- レスポンス時間
- エラー率
- Core Web Vitals

## 参考リンク

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Vercel CLI](https://vercel.com/docs/cli)
