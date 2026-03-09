import { Todo } from '@/types/todo';
import { STORAGE_KEY, STORAGE_VERSION_KEY, CURRENT_VERSION } from './constants';

interface LegacyTodo {
  id: string;
  text: string;
  completed: boolean;
  createdAt?: number;
}

export function getStorageVersion(): number {
  if (typeof window === 'undefined') return CURRENT_VERSION;

  const version = localStorage.getItem(STORAGE_VERSION_KEY);
  return version ? parseInt(version, 10) : 1;
}

export function setStorageVersion(version: number): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(STORAGE_VERSION_KEY, version.toString());
}

export function migrateTodos(rawData: string | null): Todo[] {
  if (!rawData) return [];

  try {
    const version = getStorageVersion();

    if (version === 1) {
      // v1からv2への移行
      const legacyTodos: LegacyTodo[] = JSON.parse(rawData);
      const migratedTodos: Todo[] = legacyTodos.map((todo, index) => ({
        id: todo.id,
        text: todo.text,
        completed: todo.completed,
        createdAt: todo.createdAt || Date.now(),
        updatedAt: Date.now(),
        priority: 'medium' as const,
        dueDate: null,
        order: index,
      }));

      // 新形式で保存
      if (typeof window !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(migratedTodos));
        setStorageVersion(CURRENT_VERSION);
      }

      return migratedTodos;
    }

    // v2以降はそのまま返す
    return JSON.parse(rawData);
  } catch (error) {
    console.error('Error migrating todos:', error);
    return [];
  }
}

export function loadTodos(): Todo[] {
  if (typeof window === 'undefined') return [];

  const rawData = localStorage.getItem(STORAGE_KEY);
  return migrateTodos(rawData);
}

export function saveTodos(todos: Todo[]): void {
  if (typeof window === 'undefined') return;

  localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
  setStorageVersion(CURRENT_VERSION);
}
