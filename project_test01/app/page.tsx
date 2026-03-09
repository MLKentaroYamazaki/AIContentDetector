import TodoApp from '@/components/TodoApp';
import ThemeToggle from '@/components/ThemeToggle';

export default function Home() {
  return (
    <main className="min-h-screen py-6 md:py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* ヘッダー */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6 md:mb-8">
          <h1 className="text-2xl md:text-4xl font-bold text-gray-800 dark:text-white">
            シンプル TODO アプリ
          </h1>
          <ThemeToggle />
        </div>

        {/* メインアプリ */}
        <TodoApp />
      </div>
    </main>
  );
}
