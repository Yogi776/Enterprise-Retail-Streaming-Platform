// GraphQL Types - Generated from schema
// Input types
export interface DateRangeInput {
  startDate: string;
  endDate: string;
}

export interface ExecutiveSummaryInput extends DateRangeInput {
  storeIds?: string[];
}

export interface LiveOrdersInput extends DateRangeInput {
  status?: string[];
  limit?: number;
}

export interface PaymentHealthInput extends DateRangeInput {
  paymentMethod?: string[];
}

export interface InventorySnapshotInput extends DateRangeInput {
  category?: string;
}

export interface DeliveryPerformanceInput extends DateRangeInput {
  carrier?: string;
}

export interface FraudAlertsInput extends DateRangeInput {
  severity?: string[];
  minScore?: number;
}

export interface RecommendationInput extends DateRangeInput {
  recommendationType?: string;
}

export interface ActiveAlertsInput {
  severity?: string[];
  category?: string;
  status?: string[];
}

// Response types
export interface ExecutiveSummaryResponse {
  liveRevenue: KPIMetric;
  totalOrders: KPIMetric;
  avgOrderValue: KPIMetric;
  paymentSuccessRate: KPIMetric;
  deliveryDelayRate: KPIMetric;
  fraudAlertCount: KPIMetric;
  stockoutRiskCount: KPIMetric;
  activeCustomers: KPIMetric;
  revenueTrend: TrendPoint[];
  orderStatusBreakdown: StatusBreakdown[];
  topCategories: {
    category: string;
    revenue: number;
    orderCount: number;
    percentageOfTotal: number;
  }[];
  aiSummary: string;
}

export interface KPIMetric {
  value: number;
  unit?: string;
  trend?: number;
  trendDirection?: 'up' | 'down' | 'flat';
  lastUpdated?: string;
}

export interface TrendPoint {
  timestamp: string;
  value: number;
  comparisonValue?: number;
}

export interface StatusBreakdown {
  status: string;
  count: number;
  percentage: number;
}

export interface ChannelBreakdown {
  channel: string;
  count: number;
}

export interface RevenueByChannel {
  channel: string;
  revenue: number;
}

export interface LiveOrdersResponse {
  orders: LiveOrder[];
  totalCount: number;
  summary: {
    totalOrders: number;
    totalRevenue: number;
    avgOrderValue: number;
    ordersByStatus: StatusBreakdown[];
    ordersByChannel: ChannelBreakdown[];
    revenueByChannel: RevenueByChannel[];
  };
}

export interface LiveOrder {
  orderId: string;
  customerId: string;
  customerName: string;
  orderTimestamp: string;
  status: string;
  totalAmount: number;
  currency: string;
  channel: string;
  country: string;
  itemCount: number;
  paymentStatus: string;
  deliveryStatus: string;
  fraudScore: number;
}

export interface PaymentHealthResponse {
  totalTransactions: KPIMetric;
  successRate: KPIMetric;
  failedCount: KPIMetric;
  avgLatencyMs: KPIMetric;
  failureReasons: { reason: string; count: number; percentage: number }[];
  paymentsByMethod: {
    method: string;
    totalCount: number;
    successCount: number;
    successRate: number;
    avgLatencyMs: number;
  }[];
  latencyTrend: TrendPoint[];
  recentFailures: {
    paymentId: string;
    orderId: string;
    customerId: string;
    customerName: string;
    amount: number;
    currency: string;
    failureReason: string;
    paymentMethod: string;
    timestamp: string;
  }[];
}

export interface InventorySnapshotResponse {
  totalProducts: KPIMetric;
  inStockRate: KPIMetric;
  lowStockCount: KPIMetric;
  outOfStockCount: KPIMetric;
  stockDistribution: StatusBreakdown[];
  lowStockProducts: {
    productId: string;
    productName: string;
    category: string;
    currentStock: number;
    reorderPoint: number;
    daysOfSupply: number;
    warehouse: string;
  }[];
  stockoutRiskProducts: {
    productId: string;
    productName: string;
    category: string;
    currentStock: number;
    daysUntilStockout: number;
    velocity: number;
  }[];
  movementTrend: TrendPoint[];
}

export interface DeliveryPerformanceResponse {
  totalDeliveries: KPIMetric;
  onTimeRate: KPIMetric;
  avgDeliveryTimeHours: KPIMetric;
  delayedCount: KPIMetric;
  onTimeVsDelayed: StatusBreakdown[];
  performanceByCarrier: {
    carrier: string;
    totalDeliveries: number;
    onTimeCount: number;
    onTimeRate: number;
    avgDeliveryTimeHours: number;
  }[];
  delayReasons: { reason: string; count: number; percentage: number }[];
  slaBreaches: {
    orderId: string;
    customerId: string;
    customerName: string;
    carrier: string;
    expectedDate: string;
    actualDate: string;
    delayHours: number;
    reason: string;
  }[];
}

