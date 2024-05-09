FROM postgres:12-alpine
#-----Debian----- 
#RUN apt-get update \
#    && apt-get -y install tzdata

#RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

#RUN localedef -i fr_FR -c -f UTF-8 -A /usr/share/locale/locale.alias fr_FR.UTF-8
#ENV LANG fr_FR.utf8

#----Alpine----
RUN apk update
RUN apk add --no-cache --update musl musl-utils musl-locales tzdata

ENV TZ=${TZ}
ENV LANG ${LOCALE_LANGUAGE}.UTF-8
ENV LANGUAGE ${LOCALE_LANGUAGE}.UTF-8
ENV LC_ALL ${LOCALE_LANGUAGE}.UTF-8
RUN ln -s /usr/share/zoneinfo/${TZ} /etc/localtime

#RUN cp /usr/share/zoneinfo/${TZ} /etc/localtime
#RUN echo 'export LC_ALL='${LOCALE_LANGUAGE}'.UTF-8' >> /etc/profile.d/locale.sh && \
#  sed -i 's|LANG=C.UTF-8|LANG='${LOCALE_LANGUAGE}'.UTF-8|' /etc/profile.d/locale.sh
