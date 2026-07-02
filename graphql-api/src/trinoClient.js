const trino = require('trino-client');

const client = trino.createClient({
  url: process.env.TRINO_HOST ? `http://${process.env.TRINO_HOST}:${process.env.TRINO_PORT || 8080}` : 'http://trino:8080',
  user: 'admin',
});

async function executeQuery(sql) {
  return new Promise((resolve, reject) => {
    client.query(sql)
      .then(result => {
        resolve(result.rows || []);
      })
      .catch(error => {
        console.error('Trino query error:', error);
        reject(error);
      });
  });
}

module.exports = { executeQuery };