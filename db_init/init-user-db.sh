 #!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username postgres --dbname 3cxcdr <<-EOSQL
    CREATE USER grafanareader WITH PASSWORD 'grafanareader';
    GRANT SELECT ON DATABASE 3cxcdr TO grafanareader;
EOSQL

