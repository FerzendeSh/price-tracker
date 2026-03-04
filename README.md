# Price Tracker (FastAPI + Vue 3)

A real-time price tracking web application built with **FastAPI** for the backend and **Vue 3** for the frontend. Users can register, log in, track product prices from e-commerce sites, view price history charts, set target price alerts, and get notified when prices drop.

## Features

- **User Authentication** — Register / Login with JWT tokens
- **Product Tracking** — Add product URLs to monitor
- **Price Scraping** — Automatic extraction from e-commerce pages (meta tags, JSON-LD, CSS selectors)
- **Price History** — View historical prices in a chart and table
- **Target Price Alerts** — Set a target and get notified when prices drop
- **Background Scheduling** — Prices are checked automatically every 30 minutes
- **Email Notifications** — Optional SMTP-based alerts

## Tech Stack

| Layer    | Technology                                               |
| -------- | -------------------------------------------------------- |
| Backend  | Python 3.11, FastAPI, SQLAlchemy 2, Alembic, APScheduler |
| Scraping | Requests, BeautifulSoup4                                 |
| Database | PostgreSQL                                               |
| Frontend | Vue 3, Pinia, Vue Router, Chart.js, Axios                |
| Build    | Vite                                                     |

## Project Structure

```
backend/
  app/
    core/config.py        # Centralized settings from .env
    models/               # SQLAlchemy models (User, Product, PriceHistory)
    schemas/              # Pydantic schemas
    routes/               # API endpoints (auth, products, prices, tracking)
    services/             # Price scraper, notifier, scheduler
    auth.py               # JWT auth helpers
    main.py               # FastAPI app entry point
  alembic/                # Database migrations
  .env                    # Environment variables
  requirements.txt

frontend/
  src/
    api/index.js          # Axios client with auth interceptor
    store/                # Pinia stores (auth, products)
    router/index.js       # Vue Router with auth guards
    components/           # NavBar, ProductCard, AddProductForm, PriceChart
    pages/                # Login, Register, Dashboard, ProductDetail
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL running on localhost:5432
- Node.js 18+

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create database
createdb real_time_price   # or via psql

# Edit .env with your settings (DB URL, secret key, etc.)

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies API to localhost:8000)
npm run dev
```

Open **http://localhost:5173** in your browser.

## API Endpoints

| Method | Endpoint                | Description           |
| ------ | ----------------------- | --------------------- |
| POST   | `/auth/register`        | Create account        |
| POST   | `/auth/login`           | Get JWT token         |
| GET    | `/auth/me`              | Current user info     |
| GET    | `/products/`            | List tracked products |
| POST   | `/products/`            | Add product to track  |
| GET    | `/products/{id}`        | Get product details   |
| PUT    | `/products/{id}`        | Update product        |
| DELETE | `/products/{id}`        | Remove product        |
| GET    | `/products/{id}/prices` | Get price history     |
| POST   | `/track/{id}/check`     | Check price now       |

## Environment Variables

| Variable               | Default                                                              | Description                       |
| ---------------------- | -------------------------------------------------------------------- | --------------------------------- |
| `DATABASE_URL`         | `postgresql+psycopg2://postgres:1991@localhost:5432/real_time_price` | DB connection string              |
| `SECRET_KEY`           | `CHANGE_ME_LATER`                                                    | JWT signing key                   |
| `CORS_ORIGINS`         | `http://localhost:5173`                                              | Allowed origins (comma-separated) |
| `PRICE_CHECK_INTERVAL` | `30`                                                                 | Minutes between automatic checks  |
| `SMTP_HOST`            | _(empty)_                                                            | SMTP server for email alerts      |
| `SMTP_PORT`            | `587`                                                                | SMTP port                         |
| `SMTP_USER`            | _(empty)_                                                            | SMTP username                     |
| `SMTP_PASSWORD`        | _(empty)_                                                            | SMTP password                     |
