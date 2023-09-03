# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Define a build-arg for APP_VERSION
ARG APP_VERSION

# Set the environment variable for the app version
ENV APP_VERSION=$APP_VERSION

ENTRYPOINT [ "python3", "main.py"]