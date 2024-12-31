# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.13-slim AS builder

# Prepare apt files and install dependencies
RUN apt update && apt-get install -y \
    apt-transport-https \
    libpq-dev \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Create necessary directories
RUN mkdir -p /webapp /data/files

WORKDIR /webapp

# Install pip requirements
COPY requirements.txt /webapp/requirements.txt
RUN python -m venv /opt/venv && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

FROM python:3.13-slim AS runner

# Prepare apt files and install dependencies
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    libpq-dev \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Copy virtual environment and application code from builder stage
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /webapp /webapp

# Set timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /webapp

EXPOSE 8181

#CMD ["python", "./ui_new/main.py"]