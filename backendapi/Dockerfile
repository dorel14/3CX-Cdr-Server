FROM python:3.13-slim AS builder

# Prepare apt files
RUN apt update \
    && apt-get install -y apt-transport-https \
    && apt install -y libpq-dev \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

RUN mkdir /fastapi

WORKDIR /fastapi

# Install pip requirements
COPY requirements.txt /fastapi/requirements.txt
RUN python -m venv /opt/venv && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Final stage
FROM python:3.13-slim

# Prepare apt files
RUN apt-get update \
    && apt-get install -y apt-transport-https \
    && apt install -y libpq-dev \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Keeps Python from generating .pyc files in the container
# Turns off buffering for easier container logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && mkdir /fastapi

WORKDIR /fastapi

# Add docker-compose-wait tool
ENV WAIT_VERSION 2.12.0
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

EXPOSE 8000

# CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]