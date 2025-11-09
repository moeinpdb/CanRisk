"""
Gail Risk Calculator Router
Endpoints اصلی محاسبه ریسک
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.questionnaire import PatientQuestionnaire
from app.models.response import GailResultResponse, ErrorResponse
from app.services.gail_service import GailService
from app.config import settings

router = APIRouter()

# Global service instance (singleton pattern)
_gail_service = None


def get_gail_service() -> GailService:
    """دریافت instance سرویس (singleton)"""
    global _gail_service
    if _gail_service is None:
        _gail_service = GailService()
    return _gail_service


@router.post(
    "/calculate",
    response_model=GailResultResponse,
    responses={
        400: {"model": ErrorResponse, "description": "خطای اعتبارسنجی"},
        500: {"model": ErrorResponse, "description": "خطای سرور"}
    },
    summary="محاسبه ریسک سرطان سینه",
    description="""
    محاسبه ریسک سرطان سینه بر اساس مدل Gail (BCRA)
    
    **ورودی:**
    - پرسشنامه کامل شامل سن، نژاد، سابقه پزشکی و خانوادگی
    
    **خروجی:**
    - ریسک مطلق و نسبی 5 ساله
    - ریسک lifetime (تا 90 سالگی)
    - دسته‌بندی ریسک (پایین/متوسط/بالا)
    - توصیه‌های بالینی
    
    **محدودیت‌ها:**
    - فقط برای زنان 35-85 سال
    - بدون سابقه سرطان سینه
    - بدون جهش BRCA1/BRCA2
    """
)
async def calculate_gail_risk(questionnaire: PatientQuestionnaire):
    """
    محاسبه ریسک Gail
    
    این endpoint پرسشنامه کامل را می‌گیرد و ریسک را محاسبه می‌کند.
    """
    
    service = get_gail_service()
    
    try:
        result = service.calculate_risk(questionnaire)
        return result
    
    except ValueError as e:
        # خطاهای validation
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": str(e),
                "error_code": "VALIDATION_ERROR"
            }
        )
    
    except Exception as e:
        # خطاهای غیرمنتظره
        if settings.DEBUG:
            error_detail = str(e)
        else:
            error_detail = "خطای داخلی سرور. لطفاً با پشتیبانی تماس بگیرید."
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": error_detail,
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.get(
    "/info",
    summary="اطلاعات مدل Gail",
    description="دریافت اطلاعات درباره مدل، نسخه و محدودیت‌ها"
)
async def get_gail_info():
    """
    اطلاعات مدل و راهنمای استفاده
    """
    return {
        "model_name": "Gail Model v2 (BCRA)",
        "version": settings.VERSION,
        "description": (
            "مدل Gail برای برآورد احتمال ابتلا به سرطان سینه تهاجمی در زنان. "
            "این مدل بر اساس داده‌های Breast Cancer Detection Demonstration Project (BCDDP) "
            "و SEER توسعه یافته است."
        ),
        "eligibility": {
            "age_range": "35-85 سال",
            "must_not_have": [
                "سابقه سرطان سینه",
                "سابقه DCIS یا LCIS",
                "سابقه رادیوتراپی قفسه سینه برای لنفوم هوچکین",
                "جهش ژنتیکی BRCA1 یا BRCA2"
            ]
        },
        "risk_factors_used": [
            "سن فعلی",
            "نژاد/قومیت",
            "سن اولین قاعدگی",
            "سن اولین زایمان",
            "تعداد بیوپسی‌های سینه",
            "وجود هایپرپلازیا آتیپیک در بیوپسی",
            "تعداد بستگان درجه یک مبتلا به سرطان سینه"
        ],
        "output": {
            "5_year_risk": "احتمال ابتلا در 5 سال آینده",
            "lifetime_risk": "احتمال ابتلا تا 90 سالگی",
            "relative_risk": "نسبت ریسک فرد به میانگین جمعیت"
        },
        "limitations": [
            "این یک برآورد آماری است، نه پیش‌بینی دقیق",
            "برای افراد با جهش BRCA مناسب نیست",
            "ممکن است برای برخی گروه‌های قومی کمتر دقیق باشد",
            "فاکتورهای ریسک دیگر (مثل تراکم سینه در ماموگرافی) را در نظر نمی‌گیرد"
        ],
        "references": [
            {
                "title": "Gail MH, et al. Projecting individualized probabilities of developing breast cancer for white females who are being examined annually.",
                "journal": "J Natl Cancer Inst. 1989;81(24):1879-86"
            },
            {
                "title": "Costantino JP, et al. Validation studies for models projecting the risk of invasive and total breast cancer incidence.",
                "journal": "J Natl Cancer Inst. 1999;91(18):1541-8"
            },
            {
                "title": "NCI Breast Cancer Risk Assessment Tool",
                "url": "https://bcrisktool.cancer.gov/"
            }
        ],
        "disclaimer": (
            "این ابزار فقط برای اهداف آموزشی و آگاه‌سازی است. "
            "نتایج نباید جایگزین مشاوره پزشکی حرفه‌ای شوند. "
            "لطفاً همیشه با پزشک متخصص خود مشورت کنید."
        )
    }


@router.get(
    "/races",
    summary="لیست نژادها",
    description="دریافت لیست نژادها و زیرگروه‌های پشتیبانی شده"
)
async def get_supported_races():
    """لیست کامل نژادها و کدهای آنها"""
    return {
        "main_races": [
            {"code": 1, "name": "White/Other", "name_fa": "سفیدپوست/سایر"},
            {"code": 2, "name": "African American", "name_fa": "آفریقایی-آمریکایی"},
            {"code": 3, "name": "Hispanic/Latina", "name_fa": "اسپانیایی‌تبار/لاتین"},
            {"code": 4, "name": "Asian/Pacific Islander", "name_fa": "آسیایی/جزایر اقیانوس آرام"}
        ],
        "asian_subraces": [
            {"code": 7, "name": "Chinese", "name_fa": "چینی"},
            {"code": 8, "name": "Japanese", "name_fa": "ژاپنی"},
            {"code": 9, "name": "Filipino", "name_fa": "فیلیپینی"},
            {"code": 10, "name": "Hawaiian", "name_fa": "هاوایی"},
            {"code": 11, "name": "Other Pacific Islander", "name_fa": "سایر جزایر اقیانوس آرام"},
            {"code": 12, "name": "Other Asian", "name_fa": "سایر آسیایی"}
        ],
        "note": "اگر نژاد 'آسیایی/جزایر اقیانوس آرام' (4) را انتخاب کردید، لطفاً زیرگروه را هم مشخص کنید."
    }