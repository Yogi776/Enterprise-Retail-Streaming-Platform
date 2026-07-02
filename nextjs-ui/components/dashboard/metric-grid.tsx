"use client";

import { KPICard } from "./kpi-card";

interface MetricGridProps {
  children: React.ReactNode;
  columns?: 2 | 3 | 4;
}

export function MetricGrid({ children, columns = 4 }: MetricGridProps) {
  const gridClasses = {
    2: "grid-cols-1 md:grid-cols-2",
    3: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
    4: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-4",
  };

  return (
    <div className={`grid ${gridClasses[columns]} gap-4`}>
      {children}
    </div>
  );
}