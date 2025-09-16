import { render, screen } from '@testing-library/react';
import HomePage from '../app/page';

describe('HomePage', () => {
  it('renders the main heading', () => {
    render(<HomePage />);

    const heading = screen.getByRole('heading', { name: /english cafe/i });
    expect(heading).toBeInTheDocument();
  });

  it('renders the subtitle', () => {
    render(<HomePage />);

    const subtitle = screen.getByText(/アットホームな雰囲気で英語を学ぼう/i);
    expect(subtitle).toBeInTheDocument();
  });

  it('renders welcome section', () => {
    render(<HomePage />);

    const welcomeHeading = screen.getByRole('heading', { name: /ようこそ/i });
    expect(welcomeHeading).toBeInTheDocument();

    const description = screen.getByText(/英会話カフェで楽しく英語を学びませんか？/i);
    expect(description).toBeInTheDocument();
  });

  it('renders feature list', () => {
    render(<HomePage />);

    expect(screen.getByText(/✅ ネイティブ講師/)).toBeInTheDocument();
    expect(screen.getByText(/✅ カフェスタイル/)).toBeInTheDocument();
    expect(screen.getByText(/✅ 少人数制/)).toBeInTheDocument();
    expect(screen.getByText(/✅ 実践重視/)).toBeInTheDocument();
  });

  it('renders CTA buttons', () => {
    render(<HomePage />);

    const trialButton = screen.getByRole('link', { name: /無料体験レッスンを予約/i });
    expect(trialButton).toBeInTheDocument();
    expect(trialButton).toHaveAttribute('href', '/contact');

    const lessonsButton = screen.getByRole('link', { name: /レッスン詳細を見る/i });
    expect(lessonsButton).toBeInTheDocument();
    expect(lessonsButton).toHaveAttribute('href', '/lessons');
  });

  it('renders API test link', () => {
    render(<HomePage />);

    const apiLink = screen.getByRole('link', { name: /api接続テスト/i });
    expect(apiLink).toBeInTheDocument();
    expect(apiLink).toHaveAttribute('href', '/api-test');
  });
});
