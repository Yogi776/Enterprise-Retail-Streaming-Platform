# Enterprise Retail Streaming Platform — UI/UX Design Document

> **Version:** 1.0
> **Last Updated:** July 1, 2026
> **Target:** Enterprise Retail Streaming Platform (Next.js UI)
> **Design System:** Tailwind CSS + shadcn/ui + Recharts

---

## 1. Product Vision

The **Retail Command Center** is a real-time intelligence platform that transforms retail operations from reactive firefighting into proactive decision-making. It serves as the single source of truth for executives, operations teams, fraud analysts, and customer success managers — providing live visibility into orders, payments, inventory, delivery, and customer behavior across all channels.

The product feels like a premium Bloomberg terminal meets a modern SaaS dashboard: information-dense yet scannable, real-time yet stable, powerful yet approachable. Every screen answers a specific business question within 2 seconds of looking at it.

---

## 2. User Personas

### 2.1 Chief Revenue Officer (CRO)

| Attribute | Detail |
|---|---|
| **Goals** | Understand daily revenue trajectory, identify trends, assess channel performance |
| **Key Questions** | "Where are we vs. target today?" "Which channels are over/under-performing?" "What caused the revenue dip at 2pm?" |
| **Most Used Pages** | Executive Overview, Orders Monitor, Revenue Analytics |
| **KPIs Needed** | Live Revenue, Total Orders, AOV, Conversion Rate, Revenue by Channel |
| **Actions from Insights** | Reallocate marketing budget, trigger promotions on under-performing channels |

### 2.2 VP Retail Operations

| Attribute | Detail |
|---|---|
| **Goals** | Keep the retail engine running — orders flowing, payments clearing, inventory stocked |
| **Key Questions** | "Any payment failures spiking?" "Which SKUs are at stockout risk?" "Delivery SLA status?" |
| **Most Used Pages** | Payment Health, Inventory Control Tower, Delivery Performance |
| **KPIs Needed** | Payment Success Rate, Stockout Count, Delivery Delay Rate, Fraud Alert Count |
| **Actions from Insights** | Trigger emergency reorder, escalate payment provider issue, contact carrier |

### 2.3 Supply Chain Manager

| Attribute | Detail |
|---|---|
| **Goals** | Optimize inventory placement, prevent stockouts, manage supplier relationships |
| **Key Questions** | "Which products are at risk of stockout in next 7 days?" "What's our inventory turnover by category?" |
| **Most Used Pages** | Inventory Control Tower, Category Performance |
| **KPIs Needed** | Stockout Events, Low Stock Alerts, Reorder Recommendations, Inventory Turnover |
| **Actions from Insights** | Place emergency orders, adjust reorder points, contact suppliers |

### 2.4 Inventory Planner

| Attribute | Detail |
|---|---|
| **Goals** | Maintain 99.5% inventory availability, minimize carrying costs |
| **Key Questions** | "What's the stock level for SKU-X right now?" "When should we reorder product Y?" |
| **Most Used Pages** | Inventory Control Tower, Product Performance |
| **KPIs Needed** | Current Stock, Days of Supply, Reorder Point, Lead Time |
| **Actions from Insights** | Adjust safety stock levels, update demand forecasts, negotiate supplier lead times |

### 2.5 Fraud Analyst

| Attribute | Detail |
|---|---|
| **Goals** | Detect and prevent fraudulent transactions in real-time |
| **Key Questions** | "Which orders have high fraud scores?" "Is fraud rate within acceptable bounds?" |
| **Most Used Pages** | Fraud Monitoring, Customer 360 |
| **KPIs Needed** | Fraud Alert Count, Blocked Amount, Fraud Rate, Top Fraud Types |
| **Actions from Insights** | Block suspicious orders, escalate to risk team, adjust fraud rules |

### 2.6 Finance Analyst

| Attribute | Detail |
|---|---|
| **Goals** | Track revenue accuracy, ensure payment reconciliation, monitor refund rates |
| **Key Questions** | "Do order totals match payment amounts?" "What's our refund rate by channel?" |
| **Most Used Pages** | Payment Health, Reports |
| **KPIs Needed** | Payment Success Rate, Refund Rate, Revenue by Channel, Failed Payment Count |
| **Actions from Insights** | Raise disputes with payment providers, adjust payment method routing |

### 2.7 Customer Success Manager

| Attribute | Detail |
|---|---|
| **Goals** | Maximize customer lifetime value, reduce churn, improve satisfaction |
| **Key Questions** | "Which customers are at risk of churn?" "What's the NPS trend?" "Who are our power users?" |
| **Most Used Pages** | Customer 360, Customer Segments, Behavior Analytics |
| **KPIs Needed** | Active Customers, Churn Rate, LTV Distribution, Repeat Purchase Rate |
| **Actions from Insights** | Launch retention campaigns, personalize recommendations, escalate at-risk accounts |

### 2.8 Data Product Owner

| Attribute | Detail |
|---|---|
| **Goals** | Maintain data product catalog, ensure data quality, track usage |
| **Key Questions** | "Which data products are most consumed?" "What's the freshness SLA for each table?" |
| **Most Used Pages** | Data Product Catalog, Data Quality, Lineage, Usage Analytics |
| **KPIs Needed** | Data Product Count, Consumer Count, Freshness (time since last update), Quality Score |
| **Actions from Insights** | Deprecate unused products, improve low-quality datasets, onboard new consumers |

### 2.9 Data Platform Engineer

| Attribute | Detail |
|---|---|
| **Goals** | Keep the platform running, optimize query performance, manage data pipelines |
| **Key Questions** | "Is Kafka consumer lag healthy?" "Are Flink jobs running?" "Which queries are timing out?" |
| **Most Used Pages** | Platform Health Dashboard, Grafana, Data Lineage |
| **KPIs Needed** | Kafka Throughput, Flink Processing Latency, Trino Query Time, MinIO Health |
| **Actions from Insights** | Restart failed jobs, tune Kafka consumer settings, optimize Iceberg compaction |

### 2.10 Executive Leadership Team

| Attribute | Detail |
|---|---|
| **Goals** | Strategic oversight — understand business momentum, market position, risk areas |
| **Key Questions** | "What's the 30,000-foot view of the business?" "Any existential risks?" "How are we trending vs. last quarter?" |
| **Most Used Pages** | Executive Overview, AI Assistant |
| **KPIs Needed** | Revenue vs. Target, Order Count, Customer Acquisition, Fraud Loss Prevention |
| **Actions from Insights** | Board presentations, strategic planning, resource allocation |

---

## 3. Information Architecture

```
Retail Command Center
├── Executive Overview              (/)
├── Live Operations                 (/live-operations)
│   ├── Orders Monitor             (/live-operations/orders)
│   ├── Payment Health             (/live-operations/payments)
│   ├── Inventory Control Tower    (/live-operations/inventory)
│   ├── Delivery Performance       (/live-operations/delivery)
│   └── Fraud Monitoring           (/live-operations/fraud)
├── Customer Intelligence          (/customer-intelligence)
│   ├── Customer 360              (/customer-intelligence/customer-360)
│   ├── Customer Segments          (/customer-intelligence/segments)
│   └── Behavior Analytics        (/customer-intelligence/behavior)
├── Product Intelligence           (/product-intelligence)
│   ├── Product Performance        (/product-intelligence/performance)
│   ├── Category Performance        (/product-intelligence/category)
│   └── Recommendation Analytics   (/product-intelligence/recommendations)
├── Data Products                  (/data-products)
│   ├── Data Product Catalog       (/data-products/catalog)
│   ├── Lineage                    (/data-products/lineage)
│   ├── Data Quality              (/data-products/quality)
│   └── Usage Analytics           (/data-products/usage)
├── AI Assistant                  (/ai-assistant)
├── Alerts & Incidents            (/alerts)
├── Reports                       (/reports)
└── Admin Settings               (/admin)
```

