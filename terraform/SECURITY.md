# Terraform セキュリティガイド

## APIキー管理のベストプラクティス

### 1. 本番環境での設定方法

#### オプション A: terraform.tfvars ファイル（ローカル開発推奨）
```bash
cd terraform/environments/prod
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvars を編集して実際のAPIキーを設定
```

#### オプション B: 環境変数（CI/CD推奨）
```bash
# 環境変数を設定
source ../../scripts/set-env-vars.sh
```

### 2. 必要なAPIキーの取得方法

#### New Relic
1. [New Relic One](https://one.newrelic.com) にログイン
2. Account Settings → API Keys
3. 以下を取得：
   - Account ID
   - User API Key
   - License Key

#### Grafana Cloud
1. [Grafana Cloud](https://grafana.com) にログイン
2. My Account → API Keys
3. Service Account Token を作成

#### Render
1. [Render Dashboard](https://dashboard.render.com) にログイン
2. Account Settings → API Keys
3. API Key を作成（`rnd_` で始まる）

### 3. セキュリティチェックリスト

- [ ] `terraform.tfvars` が `.gitignore` に含まれている
- [ ] APIキーに適切な権限のみが設定されている
- [ ] 定期的にAPIキーをローテーションしている
- [ ] CI/CDでは環境変数を使用している
- [ ] 本番環境のAPIキーは開発環境と分離している

### 4. 緊急時の対応

APIキーが漏洩した場合：
1. 該当サービスでAPIキーを即座に無効化
2. 新しいAPIキーを生成
3. terraform.tfvars または環境変数を更新
4. `terraform plan` で変更を確認
5. `terraform apply` で適用

### 5. 監査とモニタリング

- APIキーの使用状況を定期的に確認
- 不審なアクティビティがないかモニタリング
- アクセスログの定期的な確認