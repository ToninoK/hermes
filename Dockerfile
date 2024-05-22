FROM python:3.9 AS python-base

RUN mkdir app

WORKDIR /app

ENV PATH="/root/.local/bin:$PATH"
COPY poetry.lock pyproject.toml /app/

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry config virtualenvs.create false
RUN poetry install

COPY . .
EXPOSE 5000

CMD ["uvicorn", "src.app:app", "--reload", "--host", "0.0.0.0", "--port", "5000"]




