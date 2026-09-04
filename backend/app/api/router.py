from fastapi import APIRouter
from app.api.routes import health, dashboard, recovery, payments, analytics, recovery_cases, ai

api_router = APIRouter(prefix="/api")

# Core API routers
api_router.include_router(health.router)
api_router.include_router(dashboard.router)
api_router.include_router(recovery.router)
api_router.include_router(payments.router)
api_router.include_router(analytics.router)
api_router.include_router(ai.router)

# Legacy alias for recovery-cases
api_router.include_router(recovery_cases.router)
