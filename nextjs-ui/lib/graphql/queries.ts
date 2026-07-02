import { gql } from "@apollo/client";

// ============================================================
// EXECUTIVE SUMMARY
// ============================================================

export const EXECUTIVE_SUMMARY_QUERY = gql`
  query ExecutiveSummary($input: ExecutiveSummaryInput!) {
    executiveSummary(input: $input) {
      liveRevenue {
        value
        unit
        trend
        trendDirection
        lastUpdated
      }
      totalOrders {
        value
        trend
        trendDirection
        lastUpdated
      }
      avgOrderValue {
        value
        unit
        trend
        trendDirection
      }
      paymentSuccessRate {
        value
        unit
        trend
        trendDirection
      }
      deliveryDelayRate {
        value
        unit
        trend
        trendDirection
      }
      fraudAlertCount {
        value
        trend
        trendDirection
      }
      stockoutRiskCount {
        value
        trend
        trendDirection
      }
      activeCustomers {
        value
        trend
        trendDirection
      }
      revenueTrend {
        timestamp
        value
        comparisonValue
      }
      orderStatusBreakdown {
        status
        count
        percentage
      }
      topCategories {
        category
        revenue
        orderCount
        percentageOfTotal
      }
      aiSummary
    }
  }
`;

// ============================================================
// LIVE ORDERS
// ============================================================

export const LIVE_ORDERS_QUERY = gql`
  query LiveOrders($input: LiveOrdersInput!) {
    liveOrders(input: $input) {
      orders {
        orderId
        customerId
        customerName
        orderTimestamp
        status
        totalAmount
        currency
        channel
        country
        itemCount
        paymentStatus
        deliveryStatus
        fraudScore
      }
      totalCount
      summary {
        totalOrders
        totalRevenue
        avgOrderValue
        ordersByStatus {
          status
          count
          percentage
        }
        ordersByChannel {
          channel
          count
        }
        revenueByChannel {
          channel
          revenue
        }
      }
    }
  }
`;

// ============================================================
// PAYMENT HEALTH
// ============================================================

export const PAYMENT_HEALTH_QUERY = gql`
  query PaymentHealth($input: PaymentHealthInput!) {
    paymentHealth(input: $input) {
      totalTransactions {
        value
        trend
        trendDirection
      }
      successRate {
        value
        unit
        trend
        trendDirection
      }
      failedCount {
        value
        trend
        trendDirection
      }
      avgLatencyMs {
        value
        unit
        trend
        trendDirection
      }
      failureReasons {
        reason
        count
        percentage
      }
      paymentsByMethod {
        method
        totalCount
        successCount
        successRate
        avgLatencyMs
      }
      latencyTrend {
        timestamp
        value
      }
      recentFailures {
        paymentId
        orderId
        customerId
        customerName
        amount
        currency
        failureReason
        paymentMethod
        timestamp
      }
    }
  }
`;

// ============================================================
// INVENTORY
// ============================================================

export const INVENTORY_SNAPSHOT_QUERY = gql`
  query InventorySnapshot($input: InventorySnapshotInput!) {
    inventorySnapshot(input: $input) {
      totalProducts {
        value
        trend
        trendDirection
      }
      inStockRate {
        value
        unit
        trend
        trendDirection
      }
      lowStockCount {
        value
        trend
        trendDirection
      }
      outOfStockCount {
        value
        trend
        trendDirection
      }
      stockDistribution {
        status
        count
        percentage
      }
      lowStockProducts {
        productId
        productName
        category
        currentStock
        reorderPoint
        daysOfSupply
        warehouse
      }
      stockoutRiskProducts {
        productId
        productName
        category
        currentStock
        daysUntilStockout
        velocity
      }
      movementTrend {
        timestamp
        value
      }
    }
  }
`;

// ============================================================
// DELIVERY
// ============================================================

export const DELIVERY_PERFORMANCE_QUERY = gql`
  query DeliveryPerformance($input: DeliveryPerformanceInput!) {
    deliveryPerformance(input: $input) {
      totalDeliveries {
        value
        trend
        trendDirection
      }
      onTimeRate {
        value
        unit
        trend
        trendDirection
      }
      avgDeliveryTimeHours {
        value
        unit
        trend
        trendDirection
      }
      delayedCount {
        value
        trend
        trendDirection
      }
      onTimeVsDelayed {
        status
        count
        percentage
      }
      performanceByCarrier {
        carrier
        totalDeliveries
        onTimeCount
        onTimeRate
        avgDeliveryTimeHours
      }
      delayReasons {
        reason
        count
        percentage
      }
      slaBreaches {
        orderId
        customerId
        customerName
        carrier
        expectedDate
        actualDate
        delayHours
        reason
      }
    }
  }
`;

// ============================================================
// FRAUD
// ============================================================

export const FRAUD_ALERTS_QUERY = gql`
  query FraudAlerts($input: FraudAlertsInput!) {
    fraudAlerts(input: $input) {
      fraudAlertCount {
        value
        trend
        trendDirection
      }
      blockedAmount {
        value
        unit
        trend
        trendDirection
      }
      fraudRate {
        value
        unit
        trend
        trendDirection
      }
      avgFraudScore {
        value
        trend
        trendDirection
      }
      alertsBySeverity {
        severity
        count
        percentage
      }
      fraudTrend {
        timestamp
        value
      }
      fraudByType {
        fraudType
        count
      }
      highRiskTransactions {
        orderId
        customerId
        customerName
        fraudScore
        riskFactors
        amount
        currency
        timestamp
      }
    }
  }
`;

