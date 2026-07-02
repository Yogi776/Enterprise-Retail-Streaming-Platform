"use client";

import { useMemo } from "react";
import { useQuery } from "@apollo/client";
import {
  DollarSign,
  ShoppingCart,
  TrendingUp,
  CreditCard,
  AlertTriangle,
  Users,
  Truck,
  Package,
} from "lucide-react";

import { PageHeader } from "@/components/layout/page-header";
import { KPICard } from "@/components/dashboard/kpi-card";
import { MetricGrid } from "@/components/dashboard/metric-grid";
import { ChartCard } from "@/components/dashboard/chart-card";
import { InsightCard } from "@/components/dashboard/insight-card";
import { AreaChart } from "@/components/charts/area-chart";
import { DonutChart } from "@/components/charts/donut-chart";
import { LineChart } from "@/components/charts/line-chart";
import { BarChart } from "@/components/charts/bar-chart";
import { StatusBadge } from "@/components/shared/status-badge";
import { PageSkeleton } from "@/components/shared/loading-state";
import { EmptyState, ErrorState } from "@/components/shared/empty-state";
import { useRealtime } from "@/hooks/use-realtime";
import { EXECUTIVE_SUMMARY_QUERY } from "@/lib/graphql/queries";
import type { ExecutiveSummaryResponse } from "@/lib/graphql/types";

function getKPIVariant(metric: { value: number; unit?: string }): "default" | "success" | "warning" | "critical" {
  if (metric.unit === "%") {
    if (metric.value >= 95) return "success";
    if (metric.value >= 90) return "warning";
    return "critical";
  }
  return "default";
}

