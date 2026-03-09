'use client';

import { TodoFilter } from '@/types/todo';

interface TodoFiltersProps {
  filter: TodoFilter;
  onFilterChange: (filter: TodoFilter) => void;
  stats: {
    total: number;
    active: number;
    completed: number;
  };
}

export default function TodoFilters({ filter, onFilterChange, stats }: TodoFiltersProps) {
  const buttons: { label: string; value: TodoFilter; count: number }[] = [
    { label: 'すべて', value: 'all', count: stats.total },
    { label: '進行中', value: 'active', count: stats.active },
    { label: '完了', value: 'completed', count: stats.completed },
  ];

  return (
    <div className="flex flex-wrap gap-2 my-4">
      {buttons.map((btn) => (
        <button
          key={btn.value}
          onClick={() => onFilterChange(btn.value)}
          className={`flex-1 sm:flex-none px-4 py-2.5 md:py-2 rounded-lg font-medium transition-colors text-sm md:text-base min-h-[44px] ${
            filter === btn.value
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
          }`}
        >
          {btn.label} ({btn.count})
        </button>
      ))}
    </div>
  );
}
