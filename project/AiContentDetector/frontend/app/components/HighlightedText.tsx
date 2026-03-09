"use client";

interface Section {
  text: string;
  ai_probability: number;
}

interface Props {
  sections: Section[];
}

function probabilityToColor(prob: number): string {
  if (prob >= 0.75) return "bg-red-200 border-b-2 border-red-400";
  if (prob >= 0.5) return "bg-orange-100 border-b-2 border-orange-300";
  return "";
}

export default function HighlightedText({ sections }: Props) {
  if (sections.length === 0) return null;

  return (
    <div className="p-6 bg-white border border-gray-200 rounded-2xl shadow-sm">
      <h2 className="text-lg font-semibold text-gray-700 mb-3">テキスト解析</h2>
      <div className="flex flex-wrap gap-x-1 gap-y-1 text-sm leading-7 text-gray-800">
        {sections.map((section, i) => (
          <span
            key={i}
            className={`px-0.5 rounded ${probabilityToColor(section.ai_probability)}`}
            title={`AI確率: ${Math.round(section.ai_probability * 100)}%`}
          >
            {section.text}
          </span>
        ))}
      </div>
      <div className="mt-3 flex items-center gap-4 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded bg-red-200 border-b-2 border-red-400" />
          AI確率 75%+
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded bg-orange-100 border-b-2 border-orange-300" />
          AI確率 50〜74%
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded bg-white border border-gray-200" />
          人間らしい
        </span>
      </div>
    </div>
  );
}