**Navigation Principles:**
- Sidebar groups align with team ownership (Live Operations = Ops team, Customer Intelligence = CX team)
- Deepest pages are the most specific (Fraud Monitoring → specific fraud details)
- Admin section visible only to Data Platform Engineer role
- Alerts badge count shown on sidebar icon when active alerts > 0

---

## 4. Page-by-Page UX Design

---

### 4.1 Executive Overview (`/executive`)

| Attribute | Detail |
|---|---|
| **Purpose** | Single-pane-of-glass business health for executives and CRO |
| **Target Users** | CRO, Executive Leadership Team, VP Operations |
| **Business Questions** | "Where are we vs. target today?" "What needs immediate attention?" "What's the revenue trend?" |

**KPI Cards (8 cards in 2-row grid):**

| KPI | Display | Color Logic |
|-----|---------|-----------|
| Live Revenue | $X,XXX,XXX with trend arrow | Green if > yesterday, red if < |
| Total Orders | X,XXX with trend arrow | Green if > yesterday |
| Avg Order Value | $XX.XX with trend arrow | Green if > yesterday |
| Payment Success Rate | XX.X% with trend arrow | Green if > 95%, amber if 90-95%, red if < 90% |
| Fraud Alert Count | XX with severity indicator | Red if > threshold, amber if elevated |
| Active Customers | X,XXX with trend | Green if > yesterday |
| Delivery Delay Rate | X.X% with trend | Green if < 5%, amber if 5-10%, red if > 10% |
| Stockout Risk Count | XX with severity | Red if > threshold |

**Charts:**
1. **Revenue Trend** (AreaChart) — Last 24h, hourly buckets, vs. yesterday's overlay
2. **Orders Per Minute** (LineChart) — Last 4 hours, 1-min buckets, real-time
3. **Order Status Distribution** (DonutChart) — Completed / Pending / Failed / Cancelled
4. **Top 5 Categories by Revenue** (HorizontalBarChart)
5. **Payment Success Rate Trend** (LineChart) — Last 24h with threshold line at 95%

**AI Summary Card:**
- Card with blue left border
- Icon: Sparkles
- Title: "AI Insight"
- Body: 2-3 sentence natural language summary of current state
  - Example: "Revenue is tracking 12% above yesterday's pace. Payment success rate dropped to 94.2% at 2pm — primarily due to a Stripe webhook delay affecting card payments. Fraud alerts are elevated in the UK region (7 high-risk orders in the last 30 minutes)."

**Filters:** Date range (default: today), Country (default: all), Channel (default: all)

**Real-time Refresh:** 5 seconds, with pause/resume control

**Empty State:** "No data available for today. Data generation may be paused." with "Resume Data" button
**Loading State:** KPI cards show skeleton pulse; charts show line skeleton
**Error State:** Banner at top "Failed to load dashboard data. [Retry]"

---

### 4.2 Orders Monitor (`/live-operations/orders`)

| Attribute | Detail |
|---|---|
| **Purpose** | Live stream of incoming orders with filtering and drill-down |
| **Target Users** | CRO, VP Operations, Operations Team |
| **Business Questions** | "What's the order volume right now?" "Which orders failed?" "Which channel is hottest?" |

**Layout:**
- Top: KPI summary row (4 cards: Orders Today, Revenue Today, Avg Value, Failed Orders)
- Middle: Charts row (Order Volume by Hour, Revenue by Channel, Orders by Status)
- Bottom: Live Events Table (sortable, filterable)

**Live Events Table Columns:**
| Column | Type | Notes |
|--------|------|-------|
| Order ID | Link | Click opens Order Detail drawer |
| Timestamp | DateTime | Format: HH:mm:ss |
| Customer | CustomerLink | Click opens Customer 360 |
| Channel | Badge | POS / Web / Mobile / App |
| Items | Count | "X items" |
| Amount | Currency | Right-aligned |
| Status | StatusBadge | completed / pending / failed / cancelled |
| Actions | Buttons | View / Refund (if applicable) |

**Row Animation:** New rows flash blue for 2 seconds then fade to normal

**Filters:** Date range, Channel, Status, Country, Min Amount, Max Amount

**Drawer (Order Detail):** Slides in from right
- Order summary header
- Line items table
- Customer info (linked)
- Payment status (linked)
- Delivery status (linked)
- Timeline of events

---

### 4.3 Payment Health (`/live-operations/payments`)

| Attribute | Detail |
|---|---|
| **Purpose** | Monitor payment success/failure rates and diagnose payment issues |
| **Target Users** | VP Operations, Finance Analyst, Fraud Analyst |
| **Business Questions** | "What's our payment success rate?" "Why are payments failing?" "Which payment methods are underperforming?" |

**KPI Cards:**
| KPI | Notes |
|-----|-------|
| Total Transactions | Today |
| Success Rate | % with color logic |
| Failed Transactions | Count |
| Avg Payment Latency | Seconds |

**Charts:**
1. **Success vs Failure Rate** (AreaChart stacked) — Last 24h
2. **Failure Reasons Breakdown** (PieChart) — Insufficient Funds / Declined / Timeout / Invalid Card / Other
3. **Payment Method Performance** (GroupedBarChart) — Success rate by method: Credit Card / Debit Card / Wallet / Bank Transfer
4. **Payment Latency Distribution** (Histogram) — P50 / P95 / P99

**Table: Recent Failed Payments**
| Column | Notes |
|--------|-------|
| Payment ID | Link to detail |
| Order ID | Link |
| Customer | Link to Customer 360 |
| Amount | |
| Failure Reason | Badge color by reason type |
| Timestamp | |
| Retry Action | Button |

**Filters:** Date range, Payment Method, Failure Reason, Country

---

### 4.4 Inventory Control Tower (`/live-operations/inventory`)

| Attribute | Detail |
|---|---|
| **Purpose** | Real-time inventory health monitoring and reorder decision support |
| **Target Users** | VP Operations, Supply Chain Manager, Inventory Planner |
| **Business Questions** | "Which SKUs are at stockout risk?" "What's our inventory coverage?" "Where are the stockout hotspots?" |

**KPI Cards:**
| KPI | Notes |
|-----|-------|
| Total SKUs | Active products |
| In Stock | % of SKUs with qty > 0 |
| Low Stock | Count with qty < reorder point |
| Out of Stock | Count with qty = 0 |

**Charts:**
1. **Stock Status Distribution** (DonutChart) — In Stock / Low Stock / Out of Stock
2. **Stockout Events Over Time** (BarChart) — Daily counts, last 30 days
3. **Low Stock by Category** (HorizontalBarChart) — Top 10 categories with most low-stock SKUs
4. **Inventory Movement** (LineChart) — Units in / Units out, last 7 days

