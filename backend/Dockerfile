# For more information, please refer to https://aka.ms/vscode-docker-python
# using ubuntu LTS version
FROM python:3.13-slim AS builder

# avoid stuck build due to user prompt
ARG DEBIAN_FRONTEND=noninteractive

# Prepare apt files and install dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    python3-pip python3-wheel gcc g++ curl libpq-dev iputils-ping \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home myuser

# Activate the virtual environment
RUN python -m venv /home/myuser/venv
ENV PATH="/home/myuser/venv/bin:$PATH"

# Create necessary directories
RUN mkdir /home/myuser/app
WORKDIR /home/myuser/app

# Install pip requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir wheel && \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim AS runner

# Prepare apt files and install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    net-tools tzdata curl locales iputils-ping \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set environment variables
ENV LANG ${LOCALE_LANGUAGE}.utf8
ENV APP_DIR=/home/appuser/app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/venv/bin:$PATH" \
    VIRTUAL_ENV=/home/appuser/venv

# Copy virtual environment and application code from builder stage
COPY --from=builder /home/myuser/venv /home/appuser/venv
COPY --from=builder /home/myuser/app /home/appuser/app

# Add docker-compose-wait tool
ENV WAIT_VERSION 2.12.0
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

# Create necessary directories and set permissions
RUN groupadd -r appgroup && \
    useradd -u 1000 --create-home appuser --no-log-init -g appgroup --shell /bin/bash --groups sudo && \
    mkdir -p /opt/cdrfiles /opt/cdrfiles_archives && \
    chown -R appuser:appgroup /opt/cdrfiles /opt/cdrfiles_archives && \
    chmod -R 777 ${APP_DIR} /opt/cdrfiles /opt/cdrfiles_archives

WORKDIR ${APP_DIR}

# Expose port
EXPOSE 5000
