"use client";

import { Lightbulb } from "lucide-react";

interface Props {
  overallScore: number;
  sentenceVariability: number;
}

function getAdvices(overallScore: number, sentenceVariability: number): string[] {
  const advices: string[] = [];

  if (overallScore < 50) {
    advices.push("テキストは人間らしい特徴を持っています。このまま使用できます。");
    return advices;
  }

  if (sentenceVariability < 0.3) {
    advices.push("文の長さにバラつきを持たせましょう。短い文と長い文を意図的に混ぜてみてください。");
  }
  if (overallScore >= 75) {
    advices.push("体験談や感情表現を加えると、より人間らしい文章になります。");
    advices.push("「〜となっています」「〜の見込みです」などの定型表現を言い換えてみましょう。");
  }
  if (advices.length === 0) {
    advices.push("一部の表現を口語的に書き直すと、より自然な印象になります。");
  }

  return advices;
}

export default function AdviceSection({ overallScore, sentenceVariability }: Props) {
  const advices = getAdvices(overallScore, sentenceVariability);

  return (
    <div className="p-6 bg-amber-50 border border-amber-200 rounded-2xl">
      <h2 className="flex items-center gap-2 text-lg font-semibold text-amber-800 mb-3">
        <Lightbulb size={20} />
        人間らしく修正するためのアドバイス
      </h2>
      <ul className="flex flex-col gap-2">
        {advices.map((advice, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-amber-900">
            <span className="mt-0.5 shrink-0 w-5 h-5 flex items-center justify-center rounded-full bg-amber-300 text-amber-900 font-bold text-xs">
              {i + 1}
            </span>
            {advice}
          </li>
        ))}
      </ul>
    </div>
  );
}
