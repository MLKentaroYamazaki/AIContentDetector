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
      <h2 className="text-lg font-semibold text-gray-700 mb-4">分析内訳</h2>
      <ResponsiveContainer width="100%" height={240}>
        <RechartsRadar data={data} outerRadius="70%">
          <PolarGrid />
          <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12 }} />
          <Tooltip />
          <Radar dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
        </RechartsRadar>
      </ResponsiveContainer>
    </div>
  );
}
