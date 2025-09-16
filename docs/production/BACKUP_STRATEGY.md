# バックアップ戦略・設定ガイド

## 概要

英会話カフェWebサイトのデータ保護とビジネス継続性を確保するためのバックアップ戦略と設定ガイド。

---

## 1. バックアップ戦略の基本方針

### 1.1 バックアップ目標

- **RTO (Recovery Time Objective)**: 4時間以内
- **RPO (Recovery Point Objective)**: 24時間以内
- **データ保持期間**: 30日間（日次）、12ヶ月間（月次）
- **可用性目標**: 99.9%

### 1.2 バックアップ対象

#### 重要度: 高
- **PostgreSQLデータベース**: 問い合わせデータ、管理者情報
- **アプリケーション設定**: 環境変数、設定ファイル
- **SSL証明書**: セキュリティ証明書

#### 重要度: 中
- **ログファイル**: アクセスログ、エラーログ
- **静的ファイル**: 画像、ドキュメント

#### 重要度: 低
- **一時ファイル**: キャッシュ、セッションデータ

### 1.3 バックアップ方式

- **フルバックアップ**: 週次（日曜日 2:00 AM）
- **増分バックアップ**: 日次（毎日 2:00 AM）
- **リアルタイムレプリケーション**: データベース（将来実装）

---

## 2. データベースバックアップ

### 2.1 PostgreSQL バックアップ設定

#### 自動バックアップスクリプト

```bash
#!/bin/bash
# db-backup.sh - PostgreSQLデータベースバックアップスクリプト

set -e

# 設定
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-english_cafe_db}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD}"
BACKUP_DIR="${BACKUP_DIR:-/backups/database}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# ログ設定
LOG_FILE="/var/log/db-backup.log"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# バックアップディレクトリ作成
mkdir -p "$BACKUP_DIR"

log "データベースバックアップを開始します"

# PostgreSQLダンプ実行
export PGPASSWORD="$DB_PASSWORD"

if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
   --verbose --clean --if-exists --create > "$BACKUP_FILE"; then
    
    log "バックアップが正常に完了しました: $BACKUP_FILE"
    
    # 圧縮
    gzip "$BACKUP_FILE"
    log "バックアップファイルを圧縮しました: $BACKUP_FILE.gz"
    
    # バックアップサイズ確認
    BACKUP_SIZE=$(du -h "$BACKUP_FILE.gz" | cut -f1)
    log "バックアップサイズ: $BACKUP_SIZE"
    
    # 古いバックアップファイル削除
    find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    log "古いバックアップファイルを削除しました（$RETENTION_DAYS日以前）"
    
    # バックアップ検証
    if zcat "$BACKUP_FILE.gz" | head -10 | grep -q "PostgreSQL database dump"; then
        log "バックアップファイルの整合性確認: OK"
    else
        log "ERROR: バックアップファイルの整合性確認: NG"
        exit 1
    fi
    
else
    log "ERROR: データベースバックアップに失敗しました"
    exit 1
fi

unset PGPASSWORD
log "データベースバックアップが完了しました"
```

#### cron設定

```bash
# crontab -e で設定
# 毎日午前2時にデータベースバックアップ実行
0 2 * * * /scripts/db-backup.sh >> /var/log/cron.log 2>&1

# 毎週日曜日午前1時にフルバックアップ実行
0 1 * * 0 /scripts/db-full-backup.sh >> /var/log/cron.log 2>&1
```

### 2.2 Render PostgreSQL バックアップ

#### Render CLI を使用したバックアップ

```bash
#!/bin/bash
# render-db-backup.sh

# Render CLI インストール（初回のみ）
# curl -fsSL https://cli.render.com/install | sh

# 認証（初回のみ）
# render auth login

# データベースバックアップ作成
render postgres backup create --database-id="your-database-id"

# バックアップ一覧確認
render postgres backup list --database-id="your-database-id"

# バックアップダウンロード
BACKUP_ID=$(render postgres backup list --database-id="your-database-id" --format=json | jq -r '.[0].id')
render postgres backup download --database-id="your-database-id" --backup-id="$BACKUP_ID" --output="backup_$(date +%Y%m%d).sql"
```

### 2.3 バックアップ復旧手順

#### ローカル環境での復旧

