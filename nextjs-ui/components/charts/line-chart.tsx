"use client";

import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { cn } from "@/lib/utils/cn";

interface LineChartProps {
  data: Record<string, any>[];
  xKey: string;
  yKey: string | string[];
  title?: string;
  height?: number;
  showGrid?: boolean;
  showTooltip?: boolean;
  showLegend?: boolean;
  comparisonData?: Record<string, any>[];
  comparisonKey?: string;
  referenceLine?: { y: number; label: string };
  colors?: string[];
  className?: string;
}

const DEFAULT_COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"];

export function LineChart({
  data,
  xKey,
  yKey,
  height = 300,
  showGrid = true,
  showTooltip = true,
  showLegend = true,
  referenceLine,
  colors = DEFAULT_COLORS,
  className,
}: LineChartProps) {
  const yKeys = Array.isArray(yKey) ? yKey : [yKey];

  return (
    <div className={cn("", className)} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsLineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          {showGrid && (
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          )}
          <XAxis
            dataKey={xKey}
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: "#334155" }}
          />
          <YAxis
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            tickLine={false}
            axisLine={false}
            width={50}
          />
          {showTooltip && (
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                border: "1px solid #334155",
                borderRadius: "8px",
                color: "#e2e8f0",
              }}
              labelStyle={{ color: "#e2e8f0" }}
            />
          )}
          {showLegend && (
            <Legend
              wrapperStyle={{ paddingTop: "10px" }}
              formatter={(value) => (
                <span className="text-xs text-slate-400">{value}</span>
              )}
            />
          )}
          {referenceLine && (
            <ReferenceLine
              y={referenceLine.y}
              stroke="#ef4444"
              strokeDasharray="5 5"
              label={{
                value: referenceLine.label,
                fill: "#ef4444",
                fontSize: 11,
                position: "right",
              }}
            />
          )}
          {yKeys.map((key, index) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={colors[index % colors.length]}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: colors[index % colors.length] }}
            />
          ))}
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
  );
}