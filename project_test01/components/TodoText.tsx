'use client';

import { useState, useEffect, useRef } from 'react';

interface TodoTextProps {
  text: string;
  completed: boolean;
  onUpdate: (text: string) => void;
}

export default function TodoText({ text, completed, onUpdate }: TodoTextProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(text);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleSave = () => {
    const trimmed = editValue.trim();
    if (trimmed && trimmed !== text) {
      onUpdate(trimmed);
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditValue(text);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      handleCancel();
    }
  };

  if (isEditing) {
    return (
      <input
        ref={inputRef}
        type="text"
        value={editValue}
        onChange={(e) => setEditValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onBlur={handleSave}
        className="flex-1 px-2 py-1 border border-blue-500 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
      />
    );
  }

  return (
    <span
      onClick={() => !completed && setIsEditing(true)}
      className={`flex-1 cursor-pointer ${
        completed
          ? 'line-through text-gray-400 dark:text-gray-500'
          : 'text-gray-800 dark:text-gray-200'
      }`}
    >
      {text}
    </span>
  );
}
