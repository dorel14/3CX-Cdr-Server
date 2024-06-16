# For more information, please refer to https://aka.ms/vscode-docker-python
# using ubuntu LTS version
FROM python:3.12-slim-bookworm AS builder

# avoid stuck build due to user prompt
ARG DEBIAN_FRONTEND=noninteractive

#Prepare apt files
RUN apt-get update && apt-get install --no-install-recommends -y python3-pip python3-wheel gcc g++ curl libpq-dev iputils-ping
RUN	apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home myuser

# Activate the virtual environment
RUN python -m venv /home/myuser/venv
ENV PATH="/home/myuser/venv/bin:$PATH"

RUN mkdir /home/myuser/app
WORKDIR /home/myuser/app
# Install pip requirements
#COPY requirements.txt .

RUN pip3 install --upgrade pip \
&& pip3 install --no-cache-dir wheel \
&& pip3 install --no-cache-dir -r requirements.txt



FROM python:3.12-slim-bookworm AS runner
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
ENV APP_DIR=/home/appuser/app

COPY --from=builder /home/myuser/venv /home/appuser/venv

# Add docker-compose-wait tool -------------------
ENV WAIT_VERSION 2.12.0
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

RUN groupadd -r appgroup \
&& useradd -u 1000  --create-home appuser --no-log-init -g appgroup --shell /bin/bash --groups sudo

RUN rm -rf ${APP_DIR} \ 
&& mkdir ${APP_DIR} \
&& mkdir /home/appuser/cdrfiles \
&& mkdir -p /opt/cdrfiles \
&& mkdir -p /opt/cdrfiles_archives \
&& chown -R appuser:appgroup /opt/cdrfiles \
&& chown -R appuser:appgroup /opt/cdrfiles_archives



WORKDIR ${APP_DIR}
#COPY --chown=appuser:appgroup . .



# RUN chown -R appuser  /home/appuser/*




RUN chmod -R 777 ${APP_DIR} \
&& chmod -R 777 /opt/cdrfiles \
&& chmod -R 777 /opt/cdrfiles_archives 

#USER appuser
# Keeps Python from generating .pyc files in the container
# Turns off buffering for easier container logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/venv/bin:$PATH"

# activate virtual environment
ENV VIRTUAL_ENV=/home/appuser/venv
ENV PATH="/home/appuser/venv/bin:$PATH"


#Port d'écoute
EXPOSE 5000