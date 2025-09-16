# セキュリティ監視設定ガイド

## 概要

英会話カフェWebサイトのセキュリティ監視設定と運用ガイド。本番環境でのセキュリティ脅威の検知、対応、予防策について説明する。

---

## 1. セキュリティ監視の基本方針

### 1.1 監視目標

- **可用性の確保**: サービスの継続的な提供
- **機密性の保護**: 個人情報・機密データの保護
- **完全性の維持**: データの改ざん・破損の防止
- **早期検知**: セキュリティインシデントの迅速な発見
- **迅速な対応**: インシデント発生時の適切な対応

### 1.2 監視対象

- **Webアプリケーション**: フロントエンド・バックエンド
- **データベース**: PostgreSQL
- **ネットワーク通信**: HTTPS通信・API通信
- **ユーザーアクセス**: 異常なアクセスパターン
- **システムリソース**: CPU・メモリ・ディスク使用量

---

## 2. セキュリティヘッダー監視

### 2.1 必須セキュリティヘッダー

#### フロントエンド (Vercel)

```javascript
// next.config.js でのセキュリティヘッダー設定
const securityHeaders = [
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block'
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin'
  },
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.youtube.com https://www.google.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://english-cafe-backend.onrender.com; frame-src https://www.youtube.com https://www.google.com;"
  }
]
```

#### バックエンド (FastAPI)

```python
# セキュリティミドルウェア設定
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["english-cafe-backend.onrender.com", "localhost"]
)

# セキュリティヘッダー追加
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

### 2.2 セキュリティヘッダー監視スクリプト

```bash
#!/bin/bash
# security-header-check.sh

check_security_headers() {
    local url="$1"
    local service_name="$2"
    
    echo "=== $service_name セキュリティヘッダーチェック ==="
    
    headers=$(curl -s -I "$url")
    
    # 必須ヘッダーチェック
    required_headers=(
        "x-content-type-options"
        "x-frame-options"
        "referrer-policy"
    )
    
    for header in "${required_headers[@]}"; do
        if echo "$headers" | grep -i "$header" > /dev/null; then
            echo "✓ $header: 設定済み"
        else
            echo "✗ $header: 未設定"
        fi
    done
}

# 実行例
check_security_headers "https://english-cafe-website.vercel.app" "フロントエンド"
check_security_headers "https://english-cafe-backend.onrender.com/health" "バックエンド"
```

---

## 3. アクセス監視

### 3.1 異常アクセスパターンの検知

#### 監視対象

- **ブルートフォース攻撃**: 短時間での大量ログイン試行
- **DDoS攻撃**: 異常に多いリクエスト数
- **スキャン攻撃**: 存在しないパスへの大量アクセス
- **SQLインジェクション**: 不正なクエリパラメータ
- **XSS攻撃**: 不正なスクリプト挿入試行

#### 検知基準

```python
# backend/app/middleware/security_monitoring.py

import time
from collections import defaultdict
from fastapi import Request, HTTPException

class SecurityMonitoring:
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.blocked_ips = set()
        
    def check_rate_limit(self, client_ip: str, max_requests: int = 100, window: int = 60):
        """レート制限チェック"""
        now = time.time()
        
        # 古いリクエスト記録を削除
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if now - req_time < window
        ]
        
        # 現在のリクエストを記録
        self.request_counts[client_ip].append(now)
        
        # レート制限チェック
        if len(self.request_counts[client_ip]) > max_requests:
            self.blocked_ips.add(client_ip)
            raise HTTPException(status_code=429, detail="Too Many Requests")
    
    def check_malicious_patterns(self, request: Request):
        """悪意のあるパターンチェック"""
        url = str(request.url)
        query_params = str(request.query_params)
        
        # SQLインジェクションパターン
        sql_patterns = [
            "' OR '1'='1",
            "'; DROP TABLE",
            "UNION SELECT",
            "' OR 1=1--"
        ]
        
        # XSSパターン
        xss_patterns = [
            "<script>",
            "javascript:",
            "onerror=",
            "onload="
        ]
        
        for pattern in sql_patterns + xss_patterns:
            if pattern.lower() in url.lower() or pattern.lower() in query_params.lower():
                # ログ記録
                logger.warning(f"Malicious pattern detected: {pattern} from IP: {request.client.host}")
                raise HTTPException(status_code=400, detail="Bad Request")
