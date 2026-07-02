const { TrinoDriver } = require("@cubejs-backend/trino-driver");

const CLUSTER_NAME = process.env.TRINO_CLUSTER_NAME || "minervac";

class DataSenseTrinoDriver extends TrinoDriver {
  constructor(opts = {}) {
    super(opts);

    const origRequest = this.client.request.bind(this.client);
    this.client.request = function (reqOpts, callback) {
      if (reqOpts && typeof reqOpts === "object") {
        if (!reqOpts.headers) reqOpts.headers = {};
        reqOpts.headers["cluster-name"] = CLUSTER_NAME;
      }
      return origRequest(reqOpts, callback);
    };
  }
}

function requireOptional(packageName, label) {
  try {
    return require(packageName);
  } catch (e) {
    console.warn(`[cube] ${label} driver not loaded (${packageName}). npm install if needed.`);
    return null;
  }
}

const PostgresDriver = requireOptional("@cubejs-backend/postgres-driver", "Postgres/Redshift");
const SnowflakeDriver = requireOptional("@cubejs-backend/snowflake-driver", "Snowflake");
const BigQueryDriver = requireOptional("@cubejs-backend/bigquery-driver", "BigQuery");
const AthenaDriver = requireOptional("@cubejs-backend/athena-driver", "Athena");
const DatabricksDriver = requireOptional(
  "@cubejs-backend/databricks-jdbc-driver",
  "Databricks",
);
const MSSqlDriver = requireOptional("@cubejs-backend/mssql-driver", "MSSQL");
const DuckDBDriver = requireOptional("@cubejs-backend/duckdb-driver", "DuckDB");
const MySqlDriver = requireOptional("@cubejs-backend/mysql-driver", "MySQL");
const ClickHouseDriver = requireOptional("@cubejs-backend/clickhouse-driver", "ClickHouse");
const OracleDriver = requireOptional("@cubejs-backend/oracle-driver", "Oracle");
const SqliteDriver = requireOptional("@cubejs-backend/sqlite-driver", "SQLite");
const HiveDriver = requireOptional("@cubejs-backend/hive-driver", "Hive");
const MongoBIDriver = requireOptional("@cubejs-backend/mongobi-driver", "MongoBI");
const PinotDriver = requireOptional("@cubejs-backend/pinot-driver", "Pinot");
const DruidDriver = requireOptional("@cubejs-backend/druid-driver", "Druid");
const ElasticsearchDriver = requireOptional(
  "@cubejs-backend/elasticsearch-driver",
  "Elasticsearch",
);
const FireboltDriver = requireOptional("@cubejs-backend/firebolt-driver", "Firebolt");
const QuestDBDriver = requireOptional("@cubejs-backend/questdb-driver", "QuestDB");
const VerticaDriver = requireOptional("@cubejs-backend/vertica-driver", "Vertica");
const MaterializeDriver = requireOptional("@cubejs-backend/materialize-driver", "Materialize");
const prestodb = requireOptional("@cubejs-backend/prestodb-driver", "Presto");
const PrestoDriver = prestodb && prestodb.PrestoDriver;

function envBool(name) {
  const v = process.env[name];
  return v === "1" || String(v).toLowerCase() === "true";
}

function intEnv(name, fallback) {
  const v = process.env[name];
  if (v === undefined || v === "") return fallback;
  const n = parseInt(v, 10);
  return Number.isFinite(n) ? n : fallback;
}

/** Standard MySqlDriver / MongoBI-style config (see Cube MySQL docs). */
function mysqlDriverInstance(Driver, dataSourceTag, prefix) {
  if (!Driver) return null;
  return new Driver({
    dataSource: dataSourceTag,
    host: process.env[`${prefix}HOST`],
    port: intEnv(`${prefix}PORT`, 3306),
    database: process.env[`${prefix}DATABASE`],
    user: process.env[`${prefix}USER`],
    password: process.env[`${prefix}PASSWORD`],
    ssl: envBool(`${prefix}SSL`) ? {} : undefined,
  });
}

