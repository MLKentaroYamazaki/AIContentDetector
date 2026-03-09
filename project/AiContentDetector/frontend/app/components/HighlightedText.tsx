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
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">文章解析</h2>
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-3 h-3 rounded bg-red-100 border-b-2 border-red-400" />
            AI確率 75%+
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-3 h-3 rounded bg-orange-50 border-b-2 border-orange-300" />
            50〜74%
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-3 h-3 rounded bg-gray-100 border border-gray-200" />
            人間らしい
          </span>
        </div>
      </div>
      <div className="text-sm leading-8 text-gray-800">
        {sections.map((section, i) => (
          <span
            key={i}
            className={`rounded px-0.5 ${probabilityToColor(section.ai_probability)}`}
            title={`AI確率: ${Math.round(section.ai_probability * 100)}%`}
          >
            {section.text}
          </span>
        ))}
      </div>
    </div>
  );
}
