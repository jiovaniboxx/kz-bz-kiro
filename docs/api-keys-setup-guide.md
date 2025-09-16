# 英会話カフェWebサイト - APIキー・トークン設定ガイド

## 📋 概要

このドキュメントでは、Terraformで監視インフラを構築するために必要なAPIキーとトークンの取得方法を詳しく説明します。

## 🎯 必要な認証情報一覧

| サービス | 認証情報 | 用途 | 必須/オプション |
|---------|---------|------|----------------|
| New Relic | Account ID | アカウント識別 | 必須 |
| New Relic | User API Key | リソース管理 | 必須 |
| New Relic | License Key | Browser監視 | 必須 |
| Grafana Cloud | URL | インスタンス接続 | 必須 |
| Grafana Cloud | Service Account Token | リソース管理 | 必須 |
| Grafana Cloud | API Key | フロントエンド統合 | オプション |
| Vercel | Personal Access Token | プロジェクト管理 | 必須 |
| Slack | Webhook URL | アラート通知 | 必須 |
| GitHub | Repository | ソースコード連携 | 必須 |

## 🔴 New Relic 設定

### 前提条件
- New Relicアカウント（無料プランで可）
- 管理者権限

### 1. Account ID の取得

```bash
# 手順:
1. https://one.newrelic.com/ にログイン
2. 右上のアカウント名をクリック
3. "Account settings" を選択
4. "Account ID" をコピー

# 例: 1234567890
```

### 2. User API Key の取得

```bash
# 手順:
1. 右上のアカウント名をクリック
2. "API keys" を選択
3. "Create a key" をクリック
4. 以下を設定:
   - Key type: User
   - Name: terraform-monitoring
   - Notes: Terraform infrastructure management
5. "Create key" をクリック
6. 生成されたキーをコピー

# 形式: NRAK-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### 3. License Key の取得

```bash
# 手順:
1. 右上のアカウント名をクリック
2. "API keys" を選択
3. "License keys" タブを選択
4. "Browser" 用のLicense keyをコピー

# 形式: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### New Relic API テスト

```bash
# API接続テスト
curl -H "Api-Key: YOUR_USER_API_KEY" \
     "https://api.newrelic.com/v2/applications.json"

# 成功時のレスポンス例:
{
  "applications": []
}
```

## 🟠 Grafana Cloud 設定

### 前提条件
- Grafana Cloudアカウント（無料プランで可）
- 組織の管理者権限

### 1. Grafana URL の確認

```bash
# Grafana CloudのダッシュボードURL
# 例: https://your-org.grafana.net

# 確認方法:
1. https://grafana.com/ にログイン
2. ダッシュボードのURLを確認
```

### 2. Service Account Token の作成

```bash
# 手順:
1. Grafana Cloudにログイン
2. 左サイドバー → "Administration" → "Service accounts"
3. "Add service account" をクリック
4. 以下を設定:
   - Display name: terraform-monitoring
   - Role: Admin
5. "Create" をクリック
6. "Add service account token" をクリック
7. Token name: terraform-token
8. "Generate token" をクリック
9. 生成されたトークンをコピー

# 形式: glsa_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_XXXXXXXX
```

### 3. API Key の作成 (オプション)

```bash
# 手順:
1. 左サイドバー → "Configuration" → "API Keys"
2. "New API Key" をクリック
3. 以下を設定:
   - Key name: frontend-integration
   - Role: Viewer
4. "Add" をクリック
5. 生成されたキーをコピー

# 形式: eyJrIjoiXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Grafana API テスト

```bash
# API接続テスト
curl -H "Authorization: Bearer YOUR_SERVICE_ACCOUNT_TOKEN" \
     "https://your-org.grafana.net/api/org"

# 成功時のレスポンス例:
{
  "id": 1,
  "name": "your-org",
  "address": {
    "address1": "",
    "address2": "",
    "city": "",
    "zipCode": "",
    "state": "",
    "country": ""
  }
}
```

## 🔵 Vercel 設定

### 前提条件
- Vercelアカウント
- プロジェクトの管理権限

### Personal Access Token の作成

```bash
# 手順:
1. https://vercel.com/ にログイン
2. 右上のアバター → "Settings"
3. 左サイドバー → "Tokens"
4. "Create Token" をクリック
5. 以下を設定:
   - Token Name: terraform-monitoring
   - Scope: Full Account
   - Expiration: No Expiration (推奨)
