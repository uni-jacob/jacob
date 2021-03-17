FROM python:3.9-slim

# System deps
RUN apt-get update && apt-get install -y -qq git gcc
# Download and install poetry
RUN pip install poetry

# Copy Poetry's files
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN pip install --upgrade pip

# Install deps
RUN poetry config virtualenvs.create false \
 && poetry install --no-dev --no-interaction

# Copy sources
COPY . /code
