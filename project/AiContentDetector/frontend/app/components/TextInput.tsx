"use client";

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
}

const MAX_CHARS = 5000;

export default function TextInput({ value, onChange, onSubmit, isLoading }: Props) {
  const ratio = value.length / MAX_CHARS;

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 flex flex-col gap-3">
      <div className="relative">
        <textarea
          className="w-full h-52 p-4 border border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent text-gray-800 text-sm leading-relaxed placeholder-gray-400 transition"
          placeholder="判定したいテキストを入力してください（最大5,000文字）"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          maxLength={MAX_CHARS}
        />
        <span className={`absolute bottom-3 right-3 text-xs ${ratio > 0.9 ? "text-red-400" : "text-gray-400"}`}>
          {value.length} / {MAX_CHARS}
        </span>
      </div>
      <div className="flex items-center justify-between">
        <p className="text-xs text-gray-400">統計解析 + Claude API による類似度スコアで判定</p>
        <button
          onClick={onSubmit}
          disabled={isLoading || value.trim().length === 0}
          className="px-6 py-2 bg-indigo-600 text-white rounded-xl font-medium text-sm hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-sm"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              解析中...
            </span>
          ) : "AI判定する"}
        </button>
      </div>
    </div>
  );
}
