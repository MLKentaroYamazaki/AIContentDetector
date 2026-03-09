'use client';

import { useState } from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Todo } from '@/types/todo';
import { PRIORITY_CONFIG } from '@/lib/constants';
import TodoText from './TodoText';
import PriorityBadge from './PriorityBadge';
import DueDateBadge from './DueDateBadge';
import PrioritySelector from './PrioritySelector';
import DatePicker from './DatePicker';
import DeleteConfirmModal from './DeleteConfirmModal';

interface TodoItemProps {
  todo: Todo;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onUpdateText: (id: string, text: string) => void;
  onUpdatePriority: (id: string, priority: Todo['priority']) => void;
  onUpdateDueDate: (id: string, dueDate: number | null) => void;
}

export default function TodoItem({
  todo,
  onToggle,
  onDelete,
  onUpdateText,
  onUpdatePriority,
  onUpdateDueDate,
}: TodoItemProps) {
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: todo.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const priorityConfig = PRIORITY_CONFIG[todo.priority];

  const handleDeleteClick = () => {
    setIsDeleteModalOpen(true);
  };

  const handleConfirmDelete = () => {
    onDelete(todo.id);
    setIsDeleteModalOpen(false);
  };

  const handleCancelDelete = () => {
    setIsDeleteModalOpen(false);
  };

  // 優先度に応じた付箋の色
  const stickyColors = {
    high: 'from-pink-100 to-pink-50 dark:from-pink-200 dark:to-pink-100',
    medium: 'from-yellow-100 to-yellow-50 dark:from-yellow-200 dark:to-yellow-100',
    low: 'from-blue-100 to-blue-50 dark:from-blue-200 dark:to-blue-100',
  };

  // ランダムな傾き（IDから生成して一貫性を保つ）
  const rotation = ((parseInt(todo.id.slice(-2), 36) % 5) - 2) * 0.5;

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex flex-col gap-3 p-4 bg-gradient-to-br ${stickyColors[todo.priority]} border-none rounded-md shadow-[4px_4px_10px_rgba(0,0,0,0.15)] hover:shadow-[6px_6px_14px_rgba(0,0,0,0.2)] transition-all duration-200 hover:scale-[1.02] dark:text-gray-900`}
    >
      {/* メイン行：チェックボックス、テキスト、削除ボタン */}
      <div className="flex items-center gap-2 md:gap-3">
        {/* ドラッグハンドル */}
        <span
          {...attributes}
          {...listeners}
          className="cursor-move text-gray-600 hover:text-gray-800 dark:text-gray-700 dark:hover:text-gray-900 touch-none p-2 -ml-2 text-lg md:text-base md:p-0 md:ml-0"
        >
          ⋮⋮
        </span>

        {/* チェックボックス */}
        <input
          type="checkbox"
          checked={todo.completed}
          onChange={() => onToggle(todo.id)}
          className="w-6 h-6 md:w-5 md:h-5 text-amber-600 rounded focus:ring-2 focus:ring-amber-500 cursor-pointer accent-amber-500"
        />

        {/* テキスト */}
        <TodoText
          text={todo.text}
          completed={todo.completed}
          onUpdate={(text) => onUpdateText(todo.id, text)}
        />

        {/* 削除ボタン */}
        <button
          onClick={handleDeleteClick}
          className="px-4 py-2 md:px-3 md:py-1 text-red-700 hover:text-red-900 hover:bg-red-100 dark:hover:bg-red-200 rounded transition-colors font-medium min-w-[44px] min-h-[44px] md:min-w-0 md:min-h-0"
          aria-label="削除"
        >
          ✕
        </button>
      </div>

      {/* 詳細行：優先度、期限 */}
      <div className="flex flex-col md:flex-row md:items-center gap-3 pl-0 md:pl-8">
        <div className="flex items-center gap-2">
          <span className="text-sm md:text-xs text-gray-700 dark:text-gray-800 font-medium">優先度:</span>
          <PrioritySelector
            priority={todo.priority}
            onChange={(priority) => onUpdatePriority(todo.id, priority)}
          />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm md:text-xs text-gray-700 dark:text-gray-800 font-medium">期限:</span>
          <DatePicker
            dueDate={todo.dueDate}
            onChange={(date) => onUpdateDueDate(todo.id, date)}
          />
        </div>

        {/* バッジ */}
        <div className="flex items-center gap-2 md:ml-auto">
          <PriorityBadge priority={todo.priority} />
          <DueDateBadge dueDate={todo.dueDate} />
        </div>
      </div>

      <DeleteConfirmModal
        isOpen={isDeleteModalOpen}
        todoText={todo.text}
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
      />
    </div>
  );
}
