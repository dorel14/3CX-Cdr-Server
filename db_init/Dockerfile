FROM postgres:12
RUN apt-get update \
    && apt-get -y install tzdata -y

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN localedef -i fr_FR -c -f UTF-8 -A /usr/share/locale/locale.alias fr_FR.UTF-8
ENV LANG fr_FR.utf8
COPY ./db_init/init-user-db.sh /docker-entrypoint-initdb.d/init-user-db.sh
COPY ./db_init/pg-healcheck.sh /db_init/pg-healcheck.sh
RUN chmod +x /db_init/pg-healcheck.sh
