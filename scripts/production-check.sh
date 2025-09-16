#!/bin/bash

# 本番環境最終確認スクリプト
# 英会話カフェWebサイトの本番環境での動作確認を自動化

set -e

# 色付きログ出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 設定
FRONTEND_URL="${FRONTEND_URL:-https://english-cafe-website.vercel.app}"
BACKEND_URL="${BACKEND_URL:-https://english-cafe-backend.onrender.com}"
TIMEOUT=30

log_info "英会話カフェWebサイト 本番環境最終確認を開始します"
log_info "フロントエンド URL: $FRONTEND_URL"
log_info "バックエンド URL: $BACKEND_URL"

# 結果記録用
RESULTS_FILE="production-check-results-$(date +%Y%m%d-%H%M%S).txt"
echo "本番環境最終確認結果 - $(date)" > "$RESULTS_FILE"
echo "=================================" >> "$RESULTS_FILE"

# 1. フロントエンド基本動作確認
log_info "1. フロントエンド基本動作確認"

check_frontend_page() {
    local path="$1"
    local description="$2"
    local url="$FRONTEND_URL$path"
    
    log_info "  チェック中: $description ($url)"
    
    if curl -s -f -m $TIMEOUT "$url" > /dev/null; then
        log_success "  ✓ $description - OK"
        echo "✓ $description - OK" >> "$RESULTS_FILE"
        return 0
    else
        log_error "  ✗ $description - FAILED"
        echo "✗ $description - FAILED" >> "$RESULTS_FILE"
        return 1
    fi
}

# フロントエンドページチェック
FRONTEND_CHECKS=0
FRONTEND_PASSED=0

pages=(
    "/" "ホームページ"
    "/instructors" "講師一覧ページ"
    "/lessons" "レッスンページ"
    "/contact" "問い合わせページ"
)