**Table: Low Stock & Stockout Products**
| Column | Notes |
|--------|-------|
| SKU | Product name + SKU ID |
| Category | Badge |
| Current Stock | Number, red if 0 |
| Reorder Point | Threshold |
| Days of Supply | Calculated |
| Status | In Stock / Low / Out |
| Action | Reorder button |

**Filters:** Category, Warehouse, Supplier, Stock Status, Country

**Recommendations Panel:** Right sidebar showing AI-generated reorder suggestions based on velocity and stockout risk score.

---

### 4.5 Delivery Performance (`/live-operations/delivery`)

| Attribute | Detail |
|---|---|
| **Purpose** | Monitor delivery SLA compliance and carrier performance |
| **Target Users** | VP Operations, Supply Chain Manager |
| **Business Questions** | "What's our on-time delivery rate?" "Which carriers are underperforming?" "Any SLA breaches?" |

**KPI Cards:**
| KPI | Notes |
|-----|-------|
| Total Deliveries Today | Count |
| On-Time Rate | % of orders delivered on time |
| Avg Delivery Time | Hours from order to delivery |
| Delayed | Count with % |

**Charts:**
1. **On-Time vs Delayed** (DonutChart) — Proportion
2. **Delivery Performance by Carrier** (GroupedBarChart) — On-time % by carrier
3. **Delivery Time Trend** (LineChart) — Avg hours, last 14 days
4. **Delay Reasons** (PieChart) — Weather / Carrier / Customs / Customer / Other

**Table: SLA Breach List**
| Column | Notes |
|--------|-------|
| Order ID | Link |
| Customer | Link |
| Carrier | Badge |
| Expected Delivery | Date |
| Actual Delivery | Date |
| Delay | Hours |
| Reason | Badge |

---

### 4.6 Fraud Monitoring (`/live-operations/fraud`)

| Attribute | Detail |
|---|---|
| **Purpose** | Real-time fraud alerting and investigation workflow |
| **Target Users** | Fraud Analyst, VP Operations |
| **Business Questions** | "Which orders have high fraud scores?" "Is fraud rate within threshold?" "What's the fraud trend?" |

**KPI Cards:**
| KPI | Notes |
|-----|-------|
| Fraud Alerts | Count today |
| Blocked Amount | $ value of blocked orders |
| Fraud Rate | Alerts / Total Orders % |
| Avg Fraud Score | 0.0 - 1.0 |

**Charts:**
1. **Fraud Alerts Over Time** (BarChart) — High / Medium / Low severity, hourly
2. **Fraud Score Distribution** (Histogram) — Buckets 0.0-0.2 / 0.2-0.4 / 0.4-0.6 / 0.6-0.8 / 0.8-1.0
3. **Fraud by Type** (PieChart) — Velocity / Geographic / Behavioral / Instrument / Other

**Table: High-Risk Transactions**
| Column | Notes |
|--------|-------|
| Order ID | Link |
| Customer | Link to Customer 360 |
| Fraud Score | Number, colored: red >0.7, amber 0.4-0.7 |
| Risk Factors | Tags: "Velocity spike" / "New device" / "Mismatched address" |
| Amount | $ |
| Action | Approve / Review / Block |

**Investigation Drawer:** Order detail + customer detail + fraud signals + action buttons (Block Order / Flag for Review / Approve)

---

### 4.7 Customer 360 (`/customer-intelligence/customer-360`)

| Attribute | Detail |
|---|---|
| **Purpose** | Single customer view with full history and risk assessment |
| **Target Users** | Customer Success Manager, Fraud Analyst |
| **Business Questions** | "Who is this customer?" "What's their lifetime value?" "Are they at risk of churn?" |

**Search:** Global customer search in top nav (by email, name, or customer ID)

**Page Layout:**
- **Header:** Customer name, email, ID, loyalty tier badge, risk score gauge, churn risk badge
- **Left Column:** Profile card, Lifetime Value, Order count, AOV, Join date
- **Center Column:** Recent Orders table, Payment History, Delivery History
- **Right Column:** Behavior Timeline, Recommendation Engagement, Fraud Risk signals

**Timeline Events:**
- Order placed
- Payment completed
- Delivery completed
- Return initiated
- Review submitted
- Recommendation clicked

---

### 4.8 Customer Segments (`/customer-intelligence/segments`)

| Attribute | Detail |
|---|---|
| **Purpose** | Understand customer base composition and segment performance |
| **Target Users** | Customer Success Manager, Marketing, CRO |

**Segment Cards:**
- New Customers (joined last 30 days)
- Active Customers (ordered last 30 days)
- At-Risk Customers (ordered 60-90 days ago)
- Churned Customers (no orders in 90+ days)
- VIP Customers (LTV > $10,000)

Each card shows: Count, % of total, Avg LTV, Avg AOV, Trend vs last period

**Charts:**
1. **Customer Composition** (DonutChart) — By segment
2. **Segment LTV Distribution** (BoxPlot or ViolinChart)
3. **Customer Acquisition vs Churn** (AreaChart stacked)

---

### 4.9 Behavior Analytics (`/customer-intelligence/behavior`)

| Attribute | Detail |
|---|---|
| **Purpose** | Understand how customers interact with the platform |
| **Target Users** | Marketing, Customer Success Manager, Product |

**Charts:**
1. **Session Volume** (AreaChart) — Page views / Sessions, hourly
2. **Conversion Funnel** (FunnelChart) — Visit → Product View → Add to Cart → Checkout → Order
3. **Top Pages** (Table) — Page path, Views, Unique Visitors, Avg Time
4. **Cart Abandonment Rate** (LineChart) — % over time
5. **Wishlist vs Purchase** (BarChart) — Wishlisted vs Purchased

**Tables:**
- Top Products by Views
- Top Products by Add-to-Cart
- Top Products by Purchase
- Recently Viewed Products

---

### 4.10 Product Performance (`/product-intelligence/performance`)

| Attribute | Detail |
|---|---|
| **Purpose** | Understand product-level revenue and conversion performance |
| **Target Users** | CRO, Inventory Planner, Merchandising |

**KPI Cards:** Total Products, Total Revenue, Avg Conversion Rate, Return Rate

**Charts:**
1. **Top 20 Products by Revenue** (HorizontalBarChart)
2. **Top 20 Products by Units Sold** (HorizontalBarChart)
3. **Revenue vs Units Sold Scatter** — Identify high-revenue low-volume vs low-revenue high-volume
4. **Product Lifecycle** (LineChart) — Orders over product lifetime

**Table:** Product Performance
| Column | Notes |
|--------|-------|
| Product | Name + Image |
| SKU | |
| Category | Badge |
| Revenue | |
| Units | |
| AOV | |
| Conv. Rate | |
| Return Rate | Red if > threshold |

---

### 4.11 Category Performance (`/product-intelligence/category`)

| Attribute | Detail |
|---|---|
| **Purpose** | Category-level revenue and margin analysis |
| **Target Users** | CRO, Merchandising, Inventory Planner |

**Charts:**
1. **Revenue by Category** (PieChart / DonutChart)
2. **Category Performance vs Target** (BarChart grouped) — Actual vs Target by category
3. **Category Trend** (LineChart) — Revenue over time by category
4. **Category Mix Evolution** (StackedAreaChart) — % share over time

---

### 4.12 Recommendation Analytics (`/product-intelligence/recommendations`)

