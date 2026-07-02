const { executeQuery } = require('./trinoClient');

const resolvers = {
  Query: {
    orders: async (_, { limit = 100, offset = 0 }) => {
      const query = `SELECT * FROM retail.orders LIMIT ${limit} OFFSET ${offset}`;
      return await executeQuery(query);
    },
    order: async (_, { id }) => {
      const query = `SELECT * FROM retail.orders WHERE order_id = '${id}' LIMIT 1`;
      const results = await executeQuery(query);
      return results[0] || null;
    },
    payments: async (_, { order_id }) => {
      const whereClause = order_id ? `WHERE order_id = '${order_id}'` : '';
      const query = `SELECT * FROM retail.payments ${whereClause}`;
      return await executeQuery(query);
    },
    inventory: async (_, { low_stock_only = false }) => {
      const whereClause = low_stock_only ? 'WHERE is_low_stock = true' : '';
      const query = `SELECT * FROM retail.inventory ${whereClause}`;
      return await executeQuery(query);
    },
    customers: async (_, { limit = 100 }) => {
      const query = `SELECT * FROM retail.customers LIMIT ${limit}`;
      return await executeQuery(query);
    },
    daily_aggregations: async (_, { start_date, end_date }) => {
      let whereClause = '';
      if (start_date && end_date) {
        whereClause = `WHERE aggregation_date BETWEEN '${start_date}' AND '${end_date}'`;
      }
      const query = `SELECT * FROM retail.daily_aggregations ${whereClause}`;
      return await executeQuery(query);
    },
  },
};

module.exports = resolvers;