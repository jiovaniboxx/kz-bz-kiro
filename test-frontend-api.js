#!/usr/bin/env node

/**
 * フロントエンドからバックエンドへのAPI通信テスト
 * Node.jsでaxiosを使用してテスト
 */

const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000';

// Axiosインスタンスの作成
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Origin': 'http://localhost:3000'
  },
});

async function testHealthCheck() {
  console.log('🔍 ヘルスチェックテスト...');
  try {
    const response = await apiClient.get('/health');
    console.log('✅ ヘルスチェック成功:', response.data);
    return true;
  } catch (error) {
    console.error('❌ ヘルスチェック失敗:', error.message);
    return false;
  }
}

async function testContactSubmission() {
  console.log('📝 問い合わせ送信テスト...');
  
  const testData = {
    name: 'Node.jsテスト',
    email: 'nodejs-test@example.com',
    phone: '090-1234-5678',
    lesson_type: 'trial',
    preferred_contact: 'email',
    message: 'Node.jsからのテスト送信です。フロントエンドAPI通信の確認を行っています。'
  };

  try {
    const response = await apiClient.post('/api/v1/contacts/', testData);
    console.log('✅ 問い合わせ送信成功:', response.data);
    return true;
  } catch (error) {
    console.error('❌ 問い合わせ送信失敗:', error.response?.data || error.message);
    return false;
  }
}

async function testInvalidData() {
  console.log('🚫 無効データテスト...');
  
  const invalidData = {
    name: '',
    email: 'invalid-email',
    lesson_type: 'invalid-type',
    preferred_contact: 'invalid-contact',
    message: ''
  };

  try {
    const response = await apiClient.post('/api/v1/contacts/', invalidData);
    console.log('❌ 無効データが受け入れられました（予期しない結果）:', response.data);
    return false;
  } catch (error) {
    if (error.response && error.response.status === 422) {
      console.log('✅ バリデーションエラーが正しく返されました:', error.response.data);
      return true;
    } else {
      console.error('❌ 予期しないエラー:', error.response?.data || error.message);
      return false;
    }
  }
}

async function runTests() {
  console.log('🚀 フロントエンドAPI通信テストを開始...\n');

  const results = [];
  
  // ヘルスチェックテスト
  results.push(await testHealthCheck());
  console.log('');

  // 問い合わせ送信テスト
  results.push(await testContactSubmission());
  console.log('');

  // 無効データテスト
  results.push(await testInvalidData());
  console.log('');

  // 結果サマリー
  const passed = results.filter(r => r).length;
  const total = results.length;
  
  console.log('📊 テスト結果サマリー:');
  console.log(`   合格: ${passed}/${total}`);
  console.log(`   成功率: ${Math.round((passed / total) * 100)}%`);
  
  if (passed === total) {
    console.log('🎉 すべてのテストが成功しました！');
    console.log('✅ フロントエンドからバックエンドへのAPI通信は正常に動作しています。');
  } else {
    console.log('⚠️  一部のテストが失敗しました。');
    console.log('💡 バックエンドサーバーが起動していることを確認してください。');
  }

  process.exit(passed === total ? 0 : 1);
}

// テスト実行
runTests().catch(error => {
  console.error('💥 テスト実行中にエラーが発生しました:', error);
  process.exit(1);
});