| Attribute | Detail |
|---|---|
| **Purpose** | Measure recommendation engine effectiveness |
| **Target Users** | Data Product Owner, Marketing, CRO |

**KPI Cards:** Impressions, Clicks, CTR, Conversions from Recs, Revenue from Recs

**Charts:**
1. **Recommendation Funnel** (FunnelChart) — Impressions → Clicks → Add to Cart → Purchase
2. **CTR by Recommendation Type** (GroupedBarChart) — "Customers who bought X also bought" / "Recommended for you" / "Trending"
3. **Revenue Attribution** (PieChart) — Revenue from recommendations vs Organic
4. **Top Recommended Products** (Table)

---

### 4.13 Data Product Catalog (`/data-products/catalog`)

| Attribute | Detail |
|---|---|
| **Purpose** | Discover and understand available data products |
| **Target Users** | Data Product Owner, Data Platform Engineer, Analysts |

**Search:** Full-text search across product names, descriptions, owners, tags

**Data Product Card:**
- Product name + description
- Owner team + contact
- Freshness SLA (e.g., "Data updated 5 minutes ago")
- Quality Score (0-100 with color)
- Consumer count
- Tags
- OpenMetadata lineage link (opens in new tab)

**Filters:** Owner team, Category, Freshness, Quality Score range

---

### 4.14 Data Lineage (`/data-products/lineage`)

| Attribute | Detail |
|---|---|
| **Purpose** | Visualize data flow from source to consumption |
| **Target Users** | Data Platform Engineer, Data Product Owner |

**Lineage Graph:** DAG visualization showing:
- Kafka topics (source)
- Flink jobs (processing)
- Iceberg tables (storage)
- Trino views (serving)
- GraphQL queries (consumption)
- UI pages (end consumers)

Click any node to see: Table/topic/job details, column-level lineage, last update time

---

### 4.15 Data Quality (`/data-products/quality`)

| Attribute | Detail |
|---|---|
| **Purpose** | Monitor data quality metrics for all data products |
| **Target Users** | Data Product Owner, Data Platform Engineer |

**Quality Dimensions:** Completeness, Accuracy, Freshness, Consistency, Validity

**Table:** Data Product Quality Scorecard
| Column | Notes |
|--------|-------|
| Data Product | Link |
| Completeness | % non-null |
| Accuracy | % valid values |
| Freshness | Minutes since last update |
| Quality Score | Weighted composite |

---

### 4.16 AI Assistant (`/ai-assistant`)

| Attribute | Detail |
|---|---|
| **Purpose** | Natural language interface for business insights |
| **Target Users** | All personas, especially CRO and Executive Leadership |

**Layout:** Two-panel
- **Left (70%):** Chat messages, scrollable, input at bottom
- **Right (30%):** Suggested Prompts, SQL Explanation (when relevant)

**Suggested Prompts:**
- "What caused the revenue drop in the last hour?"
- "Which products are at stockout risk today?"
- "Show me the top 10 customers by lifetime value"
- "Why did payment failures increase today?"
- "What's the delivery delay rate this week vs last week?"
- "Which channels have the highest fraud rate?"
- "Summarize today's business performance"

**Chat Behavior:**
- User message (right-aligned, blue bubble)
- AI response (left-aligned, gray bubble)
- If SQL generated: show SQL in code block + "Explain this SQL" button
- If chart recommended: show chart preview
- If insight: show InsightCard with "Add to Dashboard" button
- Follow-up suggestions at bottom of response

**Safety:** No SQL write operations (no DELETE, DROP, UPDATE). All queries are SELECT only.

---

### 4.17 Alerts & Incidents (`/alerts`)

| Attribute | Detail |
|---|---|
| **Purpose** | Centralized alert management for operational issues |
| **Target Users** | VP Operations, Data Platform Engineer, Fraud Analyst |

**Alert Severities:** Critical (red), High (orange), Medium (yellow), Low (blue), Info (gray)

**Alert Card:**
- Severity badge
- Alert title
- Description
- Timestamp
- Assigned owner (avatar)
- Status: Open / Acknowledged / Resolved

**Filters:** Severity, Status, Category (Payment / Inventory / Fraud / Platform / Delivery), Date range

**Actions:** Acknowledge, Assign, Add Note, Resolve

---

### 4.18 Reports (`/reports`)

| Attribute | Detail |
|---|---|
| **Purpose** | Pre-built and custom report builder |
| **Target Users** | Finance Analyst, CRO, Executive Team |

**Report Types:**
- Daily Business Summary (PDF/Email)
- Weekly Performance Report
- Fraud Investigation Report
- Inventory Status Report
- Revenue by Channel Report

**Custom Report Builder:**
- Metric selector (add multiple metrics)
- Dimension selector (group by)
- Date range
- Filter by country/channel
- Export: PDF, CSV, Email

---

### 4.19 Admin Settings (`/admin`)

| Attribute | Detail |
|---|---|
| **Purpose** | Platform configuration and user management |
| **Target Users** | Data Platform Engineer (role-restricted) |

**Sections:**
- **User Management** — List users, invite new, assign roles
- **Roles & Permissions** — Define what each role can see/do
- **API Settings** — Manage API keys, rate limits
- **Dashboard Configuration** — Set default filters, custom KPIs
- **Feature Flags** — Enable/disable features (AI Assistant, real-time, etc.)
- **Theme Settings** — Default theme, accent color, logo upload

---

## 5. Component Architecture

### 5.1 Layout Components

#### `sidebar.tsx`
Collapsible sidebar navigation.
- **Props:** `collapsed: boolean`, `onToggle: () => void`
- **States:** Expanded (240px), Collapsed (64px icon-only)
- **Features:** Group headers, active state (blue left border), badge counts on Alerts icon, tooltip on collapsed state
- **Role-awareness:** Admin section only shown to `DATA_PLATFORM_ENGINEER` role

#### `top-nav.tsx`
Global top navigation bar.
- **Height:** 64px
- **Left:** Hamburger menu (mobile) + Breadcrumb
- **Center:** Global search input (Cmd+K shortcut)
- **Right:** Date range quick picker, notification bell with badge, user avatar dropdown
- **User dropdown:** Profile, Settings, Sign Out

#### `page-header.tsx`
Consistent page header.
- **Props:** `title: string`, `subtitle?: string`, `actions?: ReactNode`, `breadcrumbs?: Crumb[]`
- **Variants:** Default, with tabs, with action buttons

### 5.2 Dashboard Components

#### `kpi-card.tsx`
Single metric display card.
- **Props:**
  ```typescript
  interface KPICardProps {
    label: string
    value: string | number
    unit?: string
    trend?: number        // percentage change
    trendDirection?: 'up' | 'down' | 'flat'
    variant?: 'default' | 'success' | 'warning' | 'critical'
    icon?: LucideIcon
    isLoading?: boolean
    lastUpdated?: string
  }
  ```
- **Visual:** Large value, small label below, trend arrow top-right, icon top-left
- **Variants:** Default (neutral), success (green), warning (amber), critical (red)

#### `metric-grid.tsx`
Responsive grid of KPI cards.
- **Layout:** CSS Grid, 4 columns on desktop, 2 on tablet, 1 on mobile
- **Breakpoints:** `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`

#### `chart-card.tsx`
Card wrapper for charts.
- **Props:** `title: string`, `subtitle?: string`, `children: ReactNode`, `period?: string`, `actions?: ReactNode`
- **Features:** Title, optional subtitle, period selector dropdown, action buttons

