# For more information, please refer to https://aka.ms/vscode-docker-python
# using ubuntu LTS version
FROM python:3.12-slim-bookworm AS builder-image

# avoid stuck build due to user prompt
ARG DEBIAN_FRONTEND=noninteractive

#Prepare apt files
RUN apt-get update && apt-get install --no-install-recommends -y python3-pip python3-wheel gcc g++ curl libpq-dev
RUN	apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home myuser

# Activate the virtual environment
RUN python -m venv /home/myuser/venv
ENV PATH="/home/myuser/venv/bin:$PATH"

RUN mkdir /home/myuser/app
WORKDIR /home/myuser/app
# Install pip requirements
COPY requirements.txt .

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -r requirements.txt



FROM python:3.12-slim-bookworm AS runner-image
RUN apt-get update && apt-get install -y --no-install-recommends --allow-change-held-packages net-tools \
     tzdata -y\
     curl\ 
     locales\
     iputils-ping\
     locales-
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

#RUN localedef -i ${LOCALE_LANGUAGE} -c -f UTF-8 -A /usr/share/locale/locale.alias ${LOCALE_LANGUAGE}.UTF-8
ENV LANG ${LOCALE_LANGUAGE}.utf8
RUN mkdir -p /opt/cdrfiles
RUN mkdir -p /opt/cdrfiles_archives

RUN useradd -u 5678 --create-home  appuser
COPY --from=builder-image /home/myuser/venv /home/appuser/venv

RUN rm -rf /home/appuser/app
RUN mkdir /home/appuser/app
RUN mkdir /home/appuser/cdrfiles


WORKDIR /home/appuser/app

# Add docker-compose-wait tool -------------------
ENV WAIT_VERSION 2.12.0
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait



COPY . .

# RUN chown -R appuser  /home/appuser/*
RUN chown -R appuser  /home/appuser/app 
RUN chown -R appuser  /home/appuser/cdrfiles

USER appuser
# Keeps Python from generating .pyc files in the container
# Turns off buffering for easier container logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/venv/bin:$PATH"





# activate virtual environment
ENV VIRTUAL_ENV=/home/appuser/venv
ENV PATH="/home/appuser/venv/bin:$PATH"

#RUN pip3 install --upgrade pip
#RUN pip3 install alembic

#Port d'écoute
EXPOSE 5000





# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
#USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# CMD ["python", ".\tcpsrv\runserver.py"]