```bash
#!/bin/bash
# db-restore.sh - データベース復旧スクリプト

set -e

BACKUP_FILE="$1"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-english_cafe_db}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD}"

if [ -z "$BACKUP_FILE" ]; then
    echo "使用方法: $0 <backup_file.sql.gz>"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "エラー: バックアップファイルが見つかりません: $BACKUP_FILE"
    exit 1
fi

echo "データベース復旧を開始します..."
echo "バックアップファイル: $BACKUP_FILE"
echo "対象データベース: $DB_NAME"

# 確認プロンプト
read -p "本当に復旧を実行しますか？ (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "復旧をキャンセルしました"
    exit 0
fi

# データベース復旧実行
export PGPASSWORD="$DB_PASSWORD"

if zcat "$BACKUP_FILE" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; then
    echo "データベース復旧が正常に完了しました"
else
    echo "エラー: データベース復旧に失敗しました"
    exit 1
fi

unset PGPASSWORD
echo "復旧処理が完了しました"
```

#### 本番環境での復旧

```bash
#!/bin/bash
# production-restore.sh

# 1. メンテナンスモード有効化
echo "メンテナンスモードを有効化します..."
# Vercel: メンテナンスページの表示
# Render: サービス停止

# 2. 現在のデータベースバックアップ作成
echo "現在のデータベースをバックアップします..."
./db-backup.sh

# 3. データベース復旧実行
echo "データベースを復旧します..."
./db-restore.sh "$1"

# 4. アプリケーション再起動
echo "アプリケーションを再起動します..."
# Render: サービス再起動

# 5. 動作確認
echo "動作確認を実行します..."
curl -f https://english-cafe-backend.onrender.com/health

# 6. メンテナンスモード解除
echo "メンテナンスモードを解除します..."
# 正常動作確認後にメンテナンスページを無効化

echo "本番環境復旧が完了しました"
```

---

## 3. アプリケーションバックアップ

### 3.1 ソースコード管理

#### Git リポジトリバックアップ

```bash
#!/bin/bash
# git-backup.sh - Gitリポジトリバックアップ

REPO_URL="https://github.com/your-org/english-cafe-website.git"
BACKUP_DIR="/backups/git"
DATE=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$BACKUP_DIR"

# リポジトリクローン（ミラー）
git clone --mirror "$REPO_URL" "$BACKUP_DIR/repo_mirror_$DATE"

# アーカイブ作成
cd "$BACKUP_DIR"
tar -czf "repo_backup_$DATE.tar.gz" "repo_mirror_$DATE"

# 古いバックアップ削除
find "$BACKUP_DIR" -name "repo_backup_*.tar.gz" -mtime +30 -delete
find "$BACKUP_DIR" -name "repo_mirror_*" -mtime +7 -exec rm -rf {} \;

echo "Gitリポジトリバックアップが完了しました: repo_backup_$DATE.tar.gz"
```

### 3.2 設定ファイルバックアップ

#### 環境変数・設定バックアップ

```bash
#!/bin/bash
# config-backup.sh - 設定ファイルバックアップ

BACKUP_DIR="/backups/config"
DATE=$(date +"%Y%m%d_%H%M%S")
CONFIG_BACKUP="$BACKUP_DIR/config_backup_$DATE"

mkdir -p "$CONFIG_BACKUP"

# 環境変数バックアップ（機密情報は除く）
echo "# Environment Variables Backup - $DATE" > "$CONFIG_BACKUP/env_vars.txt"
env | grep -E "^(NODE_ENV|NEXT_PUBLIC_|DATABASE_URL|FRONTEND_URL|BACKEND_URL)" >> "$CONFIG_BACKUP/env_vars.txt"

# Docker設定バックアップ
cp docker-compose.yml "$CONFIG_BACKUP/"
cp Dockerfile* "$CONFIG_BACKUP/" 2>/dev/null || true

# Nginx設定バックアップ（該当する場合）
cp /etc/nginx/sites-available/english-cafe "$CONFIG_BACKUP/" 2>/dev/null || true

# SSL証明書バックアップ（該当する場合）
mkdir -p "$CONFIG_BACKUP/ssl"
cp /etc/ssl/certs/english-cafe.* "$CONFIG_BACKUP/ssl/" 2>/dev/null || true

# アーカイブ作成
cd "$BACKUP_DIR"
tar -czf "config_backup_$DATE.tar.gz" "config_backup_$DATE"
rm -rf "config_backup_$DATE"

# 古いバックアップ削除
find "$BACKUP_DIR" -name "config_backup_*.tar.gz" -mtime +30 -delete

echo "設定ファイルバックアップが完了しました: config_backup_$DATE.tar.gz"
```

### 3.3 ログファイルバックアップ

