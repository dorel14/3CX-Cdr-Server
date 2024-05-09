do 
$body$
declare 
  num_users integer;
begin
   SELECT count(*) 
     into num_users
   FROM pg_user
   WHERE usename = 'grafanareader';

   IF num_users = 0 THEN
      CREATE ROLE grafanareader LOGIN PASSWORD 'grafanareader';
   END IF;
end
$body$
;
    GRANT CONNECT ON DATABASE cdr3cxdb TO grafanareader;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO grafanareader;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafanareader;
    GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO grafanareader;
