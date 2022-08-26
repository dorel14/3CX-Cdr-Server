 #!/bin/bash
psql -v ON_ERROR_STOP=1 --username postgres --dbname cdr3cxdb <<-EOSQL
    SELECT 'CREATE USER grafanareader' WHERE NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'grafanareader')\gexec
    SELECT 'CREATE USER root' WHERE NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'root')\gexec
    GRANT CONNECT ON DATABASE cdr3cxdb TO grafanareader;
    GRANT SELECT ON DATABASE cdr3cxdb TO grafanareader;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafanareader;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO grafanareader;
EOSQL
