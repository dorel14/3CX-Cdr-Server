 #!/bin/bash
psql -v ON_ERROR_STOP=1 --username postgres --dbname cdr3cxdb <<-EOSQL
    SELECT 'CREATE USER grafanareader' WHERE NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'grafanareader')\gexec
    ALTER USER grafanareader WITH PASSWORD 'grafanareader';
    GRANT CONNECT ON DATABASE cdr3cxdb TO grafanareader;
    GRANT SELECT ON DATABASE cdr3cxdb TO grafanareader;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafanareader;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO grafanareader;
    GRANT SELECT ON SEQUENCE public.call_data_records_details_id_seq TO grafanareader;
    GRANT SELECT ON SEQUENCE public.call_data_records_id_seq TO grafanareader;
    GRANT SELECT ON SEQUENCE public.extensions_id_seq TO grafanareader;
    GRANT SELECT ON SEQUENCE public.queues_id_seq TO grafanareader;
    GRANT SELECT ON TABLE public.alembic_version TO grafanareader;
    GRANT SELECT ON TABLE public.call_data_records TO grafanareader;
    GRANT SELECT ON TABLE public.call_data_records_details TO grafanareader;
    GRANT SELECT ON TABLE public.extensions TO grafanareader;
    GRANT SELECT ON TABLE public.extensiontoqueuelink TO grafanareader;
    GRANT SELECT ON TABLE public.queues TO grafanareader;
EOSQL
