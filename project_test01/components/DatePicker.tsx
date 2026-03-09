'use client';

import { formatDate } from '@/lib/dateHelpers';

interface DatePickerProps {
  dueDate: number | null;
  onChange: (date: number | null) => void;
}

export default function DatePicker({ dueDate, onChange }: DatePickerProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.value) {
      const date = new Date(e.target.value);
      onChange(date.getTime());
    } else {
      onChange(null);
    }
  };

  const handleClear = () => {
    onChange(null);
  };

  // Unix timestampをYYYY-MM-DD形式に変換
  const dateValue = dueDate ? new Date(dueDate).toISOString().split('T')[0] : '';
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="flex items-center gap-2">
      <input
        type="date"
        value={dateValue}
        min={today}
        onChange={handleChange}
        className="px-3 py-2 md:px-2 md:py-1 text-base md:text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white min-h-[44px] md:min-h-0"
      />
      {dueDate && (
        <button
          onClick={handleClear}
          className="px-3 py-2 md:px-2 md:py-1 text-base md:text-sm text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 min-w-[44px] min-h-[44px] md:min-w-0 md:min-h-0"
          title="期限をクリア"
        >
          ✕
        </button>
      )}
    </div>
  );
}
