"use client";

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
}

const MAX_CHARS = 5000;

export default function TextInput({ value, onChange, onSubmit, isLoading }: Props) {
  return (
    <div className="flex flex-col gap-3">
      <div className="relative">
        <textarea
          className="w-full h-64 p-4 border border-gray-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800 text-sm"
          placeholder="判定したいテキストを入力してください（最大5,000文字）"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          maxLength={MAX_CHARS}
        />
        <span className="absolute bottom-3 right-3 text-xs text-gray-400">
          {value.length} / {MAX_CHARS}
        </span>
      </div>
      <button
        onClick={onSubmit}
        disabled={isLoading || value.trim().length === 0}
        className="self-end px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? "解析中..." : "AI判定する"}
      </button>
    </div>
  );
}
