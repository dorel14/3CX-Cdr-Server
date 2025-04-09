# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.13-slim AS builder
# Create the sources.list file if it doesn't exist
RUN touch /etc/apt/sources.list
# Add the default debian repository
RUN echo "deb http://deb.debian.org/debian bookworm main" >> /etc/apt/sources.list

RUN sed -i 's|http://deb.debian.org|http://ftp.fr.debian.org|g' /etc/apt/sources.list
#Prepare apt files
RUN apt update \
    && apt-get install -y apt-transport-https \
&&  apt install -y libpq-dev \
    gcc \
    g++ \
    build-essential \
    rustc cargo \
    unixodbc \
    unixodbc-dev\
    curl \
&&	apt-get clean && rm -rf /var/lib/apt/lists/*

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

RUN mkdir /data  \
&& mkdir /data/files


WORKDIR /webapp
ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

# Install pip requirements
COPY ./frontend/requirements.txt /webapp/requirements.txt
RUN /root/.local/bin/uv venv /opt/venv
RUN /root/.local/bin/uv pip install --no-cache -r requirements.txt

# final stage
FROM python:3.13-slim AS runner

ARG LOCALE_LANGUAGE=en_US
ARG ENV_LOCALE_LANGUAGE
ENV LOCALE_LANGUAGE=${ENV_LOCALE_LANGUAGE:-${LOCALE_LANGUAGE}}

ARG TZ=UTC
ARG ENV_TZ
ENV TZ=${ENV_TZ:-${TZ}}

RUN touch /etc/apt/sources.list
# Add the default debian repository
RUN echo "deb http://deb.debian.org/debian bookworm main" >> /etc/apt/sources.list

RUN sed -i 's|http://deb.debian.org|http://ftp.fr.debian.org|g' /etc/apt/sources.list


#Prepare apt files
RUN apt-get update \
    && apt-get install -y apt-transport-https \
&& apt install -y libpq-dev \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev\
    curl\
&&	apt-get clean && rm -rf /var/lib/apt/lists/* \
&& ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# Keeps Python from generating .pyc files in the container
# Turns off buffering for easier container logging

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1\
    PATH="/opt/venv/bin:$PATH"


COPY --from=builder /opt/venv /opt/venv


RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
&& mkdir /webapp
#Permet de forcer le vidage de cahche des varaibles d'environnement
ARG CACHEBUST=1

WORKDIR /webapp

#COPY . /webapp

EXPOSE 8080


CMD ["python", "./frontend/main.py"]