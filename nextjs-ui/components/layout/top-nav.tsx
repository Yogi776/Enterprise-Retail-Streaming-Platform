"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Search, Calendar, Bell, User, Moon, Sun, RefreshCw, ChevronDown } from "lucide-react";
import { useRealtime } from "@/hooks/use-realtime";
import { useTimeAgo } from "@/hooks/use-realtime";

interface TopNavProps {
  user?: {
    name: string;
    email: string;
    avatar?: string;
    role: string;
  };
}

export function TopNav({ user }: TopNavProps) {
  const router = useRouter();
  const { isPaused, toggle: toggleRealtime, lastUpdated, pollInterval } = useRealtime();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [isDarkMode, setIsDarkMode] = useState(true);

  const timeAgo = useTimeAgo(lastUpdated);

  const handleSearch = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
      setSearchQuery("");
      setIsSearchOpen(false);
    }
  }, [searchQuery, router]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "k") {
      e.preventDefault();
      setIsSearchOpen(true);
    }
    if (e.key === "Escape") {
      setIsSearchOpen(false);
    }
  }, []);

  const toggleTheme = useCallback(() => {
    setIsDarkMode((prev) => !prev);
    document.documentElement.classList.toggle("dark");
  }, []);

  return (
    <header
      className="flex items-center h-16 px-6 bg-slate-900 border-b border-slate-800 gap-4"
      onKeyDown={handleKeyDown}
    >
      {/* Breadcrumb placeholder (filled by page) */}
      <div className="flex items-center gap-2 text-sm text-slate-400 flex-shrink-0">
        <span>Retail</span>
        <ChevronDown className="w-3 h-3 rotate-[-90deg]" />
      </div>

      {/* Search Bar */}
      <div className="flex-1 max-w-xl">
        <form onSubmit={handleSearch} className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search orders, customers, products... (⌘K)"
            className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            onFocus={() => setIsSearchOpen(true)}
          />
        </form>
      </div>

      {/* Date Range Quick Pick */}
      <button className="flex items-center gap-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300 hover:bg-slate-700 transition-colors">
        <Calendar className="w-4 h-4" />
        <span>Today</span>
      </button>

      {/* Last Updated + Refresh */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-slate-500">
          {lastUpdated ? `Updated ${timeAgo}` : "Not updated"}
        </span>
        <button
          onClick={toggleRealtime}
          className={`p-2 rounded-lg transition-colors ${
            isPaused
              ? "bg-amber-500/20 text-amber-400 hover:bg-amber-500/30"
              : "bg-slate-800 text-slate-400 hover:bg-slate-700"
          }`}
          title={isPaused ? "Resume updates" : "Pause updates"}
        >
          <RefreshCw className={`w-4 h-4 ${isPaused ? "" : "animate-spin"}`} style={{ animationDuration: "3s" }} />
        </button>
      </div>

      {/* Live Indicator */}
      <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${
        isPaused
          ? "bg-slate-800 text-slate-500"
          : "bg-emerald-500/20 text-emerald-400"
      }`}>
        <span className={`w-2 h-2 rounded-full ${
          isPaused ? "bg-slate-500" : "bg-emerald-400 animate-pulse"
        }`} />
        {isPaused ? "Paused" : "Live"}
      </div>

      {/* Theme Toggle */}
      <button
        onClick={toggleTheme}
        className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200 transition-colors"
      >
        {isDarkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
      </button>

      {/* Notifications */}
      <button className="relative p-2 rounded-lg bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200 transition-colors">
        <Bell className="w-4 h-4" />
        <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
      </button>

      {/* User Avatar */}
      <button className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-slate-800 transition-colors">
        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
          <User className="w-4 h-4 text-white" />
        </div>
        <div className="text-left hidden sm:block">
          <p className="text-sm font-medium text-slate-200">{user?.name || "Data Engineer"}</p>
          <p className="text-xs text-slate-500">{user?.role || "Admin"}</p>
        </div>
      </button>
    </header>
  );
}