export type TodoPriority = 'high' | 'medium' | 'low';
export type TodoFilter = 'all' | 'active' | 'completed';

export interface Todo {
  id: string;
  text: string;
  completed: boolean;
  createdAt: number;
  updatedAt: number;
  // 拡張フィールド
  priority: TodoPriority;
  dueDate: number | null; // Unix timestamp
  order: number; // ドラッグ&ドロップ用
}
