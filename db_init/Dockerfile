FROM postgres:12
RUN localedef -i fr_FR -c -f UTF-8 -A /usr/share/locale/locale.alias fr_FR.UTF-8
ENV LANG fr_FR.utf8
COPY ./Db_init/init-user-db.sh /docker-entrypoint-initdb.d/init-user-db.sh
