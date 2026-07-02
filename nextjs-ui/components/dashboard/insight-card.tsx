"use client";

import { LucideIcon, Sparkles } from "lucide-react";
import { ReactNode } from "react";

interface InsightCardProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function InsightCard({ icon: Icon = Sparkles, title, description, action }: InsightCardProps) {
  return (
    <div className="bg-slate-900 border-l-4 border-blue-500 rounded-xl p-4">
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
          <Icon className="w-4 h-4 text-blue-400" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <h3 className="text-sm font-semibold text-slate-100">{title}</h3>
            {action && (
              <button
                onClick={action.onClick}
                className="text-xs text-blue-400 hover:text-blue-300 font-medium"
              >
                {action.label}
              </button>
            )}
          </div>
          <p className="text-sm text-slate-400 mt-1 leading-relaxed">{description}</p>
        </div>
      </div>
    </div>
  );
}