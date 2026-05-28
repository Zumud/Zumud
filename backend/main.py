from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import api_router
from backend.models.db import Base, engine, check_db_connection
from backend.utils.log import logger
import os
import uvicorn

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"

# Sentry setup for API monitoring. Only initialize when a DSN is configured;
# otherwise sentry_sdk.init() with dsn=None still installs the integration
# overhead for nothing. In production we sample a small slice of traces and
# profiles - 100% sampling is what was creating heavy CPU/memory pressure.
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    _traces = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1" if IS_PRODUCTION else "1.0"))
    _profiles = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1" if IS_PRODUCTION else "1.0"))

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            FastApiIntegration(),
            StarletteIntegration(),
        ],
        traces_sample_rate=_traces,
        profiles_sample_rate=_profiles,
        environment=ENVIRONMENT,
        send_default_pii=not IS_PRODUCTION,
    )
    logger.info(f"Sentry initialised (env={ENVIRONMENT}, traces={_traces}, profiles={_profiles})")
else:
    logger.info("SENTRY_DSN not set; Sentry disabled")

logger.info(f"Starting FastAPI application (environment={ENVIRONMENT})")

# Check database connection and create tables on startup. Failure here used to
# silently leave the app in a half-broken state; now we still let the app boot
# (so /health can report the problem and the process keeps running for
# Cloudflare/load-balancer health checks) but we record the failure clearly.
DB_INITIALISED = False
try:
    if check_db_connection():
        logger.info("Successfully connected to Supabase database")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
        DB_INITIALISED = True
    else:
        logger.error("Failed to connect to Supabase database on startup")
except Exception as e:
    logger.exception(f"Database initialization error: {e}")

app = FastAPI(
    title="Resume Tailorer API",
    description="API for Zumud - AI-powered job application assistant",
    version="1.0.0"
)

# CORS: a wildcard origin is incompatible with allow_credentials=True (browsers
# silently drop the response). Drive the list from CORS_ALLOWED_ORIGINS in the
# environment, falling back to sensible defaults per environment.
def _parse_origins(env_value: str | None, default: list[str]) -> list[str]:
    if not env_value:
        return default
    return [o.strip() for o in env_value.split(",") if o.strip()]

if IS_PRODUCTION:
    allowed_origins = _parse_origins(
        os.getenv("CORS_ALLOWED_ORIGINS"),
        [
            "https://zumud.com",
            "https://www.zumud.com",
        ],
    )
    cors_kwargs = dict(
        allow_origins=allowed_origins,
        allow_credentials=True,
    )
else:
    allowed_origins = _parse_origins(
        os.getenv("CORS_ALLOWED_ORIGINS"),
        ["http://localhost:3000", "http://127.0.0.1:3000"],
    )
    cors_kwargs = dict(
        allow_origins=allowed_origins,
        allow_credentials=True,
    )

logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    **cors_kwargs,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# # Create tables on startup
# @app.on_event("startup")
# async def startup_event():
#     create_tables()

# Include API router
app.include_router(api_router)

@app.get("/", tags=["Root"])
def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to the Zumud API!",
        "version": "1.0.0",
        "database": "Supabase PostgreSQL",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Liveness + DB health probe.

    Cloudflare and any uptime monitor hits this. We DO NOT want a transient DB
    blip to cause Cloudflare to mark the origin down (which is what produces a
    521 perception even when the API process is fine), so we always return 200
    with structured status instead of 503. Use ``status`` field for alerting.
    """
    db_healthy = check_db_connection()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "disconnected",
        "version": "1.0.0",
    }

if __name__ == "__main__":
    # Single-process dev mode. Production should run via the systemd unit /
    # script in deploy/, which uses multiple uvicorn workers and
    # auto-restart-on-crash.
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    workers = int(os.getenv("WEB_CONCURRENCY", "1"))
    log_level = os.getenv("UVICORN_LOG_LEVEL", "info")
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        workers=workers,
        log_level=log_level,
        proxy_headers=True,           # respect X-Forwarded-For from Cloudflare
        forwarded_allow_ips="*",
    )
