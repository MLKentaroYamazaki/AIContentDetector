"use client";

interface Props {
  overallScore: number;
}

function getLabel(score: number): { label: string; color: string } {
  if (score >= 75) return { label: "AIによる生成の可能性が高い", color: "text-red-600" };
  if (score >= 50) return { label: "AIによる生成の可能性がある", color: "text-orange-500" };
  if (score >= 25) return { label: "人間が書いた可能性が高い", color: "text-yellow-600" };
  return { label: "人間が書いた可能性が非常に高い", color: "text-green-600" };
}

export default function ResultCard({ overallScore }: Props) {
  const { label, color } = getLabel(overallScore);
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (overallScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-4 p-6 bg-white border border-gray-200 rounded-2xl shadow-sm">
      <h2 className="text-lg font-semibold text-gray-700">AI確信度</h2>
      <div className="relative w-36 h-36">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r={radius} fill="none" stroke="#e5e7eb" strokeWidth="10" />
          <circle
            cx="60" cy="60" r={radius}
            fill="none"
            stroke={overallScore >= 50 ? "#ef4444" : "#22c55e"}
            strokeWidth="10"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-3xl font-bold text-gray-800">
          {overallScore}%
        </span>
      </div>
      <p className={`text-sm font-medium ${color}`}>{label}</p>
    </div>
  );
}