#### `insight-card.tsx`
AI-generated insight display.
- **Props:** `icon?: LucideIcon`, `title: string`, `description: string`, `action?: { label: string, onClick: () => void }`
- **Visual:** Blue left border accent, subtle background tint

### 5.3 Chart Components

All charts wrap Recharts with consistent props.

#### `line-chart.tsx`
```typescript
interface LineChartProps {
  data: Record<string, unknown>[]
  xKey: string
  yKey: string | string[]   // allow multiple y for multi-line
  title?: string
  subtitle?: string
  height?: number            // default 300
  showGrid?: boolean
  showTooltip?: boolean
  showLegend?: boolean
  comparisonData?: Record<string, unknown>[]  // for yesterday overlay
  comparisonKey?: string
  referenceLine?: { y: number, label: string }
  colors?: string[]
}
```

#### `bar-chart.tsx`
Same props as LineChart with `orientation?: 'vertical' | 'horizontal'`

#### `area-chart.tsx`
Same as LineChart with `filled: true` and gradient fill

#### `pie-chart.tsx`
```typescript
interface PieChartProps {
  data: { name: string, value: number, color?: string }[]
  title?: string
  height?: number
  innerRadius?: number  // for donut chart, default 0
  showLabel?: boolean
  labelKey?: 'name' | 'value' | 'percent'
}
```

#### `donut-chart.tsx`
Inherits PieChart with `innerRadius={60}`

### 5.4 Table Components

#### `data-table.tsx`
Generic sortable, filterable table.
- **Props:** `columns: ColumnDef[]`, `data: T[]`, `pageSize?: number`, `searchable?: boolean`
- **Features:** Column sorting (click header), pagination, search bar, column visibility toggle
- **Empty State:** "No data found" with illustration
- **Loading State:** Skeleton rows

#### `live-events-table.tsx`
Real-time events table with new-row highlight.
- **Props:** Same as DataTable + `highlightField?: string` (field to watch for new values)
- **Animation:** New row flashes `#3b82f6` (blue) for 2 seconds then fades
- **Auto-scroll:** New rows appear at top; table auto-scrolls unless user has scrolled up

#### `alerts-table.tsx`
Alerts-specific table with severity badges and action buttons.

### 5.5 Filter Components

All filters sync with URL query params via `use-filters` hook.

#### `date-range-filter.tsx`
```typescript
interface DateRangeFilterProps {
  value?: { from: Date, to: Date }
  onChange: (range: { from: Date, to: Date }) => void
  presets?: { label: string, days: number }[]  // default: 1h, 24h, 7d, 30d
}
```

#### `channel-filter.tsx`, `region-filter.tsx`, `category-filter.tsx`
Multi-select checkbox filters. Options loaded from `lib/graphql/queries.ts` enum values.

### 5.6 Customer Components

#### `customer-profile-card.tsx`
Customer header with avatar, name, tier badge, risk score gauge.

#### `customer-timeline.tsx`
Vertical timeline of customer events (orders, payments, behavior).

#### `customer-risk-score.tsx`
Gauge visualization 0-100 with color zones (green 0-30, amber 30-60, red 60-100).

### 5.7 AI Components

#### `chat-panel.tsx`
Chat interface with message list and input.
- **Message types:** user (right-aligned blue), assistant (left-aligned gray), system
- **Attachments:** SQL code blocks, chart previews, InsightCards
- **Actions per message:** Copy, Regenerate (for assistant), "Use in Dashboard"

#### `suggested-prompts.tsx`
Sidebar of clickable suggested questions, grouped by category (Business, Operations, Customers, Technical).

#### `sql-explanation.tsx`
Expandable panel showing: the SQL query, explanation in plain English, estimated row count, execution time.

### 5.8 Shared Components

#### `loading-state.tsx`
Skeleton components for: `KPICardSkeleton`, `ChartSkeleton`, `TableSkeleton`, `PageSkeleton`

#### `empty-state.tsx`
- **Props:** `icon?: LucideIcon`, `title: string`, `description?: string`, `action?: { label: string, onClick: () => void }`

#### `error-state.tsx`
- **Props:** `title?: string`, `error?: string`, `onRetry?: () => void`
- **Visual:** Red-tinted card with AlertTriangle icon

#### `status-badge.tsx`
- **Variants:** `success`, `warning`, `error`, `pending`, `info`, `neutral`
- **Size:** `sm` | `md` | `lg`

#### `live-badge.tsx`
Pulsing green dot + "Live" text. Animation: `animate-pulse` tailwind class.

#### `refresh-indicator.tsx`
"Updated X seconds ago" with manual refresh icon button.

---

## 6. Design System

### 6.1 Color Palette

```
Brand Colors:
  slate-50  (#f8fafc)   — Background
  slate-100 (#f1f5f9)   — Card background (light mode)
  slate-900 (#0f172a)   — Card background (dark mode)
  slate-800 (#1e293b)   — Sidebar (dark mode)
  blue-600  (#2563eb)   — Primary action
  blue-700  (#1d4ed8)   — Primary action hover

Semantic Colors:
  success:  emerald-500  (#10b981) — green
  warning:  amber-500   (#f59e0b) — amber
  error:    red-500     (#ef4444) — red
  info:     blue-500    (#3b82f6) — blue
  neutral:  slate-400   (#94a3b8) — gray

Risk Severity:
  critical: red-600     (#dc2626)
  high:     orange-500  (#f97316)
  medium:   yellow-500  (#eab308)
  low:      blue-500   (#3b82f6)
  none:     slate-400  (#94a3b8)

Chart Palette:
  ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16']
```

### 6.2 Typography

```
Font Family: Inter (Google Fonts), system-ui fallback
Weights: 400 (body), 500 (label), 600 (subheading), 700 (heading)

Scale:
  text-xs   : 12px / 16px  — Caption, timestamps
  text-sm   : 14px / 20px  — Body, table cells
  text-base : 16px / 24px  — Large body
  text-lg   : 18px / 28px  — Card titles
  text-xl   : 20px / 28px  — Page titles
  text-2xl  : 24px / 32px  — KPI values
  text-3xl  : 30px / 36px  — Hero KPIs
```

### 6.3 Spacing & Layout

```
Page padding: 24px (p-6)
Card padding: 16px (p-4)
Gap between cards: 16px (gap-4)
Section gap: 24px (gap-6)
Max content width: 1600px (max-w-[1600px])
```

### 6.4 Card Design

```typescript
// Light mode
bg-white border border-slate-200 rounded-xl shadow-sm

// Dark mode
bg-slate-900 border border-slate-800 rounded-xl shadow-sm

// KPI Card specific
hover:shadow-md transition-shadow duration-200
```

### 6.5 Status Badges

```
Success: bg-emerald-100 text-emerald-700 border border-emerald-200
Warning: bg-amber-100 text-amber-700 border border-amber-200
Error:   bg-red-100 text-red-700 border border-red-200
Info:    bg-blue-100 text-blue-700 border border-blue-200
Pending: bg-slate-100 text-slate-700 border border-slate-200
```

### 6.6 Dark/Light Mode

Using `next-themes` with `class` strategy.
- Toggle in top-nav
- Persisted in localStorage
- All components use `dark:` variants
- Charts re-render on theme change (Recharts supports dark mode)

---

