# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9-slim as builder

WORKDIR /app


# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

#Prepare apt files
RUN apt-get update \
    && apt-get -y install libpq-dev \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev



# Install pip requirements
RUN python -m pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# final stage
FROM python:3.9-slim

RUN apt-get update \
    && apt-get -y install unixodbc \
    unixodbc-dev \
    libpq-dev \
    net-tools \
    tzdata -y 

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /app

RUN rm -rf /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip
RUN pip install --no-cache /wheels/*

#Port d'écoute
EXPOSE 5000


COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# CMD ["python", "runserver.py"]
