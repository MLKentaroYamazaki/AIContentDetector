'use client';

import { useMemo } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { Todo } from '@/types/todo';
import TodoItem from './TodoItem';
import EmptyState from './EmptyState';
import { TodoFilter } from '@/types/todo';

interface TodoListProps {
  todos: Todo[];
  filter: TodoFilter;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onUpdateText: (id: string, text: string) => void;
  onUpdatePriority: (id: string, priority: Todo['priority']) => void;
  onUpdateDueDate: (id: string, dueDate: number | null) => void;
  onReorder?: (activeId: string, overId: string) => void;
}

export default function TodoList({
  todos,
  filter,
  onToggle,
  onDelete,
  onUpdateText,
  onUpdatePriority,
  onUpdateDueDate,
  onReorder,
}: TodoListProps) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // order フィールドでソート（useMemoでメモ化）
  const sortedTodos = useMemo(
    () => [...todos].sort((a, b) => a.order - b.order),
    [todos]
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id && onReorder) {
      onReorder(active.id as string, over.id as string);
    }
  };

  if (todos.length === 0) {
    return <EmptyState filter={filter} />;
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
    >
      <SortableContext
        items={sortedTodos.map((todo) => todo.id)}
        strategy={verticalListSortingStrategy}
      >
        <div className="space-y-2">
          {sortedTodos.map((todo) => (
            <TodoItem
              key={todo.id}
              todo={todo}
              onToggle={onToggle}
              onDelete={onDelete}
              onUpdateText={onUpdateText}
              onUpdatePriority={onUpdatePriority}
              onUpdateDueDate={onUpdateDueDate}
            />
          ))}
        </div>
      </SortableContext>
    </DndContext>
  );
}
