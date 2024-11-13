FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.5.1

WORKDIR /app

RUN apt-get update && apt-get install -y supervisor

COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && pip install "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . .
COPY supervisor.conf /etc/supervisor/conf.d/supervisor.conf

EXPOSE $PORT

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisor.conf"]
