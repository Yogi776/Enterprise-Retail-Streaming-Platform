"use client";

import { LucideIcon, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils/cn";

interface KPICardProps {
  label: string;
  value: string | number;
  unit?: string;
  trend?: number;
  trendDirection?: "up" | "down" | "flat";
  variant?: "default" | "success" | "warning" | "critical";
  icon?: LucideIcon;
  isLoading?: boolean;
  lastUpdated?: string;
}

export function KPICard({
  label,
  value,
  unit,
  trend,
  trendDirection = "flat",
  variant = "default",
  icon: Icon,
  isLoading = false,
}: KPICardProps) {
  const variantClasses = {
    default: "border-slate-700",
    success: "border-emerald-500/30 bg-emerald-500/5",
    warning: "border-amber-500/30 bg-amber-500/5",
    critical: "border-red-500/30 bg-red-500/5",
  };

  const valueColorClasses = {
    default: "text-slate-100",
    success: "text-emerald-400",
    warning: "text-amber-400",
    critical: "text-red-400",
  };

  const trendColorClasses = {
    up: "text-emerald-400",
    down: "text-red-400",
    flat: "text-slate-400",
  };

  if (isLoading) {
    return (
      <div className={cn("bg-slate-900 border rounded-xl p-4", variantClasses.default)}>
        <div className="flex items-center justify-between mb-3">
          <div className="h-4 w-20 bg-slate-800 rounded animate-skeleton" />
        </div>
        <div className="h-8 w-32 bg-slate-800 rounded animate-skeleton mb-2" />
        <div className="h-3 w-16 bg-slate-800 rounded animate-skeleton" />
      </div>
    );
  }

  return (
    <div
      className={cn(
        "bg-slate-900 border rounded-xl p-4 hover:shadow-md transition-shadow duration-200",
        variantClasses[variant]
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-slate-400">{label}</span>
        {Icon && (
          <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center">
            <Icon className="w-4 h-4 text-slate-400" />
          </div>
        )}
      </div>

      {/* Value */}
      <div className="flex items-baseline gap-1.5 mb-1">
        <span className={cn("text-2xl font-bold", valueColorClasses[variant])}>
          {typeof value === "number" ? value.toLocaleString() : value}
        </span>
        {unit && <span className="text-sm text-slate-500">{unit}</span>}
      </div>

      {/* Trend */}
      {trend !== undefined && (
        <div className="flex items-center gap-1">
          {trendDirection === "up" && <TrendingUp className="w-3 h-3 text-emerald-400" />}
          {trendDirection === "down" && <TrendingDown className="w-3 h-3 text-red-400" />}
          {trendDirection === "flat" && <Minus className="w-3 h-3 text-slate-400" />}
          <span className={cn("text-xs font-medium", trendColorClasses[trendDirection])}>
            {trend > 0 ? "+" : ""}{trend.toFixed(1)}%
          </span>
          <span className="text-xs text-slate-500">vs yesterday</span>
        </div>
      )}
    </div>
  );
}