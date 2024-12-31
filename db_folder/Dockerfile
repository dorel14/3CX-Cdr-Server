FROM postgres:12-alpine

# Update and install necessary packages
RUN apk update && apk add --no-cache \
    musl \
    musl-utils \
    musl-locales \
    tzdata

# Set environment variables for timezone and locale
ENV TZ=${TZ}
ENV LANG=${LOCALE_LANGUAGE}.UTF-8
ENV LANGUAGE=${LOCALE_LANGUAGE}.UTF-8
ENV LC_ALL=${LOCALE_LANGUAGE}.UTF-8

# Set timezone
RUN ln -s /usr/share/zoneinfo/${TZ} /etc/localtime
