/**
 * 監視ダッシュボードページ
 */
'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/stores/authStore';
import { authService } from '@/services/authService';

interface HealthCheck {
  status: string;
  timestamp: string;
  version: string;
  uptime: number;
  checks: Record<string, any>;
}

interface SystemMetrics {
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  activeConnections: number;
  timestamp: string;
}

interface ErrorLog {
  timestamp: string;
  level: string;
  message: string;
  category: string;
  requestId: string;
}

interface UptimeStats {
  uptimePercentage: number;
  totalChecks: number;
  successfulChecks: number;
  failedChecks: number;
  averageResponseTime: number;
  lastDowntime: string | null;
  longestDowntimeMinutes: number | null;
  recentRecords: Array<{
    timestamp: string;
    status: string;
    responseTime: number;
  }>;
}

interface Alert {
  id: string;
  ruleName: string;
  severity: string;
  title: string;
  message: string;
  timestamp: string;
  resolved: boolean;
  resolvedAt: string | null;
}

export default function MonitoringPage() {
  const { admin } = useAuth();
  const [healthCheck, setHealthCheck] = useState<HealthCheck | null>(null);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [errorLogs, setErrorLogs] = useState<ErrorLog[]>([]);
  const [uptimeStats, setUptimeStats] = useState<UptimeStats | null>(null);
  const [alerts, setAlerts] = useState<{ active: Alert[]; recent: Alert[] }>({
    active: [],
    recent: [],
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMonitoringData();

    // 30秒ごとに更新
    const interval = setInterval(loadMonitoringData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadMonitoringData = async () => {
    try {
      setError(null);
      const token = await authService.getValidAccessToken();
      if (!token) {
        throw new Error('認証が必要です');
      }

      // ヘルスチェック
      const healthResponse = await fetch('/api/monitoring/health', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        setHealthCheck({
          status: healthData.status,
          timestamp: healthData.timestamp,
          version: healthData.version,
          uptime: healthData.uptime,
          checks: healthData.checks,
        });
      }

      // システムメトリクス
      const metricsResponse = await fetch('/api/monitoring/metrics', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (metricsResponse.ok) {
        const metricsData = await metricsResponse.json();
        setMetrics({
          cpuUsage: metricsData.cpu_usage,
          memoryUsage: metricsData.memory_usage,
          diskUsage: metricsData.disk_usage,
          activeConnections: metricsData.active_connections,
          timestamp: metricsData.timestamp,
        });
      }

      // エラーログ
      const logsResponse = await fetch(
        '/api/monitoring/logs/errors?per_page=10',
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (logsResponse.ok) {
        const logsData = await logsResponse.json();
        setErrorLogs(logsData.logs || []);
      }

      // アップタイム統計
      const uptimeResponse = await fetch('/api/monitoring/uptime?hours=24', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (uptimeResponse.ok) {
        const uptimeData = await uptimeResponse.json();
        setUptimeStats({
          uptimePercentage: uptimeData.uptime_percentage,
          totalChecks: uptimeData.total_checks,
          successfulChecks: uptimeData.successful_checks,
          failedChecks: uptimeData.failed_checks,
          averageResponseTime: uptimeData.average_response_time,
          lastDowntime: uptimeData.last_downtime,
          longestDowntimeMinutes: uptimeData.longest_downtime_minutes,
          recentRecords: uptimeData.recent_records || [],
        });
      }

      // アラート
      const alertsResponse = await fetch('/api/monitoring/alerts', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (alertsResponse.ok) {
        const alertsData = await alertsResponse.json();
        setAlerts({
          active: alertsData.active_alerts || [],
          recent: alertsData.recent_history || [],
        });
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : '監視データの取得に失敗しました'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const testAlert = async () => {
    try {
      const token = await authService.getValidAccessToken();
      if (!token) return;

      const response = await fetch('/api/monitoring/alerts/test/email', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        alert('テストアラートを送信しました');
      } else {
        alert('テストアラートの送信に失敗しました');
      }
    } catch (err) {
      alert('エラーが発生しました');
    }
  };

  const resolveAlert = async (alertId: string) => {
    try {
      const token = await authService.getValidAccessToken();
      if (!token) return;

      const response = await fetch(
        `/api/monitoring/alerts/${alertId}/resolve`,
        {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        // アラート一覧を再読み込み
        loadMonitoringData();
      } else {
        alert('アラートの解決に失敗しました');
      }
    } catch (err) {
      alert('エラーが発生しました');
    }
  };

  const formatUptime = (seconds: number): string => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (days > 0) {
      return `${days}日 ${hours}時間 ${minutes}分`;
    } else if (hours > 0) {
      return `${hours}時間 ${minutes}分`;
    } else {
      return `${minutes}分`;
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'unhealthy':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getUsageColor = (usage: number): string => {
    if (usage > 90) return 'bg-red-500';
    if (usage > 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">監視データを読み込み中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* ヘッダー */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">システム監視</h1>
            <p className="mt-1 text-sm text-gray-600">
              システムの健全性とパフォーマンスを監視
            </p>
          </div>
          {admin?.role === 'admin' && (
            <button
              onClick={testAlert}
              className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              テストアラート
            </button>
          )}
        </div>

        {error && (
          <div className="mb-6 rounded-md border border-red-200 bg-red-50 p-4">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* ヘルスチェック */}
        {healthCheck && (
          <div className="mb-8">
            <h2 className="mb-4 text-lg font-medium text-gray-900">
              システム状態
            </h2>
            <div className="rounded-lg bg-white p-6 shadow">
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center">
                  <span
                    className={`inline-flex rounded-full px-3 py-1 text-sm font-semibold ${getStatusColor(healthCheck.status)}`}
                  >
                    {healthCheck.status}
                  </span>
                  <span className="ml-4 text-sm text-gray-600">
                    稼働時間: {formatUptime(healthCheck.uptime)}
                  </span>
                </div>
                <span className="text-sm text-gray-500">
                  最終更新:{' '}
                  {new Date(healthCheck.timestamp).toLocaleString('ja-JP')}
                </span>
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                {Object.entries(healthCheck.checks).map(([key, check]) => (
                  <div key={key} className="rounded-lg border p-4">
                    <h3 className="font-medium capitalize text-gray-900">
                      {key}
                    </h3>
                    <span
                      className={`mt-2 inline-flex rounded-full px-2 py-1 text-xs font-semibold ${getStatusColor(check.status)}`}
                    >
                      {check.status}
                    </span>
                    {check.error && (
                      <p className="mt-1 text-xs text-red-600">{check.error}</p>
                    )}
                    {check.message && (
                      <p className="mt-1 text-xs text-gray-600">
                        {check.message}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* システムメトリクス */}
        {metrics && (
          <div className="mb-8">
            <h2 className="mb-4 text-lg font-medium text-gray-900">
              システムメトリクス
            </h2>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
              <div className="rounded-lg bg-white p-6 shadow">
                <h3 className="text-sm font-medium text-gray-500">CPU使用率</h3>
                <div className="mt-2">
                  <div className="flex items-center">
                    <span className="text-2xl font-semibold text-gray-900">
                      {metrics.cpuUsage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="mt-2 h-2 w-full rounded-full bg-gray-200">
                    <div
                      className={`h-2 rounded-full ${getUsageColor(metrics.cpuUsage)}`}
                      style={{ width: `${metrics.cpuUsage}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="rounded-lg bg-white p-6 shadow">
                <h3 className="text-sm font-medium text-gray-500">
                  メモリ使用率
                </h3>
                <div className="mt-2">
                  <div className="flex items-center">
                    <span className="text-2xl font-semibold text-gray-900">
                      {metrics.memoryUsage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="mt-2 h-2 w-full rounded-full bg-gray-200">
                    <div
                      className={`h-2 rounded-full ${getUsageColor(metrics.memoryUsage)}`}
                      style={{ width: `${metrics.memoryUsage}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="rounded-lg bg-white p-6 shadow">
                <h3 className="text-sm font-medium text-gray-500">
                  ディスク使用率
                </h3>
                <div className="mt-2">
                  <div className="flex items-center">
                    <span className="text-2xl font-semibold text-gray-900">
                      {metrics.diskUsage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="mt-2 h-2 w-full rounded-full bg-gray-200">
                    <div
                      className={`h-2 rounded-full ${getUsageColor(metrics.diskUsage)}`}
                      style={{ width: `${metrics.diskUsage}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="rounded-lg bg-white p-6 shadow">
                <h3 className="text-sm font-medium text-gray-500">
                  アクティブ接続
                </h3>
                <div className="mt-2">
                  <span className="text-2xl font-semibold text-gray-900">
                    {metrics.activeConnections}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* アップタイム統計 */}
        {uptimeStats && (
          <div className="mb-8">
            <h2 className="mb-4 text-lg font-medium text-gray-900">
              アップタイム統計（24時間）
            </h2>
            <div className="mb-4 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
              <div className="rounded-lg bg-white p-6 shadow">
                <h3 className="text-sm font-medium text-gray-500">稼働率</h3>
                <div className="mt-2">
                  <span className="text-2xl font-semibold text-gray-900">
                    {uptimeStats.uptimePercentage.toFixed(2)}%
                  </span>
                </div>
                <div className="mt-2 h-2 w-full rounded-full bg-gray-200">
                  <div
                    className={`h-2 rounded-full ${uptimeStats.uptimePercentage >= 99 ? 'bg-green-500' : uptimeStats.uptimePercentage >= 95 ? 'bg-yellow-500' : 'bg-red-500'}`}
                    style={{ width: `${uptimeStats.uptimePercentage}%` }}
                  ></div>
                </div>
              </div>

              <div className="rounded-lg bg-white p-6 shadow">
                <h3 className="text-sm font-medium text-gray-500">
                  総チェック数
                </h3>
                <div className="mt-2">
                  <span className="text-2xl font-semibold text-gray-900">
                    {uptimeStats.totalChecks}
                  </span>
                </div>
                <p className="mt-1 text-sm text-gray-600">
                  成功: {uptimeStats.successfulChecks} / 失敗:{' '}
                  {uptimeStats.failedChecks}
                </p>
              </div>

              <div className="rounded-lg bg-white p-6 shadow">
                <h3 className="text-sm font-medium text-gray-500">
                  平均応答時間
                </h3>
                <div className="mt-2">
                  <span className="text-2xl font-semibold text-gray-900">
                    {uptimeStats.averageResponseTime.toFixed(3)}s
                  </span>
                </div>
              </div>

              <div className="rounded-lg bg-white p-6 shadow">
                <h3 className="text-sm font-medium text-gray-500">
                  最後のダウンタイム
                </h3>
                <div className="mt-2">
                  <span className="text-sm text-gray-900">
                    {uptimeStats.lastDowntime
                      ? new Date(uptimeStats.lastDowntime).toLocaleString(
                          'ja-JP'
                        )
                      : 'なし'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* アクティブアラート */}
        {alerts.active.length > 0 && (
          <div className="mb-8">
            <h2 className="mb-4 text-lg font-medium text-gray-900">
              アクティブアラート
            </h2>
            <div className="overflow-hidden rounded-lg bg-white shadow">
              <div className="divide-y divide-gray-200">
                {alerts.active.map(alert => (
                  <div key={alert.id} className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span
                          className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                            alert.severity === 'critical'
                              ? 'bg-red-100 text-red-800'
                              : alert.severity === 'high'
                                ? 'bg-orange-100 text-orange-800'
                                : alert.severity === 'medium'
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-blue-100 text-blue-800'
                          }`}
                        >
                          {alert.severity.toUpperCase()}
                        </span>
                        <h3 className="text-sm font-medium text-gray-900">
                          {alert.title}
                        </h3>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-gray-500">
                          {new Date(alert.timestamp).toLocaleString('ja-JP')}
                        </span>
                        <button
                          onClick={() => resolveAlert(alert.id)}
                          className="text-xs text-blue-600 hover:text-blue-500"
                        >
                          解決
                        </button>
                      </div>
                    </div>
                    <p className="mt-1 text-sm text-gray-600">
                      {alert.message}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 最新のエラーログ */}
        <div>
          <h2 className="mb-4 text-lg font-medium text-gray-900">
            最新のエラーログ
          </h2>
          <div className="overflow-hidden rounded-lg bg-white shadow">
            {errorLogs.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                エラーログがありません
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {errorLogs.map((log, index) => (
                  <div key={index} className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span
                          className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                            log.level === 'ERROR'
                              ? 'bg-red-100 text-red-800'
                              : log.level === 'WARNING'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {log.level}
                        </span>
                        <span className="text-sm text-gray-600">
                          {log.category}
                        </span>
                      </div>
                      <span className="text-xs text-gray-500">
                        {new Date(log.timestamp).toLocaleString('ja-JP')}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-gray-900">{log.message}</p>
                    {log.requestId && (
                      <p className="mt-1 text-xs text-gray-500">
                        Request ID: {log.requestId}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