```bash
#!/bin/bash
# log-backup.sh - ログファイルバックアップ

LOG_DIRS=(
    "/var/log/nginx"
    "/var/log/app"
    "/var/log/postgresql"
)

BACKUP_DIR="/backups/logs"
DATE=$(date +"%Y%m%d")
LOG_BACKUP="$BACKUP_DIR/logs_backup_$DATE"

mkdir -p "$LOG_BACKUP"

for log_dir in "${LOG_DIRS[@]}"; do
    if [ -d "$log_dir" ]; then
        dir_name=$(basename "$log_dir")
        mkdir -p "$LOG_BACKUP/$dir_name"
        
        # 過去7日間のログをバックアップ
        find "$log_dir" -name "*.log*" -mtime -7 -exec cp {} "$LOG_BACKUP/$dir_name/" \;
    fi
done

# アーカイブ作成
cd "$BACKUP_DIR"
tar -czf "logs_backup_$DATE.tar.gz" "logs_backup_$DATE"
rm -rf "logs_backup_$DATE"

# 古いログバックアップ削除（7日間保持）
find "$BACKUP_DIR" -name "logs_backup_*.tar.gz" -mtime +7 -delete

echo "ログファイルバックアップが完了しました: logs_backup_$DATE.tar.gz"
```

---

## 4. クラウドストレージバックアップ

### 4.1 AWS S3 バックアップ

```bash
#!/bin/bash
# s3-backup.sh - AWS S3へのバックアップ

# AWS CLI設定が必要
# aws configure

S3_BUCKET="english-cafe-backups"
LOCAL_BACKUP_DIR="/backups"
S3_PREFIX="production"

# S3バケット作成（初回のみ）
aws s3 mb s3://$S3_BUCKET --region ap-northeast-1

# バックアップファイルをS3にアップロード
aws s3 sync "$LOCAL_BACKUP_DIR" "s3://$S3_BUCKET/$S3_PREFIX" \
    --exclude "*.tmp" \
    --delete \
    --storage-class STANDARD_IA

# 古いバックアップの削除（S3 Lifecycle Policy推奨）
aws s3api put-bucket-lifecycle-configuration \
    --bucket $S3_BUCKET \
    --lifecycle-configuration file://s3-lifecycle.json

echo "S3バックアップが完了しました"
```

#### S3 Lifecycle Policy設定

```json
{
  "Rules": [
    {
      "ID": "BackupRetentionRule",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "production/"
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "GLACIER"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ],
      "Expiration": {
        "Days": 2555
      }
    }
  ]
}
```

### 4.2 Google Cloud Storage バックアップ

```bash
#!/bin/bash
# gcs-backup.sh - Google Cloud Storageへのバックアップ

# gcloud CLI設定が必要
# gcloud auth login
# gcloud config set project your-project-id

GCS_BUCKET="english-cafe-backups"
LOCAL_BACKUP_DIR="/backups"

# バケット作成（初回のみ）
gsutil mb -l asia-northeast1 gs://$GCS_BUCKET

# バックアップファイルをGCSにアップロード
gsutil -m rsync -r -d "$LOCAL_BACKUP_DIR" "gs://$GCS_BUCKET/production"

# オブジェクトライフサイクル設定
gsutil lifecycle set gcs-lifecycle.json gs://$GCS_BUCKET

echo "GCSバックアップが完了しました"
```

---

## 5. バックアップ監視・検証

### 5.1 バックアップ監視スクリプト

