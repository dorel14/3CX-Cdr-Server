FROM postgres:12-alpine
#-----Debian----- 
#RUN apt-get update \
#    && apt-get -y install tzdata

#RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

#RUN localedef -i fr_FR -c -f UTF-8 -A /usr/share/locale/locale.alias fr_FR.UTF-8
#ENV LANG fr_FR.utf8

#----Alpine----
RUN apk add --no-cache --update musl musl-utils musl-locales tzdata

ENV TZ=Europe/Paris
RUN cp /usr/share/zoneinfo/Europe/Paris /etc/localtime
RUN echo 'export LC_ALL=fr_FR.UTF-8' >> /etc/profile.d/locale.sh && \
  sed -i 's|LANG=C.UTF-8|LANG=fr_FR.UTF-8|' /etc/profile.d/locale.sh
