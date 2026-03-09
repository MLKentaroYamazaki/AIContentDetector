import { TodoPriority } from '@/types/todo';

export const STORAGE_KEY = 'todos_app_data';
export const STORAGE_VERSION_KEY = 'todos_version';
export const CURRENT_VERSION = 2;

export const PRIORITY_CONFIG: Record<TodoPriority, {
  label: string;
  icon: string;
  bgColor: string;
  borderColor: string;
  textColor: string;
}> = {
  high: {
    label: '高',
    icon: '🔴',
    bgColor: 'bg-red-50 dark:bg-red-950',
    borderColor: 'border-l-4 border-l-red-500',
    textColor: 'text-red-600 dark:text-red-400',
  },
  medium: {
    label: '中',
    icon: '🟡',
    bgColor: 'bg-yellow-50 dark:bg-yellow-950',
    borderColor: 'border-l-4 border-l-yellow-500',
    textColor: 'text-yellow-600 dark:text-yellow-400',
  },
  low: {
    label: '低',
    icon: '🔵',
    bgColor: 'bg-blue-50 dark:bg-blue-950',
    borderColor: 'border-l-4 border-l-blue-500',
    textColor: 'text-blue-600 dark:text-blue-400',
  },
};