```bash
#!/bin/bash
# backup-monitor.sh - バックアップ監視

BACKUP_DIR="/backups"
LOG_FILE="/var/log/backup-monitor.log"
ALERT_EMAIL="admin@english-cafe.com"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

send_alert() {
    local subject="$1"
    local message="$2"
    
    echo "$message" | mail -s "$subject" "$ALERT_EMAIL"
    log "アラートを送信しました: $subject"
}

# 1. 最新バックアップファイルの存在確認
check_latest_backup() {
    local backup_type="$1"
    local max_age_hours="$2"
    
    latest_backup=$(find "$BACKUP_DIR" -name "${backup_type}_backup_*.gz" -mtime -1 | sort | tail -1)
    
    if [ -z "$latest_backup" ]; then
        send_alert "バックアップエラー" "${backup_type}の最新バックアップが見つかりません"
        return 1
    fi
    
    # ファイル年齢確認
    file_age=$(( ($(date +%s) - $(stat -c %Y "$latest_backup")) / 3600 ))
    
    if [ $file_age -gt $max_age_hours ]; then
        send_alert "バックアップ警告" "${backup_type}のバックアップが古すぎます（${file_age}時間前）"
        return 1
    fi
    
    log "${backup_type}バックアップ確認: OK ($latest_backup)"
    return 0
}

# 2. バックアップファイルサイズ確認
check_backup_size() {
    local backup_file="$1"
    local min_size_mb="$2"
    
    if [ ! -f "$backup_file" ]; then
        return 1
    fi
    
    file_size_mb=$(( $(stat -c %s "$backup_file") / 1024 / 1024 ))
    
    if [ $file_size_mb -lt $min_size_mb ]; then
        send_alert "バックアップサイズ警告" "バックアップファイルサイズが小さすぎます: ${file_size_mb}MB"
        return 1
    fi
    
    log "バックアップサイズ確認: OK (${file_size_mb}MB)"
    return 0
}

# 3. バックアップ整合性確認
check_backup_integrity() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        return 1
    fi
    
    # gzipファイルの整合性確認
    if ! gzip -t "$backup_file" 2>/dev/null; then
        send_alert "バックアップ整合性エラー" "バックアップファイルが破損しています: $backup_file"
        return 1
    fi
    
    # SQLダンプの基本構造確認
    if zcat "$backup_file" | head -10 | grep -q "PostgreSQL database dump"; then
        log "バックアップ整合性確認: OK"
        return 0
    else
        send_alert "バックアップ内容エラー" "バックアップファイルの内容が不正です: $backup_file"
        return 1
    fi
}

# 監視実行
log "バックアップ監視を開始します"

# データベースバックアップ確認
if check_latest_backup "db" 25; then
    latest_db_backup=$(find "$BACKUP_DIR" -name "db_backup_*.gz" -mtime -1 | sort | tail -1)
    check_backup_size "$latest_db_backup" 1
    check_backup_integrity "$latest_db_backup"
fi

# 設定バックアップ確認
check_latest_backup "config" 25

# ログバックアップ確認
check_latest_backup "logs" 25

log "バックアップ監視が完了しました"
```

### 5.2 バックアップテスト

```bash
#!/bin/bash
# backup-test.sh - バックアップ復旧テスト

TEST_DB_NAME="test_restore_db"
BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "使用方法: $0 <backup_file.sql.gz>"
    exit 1
fi

echo "バックアップ復旧テストを開始します..."

# テスト用データベース作成
createdb "$TEST_DB_NAME"

# バックアップ復旧実行
if zcat "$BACKUP_FILE" | psql -d "$TEST_DB_NAME"; then
    echo "復旧テスト: 成功"
    
    # 基本的なデータ整合性確認
    table_count=$(psql -d "$TEST_DB_NAME" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")
    echo "テーブル数: $table_count"
    
    contact_count=$(psql -d "$TEST_DB_NAME" -t -c "SELECT count(*) FROM contacts;" 2>/dev/null || echo "0")
    echo "問い合わせ件数: $contact_count"
    
else
    echo "復旧テスト: 失敗"
fi

# テスト用データベース削除
dropdb "$TEST_DB_NAME"

echo "バックアップ復旧テストが完了しました"
```

---

## 6. 災害復旧計画

### 6.1 災害シナリオ別復旧手順

#### シナリオ1: データベース障害

```bash
#!/bin/bash
# disaster-recovery-db.sh

echo "=== データベース障害復旧手順 ==="

# 1. 障害確認
echo "1. データベース接続確認..."
if ! pg_isready -h "$DB_HOST" -p "$DB_PORT"; then
    echo "データベースに接続できません"
else
    echo "データベースは稼働中です"
    exit 0
fi

# 2. 最新バックアップ特定
echo "2. 最新バックアップを特定..."
LATEST_BACKUP=$(find /backups/database -name "db_backup_*.sql.gz" | sort | tail -1)
echo "最新バックアップ: $LATEST_BACKUP"

# 3. データベース復旧
echo "3. データベース復旧実行..."
./db-restore.sh "$LATEST_BACKUP"

# 4. 動作確認
echo "4. 動作確認..."
curl -f https://english-cafe-backend.onrender.com/health

echo "データベース復旧が完了しました"
```

#### シナリオ2: アプリケーション障害

