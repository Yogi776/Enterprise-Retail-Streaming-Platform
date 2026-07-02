"use client";

export function LiveBadge() {
  return (
    <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-medium">
      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
      Live
    </div>
  );
}

export function PausedBadge() {
  return (
    <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-slate-700 text-slate-400 text-xs font-medium">
      <span className="w-2 h-2 rounded-full bg-slate-500" />
      Paused
    </div>
  );
}