module.exports = {
  driverFactory: ({ dataSource } = {}) => {
    const ds = (dataSource || "default").toLowerCase();

    if (ds === "databricks" && DatabricksDriver) {
      return new DatabricksDriver({
        url: process.env.CUBEJS_DS_DATABRICKS_URL,
        httpPath: process.env.CUBEJS_DS_DATABRICKS_HTTP_PATH,
        token: process.env.CUBEJS_DS_DATABRICKS_TOKEN,
      });
    }
    if (ds === "snowflake" && SnowflakeDriver) {
      return new SnowflakeDriver({
        account: process.env.CUBEJS_DS_SNOWFLAKE_ACCOUNT,
        username: process.env.CUBEJS_DS_SNOWFLAKE_USER,
        password: process.env.CUBEJS_DS_SNOWFLAKE_PASSWORD,
        warehouse: process.env.CUBEJS_DS_SNOWFLAKE_WAREHOUSE,
      });
    }
    if ((ds === "postgresql" || ds === "postgres" || ds === "redshift") && PostgresDriver) {
      const pgPortRaw =
        process.env.CUBEJS_DS_POSTGRES_PORT || process.env.CUBEJS_DS_REDSHIFT_PORT;
      const pgPort = pgPortRaw ? parseInt(pgPortRaw, 10) : 5432;
      return new PostgresDriver({
        host: process.env.CUBEJS_DS_POSTGRES_HOST || process.env.CUBEJS_DS_REDSHIFT_HOST,
        port: Number.isFinite(pgPort) ? pgPort : 5432,
        database: process.env.CUBEJS_DS_POSTGRES_DB || process.env.CUBEJS_DS_REDSHIFT_DB,
        user: process.env.CUBEJS_DS_POSTGRES_USER || process.env.CUBEJS_DS_REDSHIFT_USER,
        password: process.env.CUBEJS_DS_POSTGRES_PASSWORD || process.env.CUBEJS_DS_REDSHIFT_PASSWORD,
        ssl: envBool("CUBEJS_DS_POSTGRES_SSL"),
      });
    }
    if (ds === "risingwave" && PostgresDriver) {
      return new PostgresDriver({
        host: process.env.CUBEJS_DS_RISINGWAVE_HOST,
        port: intEnv("CUBEJS_DS_RISINGWAVE_PORT", 4566),
        database: process.env.CUBEJS_DS_RISINGWAVE_DATABASE,
        user: process.env.CUBEJS_DS_RISINGWAVE_USER,
        password: process.env.CUBEJS_DS_RISINGWAVE_PASSWORD,
        ssl: envBool("CUBEJS_DS_RISINGWAVE_SSL"),
      });
    }
    if (ds === "bigquery" && BigQueryDriver) {
      return new BigQueryDriver({
        keyFilename: process.env.CUBEJS_DS_BIGQUERY_KEYFILE,
        credentials: process.env.CUBEJS_DS_BIGQUERY_CREDENTIALS_JSON
          ? JSON.parse(process.env.CUBEJS_DS_BIGQUERY_CREDENTIALS_JSON)
          : undefined,
        projectId: process.env.CUBEJS_DS_BIGQUERY_PROJECT,
      });
    }
    if (ds === "athena" && AthenaDriver) {
      return new AthenaDriver({
        credentials: {
          accessKeyId: process.env.CUBEJS_AWS_KEY,
          secretAccessKey: process.env.CUBEJS_AWS_SECRET,
        },
        region: process.env.CUBEJS_AWS_REGION || "us-east-1",
        s3OutputLocation: process.env.CUBEJS_ATHENA_S3_OUTPUT,
      });
    }

    const mssqlBase = (pfx) =>
      MSSqlDriver
        ? new MSSqlDriver({
            server: process.env[`${pfx}HOST`],
            port: intEnv(`${pfx}PORT`, 1433),
            database: process.env[`${pfx}DATABASE`],
            user: process.env[`${pfx}USER`],
            password: process.env[`${pfx}PASSWORD`],
            options: {
              encrypt: envBool(`${pfx}SSL`),
              useUTC: true,
            },
          })
        : null;

    if (ds === "mssql" && MSSqlDriver) {
      return mssqlBase("CUBEJS_DS_MSSQL_");
    }
    if (ds === "fabric" && MSSqlDriver) {
      return mssqlBase("CUBEJS_DS_FABRIC_");
    }
    if (ds === "synapse" && MSSqlDriver) {
      return mssqlBase("CUBEJS_DS_SYNAPSE_");
    }
    if (ds === "duckdb" && DuckDBDriver) {
      return new DuckDBDriver({
        databasePath: process.env.CUBEJS_DS_DUCKDB_DATABASE_PATH,
        motherDuckToken: process.env.CUBEJS_DS_DUCKDB_MOTHERDUCK_TOKEN,
      });
    }

    if (ds === "mysql" && MySqlDriver) {
      const c = mysqlDriverInstance(MySqlDriver, "mysql", "CUBEJS_DS_MYSQL_");
      if (c) return c;
    }
    if (ds === "singlestore" && MySqlDriver) {
      const c = mysqlDriverInstance(MySqlDriver, "singlestore", "CUBEJS_DS_SINGLESTORE_");
      if (c) return c;
    }
    if (ds === "mongobi" && MongoBIDriver) {
      const c = mysqlDriverInstance(MongoBIDriver, "mongobi", "CUBEJS_DS_MONGOBI_");
      if (c) return c;
    }

    if (ds === "clickhouse" && ClickHouseDriver) {
      return new ClickHouseDriver({
        dataSource: "clickhouse",
        host: process.env.CUBEJS_DS_CLICKHOUSE_HOST,
        port: intEnv("CUBEJS_DS_CLICKHOUSE_PORT", 8123),
        database: process.env.CUBEJS_DS_CLICKHOUSE_DATABASE,
        username: process.env.CUBEJS_DS_CLICKHOUSE_USER,
        password: process.env.CUBEJS_DS_CLICKHOUSE_PASSWORD,
        protocol: envBool("CUBEJS_DS_CLICKHOUSE_SSL") ? "https:" : "http:",
      });
    }

    if (ds === "oracle" && OracleDriver) {
      return new OracleDriver({
        host: process.env.CUBEJS_DS_ORACLE_HOST,
        port: intEnv("CUBEJS_DS_ORACLE_PORT", 1521),
        database: process.env.CUBEJS_DS_ORACLE_DATABASE,
        user: process.env.CUBEJS_DS_ORACLE_USER,
        password: process.env.CUBEJS_DS_ORACLE_PASSWORD,
      });
    }

    if (ds === "sqlite" && SqliteDriver) {
      return new SqliteDriver({
        dataSource: "sqlite",
        database: process.env.CUBEJS_DS_SQLITE_DATABASE,
      });
    }

    if (ds === "hive" && HiveDriver) {
      return new HiveDriver({
        host: process.env.CUBEJS_DS_HIVE_HOST,
        port: intEnv("CUBEJS_DS_HIVE_PORT", 10000),
        database: process.env.CUBEJS_DS_HIVE_DATABASE,
        username: process.env.CUBEJS_DS_HIVE_USER,
        password: process.env.CUBEJS_DS_HIVE_PASSWORD,
      });
    }

    if (ds === "pinot" && PinotDriver) {
      return new PinotDriver({
        host: process.env.CUBEJS_DS_PINOT_HOST,
        port: intEnv("CUBEJS_DS_PINOT_PORT", 8000),
        database: process.env.CUBEJS_DS_PINOT_DATABASE,
      });
    }

    if (ds === "druid" && DruidDriver) {
      return new DruidDriver({
        host: process.env.CUBEJS_DS_DRUID_HOST,
        port: intEnv("CUBEJS_DS_DRUID_PORT", 8082),
        database: process.env.CUBEJS_DS_DRUID_DATABASE,
        user: process.env.CUBEJS_DS_DRUID_USER,
        password: process.env.CUBEJS_DS_DRUID_PASSWORD,
      });
    }

    if (ds === "elasticsearch" && ElasticsearchDriver) {
      const esUrl =
        process.env.CUBEJS_DS_ELASTICSEARCH_URL ||
        (process.env.CUBEJS_DS_ELASTICSEARCH_HOST
          ? `${envBool("CUBEJS_DS_ELASTICSEARCH_SSL") ? "https" : "http"}://${
              process.env.CUBEJS_DS_ELASTICSEARCH_HOST
            }:${intEnv("CUBEJS_DS_ELASTICSEARCH_PORT", 9200)}`
          : undefined);
      return new ElasticsearchDriver({
        dataSource: "elasticsearch",
        url: esUrl,
        auth: {
          username: process.env.CUBEJS_DS_ELASTICSEARCH_USER,
          password: process.env.CUBEJS_DS_ELASTICSEARCH_PASSWORD,
        },
      });
    }

    if (ds === "firebolt" && FireboltDriver) {
      return new FireboltDriver({
        host: process.env.CUBEJS_DS_FIREBOLT_HOST,
        database: process.env.CUBEJS_DS_FIREBOLT_DATABASE,
        username: process.env.CUBEJS_DS_FIREBOLT_USER,
        password: process.env.CUBEJS_DS_FIREBOLT_PASSWORD,
      });
    }

    if (ds === "questdb" && QuestDBDriver) {
      return new QuestDBDriver({
        host: process.env.CUBEJS_DS_QUESTDB_HOST,
        port: intEnv("CUBEJS_DS_QUESTDB_PORT", 8812),
        database: process.env.CUBEJS_DS_QUESTDB_DATABASE,
        user: process.env.CUBEJS_DS_QUESTDB_USER,
        password: process.env.CUBEJS_DS_QUESTDB_PASSWORD,
      });
    }

    if (ds === "vertica" && VerticaDriver) {
      return new VerticaDriver({
        host: process.env.CUBEJS_DS_VERTICA_HOST,
        port: intEnv("CUBEJS_DS_VERTICA_PORT", 5433),
        database: process.env.CUBEJS_DS_VERTICA_DATABASE,
        user: process.env.CUBEJS_DS_VERTICA_USER,
        password: process.env.CUBEJS_DS_VERTICA_PASSWORD,
      });
    }

    if (ds === "materialize" && MaterializeDriver) {
      return new MaterializeDriver({
        host: process.env.CUBEJS_DS_MATERIALIZE_HOST,
        port: intEnv("CUBEJS_DS_MATERIALIZE_PORT", 6875),
        database: process.env.CUBEJS_DS_MATERIALIZE_DATABASE,
        user: process.env.CUBEJS_DS_MATERIALIZE_USER,
        password: process.env.CUBEJS_DS_MATERIALIZE_PASSWORD,
        ssl: envBool("CUBEJS_DS_MATERIALIZE_SSL") ? {} : undefined,
      });
    }

    if (ds === "presto" && PrestoDriver) {
      return new PrestoDriver({
        dataSource: "presto",
        host: process.env.CUBEJS_DS_PRESTO_HOST,
        port: intEnv("CUBEJS_DS_PRESTO_PORT", 8080),
        catalog: process.env.CUBEJS_DS_PRESTO_CATALOG,
        schema: process.env.CUBEJS_DS_PRESTO_SCHEMA,
        user: process.env.CUBEJS_DS_PRESTO_USER,
        basic_auth: process.env.CUBEJS_DS_PRESTO_PASSWORD
          ? {
              user: process.env.CUBEJS_DS_PRESTO_USER || "user",
              password: process.env.CUBEJS_DS_PRESTO_PASSWORD,
            }
          : undefined,
      });
    }

    /** Trino: prefer CUBEJS_DS_TRINO_* (compose); fall back to CUBEJS_DB_* (Cube docs / infra/cube/.env). */
    if (ds === "trino" || ds === "default") {
      const host =
        process.env.CUBEJS_DS_TRINO_HOST || process.env.CUBEJS_DB_HOST;
      const portRaw = process.env.CUBEJS_DS_TRINO_PORT || process.env.CUBEJS_DB_PORT;
      const portParsed = portRaw ? parseInt(portRaw, 10) : 8080;
      const port = Number.isFinite(portParsed) ? portParsed : 8080;
      const catalog =
        process.env.CUBEJS_DS_TRINO_CATALOG || process.env.CUBEJS_DB_PRESTO_CATALOG;
      const schema =
        process.env.CUBEJS_DS_TRINO_SCHEMA || process.env.CUBEJS_DB_SCHEMA;
      const user = process.env.CUBEJS_DS_TRINO_USER || process.env.CUBEJS_DB_USER;
      const password =
        process.env.CUBEJS_DS_TRINO_PASSWORD || process.env.CUBEJS_DB_PASS;
      if (host || portRaw || catalog) {
        return new DataSenseTrinoDriver({
          host,
          port,
          catalog,
          schema,
          user,
          basic_auth: password
            ? { user: user || "user", password }
            : undefined,
        });
      }
    }

    return new DataSenseTrinoDriver({});
  },

  contextToAppId: ({ securityContext }) =>
    `CUBEJS_APP_${securityContext?.org_id || "default"}`,

  scheduledRefreshContexts: async () => [
    { securityContext: { org_id: "default" } },
  ],

  queryRewrite: (query, { securityContext }) => {
    if (securityContext?.org_id && securityContext.org_id !== "default") {
      query.filters = query.filters || [];
      query.filters.push({
        member: "shared_tenant.org_id",
        operator: "equals",
        values: [securityContext.org_id],
      });
    }
    return query;
  },

  checkSqlAuth: async (req, username) => {
    const validUser = process.env.CUBEJS_SQL_USER || "datasense";
    const validPass = process.env.CUBEJS_SQL_PASSWORD || "";
    if (username === validUser) {
      return { password: validPass, securityContext: { org_id: "default" } };
    }
    throw new Error("Invalid SQL API credentials");
  },
};
