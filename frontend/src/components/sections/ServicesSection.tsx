/**
 * Services Section Component
 * レッスンタイプ、料金体系、営業時間を表示するセクション
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { Container, Card, Button, Badge, Tabs } from '@/components/ui';
import { cn } from '@/utils/cn';

interface LessonType {
  id: string;
  name: string;
  description: string;
  price: {
    amount: number;
    period: string;
  };
  duration: number;
  maxStudents: number;
  features: string[];
  popular?: boolean;
  icon: string;
}

interface BusinessHours {
  day: string;
  hours: string;
  isToday?: boolean;
}

const lessonTypes: LessonType[] = [
  {
    id: 'group',
    name: 'グループレッスン',
    description: '最大4名までの少人数制で、他の生徒と一緒に楽しく学習',
    price: { amount: 3500, period: '1回' },
    duration: 60,
    maxStudents: 4,
    features: [
      '少人数制（最大4名）',
      'ネイティブ講師',
      '教材費込み',
      '振替レッスン可能',
      'レベル別クラス',
    ],
    popular: true,
    icon: '👥',
  },
  {
    id: 'private',
    name: 'プライベートレッスン',
    description: 'マンツーマンで集中的に学習、あなたのペースで進められます',
    price: { amount: 6500, period: '1回' },
    duration: 50,
    maxStudents: 1,
    features: [
      'マンツーマン指導',
      'カスタマイズ可能',
      'フレキシブルスケジュール',
      '専用教材',
      '進捗管理',
    ],
    icon: '🎯',
  },
  {
    id: 'trial',
    name: '体験レッスン',
    description: '初回限定の無料体験レッスンで、雰囲気を体感してください',
    price: { amount: 0, period: '無料' },
    duration: 30,
    maxStudents: 4,
    features: [
      '完全無料',
      'レベルチェック',
      'カウンセリング',
      '入会相談',
      '教材見学',
    ],
    icon: '✨',
  },
];

const businessHours: BusinessHours[] = [
  { day: '月曜日', hours: '10:00 - 21:00' },
  { day: '火曜日', hours: '10:00 - 21:00' },
  { day: '水曜日', hours: '10:00 - 21:00' },
  { day: '木曜日', hours: '10:00 - 21:00' },
  { day: '金曜日', hours: '10:00 - 21:00' },
  { day: '土曜日', hours: '9:00 - 18:00' },
  { day: '日曜日', hours: '定休日' },
];

// 今日の曜日を取得
const getTodayIndex = () => {
  const today = new Date().getDay();
  return today === 0 ? 6 : today - 1; // 日曜日を6に調整
};

interface ServicesSectionProps {
  className?: string;
}

export function ServicesSection({ className }: ServicesSectionProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('lessons');
  const sectionRef = useRef<HTMLElement>(null);
  const todayIndex = getTodayIndex();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  const tabItems = [
    {
      id: 'lessons',
      label: 'レッスンタイプ',
      content: (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {lessonTypes.map((lesson, index) => (
            <Card
              key={lesson.id}
              className={cn(
                'relative transform p-6 transition-all duration-700 hover:scale-105',
                lesson.popular && 'shadow-lg ring-2 ring-primary-500',
                isVisible
                  ? 'translate-y-0 opacity-100'
                  : 'translate-y-8 opacity-0'
              )}
              style={{ transitionDelay: `${index * 150}ms` }}
            >
              {lesson.popular && (
                <Badge
                  variant="primary"
                  className="absolute -top-3 left-1/2 -translate-x-1/2 transform"
                >
                  人気No.1
                </Badge>
              )}

              <div className="mb-4 text-center">
                <div className="mb-3 text-4xl">{lesson.icon}</div>
                <h3 className="mb-2 text-xl font-bold text-gray-900">
                  {lesson.name}
                </h3>
                <p className="text-sm leading-relaxed text-gray-600">
                  {lesson.description}
                </p>
              </div>

              <div className="mb-6 text-center">
                <div className="mb-1 text-3xl font-bold text-primary-600">
                  {lesson.price.amount === 0
                    ? '無料'
                    : `¥${lesson.price.amount.toLocaleString()}`}
                </div>
                <div className="text-sm text-gray-500">
                  {lesson.price.period} / {lesson.duration}分
                </div>
                <div className="mt-1 text-xs text-gray-400">
                  定員: {lesson.maxStudents}名
                </div>
              </div>

              <ul className="mb-6 space-y-2">
                {lesson.features.map((feature, idx) => (
                  <li
                    key={idx}
                    className="flex items-center text-sm text-gray-600"
                  >
                    <svg
                      className="mr-2 h-4 w-4 flex-shrink-0 text-green-500"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>

              <Button
                className="w-full"
                variant={lesson.popular ? 'primary' : 'outline'}
                asChild
              >
                <Link href="/contact">
                  {lesson.id === 'trial' ? '無料体験を予約' : '詳細・予約'}
                </Link>
              </Button>
            </Card>
          ))}
        </div>
      ),
    },
    {
      id: 'schedule',
      label: '営業時間',
      content: (
        <div className="mx-auto max-w-2xl">
          <Card className="p-6">
            <h3 className="mb-6 text-center text-xl font-bold text-gray-900">
              営業時間・スケジュール
            </h3>

            <div className="space-y-3">
              {businessHours.map((schedule, index) => (
                <div
                  key={index}
                  className={cn(
                    'flex items-center justify-between rounded-lg px-4 py-3 transition-colors',
                    index === todayIndex
                      ? 'border border-primary-200 bg-primary-50'
                      : 'bg-gray-50',
                    schedule.hours === '定休日' && 'opacity-60'
                  )}
                >
                  <span
                    className={cn(
                      'font-medium',
                      index === todayIndex
                        ? 'text-primary-700'
                        : 'text-gray-700'
                    )}
                  >
                    {schedule.day}
                    {index === todayIndex && (
                      <Badge variant="primary" size="sm" className="ml-2">
                        今日
                      </Badge>
                    )}
                  </span>
                  <span
                    className={cn(
                      'font-mono',
                      schedule.hours === '定休日'
                        ? 'text-red-500'
                        : index === todayIndex
                          ? 'font-semibold text-primary-600'
                          : 'text-gray-600'
                    )}
                  >
                    {schedule.hours}
                  </span>
                </div>
              ))}
            </div>

            <div className="mt-6 rounded-lg bg-blue-50 p-4">
              <h4 className="mb-2 font-semibold text-blue-900">
                📅 予約について
              </h4>
              <ul className="space-y-1 text-sm text-blue-800">
                <li>• レッスンは完全予約制です</li>
                <li>• 前日までのキャンセルで振替可能</li>
                <li>• 祝日は通常営業（年末年始除く）</li>
                <li>• 臨時休業はWebサイトでお知らせします</li>
              </ul>
            </div>

            <div className="mt-6 text-center">
              <Button size="lg" asChild>
                <Link href="/contact">レッスンを予約する</Link>
              </Button>
            </div>
          </Card>
        </div>
      ),
    },
    {
      id: 'pricing',
      label: '料金プラン',
      content: (
        <div className="mx-auto max-w-4xl">
          <div className="grid gap-8 md:grid-cols-2">
            {/* 月額プラン */}
            <Card className="p-6">
              <div className="mb-6 text-center">
                <h3 className="mb-2 text-xl font-bold text-gray-900">
                  月額プラン
                </h3>
                <p className="text-sm text-gray-600">
                  定期的に通いたい方におすすめ
                </p>
              </div>

              <div className="space-y-4">
                <div className="rounded-lg border p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="font-medium">月4回プラン</span>
                    <span className="text-lg font-bold text-primary-600">
                      ¥12,000
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">1回あたり ¥3,000</p>
                </div>

                <div className="rounded-lg border p-4 ring-2 ring-primary-500">
                  <Badge variant="primary" size="sm" className="mb-2">
                    おすすめ
                  </Badge>
                  <div className="mb-2 flex items-center justify-between">
                    <span className="font-medium">月8回プラン</span>
                    <span className="text-lg font-bold text-primary-600">
                      ¥20,000
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">1回あたり ¥2,500</p>
                </div>

                <div className="rounded-lg border p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="font-medium">通い放題プラン</span>
                    <span className="text-lg font-bold text-primary-600">
                      ¥35,000
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">毎日1回まで</p>
                </div>
              </div>
            </Card>

            {/* 都度払い */}
            <Card className="p-6">
              <div className="mb-6 text-center">
                <h3 className="mb-2 text-xl font-bold text-gray-900">
                  都度払い
                </h3>
                <p className="text-sm text-gray-600">
                  自分のペースで通いたい方に
                </p>
              </div>

              <div className="space-y-4">
                <div className="rounded-lg border p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="font-medium">グループレッスン</span>
                    <span className="text-lg font-bold text-primary-600">
                      ¥3,500
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">60分 / 最大4名</p>
                </div>

                <div className="rounded-lg border p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="font-medium">プライベートレッスン</span>
                    <span className="text-lg font-bold text-primary-600">
                      ¥6,500
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">50分 / マンツーマン</p>
                </div>

                <div className="rounded-lg border bg-green-50 p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="font-medium">体験レッスン</span>
                    <span className="text-lg font-bold text-green-600">
                      無料
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">30分 / 初回限定</p>
                </div>
              </div>
            </Card>
          </div>

          <div className="mt-8 rounded-lg bg-gray-50 p-6">
            <h4 className="mb-4 text-center font-semibold text-gray-900">
              💰 料金に含まれるもの
            </h4>
            <div className="grid gap-4 text-sm text-gray-600 md:grid-cols-2">
              <ul className="space-y-2">
                <li className="flex items-center">
                  <svg
                    className="mr-2 h-4 w-4 text-green-500"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  教材費
                </li>
                <li className="flex items-center">
                  <svg
                    className="mr-2 h-4 w-4 text-green-500"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  ドリンク（コーヒー・紅茶）
                </li>
              </ul>
              <ul className="space-y-2">
                <li className="flex items-center">
                  <svg
                    className="mr-2 h-4 w-4 text-green-500"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Wi-Fi利用
                </li>
                <li className="flex items-center">
                  <svg
                    className="mr-2 h-4 w-4 text-green-500"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  学習サポート
                </li>
              </ul>
            </div>
          </div>
        </div>
      ),
    },
  ];

  return (
    <section ref={sectionRef} className={cn('bg-gray-50 py-20', className)}>
      <Container>
        <div
          className={cn(
            'mb-12 transform text-center transition-all duration-1000',
            isVisible ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'
          )}
        >
          <h2 className="mb-4 text-3xl font-bold text-gray-900 md:text-4xl">
            サービス概要
          </h2>
          <p className="mx-auto max-w-3xl text-xl text-gray-600">
            あなたに最適な学習スタイルを見つけてください
          </p>
        </div>

        <Tabs
          items={tabItems}
          defaultActiveTab="lessons"
          variant="pills"
          className="mx-auto max-w-6xl"
        />
      </Container>
    </section>
  );
}