export default function ExecutivePage() {
  const { lastUpdated, markUpdated } = useRealtime();

  const { data, loading, error, refetch } = useQuery<{ executiveSummary: ExecutiveSummaryResponse }>(
    EXECUTIVE_SUMMARY_QUERY,
    {
      variables: {
        input: {
          dateRange: {
            from: new Date(new Date().setHours(0, 0, 0, 0)).toISOString(),
            to: new Date().toISOString(),
          },
        },
      },
    }
  );

  const summary = data?.executiveSummary;

  // Format revenue trend data for area chart
  const revenueTrendData = useMemo(() => {
    return summary?.revenueTrend?.map((point) => ({
      time: point.timestamp,
      Revenue: Math.round(point.value),
      "Yesterday": Math.round(point.comparisonValue ?? 0),
    })) ?? [];
  }, [summary?.revenueTrend]);

  // Order status donut data
  const orderStatusData = useMemo(() => {
    return summary?.orderStatusBreakdown?.map((item) => ({
      name: item.status.charAt(0).toUpperCase() + item.status.slice(1),
      value: item.count,
    })) ?? [];
  }, [summary?.orderStatusBreakdown]);

  // Category bar chart data
  const categoryData = useMemo(() => {
    return summary?.topCategories?.map((cat) => ({
      category: cat.category,
      Revenue: cat.revenue,
      Orders: cat.orderCount,
    })) ?? [];
  }, [summary?.topCategories]);

  if (loading && !data) return <PageSkeleton />;
  if (error) return <ErrorState error={error.message} onRetry={() => refetch()} />;

  // Show empty state if no data yet (waiting for Iceberg queries to return)
  if (!summary) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Executive Overview"
          subtitle="Real-time business performance — Live updates every 5 seconds"
          breadcrumbs={[{ label: "Retail" }, { label: "Executive" }]}
        />
        <EmptyState
          title="No data available yet"
          description="Waiting for data to flow through Kafka → Flink → Iceberg. This typically takes 30-60 seconds after starting the platform."
          action={{ label: "Retry", onClick: () => refetch() }}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Executive Overview"
        subtitle="Real-time business performance — Live updates every 5 seconds"
        breadcrumbs={[{ label: "Retail" }, { label: "Executive" }]}
      />

      {/* KPI Grid */}
      <MetricGrid columns={4}>
        <KPICard
          label="Live Revenue"
          value={`$${(summary.liveRevenue.value / 1000).toFixed(1)}K`}
          unit={summary.liveRevenue.unit}
          trend={summary.liveRevenue.trend}
          trendDirection={summary.liveRevenue.trendDirection}
          icon={DollarSign}
        />
        <KPICard
          label="Total Orders"
          value={summary.totalOrders.value.toLocaleString()}
          trend={summary.totalOrders.trend}
          trendDirection={summary.totalOrders.trendDirection}
          icon={ShoppingCart}
        />
        <KPICard
          label="Avg Order Value"
          value={`$${summary.avgOrderValue.value.toFixed(2)}`}
          trend={summary.avgOrderValue.trend}
          trendDirection={summary.avgOrderValue.trendDirection}
          icon={TrendingUp}
        />
        <KPICard
          label="Payment Success"
          value={summary.paymentSuccessRate.value.toFixed(1)}
          unit="%"
          trend={summary.paymentSuccessRate.trend}
          trendDirection={summary.paymentSuccessRate.trendDirection}
          variant={getKPIVariant(summary.paymentSuccessRate)}
          icon={CreditCard}
        />
        <KPICard
          label="Delivery Delay Rate"
          value={summary.deliveryDelayRate.value.toFixed(1)}
          unit="%"
          trend={summary.deliveryDelayRate.trend}
          trendDirection={summary.deliveryDelayRate.trendDirection}
          variant="success"
          icon={Truck}
        />
        <KPICard
          label="Fraud Alerts"
          value={summary.fraudAlertCount.value}
          trend={summary.fraudAlertCount.trend}
          trendDirection={summary.fraudAlertCount.trendDirection}
          variant={summary.fraudAlertCount.value > 20 ? "warning" : "default"}
          icon={AlertTriangle}
        />
        <KPICard
          label="Stockout Risk"
          value={summary.stockoutRiskCount.value}
          trend={summary.stockoutRiskCount.trend}
          trendDirection={summary.stockoutRiskCount.trendDirection}
          variant={summary.stockoutRiskCount.value > 30 ? "warning" : "success"}
          icon={Package}
        />
        <KPICard
          label="Active Customers"
          value={summary.activeCustomers.value.toLocaleString()}
          trend={summary.activeCustomers.trend}
          trendDirection={summary.activeCustomers.trendDirection}
          icon={Users}
        />
      </MetricGrid>

      {/* AI Insight Card */}
      <InsightCard
        title="AI Insight"
        description={summary.aiSummary}
        action={{ label: "View Details", onClick: () => {} }}
      />

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Revenue Trend */}
        <div className="lg:col-span-2">
          <ChartCard
            title="Revenue Trend"
            subtitle="Last 24 hours"
            actions={
              <select className="text-xs bg-slate-800 border border-slate-700 rounded px-2 py-1">
                <option>24h</option>
                <option>7d</option>
                <option>30d</option>
              </select>
            }
            height={280}
          >
            <AreaChart
              data={revenueTrendData}
              xKey="time"
              yKey={["Revenue", "Yesterday"]}
              colors={["#3b82f6", "#64748b"]}
            />
          </ChartCard>
        </div>

        {/* Order Status Distribution */}
        <ChartCard
          title="Order Status"
          subtitle="Distribution"
          height={280}
        >
          <DonutChart
            data={orderStatusData}
            innerRadius={55}
            showLabel
            labelKey="percent"
          />
        </ChartCard>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Top Categories */}
        <ChartCard
          title="Top Categories by Revenue"
          subtitle="Last 24 hours"
          height={280}
        >
          <BarChart
            data={categoryData}
            xKey="category"
            yKey={["Revenue", "Orders"]}
            colors={["#3b82f6", "#10b981"]}
            orientation="horizontal"
          />
        </ChartCard>

        {/* Payment Success Rate */}
        <ChartCard
          title="Payment Success Rate Trend"
          subtitle="Last 24 hours"
          height={280}
        >
          <LineChart
            data={revenueTrendData}
            xKey="time"
            yKey="Success Rate"
            colors={["#10b981"]}
            referenceLine={{ y: 95, label: "Target 95%" }}
          />
        </ChartCard>
      </div>
    </div>
  );
}