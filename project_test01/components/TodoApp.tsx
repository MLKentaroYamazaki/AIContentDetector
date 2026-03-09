'use client';

import { useState, useMemo } from 'react';
import { TodoFilter } from '@/types/todo';
import { useTodos } from '@/hooks/useTodos';
import TodoInput from './TodoInput';
import TodoFilters from './TodoFilters';
import TodoList from './TodoList';

export default function TodoApp() {
  const {
    todos,
    isInitialized,
    addTodo,
    deleteTodo,
    toggleTodo,
    updateTodoText,
    updateTodoPriority,
    updateTodoDueDate,
    reorderTodos,
  } = useTodos();

  const [filter, setFilter] = useState<TodoFilter>('all');

  // フィルター済みのTODOリスト
  const filteredTodos = useMemo(() => {
    switch (filter) {
      case 'active':
        return todos.filter((todo) => !todo.completed);
      case 'completed':
        return todos.filter((todo) => todo.completed);
      default:
        return todos;
    }
  }, [todos, filter]);

  // 統計（1回のループで計算）
  const stats = useMemo(() =>
    todos.reduce(
      (acc, todo) => ({
        total: acc.total + 1,
        active: acc.active + (todo.completed ? 0 : 1),
        completed: acc.completed + (todo.completed ? 1 : 0),
      }),
      { total: 0, active: 0, completed: 0 }
    ),
    [todos]
  );

  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-gray-500 dark:text-gray-400">読み込み中...</div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      <TodoInput onAdd={addTodo} />

      <TodoFilters
        filter={filter}
        onFilterChange={setFilter}
        stats={stats}
      />

      <TodoList
        todos={filteredTodos}
        filter={filter}
        onToggle={toggleTodo}
        onDelete={deleteTodo}
        onUpdateText={updateTodoText}
        onUpdatePriority={updateTodoPriority}
        onUpdateDueDate={updateTodoDueDate}
        onReorder={reorderTodos}
      />
    </div>
  );
}
