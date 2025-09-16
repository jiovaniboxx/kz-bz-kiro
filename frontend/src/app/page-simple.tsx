export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="mb-4 text-4xl font-bold text-gray-900">
            English Cafe
          </h1>
          <p className="mb-8 text-xl text-gray-600">
            アットホームな雰囲気で英語を学ぼう
          </p>
          <div className="mx-auto max-w-md rounded-lg bg-white p-8 shadow-md">
            <h2 className="mb-4 text-2xl font-semibold">動作確認</h2>
            <p className="mb-4 text-gray-700">
              Docker Composeでの動作確認用のシンプルなページです。
            </p>
            <div className="space-y-2">
              <p className="text-sm text-gray-500">✅ Next.js 14</p>
              <p className="text-sm text-gray-500">✅ Tailwind CSS</p>
              <p className="text-sm text-gray-500">✅ TypeScript</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