export interface FraudAlertsResponse {
  fraudAlertCount: KPIMetric;
  blockedAmount: KPIMetric;
  fraudRate: KPIMetric;
  avgFraudScore: KPIMetric;
  alertsBySeverity: { severity: string; count: number; percentage: number }[];
  fraudTrend: TrendPoint[];
  fraudByType: { fraudType: string; count: number }[];
  highRiskTransactions: {
    orderId: string;
    customerId: string;
    customerName: string;
    fraudScore: number;
    riskFactors: string[];
    amount: number;
    currency: string;
    timestamp: string;
  }[];
}

export interface Customer360Response {
  customer: {
    customerId: string;
    email: string;
    firstName: string;
    lastName: string;
    phone: string;
    loyaltyTier: string;
    customerSegment: string;
    country: string;
    joinDate: string;
    lastOrderDate: string;
    isActive: boolean;
  };
  lifetimeValue: KPIMetric;
  orderCount: number;
  avgOrderValue: number;
  churnRiskScore: number;
  churnRiskLevel: string;
  recentOrders: {
    orderId: string;
    orderTimestamp: string;
    status: string;
    totalAmount: number;
    itemCount: number;
  }[];
  paymentHistory: {
    paymentId: string;
    paymentTimestamp: string;
    amount: number;
    paymentStatus: string;
    paymentMethod: string;
  }[];
  deliveryHistory: {
    deliveryId: string;
    status: string;
    carrier: string;
    deliveryTimestamp: string;
  }[];
  behaviorTimeline: {
    timestamp: string;
    eventType: string;
    description: string;
    productId?: string;
    productName?: string;
  }[];
  recommendationEngagement: {
    impressions: number;
    clicks: number;
    conversions: number;
    ctr: number;
  };
}

export interface CustomerSegmentsResponse {
  segments: {
    segment: string;
    count: number;
    percentageOfTotal: number;
    avgLTV: number;
    avgAOV: number;
    avgOrdersPerCustomer: number;
    churnRate: number;
    trend: number;
    trendDirection: 'up' | 'down' | 'flat';
  }[];
  customerComposition: { segment: string; count: number }[];
  acquisitionTrend: TrendPoint[];
  churnTrend: TrendPoint[];
}

export interface ProductPerformanceResponse {
  products: {
    productId: string;
    productName: string;
    sku: string;
    category: string;
    revenue: number;
    units: number;
    aov: number;
    conversionRate: number;
    returnRate: number;
  }[];
  totalProducts: number;
  totalRevenue: number;
  avgConversionRate: number;
}

export interface CategoryPerformanceResponse {
  categories: {
    category: string;
    revenue: number;
    percentageOfTotal: number;
    trend: number;
  }[];
  totalRevenue: number;
}

export interface RecommendationPerformanceResponse {
  impressions: KPIMetric;
  clicks: KPIMetric;
  ctr: KPIMetric;
  conversions: KPIMetric;
  revenueFromRecs: KPIMetric;
  funnel: { stage: string; count: number; dropoffRate: number }[];
  ctrByType: {
    recommendationType: string;
    impressions: number;
    clicks: number;
    ctr: number;
  }[];
  topRecommendedProducts: {
    productId: string;
    productName: string;
    impressions: number;
    clicks: number;
    conversions: number;
    revenue: number;
  }[];
}

export interface ActiveAlertsResponse {
  totalActive: number;
  criticalCount: number;
  highCount: number;
  alerts: {
    alertId: string;
    title: string;
    description: string;
    severity: string;
    status: string;
    category: string;
    timestamp: string;
    acknowledgedAt?: string;
    resolvedAt?: string;
    assignedTo?: string;
    source?: string;
  }[];
}

export interface DataProduct {
  id: string;
  name: string;
  description: string;
  owner: string;
  ownerTeam: string;
  category: string;
  tags: string[];
  freshnessMinutes: number;
  qualityScore: number;
  consumerCount: number;
  lastUpdated: string;
  tablePath: string;
}

export interface DataQualityResponse {
  dataProduct: string;
  completeness: number;
  accuracy: number;
  freshness: number;
  qualityScore: number;
}

export interface ChatMessage {
  id: string;
  role: string;
  content: string;
  sqlQuery?: string;
  chartType?: string;
  insightCard?: boolean;
  timestamp: string;
}

export interface ChatMessageInput {
  role: string;
  content: string;
}

export interface AIChatResponse {
  message: ChatMessage;
  suggestions: string[];
}

// Re-export common types
export type { DateRangeInput as default };