## 7. GraphQL Data Contracts

### 7.1 `executiveSummary`

```typescript
query ExecutiveSummary($input: ExecutiveSummaryInput!): ExecutiveSummary

input ExecutiveSummaryInput {
  dateRange: DateRangeInput!
  countries: [String!]
  channels: [String!]
}

input DateRangeInput {
  from: String!  // ISO8601
  to: String!
}

type ExecutiveSummary {
  liveRevenue: Metric!
  totalOrders: Metric!
  avgOrderValue: Metric!
  paymentSuccessRate: Metric!
  deliveryDelayRate: Metric!
  fraudAlertCount: Metric!
  stockoutRiskCount: Metric!
  activeCustomers: Metric!
  revenueTrend: [TimeSeriesPoint!]!
  orderStatusBreakdown: [StatusCount!]!
  topCategories: [CategoryPerformance!]!
  aiSummary: String!
}

type Metric {
  value: Float!
  unit: String
  trend: Float          // percentage change vs previous period
  trendDirection: String // "up" | "down" | "flat"
  lastUpdated: String!   // ISO8601
}

type TimeSeriesPoint {
  timestamp: String!
  value: Float!
  comparisonValue: Float  // optional, for vs-previous-period overlay
}

type StatusCount {
  status: String!
  count: Int!
  percentage: Float!
}

type CategoryPerformance {
  category: String!
  revenue: Float!
  orderCount: Int!
  percentageOfTotal: Float!
}
```

### 7.2 `liveOrders`

```typescript
query LiveOrders($input: LiveOrdersInput!): LiveOrdersPayload

input LiveOrdersInput {
  dateRange: DateRangeInput!
  countries: [String!]
  channels: [String!]
  status: [String!]
  limit: Int = 100
  offset: Int = 0
}

type LiveOrdersPayload {
  orders: [Order!]!
  totalCount: Int!
  summary: OrdersSummary!
}

type Order {
  orderId: ID!
  customerId: String!
  customerName: String
  orderTimestamp: String!
  status: String!        // completed | pending | failed | cancelled
  totalAmount: Float!
  currency: String!
  channel: String!      // POS | Web | Mobile | App
  country: String!
  itemCount: Int!
  paymentStatus: String
  deliveryStatus: String
  fraudScore: Float
}

type OrdersSummary {
  totalOrders: Int!
  totalRevenue: Float!
  avgOrderValue: Float!
  ordersByStatus: [StatusCount!]!
  ordersByChannel: [ChannelCount!]!
  revenueByChannel: [ChannelRevenue!]!
}

type ChannelCount {
  channel: String!
  count: Int!
}

type ChannelRevenue {
  channel: String!
  revenue: Float!
}
```

### 7.3 `paymentHealth`

```typescript
query PaymentHealth($input: PaymentHealthInput!): PaymentHealthPayload

input PaymentHealthInput {
  dateRange: DateRangeInput!
  countries: [String!]
  paymentMethods: [String!]
}

type PaymentHealthPayload {
  totalTransactions: Metric!
  successRate: Metric!
  failedCount: Metric!
  avgLatencyMs: Metric!
  failureReasons: [FailureReasonCount!]!
  paymentsByMethod: [MethodPerformance!]!
  latencyTrend: [TimeSeriesPoint!]!
  recentFailures: [FailedPayment!]!
}

type FailureReasonCount {
  reason: String!
  count: Int!
  percentage: Float!
}

type MethodPerformance {
  method: String!
  totalCount: Int!
  successCount: Int!
  successRate: Float!
  avgLatencyMs: Float!
}

type FailedPayment {
  paymentId: ID!
  orderId: String!
  customerId: String!
  customerName: String
  amount: Float!
  currency: String!
  failureReason: String!
  paymentMethod: String!
  timestamp: String!
}

type Metric {
  value: Float!
  unit: String
  trend: Float
  trendDirection: String
  lastUpdated: String!
}
```

### 7.4 `inventorySnapshot`

```typescript
query InventorySnapshot($input: InventorySnapshotInput!): InventorySnapshotPayload

input InventorySnapshotInput {
  countries: [String!]
  categories: [String!]
}

type InventorySnapshotPayload {
  totalProducts: Metric!
  inStockRate: Metric!
  lowStockCount: Metric!
  outOfStockCount: Metric!
  stockDistribution: [StockDistribution!]!
  lowStockProducts: [LowStockProduct!]!
  stockoutRiskProducts: [StockoutRiskProduct!]!
  movementTrend: [TimeSeriesPoint!]!
}

type StockDistribution {
  status: String!  // in_stock | low_stock | out_of_stock
  count: Int!
  percentage: Float!
}

type LowStockProduct {
  productId: String!
  productName: String!
  category: String!
  currentStock: Int!
  reorderPoint: Int!
  daysOfSupply: Float!
  warehouse: String
}

type StockoutRiskProduct {
  productId: String!
  productName: String!
  category: String!
  currentStock: Int!
  daysUntilStockout: Float!
  velocity: Float!  // units sold per day
}
```

### 7.5 `deliveryPerformance`

```typescript
query DeliveryPerformance($input: DeliveryPerformanceInput!): DeliveryPerformancePayload

input DeliveryPerformanceInput {
  dateRange: DateRangeInput!
  countries: [String!]
  carriers: [String!]
}

type DeliveryPerformancePayload {
  totalDeliveries: Metric!
  onTimeRate: Metric!
  avgDeliveryTimeHours: Metric!
  delayedCount: Metric!
  onTimeVsDelayed: [StatusCount!]!
  performanceByCarrier: [CarrierPerformance!]!
  delayReasons: [DelayReasonCount!]!
  slaBreaches: [SLABreach!]!
}

type CarrierPerformance {
  carrier: String!
  totalDeliveries: Int!
  onTimeCount: Int!
  onTimeRate: Float!
  avgDeliveryTimeHours: Float!
}

type DelayReasonCount {
  reason: String!
  count: Int!
  percentage: Float!
}

type SLABreach {
  orderId: String!
  customerId: String!
  customerName: String
  carrier: String!
  expectedDate: String!
  actualDate: String
  delayHours: Float!
  reason: String!
}
```

### 7.6 `fraudAlerts`

```typescript
query FraudAlerts($input: FraudAlertsInput!): FraudAlertsPayload

input FraudAlertsInput {
  dateRange: DateRangeInput!
  countries: [String!]
  minScore: Float = 0.0
  severity: [String!]
}

type FraudAlertsPayload {
  fraudAlertCount: Metric!
  blockedAmount: Metric!
  fraudRate: Metric!
  avgFraudScore: Metric!
  alertsBySeverity: [SeverityCount!]!
  fraudTrend: [TimeSeriesPoint!]!
  fraudByType: [FraudTypeCount!]!
  highRiskTransactions: [HighRiskTransaction!]!
}

type SeverityCount {
  severity: String!  // high | medium | low
  count: Int!
  percentage: Float!
}

type FraudTypeCount {
  fraudType: String!
  count: Int!
}

type HighRiskTransaction {
  orderId: String!
  customerId: String!
  customerName: String
  fraudScore: Float!
  riskFactors: [String!]!
  amount: Float!
  currency: String!
  timestamp: String!
}
```

### 7.7 `customer360`

