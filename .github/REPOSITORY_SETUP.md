# Repository Setup Guide

このドキュメントでは、GitHubリポジトリの推奨設定について説明します。

## ブランチ戦略

### メインブランチ
- `main`: 本番環境にデプロイされる安定版
- `develop`: 開発中の機能を統合するブランチ

### 機能ブランチ
- `feature/[機能名]`: 新機能開発用
- `bugfix/[バグ名]`: バグ修正用
- `hotfix/[修正名]`: 緊急修正用
- `chore/[作業名]`: メンテナンス作業用

## ブランチ保護ルール

### main ブランチ
以下の設定を推奨します：

1. **Protect this branch**: ✅
2. **Require a pull request before merging**: ✅
   - Require approvals: 1
   - Dismiss stale PR approvals when new commits are pushed: ✅
   - Require review from code owners: ✅
3. **Require status checks to pass before merging**: ✅
   - Require branches to be up to date before merging: ✅
   - Status checks:
     - `frontend-test`
     - `backend-test`
     - `e2e-test`
     - `security-scan`
4. **Require conversation resolution before merging**: ✅
5. **Require signed commits**: ✅ (推奨)
6. **Require linear history**: ✅
7. **Include administrators**: ✅

### develop ブランチ
以下の設定を推奨します：

1. **Protect this branch**: ✅
2. **Require a pull request before merging**: ✅
   - Require approvals: 1
3. **Require status checks to pass before merging**: ✅
   - Status checks:
     - `frontend-test`
     - `backend-test`

## リポジトリ設定

### General Settings
- **Default branch**: `main`
- **Template repository**: ❌
- **Issues**: ✅
- **Projects**: ✅
- **Wiki**: ❌ (ドキュメントはREADMEとdocsディレクトリで管理)
- **Discussions**: ✅ (コミュニティがある場合)

### Pull Requests
- **Allow merge commits**: ❌
- **Allow squash merging**: ✅
- **Allow rebase merging**: ✅
- **Always suggest updating pull request branches**: ✅
- **Allow auto-merge**: ✅
- **Automatically delete head branches**: ✅

### Security
- **Dependency graph**: ✅
- **Dependabot alerts**: ✅
- **Dependabot security updates**: ✅
- **Code scanning alerts**: ✅
- **Secret scanning alerts**: ✅

## 必要なSecrets

以下のSecretsをリポジトリに設定してください：

### 本番デプロイ用
- `PRODUCTION_DEPLOY_KEY`: 本番環境へのデプロイキー
- `DATABASE_URL`: 本番データベースURL
- `EMAIL_API_KEY`: メール送信サービスのAPIキー

### 外部サービス連携用
- `CODECOV_TOKEN`: コードカバレッジレポート用
- `SENTRY_DSN`: エラー監視用（オプション）

## Environment設定

### production
- **Required reviewers**: 1人以上
- **Wait timer**: 0分
- **Deployment branches**: `main`ブランチのみ

## ラベル設定

以下のラベルを作成することを推奨します：

### 種類
- `bug`: バグ報告
- `enhancement`: 新機能・改善
- `documentation`: ドキュメント関連
- `question`: 質問
- `help wanted`: ヘルプ募集

### 優先度
- `priority: low`: 低優先度
- `priority: medium`: 中優先度
- `priority: high`: 高優先度
- `priority: critical`: 緊急

### 状態
- `status: in progress`: 作業中
- `status: needs review`: レビュー待ち
- `status: blocked`: ブロック中

### 領域
- `area: frontend`: フロントエンド
- `area: backend`: バックエンド
- `area: infrastructure`: インフラ
- `area: testing`: テスト

## コミットメッセージ規約

Conventional Commitsを使用することを推奨します：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: フォーマット
- `refactor`: リファクタリング
- `test`: テスト
- `chore`: その他

### Examples
```
feat(auth): add user authentication
fix(api): resolve contact form validation issue
docs: update README with setup instructions
chore(deps): update dependencies
```

## 自動化設定

### GitHub Actions
- CI/CDパイプラインが自動実行されます
- PRチェックが自動実行されます
- 依存関係の更新が週次で自動実行されます

### Dependabot
`.github/dependabot.yml`を作成して依存関係の自動更新を設定してください。

## セキュリティ

### Code Scanning
- CodeQLが自動実行されます
- Trivyによる脆弱性スキャンが実行されます

### Secret Scanning
- GitHubのSecret Scanningが有効になります
- 誤ってコミットされたシークレットを検出します

## 監視とアラート

### 通知設定
- 重要なワークフローの失敗時にSlack/Teamsに通知
- セキュリティアラートの通知
- デプロイ完了/失敗の通知

この設定により、安全で効率的な開発フローを実現できます。