6. "Create" をクリック
7. 生成されたトークンをコピー

# 形式: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Vercel API テスト

```bash
# API接続テスト
curl -H "Authorization: Bearer YOUR_VERCEL_TOKEN" \
     "https://api.vercel.com/v2/user"

# 成功時のレスポンス例:
{
  "user": {
    "uid": "XXXXXXXX",
    "email": "user@example.com",
    "name": "User Name",
    "username": "username"
  }
}
```

## 🟣 Render 設定

### 前提条件
- Renderアカウント
- プロジェクトの管理権限

### API Key の取得

```bash
# 手順:
1. https://render.com/ にログイン
2. 右上のアバター → "Account Settings"
3. 左サイドバー → "API Keys"
4. "Create API Key" をクリック
5. 以下を設定:
   - Name: terraform-monitoring
   - Permissions: Full Access
6. "Create" をクリック
7. 生成されたキーをコピー

# 形式: rnd_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Render API テスト

```bash
# API接続テスト
curl -H "Authorization: Bearer YOUR_RENDER_API_KEY" \
     "https://api.render.com/v1/services"

# 成功時のレスポンス例:
{
  "services": []
}
```

## 📢 Slack 通知設定

### 前提条件
- Slackワークスペースの管理権限
- 通知用チャンネルの作成権限

### Incoming Webhook の作成

```bash
# 手順:
1. https://api.slack.com/apps にアクセス
2. "Create New App" をクリック
3. "From scratch" を選択
4. 以下を設定:
   - App Name: English Cafe Monitoring
   - Pick a workspace: 対象のワークスペース
5. "Create App" をクリック
6. 左サイドバー → "Incoming Webhooks"
7. "Activate Incoming Webhooks" をオンにする
8. "Add New Webhook to Workspace" をクリック
9. 通知先チャンネルを選択（例: #prod-alerts）
10. "Allow" をクリック
11. 生成されたWebhook URLをコピー

# 形式: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
```

### Slack Webhook テスト

```bash
# Webhook接続テスト
curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Hello from English Cafe Monitoring!"}' \
     YOUR_WEBHOOK_URL

# 成功時: Slackチャンネルにメッセージが投稿される
```

## 🔧 terraform.tfvars 設定例

```hcl
# terraform/environments/prod/terraform.tfvars

# Application Configuration
application_name = "english-cafe-prod"
aws_region      = "ap-northeast-1"

# New Relic Configuration
newrelic_account_id  = "1234567890"
newrelic_api_key     = "NRAK-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
newrelic_license_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Grafana Configuration
grafana_url                  = "https://your-org.grafana.net"
grafana_auth_token          = "glsa_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_XXXXXXXX"
grafana_prometheus_endpoint = "https://prometheus-prod-01-eu-west-0.grafana.net/api/prom"
grafana_api_key            = "eyJrIjoiXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Prometheus Configuration (Grafana Cloud内蔵)
prometheus_url      = "https://prometheus-prod-01-eu-west-0.grafana.net/api/prom"
prometheus_username = "your-prometheus-username"
prometheus_password = "your-prometheus-password"

# Vercel Configuration
vercel_api_token    = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
vercel_project_name = "english-cafe"
custom_domain       = "english-cafe.com"  # オプション

# Render Configuration
render_service_name = "english-cafe-api"

# GitHub Configuration
github_repository = "your-org/english-cafe-website"

# Notification Configuration
slack_webhook_url           = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
admin_email                = "admin@english-cafe.com"
pagerduty_integration_key   = ""  # オプション

# Runbook Configuration
runbook_url = "https://github.com/your-org/english-cafe/wiki/runbooks"

# Alert Thresholds (Production)
alert_thresholds = {
  error_rate_critical    = 2
  error_rate_warning     = 1
  response_time_critical = 2000
  response_time_warning  = 1500
  memory_usage_critical  = 80
  memory_usage_warning   = 70
  lcp_critical          = 2500
  lcp_warning           = 2000
  fid_critical          = 100
  fid_warning           = 75
  cls_critical          = 0.1
  cls_warning           = 0.05
}
```

## 🔒 セキュリティのベストプラクティス

### 1. 環境変数での管理

```bash
# 機密情報を環境変数で管理（推奨）
export TF_VAR_newrelic_api_key="NRAK-XXXXXXXX"
export TF_VAR_newrelic_license_key="XXXXXXXX"
export TF_VAR_grafana_auth_token="glsa_XXXXXXXX"
export TF_VAR_vercel_api_token="XXXXXXXX"
export TF_VAR_slack_webhook_url="https://hooks.slack.com/services/XXXXXXXX"

