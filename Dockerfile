FROM python:3.10-slim-buster

ARG TIMEZONE=Etc/UTC

ENV DEBIAN_FRONTEND=noninteractive

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    gcc build-essential vim curl \
    iputils-ping tzdata \
    libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 default-libmysqlclient-dev && \
    ln -sf /usr/share/zoneinfo/$TIMEZONE /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
# Install dependencies and update SQLite to the latest version
COPY . /var/www/html/app
WORKDIR /var/www/html/app
