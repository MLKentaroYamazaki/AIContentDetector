"use client";

interface Props {
  overallScore: number;
}

function getLabel(score: number): { label: string; color: string; bg: string } {
  if (score >= 75) return { label: "AIによる生成の可能性が高い", color: "text-red-600", bg: "bg-red-50 border-red-200" };
  if (score >= 50) return { label: "AIによる生成の可能性がある", color: "text-orange-500", bg: "bg-orange-50 border-orange-200" };
  if (score >= 25) return { label: "人間が書いた可能性が高い", color: "text-yellow-600", bg: "bg-yellow-50 border-yellow-200" };
  return { label: "人間が書いた可能性が非常に高い", color: "text-green-600", bg: "bg-green-50 border-green-200" };
}

function getStrokeColor(score: number): string {
  if (score >= 75) return "#ef4444";
  if (score >= 50) return "#f97316";
  if (score >= 25) return "#eab308";
  return "#22c55e";
}

export default function ResultCard({ overallScore }: Props) {
  const { label, color, bg } = getLabel(overallScore);
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (overallScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-4 p-6 bg-white border border-gray-200 rounded-2xl shadow-sm">
      <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">AI確信度スコア</h2>
      <div className="relative w-40 h-40">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r={radius} fill="none" stroke="#f1f5f9" strokeWidth="12" />
          <circle
            cx="60" cy="60" r={radius}
            fill="none"
            stroke={getStrokeColor(overallScore)}
            strokeWidth="12"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold text-gray-900">{overallScore}</span>
          <span className="text-sm text-gray-400 font-medium">/ 100</span>
        </div>
      </div>
      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${bg} ${color}`}>
        {label}
      </span>
    </div>
  );
}
