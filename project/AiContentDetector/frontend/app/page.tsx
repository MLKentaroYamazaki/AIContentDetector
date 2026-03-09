"use client";

import { useState } from "react";
import TextInput from "./components/TextInput";
import ResultCard from "./components/ResultCard";
import RadarChart from "./components/RadarChart";
import AdviceSection from "./components/AdviceSection";
import HighlightedText from "./components/HighlightedText";

interface AnalyzeResult {
  overall_score: number;
  statistical_score: number;
  similarity_score: number;
  breakdown: {
    sentence_variability: number;
    top_k_overlap: number;
  };
  highlighted_sections: { text: string; ai_probability: number }[];
  advice: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/v1/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: text }),
      });
      if (!res.ok) throw new Error(`サーバーエラー: ${res.status}`);
      setResult(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "不明なエラーが発生しました");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 py-12 px-4">
      <div className="max-w-3xl mx-auto flex flex-col gap-8">

        <header className="text-center">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-indigo-600 rounded-2xl mb-4 shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 tracking-tight">AI Content Detector</h1>
          <p className="mt-2 text-gray-500 text-sm">
            テキストが人間によって書かれたものかAIによって生成されたものかを、AIが判定します
          </p>
        </header>

        <TextInput
          value={text}
          onChange={setText}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
            {error}
          </div>
        )}

        {result && (
          <div className="flex flex-col gap-5">
            <div className="grid grid-cols-2 gap-5">
              <ResultCard overallScore={result.overall_score} />
              <RadarChart
                statisticalScore={result.statistical_score}
                sentenceVariability={result.breakdown.sentence_variability}
                punctuationDensity={result.breakdown.top_k_overlap}
              />
            </div>
            <HighlightedText sections={result.highlighted_sections} />
            <AdviceSection advice={result.advice} />
          </div>
        )}

      </div>
    </main>
  );
}
