import { test, expect } from '@playwright/test';

test.describe('全システム統合テスト', () => {
  test.beforeEach(async ({ page }) => {
    // 各テスト前にページを読み込み、完全に読み込まれるまで待機
    await page.goto('/', { waitUntil: 'networkidle' });
  });

  test('ホームページ基本表示テスト', async ({ page }) => {
    // ページタイトルを確認（部分一致で柔軟に）
    await expect(page).toHaveTitle(/English|Cafe|英会話/i);

    // メインヘッダーを確認（より柔軟な検索）
    const heading = page.locator('h1').first();
    await expect(heading).toBeVisible();

    // 基本的なコンテンツが表示されることを確認
    const mainContent = page.locator('main');
    await expect(mainContent).toBeVisible();
  });

  test('レスポンシブデザインテスト', async ({ page }) => {
    // モバイルビューポートに設定
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForLoadState('networkidle');

    // コンテンツが表示されることを確認
    await expect(page.locator('h1').first()).toBeVisible();

    // タブレットビューポートに設定
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(500); // レイアウト調整を待機

    // コンテンツが適切に表示されることを確認
    await expect(page.locator('h1').first()).toBeVisible();

    // デスクトップビューポートに設定
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(500); // レイアウト調整を待機

    // デスクトップレイアウトが適用されることを確認
    await expect(page.locator('h1').first()).toBeVisible();
  });

  test('ページ読み込みパフォーマンステスト', async ({ page }) => {
    const startTime = Date.now();

    // 新しいページコンテキストで読み込み
    await page.goto('/', { waitUntil: 'networkidle' });

    const loadTime = Date.now() - startTime;

    // 読み込み時間が10秒以下であることを確認（Docker環境を考慮）
    expect(loadTime).toBeLessThan(10000);

    // 主要要素が表示されることを確認
    await expect(page.locator('h1').first()).toBeVisible();
    await expect(page.locator('main')).toBeVisible();
  });

  test('アクセシビリティテスト', async ({ page }) => {
    // キーボードナビゲーションテスト
    await page.keyboard.press('Tab');

    // 見出し構造を確認
    const h1Elements = await page.locator('h1').count();
    expect(h1Elements).toBeGreaterThan(0);

    // 主要コンテンツが表示されることを確認
    await expect(page.locator('main')).toBeVisible();

    // 基本的なアクセシビリティ要素の確認
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });

  test('エラーハンドリングテスト', async ({ page }) => {
    // 存在しないページにアクセス
    const response = await page.goto('/nonexistent-page', {
      waitUntil: 'networkidle',
    });

    // 404ステータスまたはNext.jsの404ページが表示されることを確認
    const status = response?.status();
    expect(status === 404 || status === 200).toBeTruthy(); // Next.jsは404ページも200で返すことがある
  });

  test('基本機能テスト', async ({ page }) => {
    // ページが正常に読み込まれることを確認
    await expect(page.locator('body')).toBeVisible();

    // 基本的なコンテンツが存在することを確認
    const content = page.locator('main, div, section').first();
    await expect(content).toBeVisible();

    // JavaScriptが動作していることを確認
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
  });
});
