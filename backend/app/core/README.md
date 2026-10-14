# Shared Core

The core contains only shared technical primitives: structured JSON logs, a SQLAlchemy declarative base with common audit columns, a generic async repository, provider-neutral `RatePoint`/`RateProvider` contracts, and common exceptions. Source parsing and analysis rules live in their owning modules.

`Database` translates PostgreSQL URLs to `postgresql+asyncpg`, accepts the Supabase transaction-pooler `?ssl=require` option, and disables asyncpg statement caching on port `6543` as required for transaction mode. No credentials are embedded in source. The application creates tables from imported models at startup for this MVP; schema evolution beyond a fresh project should move to versioned migrations before production use.