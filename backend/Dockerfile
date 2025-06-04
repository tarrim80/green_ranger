FROM python:3.12-slim

RUN pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-root

COPY . /app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
