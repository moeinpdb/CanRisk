"""
Health Check Router
"""

from fastapi import APIRouter
from app.models.response import HealthResponse
from app.config import settings

router = APIRouter()


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health Check",
    description="بررسی وضعیت سلامت سرویس"
)
async def health_check():
    """
    Health check endpoint
    
    برای monitoring و بررسی آماده بودن سرویس
    """
    
    # بررسی اینکه مدل Gail initialize شده
    try:
        from app.calculators.gail_model import create_calculator
        calc = create_calculator()
        model_ready = calc.is_initialized
    except Exception:
        model_ready = False
    
    return HealthResponse(
        status="healthy" if model_ready else "degraded",
        service=settings.APP_NAME,
        version=settings.VERSION,
        calculator_ready=model_ready  # ✅ نام جدید
    )