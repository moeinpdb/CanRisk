"""
FastAPI Main Application
نقطه ورود اصلی API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import logging

from app.config import settings
from app.routers import gail_router, health_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## 🎗️ API محاسبه ریسک سرطان سینه (مدل Gail)
    
    این API بر اساس مدل Gail (نسخه 2) که توسط National Cancer Institute (NCI) 
    توسعه یافته، ریسک ابتلا به سرطان سینه تهاجمی را برآورد می‌کند.
    
    ### ویژگی‌ها:
    - محاسبه ریسک 5 ساله
    - محاسبه ریسک lifetime (تا 90 سالگی)
    - پشتیبانی از 12 گروه نژادی/قومی
    - توصیه‌های بالینی شخصی‌سازی شده
    
    ### محدودیت‌ها:
    - فقط برای زنان 35-85 سال
    - بدون سابقه سرطان سینه
    - بدون جهش BRCA1/BRCA2
    
    ### مراجع:
    - [NCI Breast Cancer Risk Assessment Tool](https://bcrisktool.cancer.gov/)
    - [Gail Model Documentation](https://www.cancer.gov/bcrisktool/about-tool.aspx)
    
    ---
    **⚠️ سلب مسئولیت:** این ابزار فقط برای اهداف آموزشی است و نباید جایگزین مشاوره پزشکی شود.
    """,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    # contact و license اختیاری هستند - می‌توانید حذف کنید
    # contact={
    #     "name": "Support Team",
    #     "email": "support@example.com",
    # },
    # license_info={
    #     "name": "MIT",
    #     "url": "https://opensource.org/licenses/MIT",
    # }
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    health_router,
    prefix="/api/health",
    tags=["🏥 Health"]
)

app.include_router(
    gail_router,
    prefix="/api/gail",
    tags=["🎗️ Gail Risk Calculator"]
)


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Redirect به API documentation"""
    return RedirectResponse(url="/api/docs")


# Startup event
@app.on_event("startup")
async def startup_event():
    """راه‌اندازی اولیه"""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"📝 Debug mode: {settings.DEBUG}")
    logger.info(f"🌐 API Docs: http://{settings.HOST}:{settings.PORT}/api/docs")
    
    # Pre-initialize Gail calculator
    try:
        from app.calculators.gail_model import create_calculator
        calc = create_calculator()
        logger.info("✅ Gail calculator initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gail calculator: {e}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """خاموش شدن"""
    logger.info(f"🛑 Shutting down {settings.APP_NAME}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )