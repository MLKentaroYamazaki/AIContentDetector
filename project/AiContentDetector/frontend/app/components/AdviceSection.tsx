"use client";

import { Lightbulb } from "lucide-react";

interface Props {
  advice: string;
}

export default function AdviceSection({ advice }: Props) {
  const lines = advice.split("\n").filter((l) => l.trim().length > 0);

  return (
    <div className="p-6 bg-amber-50 border border-amber-200 rounded-2xl">
      <h2 className="flex items-center gap-2 text-lg font-semibold text-amber-800 mb-3">
        <Lightbulb size={20} />
        人間らしく修正するためのアドバイス
      </h2>
      <ul className="flex flex-col gap-2">
        {lines.map((line, i) => (
          <li key={i} className="text-sm text-amber-900 leading-relaxed">
            {line}
          </li>
        ))}
      </ul>
    </div>
  );
}
