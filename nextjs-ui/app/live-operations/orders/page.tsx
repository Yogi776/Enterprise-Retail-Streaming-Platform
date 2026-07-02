"use client";

import { useState } from "react";
import { useQuery } from "@apollo/client";
import {
  ShoppingCart,
  DollarSign,
  TrendingUp,
  AlertCircle,
  Filter,
  RefreshCw,
  Download,
} from "lucide-react";

import { PageHeader } from "@/components/layout/page-header";
import { KPICard } from "@/components/dashboard/kpi-card";
import { MetricGrid } from "@/components/dashboard/metric-grid";
import { ChartCard } from "@/components/dashboard/chart-card";
import { BarChart } from "@/components/charts/bar-chart";
import { DonutChart } from "@/components/charts/donut-chart";
import { StatusBadge } from "@/components/shared/status-badge";
import { PageSkeleton, ChartSkeleton, TableSkeleton } from "@/components/shared/loading-state";
import { EmptyState, ErrorState } from "@/components/shared/empty-state";
import { useRealtime } from "@/hooks/use-realtime";
import { LIVE_ORDERS_QUERY } from "@/lib/graphql/queries";
import type { LiveOrdersResponse, LiveOrder } from "@/lib/graphql/types";

const CHANNEL_COLORS: Record<string, string> = {
  Web: "#3b82f6",
  Mobile: "#10b981",
  App: "#8b5cf6",
  POS: "#f59e0b",
};

const STATUS_BADGE_VARIANT: Record<string, "success" | "warning" | "error" | "pending"> = {
  completed: "success",
  pending: "pending",
  failed: "error",
  cancelled: "warning",
};

function formatCurrency(amount: number, currency: string) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
  }).format(amount);
}

function formatTime(isoString: string) {
  return new Date(isoString).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

export default function OrdersPage() {
  const { isPaused } = useRealtime();
  const [limit, setLimit] = useState(50);

  const now = new Date();
  const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);

  const { data, loading, error, refetch } = useQuery<{ liveOrders: LiveOrdersResponse }>(
    LIVE_ORDERS_QUERY,
    {
      variables: {
        input: {
          dateRange: {
            from: startOfDay.toISOString(),
            to: now.toISOString(),
          },
          limit,
        },
      },
      pollInterval: isPaused ? 0 : 10_000,
    }
  );

  const payload = data?.liveOrders;

  if (loading && !payload) return <PageSkeleton />;
  if (error) return <ErrorState error={error.message} onRetry={() => refetch()} />;

  if (!payload) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Orders Monitor"
          subtitle="Live order stream — updated every 10 seconds"
          breadcrumbs={[{ label: "Retail" }, { label: "Live Operations" }, { label: "Orders" }]}
        />
        <EmptyState
          title="No orders yet"
          description="Waiting for orders to flow from Kafka → Flink → Iceberg. This typically takes 30-60 seconds."
          action={{ label: "Retry", onClick: () => refetch() }}
        />
      </div>
    );
  }

  const { orders, totalCount, summary } = payload;

  const hourlyData = summary.ordersByChannel.length > 0
    ? summary.ordersByChannel.map((c) => ({
        channel: c.channel,
        Orders: c.count,
      }))
    : [];

  const ordersByStatusData = summary.ordersByStatus.map((s) => ({
    name: s.status.charAt(0).toUpperCase() + s.status.slice(1),
    value: s.count,
  }));

  const failedCount = summary.ordersByStatus.find((s) => s.status === "failed")?.count ?? 0;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Orders Monitor"
        subtitle={`Live order stream — ${totalCount.toLocaleString()} orders today`}
        breadcrumbs={[{ label: "Retail" }, { label: "Live Operations" }, { label: "Orders" }]}
        actions={
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300 hover:bg-slate-700 transition-colors">
              <Filter className="w-4 h-4" />
              Filters
            </button>
            <button className="flex items-center gap-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300 hover:bg-slate-700 transition-colors">
              <Download className="w-4 h-4" />
              Export
            </button>
            <button
              onClick={() => refetch()}
              className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm text-white transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>
        }
      />

      {/* KPI Row */}
      <MetricGrid columns={4}>
        <KPICard
          label="Orders Today"
          value={summary.totalOrders.toLocaleString()}
          trend={summary.totalOrders > 0 ? ((summary.totalOrders / (summary.totalOrders || 1)) * 100 - 100) : 0}
          trendDirection="up"
          icon={ShoppingCart}
        />
        <KPICard
          label="Revenue Today"
          value={`$${(summary.totalRevenue / 1000).toFixed(1)}K`}
          trend={summary.totalRevenue > 0 ? ((summary.totalRevenue / (summary.totalRevenue || 1)) * 100 - 100) : 0}
          trendDirection="up"
          icon={DollarSign}
        />
        <KPICard
          label="Avg Order Value"
          value={`$${summary.avgOrderValue.toFixed(2)}`}
          trend={0}
          trendDirection="flat"
          icon={TrendingUp}
        />
        <KPICard
          label="Failed Orders"
          value={failedCount}
          variant={failedCount > 0 ? "warning" : "default"}
          icon={AlertCircle}
        />
      </MetricGrid>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          {loading ? (
            <ChartSkeleton height={220} />
          ) : (
            <ChartCard title="Orders by Channel" subtitle="Today" height={220}>
              <BarChart
                data={hourlyData}
                xKey="channel"
                yKey="Orders"
                colors={["#3b82f6"]}
              />
            </ChartCard>
          )}
        </div>
        <ChartCard title="Order Status" subtitle="Distribution" height={220}>
          {loading ? (
            <ChartSkeleton height={220} />
          ) : (
            <DonutChart
              data={ordersByStatusData}
              innerRadius={50}
              showLabel
              labelKey="percent"
            />
          )}
        </ChartCard>
      </div>

      {/* Live Orders Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-100">Live Orders</h3>
          <span className="text-xs text-slate-500">{orders.length.toLocaleString()} orders</span>
        </div>

        {loading && orders.length === 0 ? (
          <TableSkeleton rows={8} />
        ) : orders.length === 0 ? (
          <EmptyState
            title="No orders in selected time range"
            description="Try adjusting your filters or date range."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-800 text-left">
                  {["Order ID", "Time", "Customer", "Channel", "Items", "Amount", "Status", "Actions"].map((col) => (
                    <th key={col} className="px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {orders.map((order: LiveOrder) => (
                  <tr
                    key={order.orderId}
                    className="hover:bg-slate-800/50 transition-colors"
                  >
                    <td className="px-4 py-3 text-sm font-mono text-blue-400 cursor-pointer hover:underline">
                      {order.orderId}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-400 font-mono">
                      {formatTime(order.orderTimestamp)}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-200">
                      {order.customerName || order.customerId}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge variant="neutral" size="sm">
                        {order.channel}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-400 text-center">
                      {order.itemCount}
                    </td>
                    <td className="px-4 py-3 text-sm font-medium text-slate-200 text-right">
                      {formatCurrency(order.totalAmount, order.currency)}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge
                        variant={STATUS_BADGE_VARIANT[order.status] ?? "neutral"}
                        size="sm"
                      >
                        {order.status}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-3">
                      <button className="text-xs text-blue-400 hover:text-blue-300 transition-colors">
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}