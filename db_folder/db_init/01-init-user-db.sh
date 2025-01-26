#!/bin/bash

set -e

# Update and install necessary packages
apk update && apk add --no-cache \
    musl \
    musl-utils \
    musl-locales \
    tzdata

# Set environment variables for timezone and locale
export TZ=${TZ}
export LANG=${LOCALE_LANGUAGE}.UTF-8
export LANGUAGE=${LOCALE_LANGUAGE}.UTF-8
export LC_ALL=${LOCALE_LANGUAGE}.UTF-8

# Set timezone
ln -s /usr/share/zoneinfo/${TZ} /etc/localtime

#createuser --superuser postgres
#createuser --superuser ${POSTGRES_USER}

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" template1  <<-EOSQL
    SELECT 'CREATE DATABASE ${POSTGRES_DB}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}')\gexec
    GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname ${POSTGRES_DB} <<-EOSQL
    SELECT 'CREATE USER grafanareader' WHERE NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'grafanareader')\gexec
    ALTER USER grafanareader WITH PASSWORD 'grafanareader';
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO grafanareader;    
    GRANT USAGE ON SCHEMA public TO grafanareader;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO grafanareader;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafanareader;
EOSQL