```typescript
query Customer360($customerId: ID!): Customer360Payload

type Customer360Payload {
  customer: CustomerProfile!
  lifetimeValue: Metric!
  orderCount: Int!
  avgOrderValue: Float!
  churnRiskScore: Float!
  churnRiskLevel: String!  // low | medium | high | critical
  recentOrders: [OrderSummary!]!
  paymentHistory: [PaymentSummary!]!
  deliveryHistory: [DeliverySummary!]!
  behaviorTimeline: [BehaviorEvent!]!
  recommendationEngagement: RecommendationStats
}

type CustomerProfile {
  customerId: ID!
  email: String!
  firstName: String!
  lastName: String!
  phone: String
  loyaltyTier: String!
  customerSegment: String!
  country: String!
  joinDate: String!
  lastOrderDate: String
  isActive: Boolean!
}

type OrderSummary {
  orderId: ID!
  orderTimestamp: String!
  status: String!
  totalAmount: Float!
  itemCount: Int!
}

type BehaviorEvent {
  timestamp: String!
  eventType: String!  // page_view | add_to_cart | wishlist | review | return
  description: String!
  productId: String
  productName: String
}
```

### 7.8 `customerSegments`

```typescript
query CustomerSegments($dateRange: DateRangeInput): CustomerSegmentsPayload

type CustomerSegmentsPayload {
  segments: [SegmentSummary!]!
  customerComposition: [SegmentCount!]!
  acquisitionTrend: [TimeSeriesPoint!]!
  churnTrend: [TimeSeriesPoint!]!
}

type SegmentSummary {
  segment: String!
  count: Int!
  percentageOfTotal: Float!
  avgLTV: Float!
  avgAOV: Float!
  avgOrdersPerCustomer: Float!
  churnRate: Float!
  trend: Float!
  trendDirection: String!
}
```

### 7.9 `recommendationPerformance`

```typescript
query RecommendationPerformance($input: RecommendationInput!): RecommendationPayload

type RecommendationPayload {
  impressions: Metric!
  clicks: Metric!
  ctr: Metric!
  conversions: Metric!
  revenueFromRecs: Metric!
  funnel: [FunnelStep!]!
  ctrByType: [RecommendationTypeStat!]!
  topRecommendedProducts: [RecommendedProduct!]!
}

type FunnelStep {
  stage: String!
  count: Int!
  dropoffRate: Float
}

type RecommendationTypeStat {
  recommendationType: String!
  impressions: Int!
  clicks: Int!
  ctr: Float!
}

type RecommendedProduct {
  productId: String!
  productName: String!
  impressions: Int!
  clicks: Int!
  conversions: Int!
  revenue: Float!
}
```

### 7.10 `activeAlerts`

```typescript
query ActiveAlerts($input: ActiveAlertsInput): ActiveAlertsPayload

input ActiveAlertsInput {
  severities: [String!]
  statuses: [String!]  // open | acknowledged | resolved
  categories: [String!]
}

type ActiveAlertsPayload {
  totalActive: Int!
  criticalCount: Int!
  highCount: Int!
  alerts: [Alert!]!
}

type Alert {
  alertId: ID!
  title: String!
  description: String!
  severity: String!
  status: String!
  category: String!
  timestamp: String!
  acknowledgedAt: String
  resolvedAt: String
  assignedTo: String
  source: String!
}
```

---

## 8. Real-Time Interaction Model

### 8.1 Polling Strategy

| Page Type | Interval | Rationale |
|-----------|----------|-----------|
| Executive Overview | 5 seconds | Highest priority, most volatile |
| Live Operations (Orders, Fraud) | 10 seconds | Near-real-time needed |
| Operational (Inventory, Delivery) | 15 seconds | Slower-moving but important |
| Analytical (Segments, Products) | 60 seconds | Slow-moving, expensive queries |
| Data Products (Catalog, Quality) | 5 minutes | Near-static metadata |

### 8.2 Live Indicator

- Pulsing green dot (`animate-pulse` in top-right of page header)
- Text: "Live" in green
- When paused: Static gray dot + "Paused" text

### 8.3 Last Updated Timestamp

Format: "Updated 5 seconds ago" → "Updated 2 minutes ago" (capped at "Updated 1 hour ago")

### 8.4 New Row Highlight

```css
@keyframes newRowFlash {
  0% { background-color: #3b82f6; }   /* blue-500 */
  100% { background-color: transparent; }
}
.animation-flash {
  animation: newRowFlash 2s ease-out forwards;
}
```

### 8.5 Pause/Resume

Floating button bottom-right corner:
- Pause icon → pauses polling, stops new row animations
- Resume icon → resumes polling immediately

### 8.6 Manual Refresh

Refresh icon button in page header. Click triggers immediate data fetch and resets polling timer.

---

## 9. Navigation & Layout Spec

### 9.1 Sidebar (240px expanded / 64px collapsed)

```
┌─────────────────────┐
│ [Logo] Retail       │  ← 64px when collapsed (icon only)
│ Command Center      │
├─────────────────────┤
│ ▼ EXECUTIVE        │  ← Group header, not clickable
│   📊 Overview      │
├─────────────────────┤
│ ▼ LIVE OPERATIONS  │
│   📦 Orders        │
│   💳 Payments      │
│   📊 Inventory     │
│   🚚 Delivery      │
│   ⚠️ Fraud         │
├─────────────────────┤
│ ▼ CUSTOMER INTEL   │
│   👤 Customer 360  │
│   👥 Segments      │
│   📈 Behavior       │
├─────────────────────┤
│ ▼ PRODUCT INTEL    │
│   📱 Performance   │
│   🏷️ Category     │
│   🎯 Recommendations
├─────────────────────┤
│ ▼ DATA PRODUCTS    │
│   📋 Catalog       │
│   🔗 Lineage       │
│   ✅ Quality       │
│   📊 Usage         │
├─────────────────────┤
│ 🤖 AI Assistant    │
│ 🔔 Alerts          │
│ 📑 Reports         │
├─────────────────────┤
│ ⚙️ Admin [HIDE]   │  ← Only for Data Platform Engineer role
└─────────────────────┘
```

### 9.2 Top Navigation Bar

```
┌──────────────────────────────────────────────────────────────────────────┐
│ ☰  │ 🔍 Search (Cmd+K)                        │ 📅 Today │ 🔔 3 │ 👤 │
└──────────────────────────────────────────────────────────────────────────┘
```

- Breadcrumb left of search
- Global search: Cmd+K opens modal with fuzzy search across orders, customers, products
- Date picker: Shows selected range, opens calendar popover
- Notification bell: Badge count, dropdown list of recent alerts
- User avatar: Dropdown with profile, settings, sign out

### 9.3 Responsive Behavior

```
Desktop (≥1280px): Full sidebar (240px) + Content
Tablet (768-1279px): Collapsed sidebar (64px) + Content
Mobile (<768px): Bottom tab bar (5 icons) + Content, sidebar becomes sheet
```

### 9.4 Role-Based Navigation