for ((i=0; i<${#pages[@]}; i+=2)); do
    path="${pages[i]}"
    description="${pages[i+1]}"
    FRONTEND_CHECKS=$((FRONTEND_CHECKS + 1))
    if check_frontend_page "$path" "$description"; then
        FRONTEND_PASSED=$((FRONTEND_PASSED + 1))
    fi
done

# 2. バックエンドAPI動作確認
log_info "2. バックエンドAPI動作確認"

check_api_endpoint() {
    local path="$1"
    local description="$2"
    local method="${3:-GET}"
    local url="$BACKEND_URL$path"
    
    log_info "  チェック中: $description ($method $url)"
    
    if curl -s -f -m $TIMEOUT -X "$method" "$url" > /dev/null; then
        log_success "  ✓ $description - OK"
        echo "✓ $description - OK" >> "$RESULTS_FILE"
        return 0
    else
        log_error "  ✗ $description - FAILED"
        echo "✗ $description - FAILED" >> "$RESULTS_FILE"
        return 1
    fi
}

# バックエンドAPIチェック
BACKEND_CHECKS=0
BACKEND_PASSED=0

apis=(
    "/health" "ヘルスチェック" "GET"
    "/api/monitoring/health" "システム監視ヘルスチェック" "GET"
    "/api/monitoring/stats" "システム統計" "GET"
)

for ((i=0; i<${#apis[@]}; i+=3)); do
    path="${apis[i]}"
    description="${apis[i+1]}"
    method="${apis[i+2]}"
    BACKEND_CHECKS=$((BACKEND_CHECKS + 1))
    if check_api_endpoint "$path" "$description" "$method"; then
        BACKEND_PASSED=$((BACKEND_PASSED + 1))
    fi
done

# 3. セキュリティヘッダー確認
log_info "3. セキュリティヘッダー確認"

check_security_headers() {
    local url="$1"
    local service_name="$2"
    
    log_info "  $service_name のセキュリティヘッダーをチェック中..."
    
    local headers=$(curl -s -I -m $TIMEOUT "$url" 2>/dev/null || echo "")
    
    if [ -z "$headers" ]; then
        log_error "  ✗ $service_name - ヘッダー取得失敗"
        echo "✗ $service_name セキュリティヘッダー - 取得失敗" >> "$RESULTS_FILE"
        return 1
    fi
    
    local security_score=0
    local total_checks=5
    
    # X-Content-Type-Options
    if echo "$headers" | grep -i "x-content-type-options" > /dev/null; then
        log_success "    ✓ X-Content-Type-Options ヘッダー設定済み"
        security_score=$((security_score + 1))
    else
        log_warning "    ⚠ X-Content-Type-Options ヘッダー未設定"
    fi
    
    # X-Frame-Options または Content-Security-Policy
    if echo "$headers" | grep -i -E "(x-frame-options|content-security-policy)" > /dev/null; then
        log_success "    ✓ フレーム保護ヘッダー設定済み"
        security_score=$((security_score + 1))
    else
        log_warning "    ⚠ フレーム保護ヘッダー未設定"
    fi
    
    # Referrer-Policy
    if echo "$headers" | grep -i "referrer-policy" > /dev/null; then
        log_success "    ✓ Referrer-Policy ヘッダー設定済み"
        security_score=$((security_score + 1))
    else
        log_warning "    ⚠ Referrer-Policy ヘッダー未設定"
    fi
    
    # Strict-Transport-Security (HTTPS必須)
    if echo "$headers" | grep -i "strict-transport-security" > /dev/null; then
        log_success "    ✓ HSTS ヘッダー設定済み"
        security_score=$((security_score + 1))
    else
        log_warning "    ⚠ HSTS ヘッダー未設定"
    fi
    
    # X-XSS-Protection
    if echo "$headers" | grep -i "x-xss-protection" > /dev/null; then
        log_success "    ✓ X-XSS-Protection ヘッダー設定済み"
        security_score=$((security_score + 1))
    else
        log_warning "    ⚠ X-XSS-Protection ヘッダー未設定"
    fi
    
    local security_percentage=$((security_score * 100 / total_checks))
    
    if [ $security_score -ge 4 ]; then
        log_success "  ✓ $service_name セキュリティヘッダー - 良好 ($security_score/$total_checks)"
        echo "✓ $service_name セキュリティヘッダー - 良好 ($security_score/$total_checks)" >> "$RESULTS_FILE"
        return 0
    elif [ $security_score -ge 2 ]; then
        log_warning "  ⚠ $service_name セキュリティヘッダー - 改善推奨 ($security_score/$total_checks)"
        echo "⚠ $service_name セキュリティヘッダー - 改善推奨 ($security_score/$total_checks)" >> "$RESULTS_FILE"
        return 1
    else
        log_error "  ✗ $service_name セキュリティヘッダー - 不十分 ($security_score/$total_checks)"
        echo "✗ $service_name セキュリティヘッダー - 不十分 ($security_score/$total_checks)" >> "$RESULTS_FILE"
        return 1
    fi
}

SECURITY_CHECKS=0
SECURITY_PASSED=0

SECURITY_CHECKS=$((SECURITY_CHECKS + 1))
if check_security_headers "$FRONTEND_URL" "フロントエンド"; then
    SECURITY_PASSED=$((SECURITY_PASSED + 1))
fi

SECURITY_CHECKS=$((SECURITY_CHECKS + 1))
if check_security_headers "$BACKEND_URL/health" "バックエンド"; then
    SECURITY_PASSED=$((SECURITY_PASSED + 1))
fi

# 4. パフォーマンス確認
log_info "4. パフォーマンス確認"

check_response_time() {
    local url="$1"
    local description="$2"
    local max_time="${3:-3}"
    
    log_info "  $description の応答時間をチェック中..."
    
    local response_time=$(curl -s -o /dev/null -w "%{time_total}" -m $TIMEOUT "$url" 2>/dev/null || echo "999")
    
    if [ "$response_time" = "999" ]; then
        log_error "  ✗ $description - 応答時間測定失敗"
        echo "✗ $description - 応答時間測定失敗" >> "$RESULTS_FILE"
        return 1
    fi
    
    # 小数点比較のため bc を使用（利用できない場合は awk を使用）
    if command -v bc > /dev/null; then
        if [ $(echo "$response_time <= $max_time" | bc) -eq 1 ]; then
            log_success "  ✓ $description - 応答時間 ${response_time}s (基準: ${max_time}s以下)"
            echo "✓ $description - 応答時間 ${response_time}s" >> "$RESULTS_FILE"
            return 0
        else
            log_warning "  ⚠ $description - 応答時間 ${response_time}s (基準: ${max_time}s以下)"
            echo "⚠ $description - 応答時間 ${response_time}s (遅い)" >> "$RESULTS_FILE"
            return 1
        fi
    else
        # bc が利用できない場合の代替処理
        local response_int=$(echo "$response_time" | cut -d. -f1)
        if [ "$response_int" -le "$max_time" ]; then
            log_success "  ✓ $description - 応答時間 ${response_time}s"
            echo "✓ $description - 応答時間 ${response_time}s" >> "$RESULTS_FILE"
            return 0
        else
            log_warning "  ⚠ $description - 応答時間 ${response_time}s (遅い可能性)"
            echo "⚠ $description - 応答時間 ${response_time}s" >> "$RESULTS_FILE"
            return 1
        fi
    fi
}

PERFORMANCE_CHECKS=0
PERFORMANCE_PASSED=0

PERFORMANCE_CHECKS=$((PERFORMANCE_CHECKS + 1))
if check_response_time "$FRONTEND_URL" "フロントエンド" "5"; then
    PERFORMANCE_PASSED=$((PERFORMANCE_PASSED + 1))
fi

PERFORMANCE_CHECKS=$((PERFORMANCE_CHECKS + 1))
if check_response_time "$BACKEND_URL/health" "バックエンドヘルスチェック" "3"; then
    PERFORMANCE_PASSED=$((PERFORMANCE_PASSED + 1))
fi

# 5. 問い合わせフォーム動作確認（実際の送信はしない）
log_info "5. 問い合わせフォーム確認"

check_contact_form() {
    local url="$FRONTEND_URL/contact"
    
    log_info "  問い合わせフォームページの確認中..."
    
    local page_content=$(curl -s -m $TIMEOUT "$url" 2>/dev/null || echo "")
    
    if [ -z "$page_content" ]; then
        log_error "  ✗ 問い合わせフォームページ取得失敗"
        echo "✗ 問い合わせフォームページ - 取得失敗" >> "$RESULTS_FILE"
        return 1
    fi
    
    # フォーム要素の存在確認
    local form_score=0
    local total_form_checks=4
    
    if echo "$page_content" | grep -i "name" > /dev/null; then
        form_score=$((form_score + 1))
    fi
    
    if echo "$page_content" | grep -i "email" > /dev/null; then
        form_score=$((form_score + 1))
    fi
    
    if echo "$page_content" | grep -i "message" > /dev/null; then
        form_score=$((form_score + 1))
    fi
    
    if echo "$page_content" | grep -i -E "(submit|送信)" > /dev/null; then
        form_score=$((form_score + 1))
    fi
    
    if [ $form_score -ge 3 ]; then
        log_success "  ✓ 問い合わせフォーム - 必要な要素が存在 ($form_score/$total_form_checks)"
        echo "✓ 問い合わせフォーム - 正常" >> "$RESULTS_FILE"
        return 0
    else
        log_error "  ✗ 問い合わせフォーム - 必要な要素が不足 ($form_score/$total_form_checks)"
        echo "✗ 問い合わせフォーム - 要素不足" >> "$RESULTS_FILE"
        return 1
    fi
}

FORM_CHECKS=1
FORM_PASSED=0

if check_contact_form; then
    FORM_PASSED=1
fi

# 6. 結果サマリー
log_info "6. 結果サマリー"

echo "" >> "$RESULTS_FILE"
echo "=== 結果サマリー ===" >> "$RESULTS_FILE"

TOTAL_CHECKS=$((FRONTEND_CHECKS + BACKEND_CHECKS + SECURITY_CHECKS + PERFORMANCE_CHECKS + FORM_CHECKS))
TOTAL_PASSED=$((FRONTEND_PASSED + BACKEND_PASSED + SECURITY_PASSED + PERFORMANCE_PASSED + FORM_PASSED))

log_info "フロントエンド基本動作: $FRONTEND_PASSED/$FRONTEND_CHECKS"
log_info "バックエンドAPI動作: $BACKEND_PASSED/$BACKEND_CHECKS"
log_info "セキュリティヘッダー: $SECURITY_PASSED/$SECURITY_CHECKS"
log_info "パフォーマンス: $PERFORMANCE_PASSED/$PERFORMANCE_CHECKS"
log_info "問い合わせフォーム: $FORM_PASSED/$FORM_CHECKS"

echo "フロントエンド基本動作: $FRONTEND_PASSED/$FRONTEND_CHECKS" >> "$RESULTS_FILE"
echo "バックエンドAPI動作: $BACKEND_PASSED/$BACKEND_CHECKS" >> "$RESULTS_FILE"
echo "セキュリティヘッダー: $SECURITY_PASSED/$SECURITY_CHECKS" >> "$RESULTS_FILE"
echo "パフォーマンス: $PERFORMANCE_PASSED/$PERFORMANCE_CHECKS" >> "$RESULTS_FILE"
echo "問い合わせフォーム: $FORM_PASSED/$FORM_CHECKS" >> "$RESULTS_FILE"

SUCCESS_RATE=$((TOTAL_PASSED * 100 / TOTAL_CHECKS))

echo "" >> "$RESULTS_FILE"
echo "総合結果: $TOTAL_PASSED/$TOTAL_CHECKS ($SUCCESS_RATE%)" >> "$RESULTS_FILE"

if [ $SUCCESS_RATE -ge 90 ]; then
    log_success "🎉 本番環境最終確認 - 優秀 ($TOTAL_PASSED/$TOTAL_CHECKS, $SUCCESS_RATE%)"
    echo "🎉 本番環境最終確認 - 優秀" >> "$RESULTS_FILE"
    exit 0
elif [ $SUCCESS_RATE -ge 80 ]; then
    log_success "✅ 本番環境最終確認 - 良好 ($TOTAL_PASSED/$TOTAL_CHECKS, $SUCCESS_RATE%)"
    echo "✅ 本番環境最終確認 - 良好" >> "$RESULTS_FILE"
    exit 0
elif [ $SUCCESS_RATE -ge 70 ]; then
    log_warning "⚠️ 本番環境最終確認 - 改善推奨 ($TOTAL_PASSED/$TOTAL_CHECKS, $SUCCESS_RATE%)"
    echo "⚠️ 本番環境最終確認 - 改善推奨" >> "$RESULTS_FILE"
    exit 1
else
    log_error "❌ 本番環境最終確認 - 要改善 ($TOTAL_PASSED/$TOTAL_CHECKS, $SUCCESS_RATE%)"
    echo "❌ 本番環境最終確認 - 要改善" >> "$RESULTS_FILE"
    exit 1
fi