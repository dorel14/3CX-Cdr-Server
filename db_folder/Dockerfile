FROM postgres:12-alpine

USER root

RUN apk update && \
    apk add --no-cache --update musl musl-utils musl-locales tzdata dos2unix

ENV TZ=${TZ}
ENV LANG ${LOCALE_LANGUAGE}.UTF-8
ENV LANGUAGE ${LOCALE_LANGUAGE}.UTF-8
ENV LC_ALL ${LOCALE_LANGUAGE}.UTF-8
ENV POSTGRES_INITDB_ARGS="--locale=${LOCALE_LANGUAGE}.UTF-8"

RUN mkdir -p /etc/localtime && \
    ln -s /usr/share/zoneinfo/${TZ} /etc/localtime




COPY ./db_init/* /docker-entrypoint-initdb.d/
RUN dos2unix /docker-entrypoint-initdb.d/* && \
    chmod -R 755 /docker-entrypoint-initdb.d && \
    chown -R postgres:postgres /docker-entrypoint-initdb.d && \
    mkdir -p /var/lib/postgresql/data && \
    chown -R postgres:postgres /var/lib/postgresql/data



