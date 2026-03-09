"use client";

import {
  RadarChart as RechartsRadar,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface Props {
  statisticalScore: number;
  sentenceVariability: number;
  punctuationDensity: number;
}

export default function RadarChart({ statisticalScore, sentenceVariability, punctuationDensity }: Props) {
  const data = [
    { subject: "統計スコア", value: statisticalScore },
    { subject: "文長ばらつき", value: Math.round((1 - sentenceVariability) * 100) },
    { subject: "句読点密度", value: Math.round(punctuationDensity * 1000) },
  ];

  return (
    <div className="p-6 bg-white border border-gray-200 rounded-2xl shadow-sm">
      <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-4">分析内訳</h2>
      <ResponsiveContainer width="100%" height={220}>
        <RechartsRadar data={data} outerRadius="70%">
          <PolarGrid stroke="#e2e8f0" />
          <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: "#64748b" }} />
          <Tooltip
            contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }}
            formatter={(value: number) => [`${value}`, "スコア"]}
          />
          <Radar dataKey="value" stroke="#6366f1" fill="#6366f1" fillOpacity={0.25} />
        </RechartsRadar>
      </ResponsiveContainer>
    </div>
  );
}
