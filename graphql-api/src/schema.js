const typeDefs = `#graphql
  type Order {
    order_id: ID!
    customer_id: String!
    order_timestamp: String!
    status: String!
    total_amount: Float!
    currency: String!
    payment_method: String!
    store_id: String!
    country: String!
  }

  type Payment {
    payment_id: ID!
    order_id: String!
    amount: Float!
    currency: String!
    payment_status: String!
    payment_method: String!
  }

  type Inventory {
    product_id: String!
    product_name: String!
    quantity_on_hand: Int!
    is_low_stock: Boolean!
    is_out_of_stock: Boolean!
  }

  type Customer {
    customer_id: String!
    email: String!
    first_name: String!
    last_name: String!
    loyalty_tier: String!
    is_active: Boolean!
  }

  type DailyAggregation {
    aggregation_date: String!
    country: String!
    total_orders: Int!
    total_revenue: Float!
    fraud_attempts: Int!
  }

  type Query {
    orders(limit: Int, offset: Int): [Order!]!
    order(id: ID!): Order
    payments(order_id: String): [Payment!]!
    inventory(low_stock_only: Boolean): [Inventory!]!
    customers(limit: Int): [Customer!]!
    daily_aggregations(start_date: String, end_date: String): [DailyAggregation!]!
  }
`;

module.exports = typeDefs;