```

### 3.2 アクセスログ分析

#### ログ形式

```json
{
  "timestamp": "2024-12-14T10:30:00Z",
  "client_ip": "192.168.1.100",
  "method": "POST",
  "path": "/api/contacts",
  "status_code": 200,
  "response_time": 0.245,
  "user_agent": "Mozilla/5.0...",
  "referer": "https://english-cafe-website.vercel.app/contact",
  "request_size": 1024,
  "response_size": 256
}
```

#### 異常検知クエリ例

```sql
-- 短時間での大量リクエスト検知
SELECT client_ip, COUNT(*) as request_count
FROM access_logs 
WHERE timestamp > NOW() - INTERVAL '5 minutes'
GROUP BY client_ip
HAVING COUNT(*) > 100;

-- 404エラーの多いIP検知
SELECT client_ip, COUNT(*) as error_count
FROM access_logs 
WHERE status_code = 404 
  AND timestamp > NOW() - INTERVAL '1 hour'
GROUP BY client_ip
HAVING COUNT(*) > 50;

-- 異常なUser-Agentパターン検知
SELECT user_agent, COUNT(*) as count
FROM access_logs 
WHERE timestamp > NOW() - INTERVAL '1 hour'
  AND (user_agent LIKE '%bot%' OR user_agent LIKE '%crawler%')
GROUP BY user_agent;
```

---

## 4. 脆弱性監視

### 4.1 依存関係の脆弱性監視

#### フロントエンド (npm audit)

```bash
#!/bin/bash
# frontend-security-check.sh

cd frontend

echo "=== npm audit 実行 ==="
npm audit --audit-level=moderate

echo "=== 高リスク脆弱性チェック ==="
npm audit --audit-level=high --json > audit-results.json

# 高リスク脆弱性が見つかった場合はアラート
if [ $(cat audit-results.json | jq '.metadata.vulnerabilities.high') -gt 0 ]; then
    echo "⚠️ 高リスク脆弱性が発見されました"
    # Slack通知やメール送信
fi
```

#### バックエンド (safety check)

```bash
#!/bin/bash
# backend-security-check.sh

cd backend

echo "=== Safety チェック実行 ==="
pip install safety
safety check --json > safety-results.json

# 脆弱性が見つかった場合はアラート
if [ $(cat safety-results.json | jq '. | length') -gt 0 ]; then
    echo "⚠️ Python依存関係に脆弱性が発見されました"
    # アラート送信
