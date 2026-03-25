# Price Tracker

Price tracker app with:
- FastAPI backend
- Vue 3 frontend
- PostgreSQL database

## Quick Start (Docker)

From the project root:

```bash
docker compose up --build -d
```

Open:
- Frontend: `http://localhost`
- Backend docs: `http://localhost:8000/docs`

Default admin login:
- Username: `Admin`
- Password: `Admin@1234`

## Stop / Restart

```bash
docker compose down
docker compose up -d
```

## Useful Commands

```bash
# container status
docker compose ps

# logs
docker compose logs -f backend
docker compose logs -f frontend

# rebuild one service
docker compose up --build -d backend
docker compose up --build -d frontend
```

## Local Development (Without Docker)

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

## Notes

- `POST /auth/register` expects: `username`, `email`, `password`
- `POST /auth/login` expects: `username`, `password`
