 #!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username postgres --dbname 3cxcdr <<-EOSQL
    GRANT CONNECT ON DATABASE 3cxcdr TO grafanareader;
    CREATE USER grafanareader WITH PASSWORD 'grafanareader';
    GRANT SELECT ON DATABASE 3cxcdr.* TO grafanareader;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafanareader;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO grafanareader;
EOSQL

