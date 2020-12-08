FROM python:3.9.0-alpine3.12

# System deps
RUN apk add build-base curl git openssl postgresql-libs postgresql-dev libressl-dev musl-dev libffi-dev

# Python deps manager
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

# Copy Poetry's files
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Install deps
RUN /root/.poetry/bin/poetry config virtualenvs.create false \
  && /root/.poetry/bin/poetry install --no-dev --no-interaction

# Copy sources
COPY . /code

# Run bot
CMD ["python", "jacob/main.py"]
