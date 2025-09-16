import { ReviewsSection } from '@/components/sections/ReviewsSection';
import { CTASection } from '@/components/sections/CTASection';
import { Container } from '@/components/ui';

export default function ReviewsPage() {
  return (
    <main>
      {/* ページヘッダー */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-700 py-16 text-white">
        <Container>
          <div className="text-center">
            <h1 className="mb-4 text-4xl font-bold md:text-5xl">
              生徒さんの声
            </h1>
            <p className="mx-auto max-w-2xl text-xl text-primary-100">
              実際に通われている生徒さんからの生の声と評価をご覧ください
            </p>
          </div>
        </Container>
      </section>

      {/* レビュー一覧 */}
      <ReviewsSection showAll={true} />

      {/* CTA */}
      <CTASection
        variant="primary"
        title="あなたも英会話を始めませんか？"
        description="多くの生徒さんに選ばれている理由を、無料体験レッスンで実感してください。きっとあなたも満足していただけるはずです。"
        primaryButtonText="無料体験レッスンを予約"
        secondaryButtonText="お問い合わせ"
      />
    </main>
  );
}
