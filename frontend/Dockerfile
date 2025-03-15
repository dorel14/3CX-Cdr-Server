FROM python:3.13-slim AS builder

# Prepare apt files
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https \
    curl \
    gcc \
    g++ \
    libpq-dev \
    unixodbc \
    unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

RUN python -m venv /opt/venv && \
    mkdir -p /webapp /data/files

WORKDIR /webapp

# Install pip requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Final stage
FROM python:3.13-slim

# Prepare apt files
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https \
    curl \
    libpq-dev \
    unixodbc \
    unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set timezone and create necessary directories
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    mkdir -p /webapp

WORKDIR /webapp

# Expose application port
EXPOSE 8080

# Command to run the application
CMD ["python", "./frontend/main.py"]