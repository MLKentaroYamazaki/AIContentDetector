'use client';

import { TodoPriority } from '@/types/todo';
import { PRIORITY_CONFIG } from '@/lib/constants';

interface PriorityBadgeProps {
  priority: TodoPriority;
}

export default function PriorityBadge({ priority }: PriorityBadgeProps) {
  const config = PRIORITY_CONFIG[priority];

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${config.textColor}`}
    >
      <span className="mr-1">{config.icon}</span>
      {config.label}
    </span>
  );
}
