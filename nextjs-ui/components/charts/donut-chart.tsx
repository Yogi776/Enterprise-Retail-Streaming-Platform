"use client";

import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { cn } from "@/lib/utils/cn";

interface PieChartProps {
  data: { name: string; value: number; color?: string }[];
  title?: string;
  height?: number;
  innerRadius?: number;
  showLabel?: boolean;
  labelKey?: "name" | "value" | "percent";
  colors?: string[];
  className?: string;
}

const DEFAULT_COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16"];

export function DonutChart({
  data,
  height = 300,
  innerRadius = 60,
  showLabel = false,
  labelKey = "percent",
  colors = DEFAULT_COLORS,
  className,
}: PieChartProps) {
  const total = data.reduce((sum, item) => sum + item.value, 0);

  const renderLabel = (props: any) => {
    if (!showLabel) return null;
    const { name, value, percent } = props;
    if (labelKey === "name") return name;
    if (labelKey === "value") return value.toLocaleString();
    if (labelKey === "percent") return `${(percent * 100).toFixed(1)}%`;
    return null;
  };

  return (
    <div className={cn("", className)} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsPieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={innerRadius}
            outerRadius={100}
            paddingAngle={2}
            dataKey="value"
            label={renderLabel}
            labelLine={false}
          >
            {data.map((entry, index) => (
              <Cell
                key={entry.name}
                fill={entry.color || colors[index % colors.length]}
                stroke="transparent"
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "#0f172a",
              border: "1px solid #334155",
              borderRadius: "8px",
              color: "#e2e8f0",
            }}
            formatter={(value: number) => [
              `${value.toLocaleString()} (${((value / total) * 100).toFixed(1)}%)`,
              "Count",
            ]}
          />
          <Legend
            formatter={(value) => (
              <span className="text-xs text-slate-400">{value}</span>
            )}
          />
        </RechartsPieChart>
      </ResponsiveContainer>
    </div>
  );
}

export function PieChart(props: Omit<PieChartProps, "innerRadius">) {
  return <DonutChart {...props} innerRadius={0} />;
}