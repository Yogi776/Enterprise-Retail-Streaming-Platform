import { useCallback, useMemo } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";

export interface FilterState {
  dateRange?: { from: string; to: string };
  countries?: string[];
  channels?: string[];
  status?: string[];
  categories?: string[];
  carriers?: string[];
  [key: string]: any;
}

export function useFilters<T extends FilterState = FilterState>() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const filters = useMemo((): T => {
    const params: Record<string, any> = {};
    searchParams.forEach((value, key) => {
      try {
        params[key] = JSON.parse(value);
      } catch {
        params[key] = value;
      }
    });
    return params as T;
  }, [searchParams]);

  const setFilter = useCallback(
    (key: string, value: any) => {
      const params = new URLSearchParams(searchParams.toString());
      if (value === undefined || value === null || value === "") {
        params.delete(key);
      } else if (Array.isArray(value)) {
        params.set(key, JSON.stringify(value));
      } else if (typeof value === "object") {
        params.set(key, JSON.stringify(value));
      } else {
        params.set(key, String(value));
      }
      router.push(`${pathname}?${params.toString()}`, { scroll: false });
    },
    [router, pathname, searchParams]
  );

  const setFilters = useCallback(
    (updates: Partial<T>) => {
      const params = new URLSearchParams(searchParams.toString());
      Object.entries(updates).forEach(([key, value]) => {
        if (value === undefined || value === null || value === "" || (Array.isArray(value) && value.length === 0)) {
          params.delete(key);
        } else if (Array.isArray(value)) {
          params.set(key, JSON.stringify(value));
        } else if (typeof value === "object") {
          params.set(key, JSON.stringify(value));
        } else {
          params.set(key, String(value));
        }
      });
      router.push(`${pathname}?${params.toString()}`, { scroll: false });
    },
    [router, pathname, searchParams]
  );

  const clearFilters = useCallback(() => {
    router.push(pathname, { scroll: false });
  }, [router, pathname]);

  const hasActiveFilters = useMemo(() => {
    return searchParams.toString().length > 0;
  }, [searchParams]);

  return {
    filters,
    setFilter,
    setFilters,
    clearFilters,
    hasActiveFilters,
  };
}