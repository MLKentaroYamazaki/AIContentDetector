"use client";

import { Lightbulb } from "lucide-react";

interface Props {
  advice: string;
}

export default function AdviceSection({ advice }: Props) {
  const lines = advice.split("\n").filter((l) => l.trim().length > 0);

  return (
    <div className="p-6 bg-white border border-gray-200 rounded-2xl shadow-sm">
      <h2 className="flex items-center gap-2 text-xs font-semibold text-gray-400 uppercase tracking-wide mb-4">
        <Lightbulb size={14} className="text-indigo-500" />
        改善アドバイス
      </h2>
      <ul className="flex flex-col gap-3">
        {lines.map((line, i) => (
          <li key={i} className="flex gap-3 text-sm text-gray-700 leading-relaxed">
            <span className="flex-shrink-0 w-5 h-5 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
              {i + 1}
            </span>
            <span>{line.replace(/^・/, "")}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
