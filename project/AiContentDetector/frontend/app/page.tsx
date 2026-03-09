"use client";

import { useState } from "react";
import TextInput from "./components/TextInput";
import ResultCard from "./components/ResultCard";
import RadarChart from "./components/RadarChart";
import AdviceSection from "./components/AdviceSection";

interface AnalyzeResult {
  overall_score: number;
  statistical_score: number;
  similarity_score: number;
  breakdown: {
    sentence_variability: number;
    top_k_overlap: number;
  };
  highlighted_sections: { text: string; ai_probability: number }[];
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
    <main className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto flex flex-col gap-8">
        <header className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">AI Content Detector</h1>
          <p className="mt-2 text-gray-500 text-sm">
            テキストが人間によって書かれたものか、AIによって生成されたものかを判定します
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
          <div className="flex flex-col gap-6">
            <ResultCard overallScore={result.overall_score} />
            <RadarChart
              statisticalScore={result.statistical_score}
              sentenceVariability={result.breakdown.sentence_variability}
              punctuationDensity={result.breakdown.top_k_overlap}
            />
            <AdviceSection
              overallScore={result.overall_score}
              sentenceVariability={result.breakdown.sentence_variability}
            />
          </div>
        )}
      </div>
    </main>
  );
}
