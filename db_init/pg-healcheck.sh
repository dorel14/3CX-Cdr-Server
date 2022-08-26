readonly SLEEP_TIME=5

readonly PG_HOST="db"
readonly PG_USER=postgres
readonly PG_DB=cdr3cxdb

# note: the PGPASSWORD envar is passed in
until timeout 3 psql -h $PG_HOST -U $PG_USER -c "select 1" -d $PG_DB > /dev/null
do
  printf "Waiting %s seconds for PostgreSQL to come up: %s@%s/%s...\n" $SLEEP_TIME $PG_USER $PG_HOST $PG_DB
  sleep $SLEEP_TIME;
done
