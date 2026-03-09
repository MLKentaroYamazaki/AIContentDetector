'use client';

import { useState, useEffect, useCallback } from 'react';
import { nanoid } from 'nanoid';
import { toast } from 'sonner';
import { Todo, TodoPriority } from '@/types/todo';
import { loadTodos, saveTodos } from '@/lib/migration';

export function useTodos() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);

  // 初回マウント時にlocalStorageから読み込み（マイグレーション処理を含む）
  useEffect(() => {
    try {
      const loadedTodos = loadTodos();
      setTodos(loadedTodos);
      setIsInitialized(true);
    } catch (error) {
      console.error('Failed to load todos:', error);
      toast.error('タスクの読み込みに失敗しました');
      setIsInitialized(true);
    }
  }, []);

  // タスクを追加
  const addTodo = useCallback(
    (text: string, priority: TodoPriority = 'medium') => {
      try {
        const newTodo: Todo = {
          id: nanoid(),
          text,
          completed: false,
          priority,
          dueDate: null,
          order: todos.length,
          createdAt: Date.now(),
          updatedAt: Date.now(),
        };
        const newTodos = [...todos, newTodo];
        setTodos(newTodos);
        saveTodos(newTodos);
        toast.success('タスクを追加しました');
      } catch (error) {
        console.error('Failed to add todo:', error);
        toast.error('タスクの追加に失敗しました');
      }
    },
    [todos]
  );

  // タスクを更新
  const updateTodo = useCallback(
    (id: string, updates: Partial<Omit<Todo, 'id' | 'createdAt'>>) => {
      try {
        const newTodos = todos.map((todo) =>
          todo.id === id
            ? { ...todo, ...updates, updatedAt: Date.now() }
            : todo
        );
        setTodos(newTodos);
        saveTodos(newTodos);
      } catch (error) {
        console.error('Failed to update todo:', error);
        toast.error('タスクの更新に失敗しました');
      }
    },
    [todos]
  );

  // タスクを削除
  const deleteTodo = useCallback(
    (id: string) => {
      try {
        const newTodos = todos.filter((todo) => todo.id !== id);
        setTodos(newTodos);
        saveTodos(newTodos);
        toast.success('タスクを削除しました');
      } catch (error) {
        console.error('Failed to delete todo:', error);
        toast.error('タスクの削除に失敗しました');
      }
    },
    [todos]
  );

  // 完了状態を切り替え
  const toggleTodo = useCallback(
    (id: string) => {
      try {
        const todo = todos.find((t) => t.id === id);
        const newTodos = todos.map((t) =>
          t.id === id
            ? { ...t, completed: !t.completed, updatedAt: Date.now() }
            : t
        );
        setTodos(newTodos);
        saveTodos(newTodos);

        if (todo) {
          toast.success(todo.completed ? 'タスクを未完了にしました' : 'タスクを完了しました');
        }
      } catch (error) {
        console.error('Failed to toggle todo:', error);
        toast.error('タスクの更新に失敗しました');
      }
    },
    [todos]
  );

  // タスクのテキストを更新
  const updateTodoText = useCallback(
    (id: string, text: string) => {
      updateTodo(id, { text });
    },
    [updateTodo]
  );

  // 優先度を更新
  const updateTodoPriority = useCallback(
    (id: string, priority: TodoPriority) => {
      updateTodo(id, { priority });
    },
    [updateTodo]
  );

  // 期限を更新
  const updateTodoDueDate = useCallback(
    (id: string, dueDate: number | null) => {
      updateTodo(id, { dueDate });
    },
    [updateTodo]
  );

  // タスクを並び替え
  const reorderTodos = useCallback(
    (activeId: string, overId: string) => {
      try {
        const oldIndex = todos.findIndex((todo) => todo.id === activeId);
        const newIndex = todos.findIndex((todo) => todo.id === overId);

        if (oldIndex === -1 || newIndex === -1) return;

        const newTodos = [...todos];
        const [movedTodo] = newTodos.splice(oldIndex, 1);
        newTodos.splice(newIndex, 0, movedTodo);

        // order フィールドを更新
        const reorderedTodos = newTodos.map((todo, index) => ({
          ...todo,
          order: index,
          updatedAt: Date.now(),
        }));

        setTodos(reorderedTodos);
        saveTodos(reorderedTodos);
      } catch (error) {
        console.error('Failed to reorder todos:', error);
        toast.error('タスクの並び替えに失敗しました');
      }
    },
    [todos]
  );

  return {
    todos,
    isInitialized,
    addTodo,
    updateTodo,
    deleteTodo,
    toggleTodo,
    updateTodoText,
    updateTodoPriority,
    updateTodoDueDate,
    reorderTodos,
  };
}
