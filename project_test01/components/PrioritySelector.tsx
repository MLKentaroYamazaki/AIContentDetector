'use client';

import { TodoPriority } from '@/types/todo';
import { PRIORITY_CONFIG } from '@/lib/constants';

interface PrioritySelectorProps {
  priority: TodoPriority;
  onChange: (priority: TodoPriority) => void;
}

export default function PrioritySelector({ priority, onChange }: PrioritySelectorProps) {
  return (
    <select
      value={priority}
      onChange={(e) => onChange(e.target.value as TodoPriority)}
      className="px-3 py-2 md:px-2 md:py-1 text-base md:text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white min-h-[44px] md:min-h-0"
    >
      {(Object.keys(PRIORITY_CONFIG) as TodoPriority[]).map((p) => (
        <option key={p} value={p}>
          {PRIORITY_CONFIG[p].icon} {PRIORITY_CONFIG[p].label}
        </option>
      ))}
    </select>
  );
}