```bash
#!/bin/bash
# disaster-recovery-app.sh

echo "=== アプリケーション障害復旧手順 ==="

# 1. サービス状態確認
echo "1. サービス状態確認..."
curl -f https://english-cafe-website.vercel.app || echo "フロントエンド障害"
curl -f https://english-cafe-backend.onrender.com/health || echo "バックエンド障害"

# 2. 最新コードデプロイ
echo "2. 最新コードデプロイ..."
git pull origin main

# Vercel再デプロイ
vercel --prod

# Render再デプロイ（手動またはGitHub連携）
echo "Renderの再デプロイを手動で実行してください"

# 3. 設定復旧
echo "3. 設定復旧..."
LATEST_CONFIG=$(find /backups/config -name "config_backup_*.tar.gz" | sort | tail -1)
tar -xzf "$LATEST_CONFIG" -C /tmp/
# 必要な設定ファイルを復旧

# 4. 動作確認
echo "4. 動作確認..."
sleep 60  # デプロイ完了待機
curl -f https://english-cafe-website.vercel.app
curl -f https://english-cafe-backend.onrender.com/health

echo "アプリケーション復旧が完了しました"
```

### 6.2 復旧時間目標 (RTO)

| 障害レベル | 復旧時間目標 | 対応内容 |
|-----------|-------------|----------|
| レベル1 | 1時間以内 | 軽微な障害、自動復旧 |
| レベル2 | 4時間以内 | 中程度の障害、手動復旧 |
| レベル3 | 8時間以内 | 重大な障害、完全復旧 |

### 6.3 復旧ポイント目標 (RPO)

- **データベース**: 24時間以内
- **設定ファイル**: 24時間以内
- **ログファイル**: 7日以内

---

## 7. バックアップ自動化

### 7.1 統合バックアップスクリプト

```bash
#!/bin/bash
# full-backup.sh - 統合バックアップスクリプト

set -e

BACKUP_ROOT="/backups"
LOG_FILE="/var/log/full-backup.log"
DATE=$(date +"%Y%m%d_%H%M%S")

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== 統合バックアップ開始 ==="

# 1. データベースバックアップ
log "1. データベースバックアップ実行中..."
if ./db-backup.sh; then
    log "データベースバックアップ: 成功"
else
    log "データベースバックアップ: 失敗"
    exit 1
fi

# 2. 設定ファイルバックアップ
log "2. 設定ファイルバックアップ実行中..."
if ./config-backup.sh; then
    log "設定ファイルバックアップ: 成功"
else
    log "設定ファイルバックアップ: 失敗"
fi

# 3. ログファイルバックアップ
log "3. ログファイルバックアップ実行中..."
if ./log-backup.sh; then
    log "ログファイルバックアップ: 成功"
else
    log "ログファイルバックアップ: 失敗"
fi

# 4. Gitリポジトリバックアップ
log "4. Gitリポジトリバックアップ実行中..."
if ./git-backup.sh; then
    log "Gitリポジトリバックアップ: 成功"
else
    log "Gitリポジトリバックアップ: 失敗"
fi

# 5. クラウドストレージ同期
log "5. クラウドストレージ同期実行中..."
if ./s3-backup.sh; then
    log "クラウドストレージ同期: 成功"
else
    log "クラウドストレージ同期: 失敗"
fi

# 6. バックアップ監視
log "6. バックアップ監視実行中..."
./backup-monitor.sh

# 7. 完了通知
BACKUP_SIZE=$(du -sh "$BACKUP_ROOT" | cut -f1)
log "=== 統合バックアップ完了 (総サイズ: $BACKUP_SIZE) ==="

# Slack通知
curl -X POST https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK \
  -H 'Content-type: application/json' \
  --data "{
    \"text\": \"✅ 統合バックアップが完了しました\",
    \"attachments\": [
      {
        \"color\": \"good\",
        \"fields\": [
          {
            \"title\": \"実行日時\",
            \"value\": \"$(date)\",
            \"short\": true
          },
          {
            \"title\": \"バックアップサイズ\",
            \"value\": \"$BACKUP_SIZE\",
            \"short\": true
          }
        ]
      }
    ]
  }"
```

### 7.2 cron設定

```bash
# /etc/crontab または crontab -e で設定

# 毎日午前2時に統合バックアップ実行
0 2 * * * /scripts/full-backup.sh

# 毎時バックアップ監視実行
0 * * * * /scripts/backup-monitor.sh

# 毎週日曜日午前1時にバックアップテスト実行
0 1 * * 0 /scripts/backup-test.sh $(find /backups/database -name "db_backup_*.sql.gz" | sort | tail -1)

# 毎月1日にバックアップ容量レポート作成
0 3 1 * * /scripts/backup-report.sh
```

---