fi
```

### 4.2 コード品質・セキュリティ監視

#### SonarQube設定例

```yaml
# sonar-project.properties
sonar.projectKey=english-cafe-website
sonar.organization=your-org
sonar.sources=.
sonar.exclusions=**/node_modules/**,**/venv/**,**/__pycache__/**
sonar.python.coverage.reportPaths=backend/coverage.xml
sonar.javascript.lcov.reportPaths=frontend/coverage/lcov.info
```

---

## 5. データベースセキュリティ監視

### 5.1 データベース接続監視

```python
# backend/app/monitoring/db_security.py

import psycopg2
from datetime import datetime, timedelta
import logging

class DatabaseSecurityMonitor:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.logger = logging.getLogger(__name__)
    
    def check_connection_anomalies(self):
        """異常な接続パターンをチェック"""
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            # 異常に多い接続数をチェック
            cursor.execute("""
                SELECT count(*) as active_connections
                FROM pg_stat_activity 
                WHERE state = 'active'
            """)
            
            active_connections = cursor.fetchone()[0]
            
            if active_connections > 50:  # 閾値
                self.logger.warning(f"High number of active connections: {active_connections}")
            
            # 長時間実行中のクエリをチェック
            cursor.execute("""
                SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
                FROM pg_stat_activity 
                WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
                  AND state = 'active'
            """)
            
            long_queries = cursor.fetchall()
            
            for query in long_queries:
                self.logger.warning(f"Long running query detected: PID {query[0]}, Duration: {query[1]}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Database security check failed: {e}")
    
    def check_failed_login_attempts(self):
        """ログイン失敗の監視"""
        # アプリケーションログからログイン失敗を監視
        # 実装は認証システムに依存
        pass
```

### 5.2 データ整合性監視

```sql
-- データ整合性チェッククエリ

-- 孤立したレコードチェック
SELECT 'orphaned_contacts' as check_type, COUNT(*) as count
FROM contacts c
LEFT JOIN contact_status cs ON c.id = cs.contact_id
WHERE cs.contact_id IS NULL;

-- 重複データチェック
SELECT 'duplicate_emails' as check_type, email, COUNT(*) as count
FROM contacts
GROUP BY email
HAVING COUNT(*) > 1;

-- 異常なデータ値チェック
SELECT 'invalid_emails' as check_type, COUNT(*) as count
FROM contacts
WHERE email NOT LIKE '%@%.%';
```

---

## 6. インシデント対応

### 6.1 セキュリティインシデント分類

#### レベル1: 低リスク
- 軽微な脆弱性の発見
- 単発的な異常アクセス
- 設定ミスによる軽微な情報漏洩

**対応時間**: 24時間以内  
**対応者**: 開発チーム

#### レベル2: 中リスク
- 中程度の脆弱性の発見
- 継続的な異常アクセス
- システムの一部機能停止

**対応時間**: 4時間以内  
**対応者**: 開発チーム + システム管理者

#### レベル3: 高リスク
- 重大な脆弱性の発見
- データ漏洩の可能性
- システム全体の停止

**対応時間**: 1時間以内  
**対応者**: 全チーム + 経営陣

### 6.2 インシデント対応手順

#### 1. 検知・報告
```bash
# 自動アラート例
curl -X POST https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK \
  -H 'Content-type: application/json' \
  --data '{
    "text": "🚨 セキュリティアラート: 異常なアクセスパターンを検知しました",
    "attachments": [
      {
        "color": "danger",
        "fields": [
          {
            "title": "検知時刻",
            "value": "'$(date)'",
            "short": true
          },
          {
            "title": "対象IP",
            "value": "'$SUSPICIOUS_IP'",
            "short": true
          }
        ]
      }
    ]
  }'
```

#### 2. 初期対応
- **即座の脅威遮断**: 不正IPのブロック、サービス停止
- **影響範囲の特定**: ログ分析、データ確認
- **関係者への通知**: チーム、経営陣、必要に応じて顧客

#### 3. 詳細調査
- **ログ分析**: アクセスログ、エラーログの詳細分析
- **システム検査**: 改ざん、データ漏洩の確認
- **脆弱性特定**: 攻撃経路の特定

#### 4. 復旧・対策
- **脆弱性修正**: パッチ適用、設定変更
- **システム復旧**: サービス再開、動作確認
- **再発防止策**: 監視強化、プロセス改善

#### 5. 事後対応
- **インシデントレポート作成**: 原因、影響、対策の文書化
- **関係者への報告**: 顧客、監督官庁への報告（必要に応じて）
- **プロセス改善**: 監視・対応プロセスの見直し

---

## 7. 監視ツール・サービス

### 7.1 無料監視ツール

#### UptimeRobot
```bash
# UptimeRobot API を使用した監視設定
curl -X POST "https://api.uptimerobot.com/v2/newMonitor" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "api_key=YOUR_API_KEY" \
  -d "format=json" \
  -d "type=1" \
  -d "url=https://english-cafe-website.vercel.app" \
  -d "friendly_name=Frontend Monitor"
```

#### Google Search Console
- セキュリティ問題の通知
- マルウェア検知
- ハッキング検知

### 7.2 ログ監視

#### 簡易ログ監視スクリプト
```python
# log_monitor.py
import re
import time
from datetime import datetime

class LogMonitor:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.suspicious_patterns = [
            r'SQL injection attempt',
            r'XSS attempt',
            r'Brute force attack',
            r'Rate limit exceeded'
        ]
    
    def monitor_logs(self):
        """ログファイルをリアルタイム監視"""
        with open(self.log_file_path, 'r') as f:
            f.seek(0, 2)  # ファイル末尾に移動
            
            while True:
                line = f.readline()
                if line:
                    self.analyze_log_line(line)
                else:
                    time.sleep(1)
    
    def analyze_log_line(self, line):
        """ログ行を分析"""
        for pattern in self.suspicious_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                self.send_alert(f"Suspicious activity detected: {line.strip()}")
    
    def send_alert(self, message):
        """アラート送信"""
        print(f"[ALERT] {datetime.now()}: {message}")
        # Slack通知、メール送信等の実装
```

---

## 8. 定期セキュリティチェック

### 8.1 日次チェック

```bash
#!/bin/bash
# daily-security-check.sh

echo "=== 日次セキュリティチェック $(date) ==="

# 1. サービス稼働状況確認
echo "1. サービス稼働状況確認"
curl -f https://english-cafe-website.vercel.app > /dev/null && echo "✓ Frontend OK" || echo "✗ Frontend DOWN"
curl -f https://english-cafe-backend.onrender.com/health > /dev/null && echo "✓ Backend OK" || echo "✗ Backend DOWN"

# 2. セキュリティヘッダー確認
echo "2. セキュリティヘッダー確認"
./scripts/security-header-check.sh

# 3. SSL証明書確認
echo "3. SSL証明書確認"
openssl s_client -connect english-cafe-website.vercel.app:443 -servername english-cafe-website.vercel.app < /dev/null 2>/dev/null | openssl x509 -noout -dates

# 4. ログ異常確認
echo "4. ログ異常確認"
# 過去24時間のエラーログをチェック
grep -i "error\|warning\|exception" /var/log/app.log | tail -10

echo "=== 日次チェック完了 ==="
```

### 8.2 週次チェック

```bash
#!/bin/bash
# weekly-security-check.sh

echo "=== 週次セキュリティチェック $(date) ==="

# 1. 依存関係脆弱性チェック
echo "1. 依存関係脆弱性チェック"
cd frontend && npm audit
cd ../backend && safety check

# 2. パフォーマンス・セキュリティテスト
echo "2. パフォーマンス・セキュリティテスト"
lighthouse https://english-cafe-website.vercel.app --output=json --output-path=lighthouse-report.json

# 3. データベース整合性チェック
echo "3. データベース整合性チェック"
python scripts/db-integrity-check.py

echo "=== 週次チェック完了 ==="
```

### 8.3 月次チェック

```bash
#!/bin/bash
# monthly-security-check.sh

echo "=== 月次セキュリティチェック $(date) ==="

# 1. 全体的なセキュリティ監査
echo "1. セキュリティ監査"
# ペネトレーションテスト（簡易版）
nmap -sV english-cafe-website.vercel.app

# 2. バックアップ整合性確認
echo "2. バックアップ整合性確認"
# バックアップからの復旧テスト

# 3. アクセスログ分析
echo "3. アクセスログ分析"
python scripts/log-analysis.py --period=30days

echo "=== 月次チェック完了 ==="
```

---

## 9. アラート設定

### 9.1 Slack通知設定

```python
# alert_service.py
import requests
import json
from datetime import datetime

class AlertService:
    def __init__(self, slack_webhook_url):
        self.slack_webhook_url = slack_webhook_url
    
    def send_security_alert(self, severity, message, details=None):
        """セキュリティアラートを送信"""
        
        color_map = {
            'low': 'good',
            'medium': 'warning', 
            'high': 'danger'
        }
        
        emoji_map = {
            'low': '🟡',
            'medium': '🟠',
            'high': '🔴'
        }
        
        payload = {
            "text": f"{emoji_map.get(severity, '⚠️')} セキュリティアラート ({severity.upper()})",
            "attachments": [
                {
                    "color": color_map.get(severity, 'warning'),
                    "fields": [
                        {
                            "title": "メッセージ",
                            "value": message,
                            "short": False
                        },
                        {
                            "title": "発生時刻",
                            "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "short": True
                        },
                        {
                            "title": "重要度",
                            "value": severity.upper(),
                            "short": True
                        }
                    ]
                }
            ]
        }
        
        if details:
            payload["attachments"][0]["fields"].append({
                "title": "詳細",
                "value": details,
                "short": False
            })
        
        try:
            response = requests.post(
                self.slack_webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
```

### 9.2 メール通知設定

```python
# email_alert.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailAlert:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_security_alert(self, to_emails, subject, message):
        """セキュリティアラートメールを送信"""
        
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = f"[SECURITY ALERT] {subject}"
        
        body = f"""
        セキュリティアラートが発生しました。
        
        時刻: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        内容: {message}
        
        至急確認をお願いします。
        
        ---
        英会話カフェWebサイト セキュリティ監視システム
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.username, to_emails, text)
            server.quit()
        except Exception as e:
            print(f"Failed to send email alert: {e}")
```

---

## 10. 運用・保守

### 10.1 セキュリティ監視の運用体制

#### 責任者・役割分担
- **セキュリティ責任者**: 全体的なセキュリティ方針・戦略
- **システム管理者**: 日常的な監視・対応
- **開発チーム**: 脆弱性修正・セキュリティ機能実装
- **インシデント対応チーム**: 緊急時対応・復旧作業

#### 連絡体制
```
レベル1 (低リスク)
└── システム管理者 → 開発チーム

レベル2 (中リスク)  
└── システム管理者 → セキュリティ責任者 → 開発チーム

レベル3 (高リスク)
└── システム管理者 → セキュリティ責任者 → 経営陣 → 全チーム
```

### 10.2 定期的な見直し

#### 四半期レビュー
- セキュリティ監視の有効性評価
- インシデント対応の振り返り
- 監視ツール・プロセスの改善
- 脅威情報の更新

#### 年次レビュー
- セキュリティ方針の見直し
- 監視体制の見直し
- 予算・リソースの見直し
- 外部監査の実施

---

## 付録

### A. 緊急連絡先

```
セキュリティ責任者: [名前] - [電話番号] - [メールアドレス]
システム管理者: [名前] - [電話番号] - [メールアドレス]
開発チームリーダー: [名前] - [電話番号] - [メールアドレス]

外部サービス:
- Vercel サポート: https://vercel.com/support
- Render サポート: https://render.com/support
```

### B. 参考資料

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls/)
- [SANS Security Policies](https://www.sans.org/information-security-policy/)

---

**最終更新日**: 2024年12月14日  
**作成者**: 開発チーム  
**承認者**: セキュリティ責任者