# terraform.tfvarsファイルは使用しない
```

### 2. 権限の最小化

```bash
# New Relic: User API Key（Admin権限不要）
# Grafana: Service Account（必要最小限のRole）
# Vercel: Project-specific token（可能であれば）
```

### 3. トークンのローテーション

```bash
# 定期的なトークン更新スケジュール
# - New Relic API Key: 6ヶ月毎
# - Grafana Service Account Token: 3ヶ月毎
# - Vercel Personal Access Token: 6ヶ月毎
# - Slack Webhook: 必要時のみ
```

### 4. .gitignore の確認

```bash
# 以下のファイルが除外されていることを確認
*.tfvars
*.tfstate
*.tfstate.*
.terraform/
.env
.env.*
```

## 🧪 統合テスト

### 全API接続テスト スクリプト

```bash
#!/bin/bash
# test-api-connections.sh

echo "🔍 Testing API connections..."

# New Relic
echo "Testing New Relic API..."
curl -s -H "Api-Key: $TF_VAR_newrelic_api_key" \
     "https://api.newrelic.com/v2/applications.json" | jq .

# Grafana
echo "Testing Grafana API..."
curl -s -H "Authorization: Bearer $TF_VAR_grafana_auth_token" \
     "$TF_VAR_grafana_url/api/org" | jq .

# Vercel
echo "Testing Vercel API..."
curl -s -H "Authorization: Bearer $TF_VAR_vercel_api_token" \
     "https://api.vercel.com/v2/user" | jq .

# Slack
echo "Testing Slack Webhook..."
curl -s -X POST -H 'Content-type: application/json' \
     --data '{"text":"API connection test successful!"}' \
     "$TF_VAR_slack_webhook_url"

echo "✅ All API tests completed!"
```

## 🚀 デプロイ手順

### 1. 認証情報の設定

```bash
# 環境変数で設定（推奨）
source .env

# または terraform.tfvars で設定
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvars を編集
```

### 2. 接続テスト

```bash
# API接続テスト
./test-api-connections.sh

# Terraform設定検証
cd terraform/environments/prod
./scripts/validate.sh
```

### 3. デプロイ実行

```bash
# プラン確認
./scripts/deploy.sh prod plan

# デプロイ実行
./scripts/deploy.sh prod apply
```

## 🔧 トラブルシューティング

### よくあるエラーと解決方法

#### 1. New Relic 401 Unauthorized
```bash
# 原因: API Keyが無効または権限不足
# 解決: User API Keyを使用、Account IDが正しいか確認
```

#### 2. Grafana 403 Forbidden
```bash
# 原因: Service Account Tokenの権限不足
# 解決: Service AccountのRoleをAdminに変更
```

#### 3. Vercel 403 Forbidden
```bash
# 原因: Personal Access TokenのScope不足
# 解決: Full Account scopeのトークンを使用
```

#### 4. Slack Webhook エラー
```bash
# 原因: Webhook URLが無効
# 解決: 新しいWebhookを作成、URLを確認
```

## 📚 参考リンク

### 公式ドキュメント
- [New Relic API Documentation](https://docs.newrelic.com/docs/apis/intro-apis/introduction-new-relic-apis/)
- [Grafana HTTP API](https://grafana.com/docs/grafana/latest/developers/http_api/)
- [Vercel API Documentation](https://vercel.com/docs/rest-api)
- [Slack API Documentation](https://api.slack.com/)

### Terraform Providers
- [New Relic Provider](https://registry.terraform.io/providers/newrelic/newrelic/latest/docs)
- [Grafana Provider](https://registry.terraform.io/providers/grafana/grafana/latest/docs)
- [Vercel Provider](https://registry.terraform.io/providers/vercel/vercel/latest/docs)

## 📞 サポート

### 技術的な問題
- GitHub Issues: [リポジトリURL]/issues
- Slack: #engineering-support

### 緊急時
- Slack: #prod-alerts
- Email: engineering-team@english-cafe.com

### ドキュメント更新
- このドキュメントの更新: [リポジトリURL]/docs/api-keys-setup-guide.md
- Wiki: [リポジトリURL]/wiki