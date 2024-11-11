# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.13-slim AS builder

#Prepare apt files
RUN apt update \
    && apt-get install -y apt-transport-https \
&&  apt install -y libpq-dev \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev\
    curl \
&&	apt-get clean && rm -rf /var/lib/apt/lists/*

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

RUN mkdir /webapp \
&& mkdir /data  \
&& mkdir /data/files


WORKDIR /webapp


# Install pip requirements
COPY requirements.txt /webapp/requirements.txt
RUN python -m venv /opt/venv && \
    pip install --upgrade pip && \
    pip install -r requirements.txt 


# final stage
FROM python:3.13-slim



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

WORKDIR /webapp

#COPY . /webapp

EXPOSE 8181


#CMD ["python", "./ui_new/main.py"]