'use client';

import { TodoFilter } from '@/types/todo';

interface EmptyStateProps {
  filter: TodoFilter;
}

export default function EmptyState({ filter }: EmptyStateProps) {
  const messages = {
    all: 'タスクがありません',
    active: '進行中のタスクがありません',
    completed: '完了したタスクがありません',
  };

  return (
    <div className="text-center py-12 text-gray-500 dark:text-gray-400">
      <p className="text-lg">{messages[filter]}</p>
    </div>
  );
}
