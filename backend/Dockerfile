FROM python:3.13-slim AS builder

ARG DEBIAN_FRONTEND=noninteractive
# Create the sources.list file if it doesn't exist
RUN touch /etc/apt/sources.list
# Add the default debian repository
RUN echo "deb http://deb.debian.org/debian bookworm main" >> /etc/apt/sources.list

RUN sed -i 's|http://deb.debian.org|http://ftp.fr.debian.org|g' /etc/apt/sources.list
RUN apt-get update && apt-get install --no-install-recommends -y \
    wget \
    gcc \
    g++ \
    iputils-ping \
    libpq-dev \
    curl \
    build-essential \
    rustc cargo \
    #python3-pip \
    #python3-wheel \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home myuser


ENV PATH="/home/myuser/.venv/bin:$PATH"
WORKDIR /home/myuser/app

ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

COPY ./backend/requirements.txt .


RUN /root/.local/bin/uv venv /home/myuser/.venv

RUN /root/.local/bin/uv pip install --no-cache -r requirements.txt
# RUN --mount=type=cache,target=/root/.cache/pip pip install --upgrade pip && \
#     pip install --no-cache-dir wheel && \
#     pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim AS runner

ARG DEBIAN_FRONTEND=noninteractive
# Set default value for LOCALE_LANGUAGE
ARG LOCALE_LANGUAGE=en_US
# Allow overriding from .env file via build-arg
ARG ENV_LOCALE_LANGUAGE
# Use ENV_LOCALE_LANGUAGE if provided, otherwise fall back to the default LOCALE_LANGUAGE
ENV LOCALE_LANGUAGE=${ENV_LOCALE_LANGUAGE:-${LOCALE_LANGUAGE}}
# Create the sources.list file if it doesn't exist
RUN touch /etc/apt/sources.list
# Add the default debian repository
RUN echo "deb http://deb.debian.org/debian bookworm main" >> /etc/apt/sources.list

RUN sed -i 's|http://deb.debian.org|http://ftp.fr.debian.org|g' /etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    locales \
    net-tools \
    tzdata \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
# Generate the locale
RUN localedef -i ${LOCALE_LANGUAGE} -c -f UTF-8 -A /usr/share/locale/locale.alias ${LOCALE_LANGUAGE}.UTF-8

ENV LANG=${LOCALE_LANGUAGE}.utf8 \
    APP_DIR=/home/appuser/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.venv/bin:$PATH" \
    VIRTUAL_ENV=/home/appuser/.venv

COPY --from=builder /home/myuser/.venv /home/appuser/.venv
COPY --from=builder /home/myuser/app /home/appuser/app


RUN groupadd -r appgroup && \
    useradd -u 1000 --create-home appuser --no-log-init -g appgroup --shell /bin/bash  --groups sudo && \
    mkdir -p /opt/cdrfiles /opt/cdrfiles_archives && \
    mkdir -p /home/appuser/app/backend/logs && \
    chown -R appuser:appgroup /opt/cdrfiles /opt/cdrfiles_archives && \
    chown -R appuser:appgroup /home/appuser/app/backend/logs && \
    chmod -R 755 ${APP_DIR} && chmod -R 755 /opt/cdrfiles /opt/cdrfiles_archives /home/appuser/app/backend/logs

WORKDIR ${APP_DIR}

#USER appuser

EXPOSE 5000