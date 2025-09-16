import { render, screen } from '@testing-library/react';
import ApiTestPage from '../app/api-test/page';

describe('ApiTestPage', () => {
  it('renders the main heading', () => {
    render(<ApiTestPage />);

    const heading = screen.getByRole('heading', { name: /api接続テスト/i });
    expect(heading).toBeInTheDocument();
  });

  it('renders the subtitle', () => {
    render(<ApiTestPage />);

    const subtitle = screen.getByText(/Docker Composeでの動作確認用のページです/i);
    expect(subtitle).toBeInTheDocument();
  });

  it('renders test information', () => {
    render(<ApiTestPage />);

    const testHeading = screen.getByRole('heading', { name: /動作確認/i });
    expect(testHeading).toBeInTheDocument();

    const description = screen.getByText(/フロントエンドとバックエンドの接続をテストします。/i);
    expect(description).toBeInTheDocument();
  });

  it('renders technology stack indicators', () => {
    render(<ApiTestPage />);

    expect(screen.getByText(/✅ Next.js 14/)).toBeInTheDocument();
    expect(screen.getByText(/✅ Tailwind CSS/)).toBeInTheDocument();
    expect(screen.getByText(/✅ TypeScript/)).toBeInTheDocument();
    expect(screen.getByText(/✅ Docker Compose/)).toBeInTheDocument();
  });

  it('renders API test link', () => {
    render(<ApiTestPage />);

    const apiLink = screen.getByRole('link', { name: /api接続テスト/i });
    expect(apiLink).toBeInTheDocument();
    expect(apiLink).toHaveAttribute('href', '/api/health');
  });

  it('renders home link', () => {
    render(<ApiTestPage />);

    const homeLink = screen.getByRole('link', { name: /ホームに戻る/i });
    expect(homeLink).toBeInTheDocument();
    expect(homeLink).toHaveAttribute('href', '/');
  });
});