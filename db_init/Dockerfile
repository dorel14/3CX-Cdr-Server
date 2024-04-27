FROM postgres:12
RUN apt-get update \
    && apt-get -y install tzdata

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN localedef -i fr_FR -c -f UTF-8 -A /usr/share/locale/locale.alias fr_FR.UTF-8
ENV LANG fr_FR.utf8

#CMD ["postgres"]

#USER postgres

#COPY init-user-db.sh /docker-entrypoint-initdb.d
#COPY init.sql /docker-entrypoint-initdb.d


#RUN chmod +x /docker-entrypoint-initdb.d/init-user-db.sh


