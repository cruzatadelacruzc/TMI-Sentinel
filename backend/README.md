# TMI Sentinel Backend (Phase 1)

FastAPI service for source ingestion, historical rate storage, the MVP exchange-rate buffer, and scheduled ingestion. This phase has no user authentication or frontend. The analytics engine depends only on the `RateProvider` protocol.

## Supabase project setup

The remote project cannot be provisioned from this repository: project creation requires an authenticated Supabase account and organization selection. Create a project in the Supabase Dashboard, choose a region, set a database password, then open **Connect** and choose **Transaction pooler**. Copy the generated string; Supabase supplies the correct pooler hostname and project-ref username. Do not construct the pooler hostname from the region.

Require SSL in the project's database settings where available. Add the connection string to a local `backend/.env`, URL-encoding reserved password characters:

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres.[project-ref]:[password]@[pooler-host]:6543/postgres?ssl=require
```

Port `6543` is transaction mode. The app disables asyncpg's prepared-statement cache on that port per Supabase's connection guidance. At startup, SQLAlchemy creates the declared tables. Keep `.env` private and never commit credentials.

## El Toque token

Register on El Toque's official website and obtain a personal API token. Set it as `EL_TOQUE_API_TOKEN` in the local `.env`. The client refuses to make requests without it. Authentication header and scheme are configurable if the authenticated API contract requires something other than `Authorization: Bearer`.

## Run locally

Python 3.11+ is recommended.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Set DATABASE_URL and EL_TOQUE_API_TOKEN in .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`; health is at `GET /api/v1/health`.

## API

- `POST /api/v1/eltoque/ingest` and `GET /api/v1/eltoque/rates?currency=USD`
- `POST /api/v1/bcc/ingest` and `GET /api/v1/bcc/rates?currency=USD&variant=column_1`
- `GET /api/v1/analytics/volatility?currency=USD&source=eltoque`
- `POST /api/v1/analytics/buffer` with `{"currency":"USD","source":"eltoque","horizon_days":7,"confidence":0.95}`
- `GET /api/v1/scheduler` and `PUT /api/v1/scheduler` with `{"interval_minutes":30,"enabled":true}`

Scheduler interval precedence is environment value, persisted runtime value, then 60 minutes. A runtime interval is still subordinate to an explicit `SCHEDULER_INTERVAL_MINUTES`. `SCHEDULER_ENABLED=false` disables automatic scheduling; manual ingestion endpoints remain available.

Buffer calculations require at least three daily observations. The MVP formula uses the confidence quantile and horizon-scaled daily volatility, plus half the average buy/sell spread when the provider supplies both values. See the analytics README for assumptions. Source authentication and parser adaptation notes live in each provider module README.

## Tests

```powershell
python -m pytest
```

Parser, scheduler precedence, and analytics tests use fixtures and an in-memory provider. Live database ingestion needs valid Supabase and El Toque credentials.