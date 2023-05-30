FROM python:3.9-slim

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

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir /streamlit

WORKDIR /streamlit

COPY requirements.txt /streamlit

RUN pip install --upgrade pip
RUN pip install -r /streamlit/requirements.txt

COPY . /streamlit

EXPOSE 8501

CMD ["streamlit", "run", "./ui/app.py"]