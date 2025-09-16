/**
 * Stats Section Component
 * 統計情報を表示するセクション
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import { Container } from '@/components/ui';
import { cn } from '@/utils/cn';

interface StatItem {
  number: number;
  label: string;
  suffix?: string;
  description?: string;
}

const stats: StatItem[] = [
  {
    number: 500,
    suffix: '+',
    label: '満足した生徒数',
    description: '2020年開校以来の累計',
  },
  {
    number: 95,
    suffix: '%',
    label: '継続率',
    description: '3ヶ月以上継続される方の割合',
  },
  {
    number: 8,
    label: 'ネイティブ講師',
    description: '多様な国籍の経験豊富な講師陣',
  },
  {
    number: 4.8,
    suffix: '/5.0',
    label: '平均評価',
    description: 'Google レビューでの評価',
  },
];

interface CountUpProps {
  end: number;
  duration?: number;
  suffix?: string;
  isVisible: boolean;
}

function CountUp({
  end,
  duration = 2000,
  suffix = '',
  isVisible,
}: CountUpProps) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!isVisible) return;

    let startTime: number;
    let animationFrame: number;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);

      // イージング関数（ease-out）
      const easeOut = 1 - Math.pow(1 - progress, 3);
      setCount(Math.floor(end * easeOut));

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [end, duration, isVisible]);

  return (
    <span>
      {count}
      {suffix}
    </span>
  );
}

interface StatsSectionProps {
  className?: string;
}

export function StatsSection({ className }: StatsSectionProps) {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={sectionRef}
      className={cn('bg-primary-600 py-16 text-white', className)}
    >
      <Container>
        <div className="mb-12 text-center">
          <h2 className="mb-4 text-3xl font-bold md:text-4xl">
            数字で見る私たちの実績
          </h2>
          <p className="mx-auto max-w-2xl text-xl text-primary-100">
            多くの生徒さんに選ばれ続けている理由があります
          </p>
        </div>

        <div className="grid grid-cols-2 gap-8 lg:grid-cols-4">
          {stats.map((stat, index) => (
            <div
              key={index}
              className={cn(
                'transform text-center transition-all duration-700',
                isVisible
                  ? 'translate-y-0 opacity-100'
                  : 'translate-y-8 opacity-0'
              )}
              style={{ transitionDelay: `${index * 150}ms` }}
            >
              <div className="mb-4">
                <div className="mb-2 text-4xl font-bold text-white md:text-5xl lg:text-6xl">
                  <CountUp
                    end={stat.number}
                    suffix={stat.suffix}
                    isVisible={isVisible}
                  />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-primary-100 md:text-xl">
                  {stat.label}
                </h3>
                {stat.description && (
                  <p className="text-sm leading-relaxed text-primary-200">
                    {stat.description}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* 装飾要素 */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute left-1/4 top-1/4 h-64 w-64 rounded-full bg-white/5" />
          <div className="absolute bottom-1/4 right-1/4 h-48 w-48 rounded-full bg-white/5" />
        </div>
      </Container>
    </section>
  );
}
