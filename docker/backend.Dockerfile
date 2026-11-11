FROM python:3.12-slim-trixie AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools \
    && pip install --no-cache-dir -r requirements.txt


FROM python:3.12-slim-trixie AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app/backend"

WORKDIR /app

RUN groupadd --system app \
    && useradd --system --gid app --create-home app

COPY --from=builder /opt/venv /opt/venv
RUN /opt/venv/bin/python -m pip uninstall --yes pip
COPY --chown=app:app backend/app ./backend/app
COPY --chown=app:app backend/alembic ./backend/alembic
COPY --chown=app:app alembic.ini ./alembic.ini

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8000"]
