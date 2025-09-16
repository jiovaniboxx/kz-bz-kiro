# Renderデプロイメントガイド

## 概要

このドキュメントでは、English Cafe WebサイトのバックエンドAPIをRenderにデプロイする手順を説明します。

## 前提条件

- Renderアカウントの作成
- GitHubリポジトリの準備
- PostgreSQLデータベースの設定
- 必要な環境変数の準備

## デプロイ手順

### 1. Renderプロジェクトの作成

#### データベースの作成

1. [Render Dashboard](https://dashboard.render.com/)にアクセス
2. "New +" → "PostgreSQL"を選択
3. データベース設定を行う：
   - **Name**: `english-cafe-db`
   - **Database**: `english_cafe`
   - **User**: `english_cafe_user`
   - **Region**: `Oregon (US West)`
   - **Plan**: `Free`

#### Webサービスの作成

1. "New +" → "Web Service"を選択
2. GitHubリポジトリを接続
3. サービス設定を行う：
   - **Name**: `english-cafe-backend`
   - **Region**: `Oregon (US West)`
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"`

### 2. 環境変数の設定

Render Dashboardで以下の環境変数を設定してください：

#### 必須環境変数

```bash
# Database
DATABASE_URL=postgresql://english_cafe_user:password@dpg-xxxxx-a.oregon-postgres.render.com/english_cafe

# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-key-here-minimum-32-characters

# CORS
CORS_ORIGINS=https://english-cafe.vercel.app,https://english-cafe.com

# Email (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@english-cafe.com

# Admin
ADMIN_EMAIL=admin@english-cafe.com
```

#### オプション環境変数

```bash
# Logging
LOG_LEVEL=INFO

# Security
ALLOWED_HOSTS=english-cafe-backend.onrender.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### 3. データベース設定

#### 接続情報の取得

1. PostgreSQLサービスのダッシュボードにアクセス
2. "Connect"タブで接続情報を確認
3. `DATABASE_URL`環境変数に設定

#### マイグレーションの実行

デプロイ時に自動的に実行されます：

```bash
alembic upgrade head
```

### 4. ヘルスチェックの設定

Renderが自動的に以下のエンドポイントでヘルスチェックを実行：

```
GET /health
```

## 環境変数詳細

### データベース設定

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `DATABASE_URL` | PostgreSQL接続URL | `postgresql://user:pass@host:port/db` |

### アプリケーション設定

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `ENVIRONMENT` | 実行環境 | `production` |
| `DEBUG` | デバッグモード | `false` |
| `SECRET_KEY` | 暗号化キー | 必須（32文字以上） |

### CORS設定

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `CORS_ORIGINS` | 許可するオリジン | `https://example.com,https://app.example.com` |

### メール設定

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `SMTP_SERVER` | SMTPサーバー | `smtp.gmail.com` |
| `SMTP_PORT` | SMTPポート | `587` |
| `SMTP_USERNAME` | SMTPユーザー名 | `your-email@gmail.com` |
| `SMTP_PASSWORD` | SMTPパスワード | `your-app-password` |
| `SMTP_FROM_EMAIL` | 送信者メールアドレス | `noreply@example.com` |

## セキュリティ設定

### HTTPS強制

Renderが自動的にHTTPSを有効化：

- Let's Encrypt SSL証明書の自動発行・更新
- HTTP → HTTPSリダイレクト

### セキュリティヘッダー

アプリケーションで以下のセキュリティヘッダーを設定：

```python
# app/main.py
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

### 入力値検証

- Pydanticによる自動バリデーション
- SQLインジェクション対策（SQLAlchemy ORM）
- XSS対策（入力値サニタイゼーション）

## パフォーマンス最適化

### データベース最適化

```python
# app/core/database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
)
```

### キャッシュ設定

```python
# レスポンスキャッシュ
@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "public, max-age=300"
    return response
```

### レート制限

```python
# app/middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

## 監視とログ

### ログ設定

```python
# app/core/logging.py
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/tmp/app.log"),
    ],
)
```

### ヘルスチェック

```python
# app/api/v1/health.py
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "database": await check_database_health(),
    }
```

### メトリクス監視

```python
# app/middleware/metrics.py
import time
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')
```

## トラブルシューティング

### よくある問題

#### 1. データベース接続エラー

```bash
# 接続URLの確認
echo $DATABASE_URL

# 接続テスト
python -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect('$DATABASE_URL')
    await conn.close()
asyncio.run(test())
"
```

#### 2. マイグレーションエラー

```bash
# マイグレーション状態の確認
alembic current

# 手動マイグレーション実行
alembic upgrade head

# マイグレーション履歴の確認
alembic history
```

#### 3. メール送信エラー

```bash
# SMTP設定の確認
python -c "
import smtplib
server = smtplib.SMTP('$SMTP_SERVER', $SMTP_PORT)
server.starttls()
server.login('$SMTP_USERNAME', '$SMTP_PASSWORD')
server.quit()
print('SMTP connection successful')
"
```

### デバッグ方法

#### ログの確認

```bash
# Renderダッシュボードでログを確認
# または CLI使用
render logs -s english-cafe-backend
```

#### 環境変数の確認

```python
# app/debug.py
import os
print("Environment variables:")
for key, value in os.environ.items():
    if key.startswith(('DATABASE', 'SMTP', 'SECRET')):
        print(f"{key}: {'*' * len(value) if 'SECRET' in key else value}")
```

## CI/CD設定

### 自動デプロイ

Renderが自動的に以下の場合にデプロイを実行：

- `main`ブランチへのプッシュ
- 環境変数の変更
- 手動デプロイの実行

### デプロイフック

```bash
# .github/workflows/deploy.yml
name: Deploy to Render
on:
  push:
    branches: [main]
    paths: ['backend/**']
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Render Deploy
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"
```

## バックアップとリストア

### データベースバックアップ

```bash
# 自動バックアップ（Renderが提供）
# 手動バックアップ
pg_dump $DATABASE_URL > backup.sql
```

### リストア

```bash
# データベースリストア
psql $DATABASE_URL < backup.sql
```

## スケーリング

### 垂直スケーリング

Renderダッシュボードでプランをアップグレード：

- **Free**: 512MB RAM, 0.1 CPU
- **Starter**: 1GB RAM, 0.5 CPU
- **Standard**: 2GB RAM, 1 CPU

### 水平スケーリング

有料プランでの複数インスタンス実行：

```yaml
# render.yaml
services:
  - type: web
    name: english-cafe-backend
    scaling:
      minInstances: 2
      maxInstances: 10
```

## セキュリティベストプラクティス

### 環境変数の管理

- 機密情報は環境変数で管理
- `.env`ファイルをGitにコミットしない
- 定期的なパスワード変更

### アクセス制御

```python
# app/middleware/auth.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    # トークン検証ロジック
    if not verify_jwt_token(token.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 監査ログ

```python
# app/middleware/audit.py
@app.middleware("http")
async def audit_log(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"Audit: {request.method} {request.url} "
        f"Status: {response.status_code} "
        f"Time: {process_time:.3f}s"
    )
    return response
```

## 参考リンク

- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL on Render](https://render.com/docs/databases)
- [Render CLI](https://render.com/docs/cli)