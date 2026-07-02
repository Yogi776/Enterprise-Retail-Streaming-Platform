"use client";

export function KPICardSkeleton() {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="h-4 w-20 bg-slate-800 rounded animate-skeleton" />
        <div className="w-8 h-8 rounded-lg bg-slate-800 animate-skeleton" />
      </div>
      <div className="h-8 w-32 bg-slate-800 rounded animate-skeleton mb-2" />
      <div className="h-3 w-16 bg-slate-800 rounded animate-skeleton" />
    </div>
  );
}

export function ChartSkeleton({ height = 300 }: { height?: number }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <div className="h-4 w-32 bg-slate-800 rounded animate-skeleton mb-4" />
      <div style={{ height }} className="flex items-end gap-2">
        {[40, 65, 45, 80, 55, 70, 60, 75, 50, 85].map((h, i) => (
          <div
            key={i}
            className="flex-1 bg-slate-800 rounded-t animate-skeleton"
            style={{ height: `${h}%` }}
          />
        ))}
      </div>
    </div>
  );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      <div className="border-b border-slate-800 p-4">
        <div className="h-4 w-48 bg-slate-800 rounded animate-skeleton" />
      </div>
      <div className="divide-y divide-slate-800">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex items-center gap-4 p-4">
            <div className="h-4 w-24 bg-slate-800 rounded animate-skeleton" />
            <div className="h-4 w-32 bg-slate-800 rounded animate-skeleton" />
            <div className="h-4 w-20 bg-slate-800 rounded animate-skeleton flex-1" />
            <div className="h-4 w-16 bg-slate-800 rounded animate-skeleton" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function PageSkeleton() {
  return (
    <div className="space-y-6">
      <div className="h-8 w-64 bg-slate-800 rounded animate-skeleton" />
      <div className="grid grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <KPICardSkeleton key={i} />
        ))}
      </div>
      <div className="grid grid-cols-2 gap-4">
        <ChartSkeleton />
        <ChartSkeleton />
      </div>
    </div>
  );
}