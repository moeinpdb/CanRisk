"""
Gail Service
منطق کسب‌وکار محاسبه ریسک Gail
"""

from datetime import datetime
from typing import Dict, List

from app.calculators.gail_model import create_calculator, GailInputParams
from app.models.questionnaire import PatientQuestionnaire
from app.models.response import (
    RiskAssessment,
    GailResultResponse,
    PatientInfo
)
from app.utils.mapper import QuestionnaireMapper


class GailService:
    """
    سرویس محاسبه ریسک Gail
    
    این کلاس منطق کسب‌وکار را مدیریت می‌کند:
    - تبدیل پرسشنامه به ورودی مدل
    - محاسبه ریسک 5 ساله و lifetime
    - تفسیر نتایج
    - تولید توصیه‌ها
    """
    
    def __init__(self):
        """مقداردهی اولیه calculator و mapper"""
        self.calculator = create_calculator()
        self.mapper = QuestionnaireMapper()
    
    def calculate_risk(
        self,
        questionnaire: PatientQuestionnaire
    ) -> GailResultResponse:
        """
        محاسبه کامل ریسک بر اساس پرسشنامه
        
        Args:
            questionnaire: پرسشنامه تکمیل شده بیمار
        
        Returns:
            نتیجه کامل ارزیابی ریسک
        
        Raises:
            ValueError: در صورت مشکل در validation یا محاسبات
        """
        
        # 1. تبدیل پرسشنامه به ورودی مدل
        gail_input = self.mapper.questionnaire_to_gail_input(questionnaire)
        
        # 2. محاسبه ریسک 5 ساله
        params_5year = GailInputParams(**gail_input)
        result_5year = self.calculator.calculate_full_risk(params_5year)
        
        # 3. محاسبه ریسک lifetime (تا 90 سالگی یا +50 سال)
        gail_input_lifetime = gail_input.copy()
        projection_lifetime = min(90, questionnaire.age + 50)
        gail_input_lifetime["projection_age"] = projection_lifetime
        
        params_lifetime = GailInputParams(**gail_input_lifetime)
        result_lifetime = self.calculator.calculate_full_risk(params_lifetime)
        
        # 4. دسته‌بندی ریسک
        risk_category = self._categorize_risk(result_5year.relative_risk)
        
        # 5. تفسیر نتایج به فارسی
        interpretation = self._interpret_risk_fa(
            result_5year.absolute_risk,
            result_5year.relative_risk,
            risk_category
        )
        
        # 6. تولید توصیه‌های بالینی
        recommendations = self._get_recommendations_fa(
            risk_category,
            questionnaire.age,
            result_5year.relative_risk
        )
        
        # 7. ساخت پاسخ
        risk_assessment = RiskAssessment(
            absolute_risk_5year=result_5year.absolute_risk,
            average_risk_5year=result_5year.average_risk,
            relative_risk_5year=result_5year.relative_risk,
            absolute_risk_lifetime=result_lifetime.absolute_risk,
            average_risk_lifetime=result_lifetime.average_risk,
            relative_risk_lifetime=result_lifetime.relative_risk,
            risk_category=risk_category,
            interpretation_fa=interpretation,
            recommendations_fa=recommendations
        )
        
        patient_info = PatientInfo(
            age=questionnaire.age,
            race_name_fa=self.mapper.get_race_name_fa(gail_input["race"]),
            projection_age_5year=params_5year.projection_age,
            projection_age_lifetime=params_lifetime.projection_age
        )
        
        return GailResultResponse(
            success=True,
            message="محاسبه ریسک با موفقیت انجام شد",
            patient_info=patient_info,
            risk_assessment=risk_assessment,
            metadata={
                "model_version": "Gail v2 (BCRA)",
                "calculation_date": datetime.utcnow().isoformat() + "Z",
                "input_params": gail_input  # برای debugging
            }
        )
    
    @staticmethod
    def _categorize_risk(relative_risk: float) -> str:
        """
        دسته‌بندی سطح ریسک
        
        معیارها:
        - پایین: < 1.0 (کمتر از میانگین)
        - متوسط: 1.0 - 1.66
        - بالا: >= 1.67 (حدود NCI برای high risk)
        
        Args:
            relative_risk: ریسک نسبی
        
        Returns:
            دسته: "پایین", "متوسط", "بالا"
        """
        if relative_risk < 1.0:
            return "پایین"
        elif relative_risk < 1.67:
            return "متوسط"
        else:
            return "بالا"
    
    @staticmethod
    def _interpret_risk_fa(
        absolute_risk: float,
        relative_risk: float,
        category: str
    ) -> str:
        """
        تفسیر فارسی ریسک
        
        Args:
            absolute_risk: ریسک مطلق
            relative_risk: ریسک نسبی
            category: دسته ریسک
        
        Returns:
            متن تفسیر به فارسی
        """
        abs_percent = absolute_risk * 100
        
        if category == "پایین":
            return (
                f"ریسک شما {relative_risk:.2f} برابر میانگین است "
                f"(احتمال ابتلا در 5 سال آینده: {abs_percent:.2f}%). "
                f"این کمتر از میانگین است که خبر خوبی است، اما همچنان "
                f"باید غربالگری‌های توصیه شده را انجام دهید."
            )
        elif category == "متوسط":
            return (
                f"ریسک شما {relative_risk:.2f} برابر میانگین است "
                f"(احتمال ابتلا در 5 سال آینده: {abs_percent:.2f}%). "
                f"شما در محدوده طبیعی قرار دارید. پیروی از دستورالعمل‌های "
                f"غربالگری استاندارد توصیه می‌شود."
            )
        else:  # بالا
            return (
                f"ریسک شما {relative_risk:.2f} برابر میانگین است "
                f"(احتمال ابتلا در 5 سال آینده: {abs_percent:.2f}%). "
                f"این بالاتر از میانگین است. حتماً با پزشک متخصص خود در مورد "
                f"استراتژی‌های پیشگیری و غربالگری دقیق‌تر مشورت کنید."
            )
    
    @staticmethod
    def _get_recommendations_fa(
        category: str,
        age: int,
        relative_risk: float
    ) -> List[str]:
        """
        تولید توصیه‌های بالینی بر اساس ریسک و سن
        
        Args:
            category: دسته ریسک
            age: سن بیمار
            relative_risk: ریسک نسبی
        
        Returns:
            لیست توصیه‌ها به فارسی
        """
        recommendations = []
        
        # توصیه‌های پایه برای همه
        if age >= 40:
            recommendations.append("ماموگرافی سالانه یا دوسالانه طبق نظر پزشک")
        else:
            recommendations.append("معاینه بالینی سالانه توسط پزشک")
        
        recommendations.extend([
            "خودآزمایی ماهانه سینه (آموزش از پزشک یا پرستار)",
            "حفظ وزن مناسب و ورزش منظم",
            "محدود کردن مصرف الکل",
            "رژیم غذایی سالم و سرشار از میوه و سبزیجات"
        ])
        
        # توصیه‌های اضافی برای ریسک بالا
        if category == "بالا" or relative_risk >= 1.67:
            recommendations.extend([
                "⚠️ مشاوره با متخصص سرطان‌شناسی یا کلینیک ریسک بالای سرطان سینه",
                "⚠️ بررسی نیاز به MRI سینه سالانه (علاوه بر ماموگرافی)",
                "⚠️ مشاوره ژنتیک در صورت سابقه خانوادگی قوی",
                "⚠️ بحث درباره داروهای پیشگیرانه (chemoprevention) مثل تاموکسیفن یا رالوکسیفن"
            ])
        
        # توصیه اضافی برای سنین بالاتر
        if age >= 50 and category in ["متوسط", "بالا"]:
            recommendations.append("معاینه بالینی هر 6 ماه یکبار")
        
        # توصیه برای سنین پایین‌تر با ریسک بالا
        if age < 40 and category == "بالا":
            recommendations.append(
                "⚠️ شروع غربالگری زودتر از 40 سالگی - طبق نظر پزشک"
            )
        
        return recommendations
