/**
 * 問い合わせ統計コンポーネント
 */
'use client';

import React, { useEffect } from 'react';
import { useContactManagement } from '@/stores/contactManagementStore';

export const ContactStats: React.FC = () => {
  const { stats, loadStats } = useContactManagement();

  useEffect(() => {
    loadStats();

    // 5分ごとに統計を更新
    const interval = setInterval(loadStats, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (!stats) {
    return (
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="animate-pulse rounded-lg bg-white p-6 shadow">
            <div className="mb-2 h-4 w-1/2 rounded bg-gray-200"></div>
            <div className="h-8 w-1/3 rounded bg-gray-200"></div>
          </div>
        ))}
      </div>
    );
  }

  const statCards = [
    {
      title: '総問い合わせ数',
      value: stats.total,
      icon: '📊',
      color: 'bg-blue-500',
      textColor: 'text-blue-600',
    },
    {
      title: '未対応',
      value: stats.pending,
      icon: '⏳',
      color: 'bg-yellow-500',
      textColor: 'text-yellow-600',
    },
    {
      title: '対応中',
      value: stats.inProgress,
      icon: '🔄',
      color: 'bg-blue-500',
      textColor: 'text-blue-600',
    },
    {
      title: '回答済み',
      value: stats.responded,
      icon: '✅',
      color: 'bg-green-500',
      textColor: 'text-green-600',
    },
  ];

  const timeStats = [
    {
      title: '今日',
      value: stats.today,
      icon: '📅',
    },
    {
      title: '今週',
      value: stats.thisWeek,
      icon: '📆',
    },
    {
      title: '今月',
      value: stats.thisMonth,
      icon: '🗓️',
    },
  ];

  return (
    <div className="space-y-6">
      {/* メインステータス */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat, index) => (
          <div key={index} className="rounded-lg bg-white p-6 shadow">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div
                  className={`h-8 w-8 ${stat.color} flex items-center justify-center rounded-md`}
                >
                  <span className="text-sm text-white">{stat.icon}</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">
                  {stat.title}
                </p>
                <p className={`text-2xl font-semibold ${stat.textColor}`}>
                  {stat.value.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 時間別統計 */}
      <div className="rounded-lg bg-white p-6 shadow">
        <h3 className="mb-4 text-lg font-medium text-gray-900">期間別統計</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {timeStats.map((stat, index) => (
            <div key={index} className="rounded-lg bg-gray-50 p-4 text-center">
              <div className="mb-2 text-2xl">{stat.icon}</div>
              <p className="text-sm text-gray-500">{stat.title}</p>
              <p className="text-xl font-semibold text-gray-900">
                {stat.value.toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* 対応率 */}
      <div className="rounded-lg bg-white p-6 shadow">
        <h3 className="mb-4 text-lg font-medium text-gray-900">対応状況</h3>
        <div className="space-y-4">
          {/* 対応率バー */}
          <div>
            <div className="mb-1 flex justify-between text-sm text-gray-600">
              <span>対応済み率</span>
              <span>
                {stats.total > 0
                  ? Math.round(
                      ((stats.responded + stats.closed) / stats.total) * 100
                    )
                  : 0}
                %
              </span>
            </div>
            <div className="h-2 w-full rounded-full bg-gray-200">
              <div
                className="h-2 rounded-full bg-green-500 transition-all duration-300"
                style={{
                  width:
                    stats.total > 0
                      ? `${((stats.responded + stats.closed) / stats.total) * 100}%`
                      : '0%',
                }}
              ></div>
            </div>
          </div>

          {/* 未対応率バー */}
          <div>
            <div className="mb-1 flex justify-between text-sm text-gray-600">
              <span>未対応率</span>
              <span>
                {stats.total > 0
                  ? Math.round((stats.pending / stats.total) * 100)
                  : 0}
                %
              </span>
            </div>
            <div className="h-2 w-full rounded-full bg-gray-200">
              <div
                className="h-2 rounded-full bg-yellow-500 transition-all duration-300"
                style={{
                  width:
                    stats.total > 0
                      ? `${(stats.pending / stats.total) * 100}%`
                      : '0%',
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
