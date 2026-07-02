import { useMemo } from "react";
import { useQuery } from "@apollo/client";
import { LIVE_ORDERS_QUERY } from "@/lib/graphql/queries";
import type { LiveOrdersResponse, LiveOrdersInput } from "@/lib/graphql/types";

const DEFAULT_POLL_INTERVAL = 10_000;  // 10 seconds

export function useLiveOrders(
  input: LiveOrdersInput,
  pollInterval: number = DEFAULT_POLL_INTERVAL
) {
  const { data, loading, error, refetch, startPolling, stopPolling } = useQuery<
    { liveOrders: LiveOrdersResponse }
  >(LIVE_ORDERS_QUERY, {
    variables: { input },
    pollInterval,
    fetchPolicy: "cache-and-network",
  });

  return {
    orders: data?.liveOrders?.orders ?? [],
    totalCount: data?.liveOrders?.totalCount ?? 0,
    summary: data?.liveOrders?.summary ?? null,
    loading,
    error,
    refetch,
  };
}

export function useOrderFilters() {
  const defaultDateRange = useMemo(() => {
    const now = new Date();
    const start = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
    return {
      from: start.toISOString(),
      to: now.toISOString(),
    };
  }, []);

  return {
    defaultDateRange,
    channels: ["POS", "Web", "Mobile", "App"],
    statuses: ["completed", "pending", "failed", "cancelled"],
    countries: ["US", "UK", "DE", "FR", "ES", "IT", "JP", "AU"],
  };
}