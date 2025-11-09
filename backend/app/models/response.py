"""
Response Models
مدل‌های پاسخ API
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class RiskAssessment(BaseModel):
    """ارزیابی ریسک محاسبه شده"""
    
    # 5-Year Risk
    absolute_risk_5year: float = Field(
        ...,
        description="ریسک مطلق 5 ساله (احتمال ابتلا در 5 سال آینده)"
    )
    average_risk_5year: float = Field(
        ...,
        description="ریسک میانگین 5 ساله (برای زنان هم سن و هم نژاد)"
    )
    relative_risk_5year: float = Field(
        ...,
        description="ریسک نسبی 5 ساله (نسبت ریسک فرد به میانگین)"
    )
    
    # Lifetime Risk (to age 90)
    absolute_risk_lifetime: Optional[float] = Field(
        None,
        description="ریسک مطلق تا 90 سالگی"
    )
    average_risk_lifetime: Optional[float] = Field(
        None,
        description="ریسک میانگین تا 90 سالگی"
    )
    relative_risk_lifetime: Optional[float] = Field(
        None,
        description="ریسک نسبی تا 90 سالگی"
    )
    
    # Interpretation
    risk_category: str = Field(
        ...,
        description="دسته‌بندی ریسک: پایین/متوسط/بالا"
    )
    interpretation_fa: str = Field(
        ...,
        description="تفسیر فارسی نتیجه"
    )
    recommendations_fa: List[str] = Field(
        ...,
        description="توصیه‌های بالینی به فارسی"
    )


class PatientInfo(BaseModel):
    """اطلاعات خلاصه بیمار"""
    
    age: int
    race_name_fa: str
    projection_age_5year: int
    projection_age_lifetime: int


class GailResultResponse(BaseModel):
    """پاسخ کامل محاسبه Gail"""
    
    success: bool = Field(True, description="وضعیت موفقیت")
    message: str = Field(..., description="پیام توضیحی")
    
    patient_info: PatientInfo = Field(..., description="اطلاعات بیمار")
    risk_assessment: RiskAssessment = Field(..., description="نتایج ارزیابی ریسک")
    
    disclaimer: str = Field(
        default=(
            "⚠️ هشدار مهم:\n"
            "این ابزار تنها یک برآورد آماری بر اساس مدل Gail است و نمی‌تواند "
            "ریسک دقیق فردی شما را تعیین کند. این نتایج نباید جایگزین مشاوره پزشکی شوند.\n\n"
            "لطفاً با پزشک متخصص خود در مورد:\n"
            "- تفسیر این نتایج\n"
            "- برنامه غربالگری مناسب\n"
            "- راهکارهای کاهش ریسک\n"
            "مشورت کنید."
        ),
        description="متن سلب مسئولیت"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="متادیتا اضافی (نسخه مدل، تاریخ محاسبه، ...)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "محاسبه ریسک با موفقیت انجام شد",
                "patient_info": {
                    "age": 45,
                    "race_name_fa": "سفیدپوست/سایر",
                    "projection_age_5year": 50,
                    "projection_age_lifetime": 90
                },
                "risk_assessment": {
                    "absolute_risk_5year": 0.0235,
                    "average_risk_5year": 0.0189,
                    "relative_risk_5year": 1.24,
                    "absolute_risk_lifetime": 0.1245,
                    "average_risk_lifetime": 0.1050,
                    "relative_risk_lifetime": 1.19,
                    "risk_category": "متوسط",
                    "interpretation_fa": "ریسک شما 1.24 برابر میانگین است (متوسط)",
                    "recommendations_fa": [
                        "ماموگرافی سالانه از 40 سالگی",
                        "معاینه بالینی هر 6-12 ماه",
                        "خودآزمایی ماهانه سینه"
                    ]
                },
                "disclaimer": "...",
                "metadata": {
                    "model_version": "Gail v2 (BCRA)",
                    "calculation_date": "2024-01-15T10:30:00Z"
                }
            }
        }


class ErrorResponse(BaseModel):
    """پاسخ خطا"""
    
    success: bool = Field(False, description="وضعیت موفقیت")
    error: str = Field(..., description="پیام خطا")
    error_code: Optional[str] = Field(None, description="کد خطا")
    details: Optional[Dict[str, Any]] = Field(None, description="جزئیات بیشتر")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "سن باید بین 35 تا 85 سال باشد",
                "error_code": "VALIDATION_ERROR",
                "details": {
                    "field": "age",
                    "value": 30,
                    "constraint": "ge=35"
                }
            }
        }


class HealthResponse(BaseModel):
    status: str = Field("healthy", description="وضعیت سرویس")
    service: str = Field(..., description="نام سرویس")
    version: str = Field(..., description="نسخه")
    calculator_ready: bool = Field(..., description="آیا محاسبه‌گر Gail آماده است")  # ✅ نام تغییر کرد
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "Gail Risk Calculator API",
                "version": "1.4.2",
                "calculator_ready": True  # ✅ نام تغییر کرد
            }
        }
