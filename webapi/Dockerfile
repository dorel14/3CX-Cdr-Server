FROM tiangolo/uvicorn-gunicorn:python3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

RUN apt-get update && \
    apt-get install -y curl \
    iputils-ping \
    && mkdir /fastapi

COPY requirements.txt /fastapi

WORKDIR /fastapi

RUN pip install --upgrade pip && pip install -r requirements.txt 

COPY . /fastapi

EXPOSE 8000

# Add docker-compose-wait tool -------------------
ENV WAIT_VERSION 2.12.0
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

# CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]