/**
 * API Test Page E2E Tests
 *
 * APIテストページの動作確認
 */

import { test, expect } from '@playwright/test';

test.describe('API Test Page', () => {
  test.beforeEach(async ({ page }) => {
    // APIテストページを読み込み
    await page.goto('/api-test', { waitUntil: 'networkidle' });
  });

  test('should load API test page correctly', async ({ page }) => {
    // ページタイトルを確認
    await expect(page).toHaveTitle(/English Cafe/i);

    // メインヘッディングを確認
    await expect(
      page.getByRole('heading', { name: 'API接続テスト' })
    ).toBeVisible();

    // 説明文を確認
    await expect(
      page.getByText('Docker Composeでの動作確認用のページです')
    ).toBeVisible();
  });

  test('should display test information', async ({ page }) => {
    // 動作確認セクションが表示される
    await expect(page.getByRole('heading', { name: '動作確認' })).toBeVisible();

    // 説明文が表示される
    await expect(
      page.getByText('フロントエンドとバックエンドの接続をテストします。')
    ).toBeVisible();

    // 技術スタックが表示される
    await expect(page.getByText('✅ Next.js 14')).toBeVisible();
    await expect(page.getByText('✅ Tailwind CSS')).toBeVisible();
    await expect(page.getByText('✅ TypeScript')).toBeVisible();
    await expect(page.getByText('✅ Docker Compose')).toBeVisible();
  });

  test('should have working API health check link', async ({ page }) => {
    // API接続テストリンクが表示される
    const apiLink = page.getByRole('link', { name: 'API接続テスト' });
    await expect(apiLink).toBeVisible();

    // リンクが正しいhrefを持つ
    await expect(apiLink).toHaveAttribute('href', '/api/health');
  });

  test('should have working home link', async ({ page }) => {
    // ホームに戻るリンクが表示される
    const homeLink = page.getByRole('link', { name: 'ホームに戻る' });
    await expect(homeLink).toBeVisible();

    // リンクが正しいhrefを持つ
    await expect(homeLink).toHaveAttribute('href', '/');
  });

  test('should navigate to home page', async ({ page }) => {
    // ホームに戻るリンクをクリック
    await page.getByRole('link', { name: 'ホームに戻る' }).click();

    // ホームページに遷移することを確認
    await expect(page).toHaveURL('/');
    await expect(
      page.getByRole('heading', { name: /English Cafe/i })
    ).toBeVisible();
  });
});