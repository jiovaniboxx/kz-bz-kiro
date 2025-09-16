/**
 * Basic E2E Tests
 *
 * 実際のページ内容に基づいた基本的なE2Eテスト
 */

import { test, expect } from '@playwright/test';

test.describe('Basic E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // 各テスト前にページを読み込み、完全に読み込まれるまで待機
    await page.goto('/', { waitUntil: 'networkidle' });
  });

  test('should load homepage with correct title and heading', async ({
    page,
  }) => {
    // ページタイトルを確認
    await expect(page).toHaveTitle(/English Cafe/i);

    // ヒーローセクションのヘッディングを確認
    await expect(
      page.getByRole('heading', { name: /English Cafe/i })
    ).toBeVisible();

    // サブタイトルを確認
    await expect(
      page.getByText('アットホームな雰囲気で英語を学ぼう')
    ).toBeVisible();
  });

  test('should display main content sections', async ({ page }) => {
    // メインヘッディングが表示される
    await expect(
      page.getByRole('heading', { name: /English Cafe/i })
    ).toBeVisible();

    // ようこそセクションが表示される
    await expect(page.getByRole('heading', { name: /ようこそ/i })).toBeVisible();

    // 説明文が表示される
    await expect(
      page.getByText('英会話カフェで楽しく英語を学びませんか？')
    ).toBeVisible();

    // 特徴リストが表示される
    await expect(page.getByText('✅ ネイティブ講師')).toBeVisible();
    await expect(page.getByText('✅ カフェスタイル')).toBeVisible();
    
    // API接続テストリンクが表示される
    await expect(page.getByRole('link', { name: 'API接続テスト' })).toBeVisible();
  });

  test('should have working API connection test link', async ({ page }) => {
    // API接続テストリンクが表示される
    const apiLink = page.getByRole('link', { name: 'API接続テスト' });
    await expect(apiLink).toBeVisible();

    // リンクが正しいhrefを持つ
    await expect(apiLink).toHaveAttribute('href', '/api-test');
  });

  test('should work on different screen sizes', async ({ page }) => {
    const screenSizes = [
      { width: 1920, height: 1080, name: 'Desktop' },
      { width: 1024, height: 768, name: 'Tablet' },
      { width: 375, height: 667, name: 'Mobile' },
    ];

    for (const size of screenSizes) {
      await page.setViewportSize({ width: size.width, height: size.height });
      await page.waitForTimeout(500); // レイアウト調整を待機

      // 主要コンテンツが表示される
      await expect(
        page.getByRole('heading', { name: /English Cafe/i })
      ).toBeVisible();
      await expect(page.locator('main')).toBeVisible();
    }
  });

  test('should have proper page structure', async ({ page }) => {
    // メインコンテンツエリアが存在する
    await expect(page.locator('main')).toBeVisible();

    // 適切なHTML構造を持つ
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBe(1); // h1は1つだけ

    // bodyが表示される
    await expect(page.locator('body')).toBeVisible();
  });
});