## 8. 運用・保守

### 8.1 定期作業

#### 日次作業
- [ ] バックアップ実行状況確認
- [ ] バックアップファイルサイズ確認
- [ ] エラーログ確認

#### 週次作業
- [ ] バックアップ復旧テスト実行
- [ ] 古いバックアップファイル削除確認
- [ ] ストレージ使用量確認

#### 月次作業
- [ ] 災害復旧手順の見直し
- [ ] バックアップ戦略の評価
- [ ] 容量計画の見直し

### 8.2 アラート設定

```python
# backup_alerts.py
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText

class BackupAlerts:
    def __init__(self):
        self.backup_dir = "/backups"
        self.alert_email = "admin@english-cafe.com"
    
    def check_backup_freshness(self):
        """バックアップの新しさをチェック"""
        db_backups = sorted([
            f for f in os.listdir(f"{self.backup_dir}/database")
            if f.startswith("db_backup_") and f.endswith(".sql.gz")
        ])
        
        if not db_backups:
            self.send_alert("バックアップなし", "データベースバックアップが見つかりません")
            return
        
        latest_backup = db_backups[-1]
        backup_time = datetime.strptime(latest_backup[10:25], "%Y%m%d_%H%M%S")
        
        if datetime.now() - backup_time > timedelta(hours=25):
            self.send_alert(
                "バックアップ遅延", 
                f"最新バックアップが古すぎます: {latest_backup}"
            )
    
    def send_alert(self, subject, message):
        """アラートメール送信"""
        msg = MIMEText(message)
        msg['Subject'] = f"[BACKUP ALERT] {subject}"
        msg['From'] = "backup-system@english-cafe.com"
        msg['To'] = self.alert_email
        
        # SMTP設定は環境に応じて調整
        try:
            with smtplib.SMTP('localhost') as server:
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send alert: {e}")

if __name__ == "__main__":
    alerts = BackupAlerts()
    alerts.check_backup_freshness()
```

---

## 9. セキュリティ考慮事項

### 9.1 バックアップデータの暗号化

```bash
#!/bin/bash
# encrypted-backup.sh - 暗号化バックアップ

GPG_RECIPIENT="backup@english-cafe.com"
BACKUP_FILE="$1"
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"

# GPG暗号化
gpg --trust-model always --encrypt --recipient "$GPG_RECIPIENT" --output "$ENCRYPTED_FILE" "$BACKUP_FILE"

# 元ファイル削除
rm "$BACKUP_FILE"

echo "バックアップを暗号化しました: $ENCRYPTED_FILE"
```

### 9.2 アクセス制御

```bash
#!/bin/bash
# backup-permissions.sh - バックアップファイルの権限設定

BACKUP_DIR="/backups"

# バックアップディレクトリの権限設定
chmod 700 "$BACKUP_DIR"
chown backup:backup "$BACKUP_DIR"

# バックアップファイルの権限設定
find "$BACKUP_DIR" -type f -name "*.sql.gz" -exec chmod 600 {} \;
find "$BACKUP_DIR" -type f -name "*.sql.gz" -exec chown backup:backup {} \;

echo "バックアップファイルの権限を設定しました"
```

---

## 10. 付録

### A. 緊急連絡先

```
バックアップ責任者: [名前] - [電話番号] - [メールアドレス]
システム管理者: [名前] - [電話番号] - [メールアドレス]
データベース管理者: [名前] - [電話番号] - [メールアドレス]

外部サービス:
- AWS サポート: https://aws.amazon.com/support/
- Google Cloud サポート: https://cloud.google.com/support/
- Render サポート: https://render.com/support
```

### B. 復旧チェックリスト

#### データベース復旧後の確認項目
- [ ] データベース接続確認
- [ ] テーブル構造確認
- [ ] データ件数確認
- [ ] インデックス確認
- [ ] 制約確認
- [ ] アプリケーション動作確認

#### アプリケーション復旧後の確認項目
- [ ] フロントエンド表示確認
- [ ] バックエンドAPI確認
- [ ] 問い合わせフォーム動作確認
- [ ] 管理機能動作確認
- [ ] SSL証明書確認

### C. 参考資料

- [PostgreSQL Backup and Restore](https://www.postgresql.org/docs/current/backup.html)
- [AWS S3 Backup Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/backup-for-s3.html)
- [Disaster Recovery Planning](https://www.ready.gov/business/implementation/IT)

---

**最終更新日**: 2024年12月14日  
**作成者**: 開発チーム  
**承認者**: システム管理者