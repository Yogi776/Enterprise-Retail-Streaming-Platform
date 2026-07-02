"use client";

import { ReactNode } from "react";

interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  actions?: ReactNode;
  height?: number;
  isLoading?: boolean;
}

export function ChartCard({
  title,
  subtitle,
  children,
  actions,
  height = 300,
}: ChartCardProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-slate-100">{title}</h3>
          {subtitle && (
            <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>
          )}
        </div>
        {actions && (
          <div className="flex items-center gap-2">
            {actions}
          </div>
        )}
      </div>

      {/* Chart */}
      <div style={{ height }}>
        {children}
      </div>
    </div>
  );
}