// ============================================================
// CUSTOMER 360
// ============================================================

export const CUSTOMER_360_QUERY = gql`
  query Customer360($customerId: ID!) {
    customer360(customerId: $customerId) {
      customer {
        customerId
        email
        firstName
        lastName
        phone
        loyaltyTier
        customerSegment
        country
        joinDate
        lastOrderDate
        isActive
      }
      lifetimeValue {
        value
        trend
        trendDirection
      }
      orderCount
      avgOrderValue
      churnRiskScore
      churnRiskLevel
      recentOrders {
        orderId
        orderTimestamp
        status
        totalAmount
        itemCount
      }
      paymentHistory {
        paymentId
        paymentTimestamp
        amount
        paymentStatus
        paymentMethod
      }
      deliveryHistory {
        deliveryId
        status
        carrier
        deliveryTimestamp
      }
      behaviorTimeline {
        timestamp
        eventType
        description
        productId
        productName
      }
      recommendationEngagement {
        impressions
        clicks
        conversions
        ctr
      }
    }
  }
`;

// ============================================================
// CUSTOMER SEGMENTS
// ============================================================

export const CUSTOMER_SEGMENTS_QUERY = gql`
  query CustomerSegments($dateRange: DateRangeInput) {
    customerSegments(dateRange: $dateRange) {
      segments {
        segment
        count
        percentageOfTotal
        avgLTV
        avgAOV
        avgOrdersPerCustomer
        churnRate
        trend
        trendDirection
      }
      customerComposition {
        segment
        count
      }
      acquisitionTrend {
        timestamp
        value
      }
      churnTrend {
        timestamp
        value
      }
    }
  }
`;

// ============================================================
// PRODUCT PERFORMANCE
// ============================================================

export const PRODUCT_PERFORMANCE_QUERY = gql`
  query ProductPerformance($dateRange: DateRangeInput, $category: String, $limit: Int) {
    productPerformance(dateRange: $dateRange, category: $category, limit: $limit) {
      products {
        productId
        productName
        sku
        category
        revenue
        units
        aov
        conversionRate
        returnRate
      }
      totalProducts
      totalRevenue
      avgConversionRate
    }
  }
`;

// ============================================================
// CATEGORY PERFORMANCE
// ============================================================

export const CATEGORY_PERFORMANCE_QUERY = gql`
  query CategoryPerformance($dateRange: DateRangeInput) {
    categoryPerformance(dateRange: $dateRange) {
      categories {
        category
        revenue
        percentageOfTotal
        trend
      }
      totalRevenue
    }
  }
`;

// ============================================================
// RECOMMENDATION ANALYTICS
// ============================================================

export const RECOMMENDATION_PERFORMANCE_QUERY = gql`
  query RecommendationPerformance($input: RecommendationInput!) {
    recommendationPerformance(input: $input) {
      impressions {
        value
        trend
        trendDirection
      }
      clicks {
        value
        trend
        trendDirection
      }
      ctr {
        value
        unit
        trend
        trendDirection
      }
      conversions {
        value
        trend
        trendDirection
      }
      revenueFromRecs {
        value
        unit
        trend
        trendDirection
      }
      funnel {
        stage
        count
        dropoffRate
      }
      ctrByType {
        recommendationType
        impressions
        clicks
        ctr
      }
      topRecommendedProducts {
        productId
        productName
        impressions
        clicks
        conversions
        revenue
      }
    }
  }
`;

// ============================================================
// ACTIVE ALERTS
// ============================================================

export const ACTIVE_ALERTS_QUERY = gql`
  query ActiveAlerts($input: ActiveAlertsInput) {
    activeAlerts(input: $input) {
      totalActive
      criticalCount
      highCount
      alerts {
        alertId
        title
        description
        severity
        status
        category
        timestamp
        acknowledgedAt
        resolvedAt
        assignedTo
        source
      }
    }
  }
`;

// ============================================================
// DATA PRODUCTS CATALOG
// ============================================================

export const DATA_PRODUCTS_CATALOG_QUERY = gql`
  query DataProductsCatalog($category: String, $owner: String) {
    dataProductsCatalog(category: $category, owner: $owner) {
      id
      name
      description
      owner
      ownerTeam
      category
      tags
      freshnessMinutes
      qualityScore
      consumerCount
      lastUpdated
      tablePath
    }
  }
`;

// ============================================================
// DATA QUALITY
// ============================================================

export const DATA_QUALITY_QUERY = gql`
  query DataQuality {
    dataQuality {
      dataProduct
      completeness
      accuracy
      freshness
      qualityScore
    }
  }
`;

// ============================================================
// AI CHAT
// ============================================================

export const AI_CHAT_MUTATION = gql`
  mutation AIChat($message: String!, $history: [ChatMessageInput!]) {
    aiChat(message: $message, history: $history) {
      message {
        id
        role
        content
        sqlQuery
        chartType
        insightCard
        timestamp
      }
      suggestions
    }
  }
`;