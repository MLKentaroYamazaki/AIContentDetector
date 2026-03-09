'use client';

import { getDueDateStatus, getRelativeDueDateText, formatDate } from '@/lib/dateHelpers';

interface DueDateBadgeProps {
  dueDate: number | null;
}

export default function DueDateBadge({ dueDate }: DueDateBadgeProps) {
  if (!dueDate) return null;

  const status = getDueDateStatus(dueDate);
  const relativeText = getRelativeDueDateText(dueDate);
  const dateText = formatDate(dueDate);

  const statusStyles = {
    overdue: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300',
    today: 'bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-300',
    upcoming: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    none: '',
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${statusStyles[status]}`}
      title={dateText}
    >
      <span className="mr-1">📅</span>
      {relativeText}
    </span>
  );
}
