# Scheduler

The scheduler uses APScheduler's in-process `AsyncIOScheduler`; it is started and stopped with the FastAPI lifespan. It calls the same independent El Toque and BCC ingestion services used by manual endpoints, and records each provider's failure separately so one failed source does not stop the other.

One `scheduler_settings` row (id `1`) stores the runtime interval and enabled state. Effective interval precedence is `SCHEDULER_INTERVAL_MINUTES`, then the persisted interval, then 60 minutes. The runtime endpoint persists the requested interval even when an environment override currently takes precedence. `SCHEDULER_ENABLED` supplies the startup enabled state unless runtime state already exists; `PUT /api/v1/scheduler` can change that state.

This is an MVP single-process scheduler. Run one API worker/replica when automatic ingestion is enabled; multiple workers would each run their own scheduler and could duplicate fetches. Rate upserts are idempotent by provider, currency, variant, and observation time.