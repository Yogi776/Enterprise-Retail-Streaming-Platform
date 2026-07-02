"use client";

import { ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

type BadgeVariant = "success" | "warning" | "error" | "pending" | "info" | "neutral";

interface StatusBadgeProps {
  variant?: BadgeVariant;
  children: ReactNode;
  size?: "sm" | "md" | "lg";
}

export function StatusBadge({
  variant = "neutral",
  children,
  size = "md",
}: StatusBadgeProps) {
  const variantClasses: Record<BadgeVariant, string> = {
    success: "bg-emerald-100 text-emerald-700 border-emerald-200",
    warning: "bg-amber-100 text-amber-700 border-amber-200",
    error: "bg-red-100 text-red-700 border-red-200",
    pending: "bg-slate-100 text-slate-700 border-slate-200",
    info: "bg-blue-100 text-blue-700 border-blue-200",
    neutral: "bg-slate-100 text-slate-700 border-slate-200",
  };

  const sizeClasses = {
    sm: "text-xs px-1.5 py-0.5",
    md: "text-xs px-2 py-0.5",
    lg: "text-sm px-2.5 py-1",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center font-medium rounded-full border",
        variantClasses[variant],
        sizeClasses[size]
      )}
    >
      {children}
    </span>
  );
}