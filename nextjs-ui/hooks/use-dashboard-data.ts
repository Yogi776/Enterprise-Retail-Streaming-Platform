import { useState, useEffect, useCallback, useRef } from "react";
import { useQuery, QueryResult } from "@apollo/client";

interface UsePollingOptions<T> {
  query: any;
  variables: Record<string, any>;
  pollInterval: number;  // milliseconds
  enabled?: boolean;
}

export function usePolling<T = any>({
  query,
  variables,
  pollInterval,
  enabled = true,
}: UsePollingOptions<T>): QueryResult<T> {
  const result = useQuery<T>(query, {
    variables,
    pollInterval: enabled ? pollInterval : 0,
    fetchPolicy: "cache-and-network",
    nextFetchPolicy: "network-only",
    notifyOnNetworkStatusChange: true,
  });

  return result;
}

export function useDashboardRefresh(
  pollInterval: number = 10_000
) {
  const [isPaused, setIsPaused] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const pauseRef = useRef(false);

  const pause = useCallback(() => {
    setIsPaused(true);
    pauseRef.current = true;
  }, []);

  const resume = useCallback(() => {
    setIsPaused(false);
    pauseRef.current = false;
  }, []);

  const toggle = useCallback(() => {
    if (pauseRef.current) {
      resume();
    } else {
      pause();
    }
  }, [pause, resume]);

  const markUpdated = useCallback(() => {
    setLastUpdated(new Date());
  }, []);

  const effectivePollInterval = isPaused ? 0 : pollInterval;

  return {
    isPaused,
    lastUpdated,
    pause,
    resume,
    toggle,
    markUpdated,
    effectivePollInterval,
    pollInterval,
  };
}

export function useTimeAgo(lastUpdated: Date | null): string {
  const [, setTick] = useState(0);

  useEffect(() => {
    if (!lastUpdated) return;

    const interval = setInterval(() => {
      setTick((t) => t + 1);
    }, 10_000);  // Update every 10 seconds

    return () => clearInterval(interval);
  }, [lastUpdated]);

  if (!lastUpdated) return "Never";

  const seconds = Math.floor((Date.now() - lastUpdated.getTime()) / 1000);

  if (seconds < 5) return "Just now";
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  return `${Math.floor(seconds / 3600)}h ago`;
}