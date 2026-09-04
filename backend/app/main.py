from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import SessionLocal
from app.api.router import api_router
from app.services.seed_service import seed_prototype_data_if_empty
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: logging and prototype data initialization
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} (Env: {settings.ENVIRONMENT})")
    db = SessionLocal()
    try:
        seed_prototype_data_if_empty(db)
    except Exception as e:
        logger.warning(f"Note: Seed execution encountered: {e}")
    finally:
        db.close()
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title="RecoverAI - Autonomous Payment Revenue Recovery API",
    description=(
        "Production-grade AI-powered payment recovery backend for the Razorpay AI Buildathon. "
        "Detects revenue at risk, diagnoses root cause, predicts recoverability, and simulates recovery workflows."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred.",
            "path": request.url.path,
        },
    )


# Mount API routes
app.include_router(api_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": "RecoverAI",
        "description": "AI Revenue Recovery Platform",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health",
    }