| Route | Roles With Access |
|-------|-------------------|
| /admin | Data Platform Engineer |
| /data-products/* | All authenticated users |
| /live-operations/* | All authenticated users |
| /executive | CRO, Executive, VP Ops |
| /ai-assistant | All authenticated users |

---

## 10. Accessibility Requirements

### 10.1 WCAG 2.1 AA Compliance Target

- All interactive elements keyboard accessible (Tab / Enter / Escape)
- Focus rings visible on all focusable elements (`focus-visible:ring`)
- ARIA labels on icon-only buttons
- ARIA live regions for real-time updates (`aria-live="polite"`)
- Color not used as sole indicator (icons + color for status)

### 10.2 Keyboard Navigation

| Key | Action |
|-----|--------|
| Tab | Move focus forward |
| Shift+Tab | Move focus backward |
| Enter/Space | Activate button or toggle |
| Escape | Close modal/drawer |
| Cmd+K | Open global search |
| Arrow Up/Down | Navigate menu or list |
| R | Refresh (when table focused) |

### 10.3 Screen Reader Support

- All charts have `aria-label` with data summary
- Tables have `aria-sort` on sortable columns
- Status badges have descriptive text, not just color
- Page titles update on navigation

### 10.4 Color Contrast

- All text meets 4.5:1 contrast ratio (AA)
- Large text (18px+) meets 3:1 (AA)
- Interactive elements have 3:1 against adjacent colors

---

## 11. Frontend Folder Structure

```
nextjs-ui/
├── app/
│   ├── layout.tsx                    # Root layout (Providers, Sidebar, TopNav)
│   ├── page.tsx                     # Redirect to /executive
│   ├── executive/
│   │   └── page.tsx                 # Executive overview
│   ├── live-operations/
│   │   ├── orders/page.tsx
│   │   ├── payments/page.tsx
│   │   ├── inventory/page.tsx
│   │   ├── delivery/page.tsx
│   │   └── fraud/page.tsx
│   ├── customer-intelligence/
│   │   ├── customer-360/page.tsx
│   │   ├── segments/page.tsx
│   │   └── behavior/page.tsx
│   ├── product-intelligence/
│   │   ├── performance/page.tsx
│   │   ├── category/page.tsx
│   │   └── recommendations/page.tsx
│   ├── data-products/
│   │   ├── catalog/page.tsx
│   │   ├── lineage/page.tsx
│   │   ├── quality/page.tsx
│   │   └── usage/page.tsx
│   ├── ai-assistant/
│   │   └── page.tsx
│   ├── alerts/
│   │   └── page.tsx
│   ├── reports/
│   │   └── page.tsx
│   └── admin/
│       └── page.tsx
│
├── components/
│   ├── layout/
│   │   ├── sidebar.tsx
│   │   ├── top-nav.tsx
│   │   ├── page-header.tsx
│   │   ├── theme-toggle.tsx
│   │   └── providers.tsx            # Apollo, Theme, QueryClient providers
│   ├── dashboard/
│   │   ├── kpi-card.tsx
│   │   ├── metric-grid.tsx
│   │   ├── chart-card.tsx
│   │   ├── insight-card.tsx
│   │   └── alert-card.tsx
│   ├── charts/
│   │   ├── line-chart.tsx
│   │   ├── bar-chart.tsx
│   │   ├── area-chart.tsx
│   │   ├── pie-chart.tsx
│   │   ├── donut-chart.tsx
│   │   └── heatmap.tsx
│   ├── tables/
│   │   ├── data-table.tsx
│   │   ├── live-events-table.tsx
│   │   └── alerts-table.tsx
│   ├── filters/
│   │   ├── date-range-filter.tsx
│   │   ├── channel-filter.tsx
│   │   ├── region-filter.tsx
│   │   └── category-filter.tsx
│   ├── customer/
│   │   ├── customer-profile-card.tsx
│   │   ├── customer-timeline.tsx
│   │   └── customer-risk-score.tsx
│   ├── ai/
│   │   ├── chat-panel.tsx
│   │   ├── suggested-prompts.tsx
│   │   └── sql-explanation.tsx
│   └── shared/
│       ├── loading-state.tsx
│       ├── empty-state.tsx
│       ├── error-state.tsx
│       ├── status-badge.tsx
│       ├── live-badge.tsx
│       └── refresh-indicator.tsx
│
├── lib/
│   ├── graphql/
│   │   ├── client.ts          # Apollo Client setup
│   │   ├── queries.ts         # All GraphQL query documents
│   │   └── types.ts            # TypeScript interfaces
│   └── utils/
│       ├── formatters.ts       # formatCurrency, formatDate, formatNumber
│       └── cn.ts               # classnames utility (clsx + tailwind-merge)
│
├── hooks/
│   ├── use-dashboard-data.ts  # Generic polling hook
│   ├── use-live-orders.ts     # 5s polling for orders
│   ├── use-filters.ts          # URL ↔ filter state sync
│   └── use-realtime.ts         # Pause/resume global realtime state
│
└── types/
    ├── retail.ts              # Domain types: Order, Payment, Customer, etc.
    └── graphql.ts               # GraphQL-generated types (or manual equivalents)
```

---

## 12. Implementation Roadmap

### Phase A: Foundation (Priority 1)
1. Set up `app/layout.tsx` with Providers, Sidebar, TopNav
2. Create shared components: KPICard, StatusBadge, LoadingState, ErrorState, EmptyState
3. Create chart components: LineChart, BarChart, AreaChart, PieChart, DonutChart
4. Set up `lib/graphql/client.ts` + `types.ts` + `queries.ts`
5. Create `use-filters.ts` and `use-realtime.ts` hooks
6. Create Executive Overview page (most critical for demos)

### Phase B: Core Pages (Priority 2)
7. Create Orders Monitor page
8. Create Payment Health page
9. Create Inventory Control Tower page
10. Create Fraud Monitoring page
11. Create Delivery Performance page
12. Create Filters components

### Phase C: Intelligence Pages (Priority 3)
13. Create Customer 360 page
14. Create Customer Segments page
15. Create Behavior Analytics page
16. Create Product Performance page
17. Create Category Performance page
18. Create Recommendation Analytics page

### Phase D: Platform Pages (Priority 4)
19. Create Data Product Catalog page
20. Create Data Lineage page
21. Create Data Quality page
22. Create AI Assistant page
23. Create Alerts & Incidents page
24. Create Reports page
25. Create Admin Settings page

### Phase E: Polish (Priority 5)
26. Add theme toggle (dark/light mode)
27. Add global search (Cmd+K)
28. Add notification system
29. Add keyboard shortcuts
30. Accessibility audit and fixes
31. Mobile responsive testing

---

## 13. Production Readiness Checklist

### Functionality
- [ ] All 19 pages implemented and routing working
- [ ] All GraphQL queries return correct data shapes
- [ ] Real-time polling works on all pages
- [ ] Pause/resume persists across navigation
- [ ] Filters sync with URL and persist on refresh
- [ ] Dark/light mode toggle works everywhere
- [ ] Empty states show for all pages with no data
- [ ] Loading skeletons show during data fetch
- [ ] Error states show on API failure with retry
- [ ] Keyboard navigation works for all interactions

### Performance
- [ ] Page load < 2s on initial load
- [ ] Polling doesn't cause memory leaks (cleanup on unmount)
- [ ] Charts re-render efficiently (useMemo)
- [ ] Tables virtualized for 1000+ rows
- [ ] Images lazy loaded

### Security
- [ ] No SQL injection (queries use variables)
- [ ] API keys not exposed in client
- [ ] Role-based access enforced on protected routes
- [ ] XSS prevention (React escapes by default)

### Monitoring
- [ ] Error boundaries catch React errors
- [ ] `window.error` caught and logged
- [ ] Analytics events fired on key actions
