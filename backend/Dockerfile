FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python deps first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy app
COPY . .

# (Optional but recommended) Run as non-root
RUN useradd -m appuser
USER appuser

EXPOSE 8000

# Run Alembic migrations then start Gunicorn (PORT provided by Render)
CMD ["sh", "-c", "alembic upgrade head && gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120"]