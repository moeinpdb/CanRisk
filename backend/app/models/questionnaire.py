"""
Questionnaire Models
مدل‌های پرسشنامه بیمار - کاملاً مطابق با NCI BCRA Tool
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


class PatientQuestionnaire(BaseModel):
    """
    پرسشنامه کامل ارزیابی ریسک سرطان سینه
    
    مطابق با:
    - NCI Breast Cancer Risk Assessment Tool
    - Gail Model v2
    """
    
    # ========== ELIGIBILITY CRITERIA ==========
    has_breast_cancer_history: bool = Field(
        ...,
        description="سابقه سرطان سینه یا DCIS/LCIS یا رادیوتراپی قفسه سینه"
    )
    
    has_genetic_mutation: Literal["yes", "no", "unknown"] = Field(
        "unknown",
        description="جهش ژنتیکی BRCA1/BRCA2 یا سندرم ژنتیکی"
    )
    
    # ========== DEMOGRAPHICS ==========
    age: int = Field(
        ...,
        ge=35,
        le=85,
        description="سن بیمار (35-85 سال)",
        examples=[45]
    )
    
    race: int = Field(
        ...,
        ge=1,
        le=5,
        description="نژاد/قومیت (1=White, 2=African American, 3=Hispanic, 4=Asian/Pacific Islander, 5=Other)",
        examples=[1]
    )
    
    sub_race: Optional[int] = Field(
        None,
        ge=7,
        le=12,
        description="زیرگروه آسیایی (7=Chinese, 8=Japanese, 9=Filipino, 10=Hawaiian, 11=Other PI, 12=Other Asian)"
    )
    
    # ========== PATIENT & FAMILY HISTORY ==========
    ever_had_biopsy: Literal["yes", "no", "unknown"] = Field(
        "unknown",
        description="سابقه بیوپسی سینه با تشخیص خوش‌خیم"
    )
    
    number_of_biopsies: Optional[int] = Field(
        None,
        ge=1,
        le=30,
        description="تعداد بیوپسی‌های انجام شده"
    )
    
    has_atypical_hyperplasia: Literal["yes", "no", "unknown"] = Field(
        "unknown",
        description="هایپرپلازیا آتیپیک در بیوپسی"
    )
    
    age_at_menarche: int = Field(
        ...,
        ge=7,
        le=17,
        description="سن اولین قاعدگی (7-17)",
        examples=[12]
    )
    
    age_at_first_birth: Optional[int] = Field(
        None,
        ge=10,
        le=55,
        description="سن اولین زایمان زنده (None = بدون فرزند)",
        examples=[28]
    )
    
    num_first_degree_relatives: int = Field(
        0,
        ge=0,
        le=10,
        description="تعداد بستگان درجه یک (مادر/خواهر/دختر) مبتلا به سرطان سینه",
        examples=[1]
    )
    
    # ========== VALIDATORS ==========
    
    @field_validator('has_breast_cancer_history')
    @classmethod
    def check_eligibility_cancer_history(cls, v):
        """بررسی واجد شرایط بودن - سابقه سرطان"""
        if v is True:
            raise ValueError(
                "این ابزار فقط برای افرادی که سابقه سرطان سینه، DCIS، LCIS یا "
                "رادیوتراپی قفسه سینه ندارند، مناسب است."
            )
        return v
    
    @field_validator('has_genetic_mutation')
    @classmethod
    def check_eligibility_genetic(cls, v):
        """بررسی واجد شرایط بودن - جهش ژنتیکی"""
        if v == "yes":
            raise ValueError(
                "این ابزار برای افرادی که جهش BRCA1/BRCA2 دارند توصیه نمی‌شود. "
                "لطفاً با متخصص ژنتیک مشورت کنید."
            )
        return v
    
    @field_validator('age_at_first_birth')
    @classmethod
    def validate_birth_age(cls, v, info):
        """اعتبارسنجی سن زایمان"""
        if v is not None:
            current_age = info.data.get('age')
            if current_age and v >= current_age:
                raise ValueError(
                    f"سن اولین زایمان ({v}) نمی‌تواند بیشتر یا مساوی سن فعلی ({current_age}) باشد"
                )
            if v < 10:
                raise ValueError("سن اولین زایمان نمی‌تواند کمتر از 10 سال باشد")
        return v
    
    @field_validator('number_of_biopsies')
    @classmethod
    def validate_biopsy_count(cls, v, info):
        """اعتبارسنجی تعداد بیوپسی"""
        ever_had = info.data.get('ever_had_biopsy')
        if ever_had == 'no' and v is not None and v > 0:
            raise ValueError("تعداد بیوپسی نمی‌تواند بیشتر از صفر باشد وقتی 'سابقه بیوپسی' خیر است")
        if ever_had == 'yes' and (v is None or v < 1):
            raise ValueError("اگر سابقه بیوپسی دارید، باید تعداد را مشخص کنید")
        return v
    
    @field_validator('sub_race')
    @classmethod
    def validate_sub_race(cls, v, info):
        """اعتبارسنجی زیرنژاد"""
        race = info.data.get('race')
        if v is not None:
            if race != 4:  # 4 = Asian/Pacific Islander
                raise ValueError("زیرنژاد فقط برای نژاد 'آسیایی/جزایر اقیانوس آرام' قابل انتخاب است")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "has_breast_cancer_history": False,
                "has_genetic_mutation": "no",
                "age": 45,
                "race": 1,
                "sub_race": None,
                "ever_had_biopsy": "yes",
                "number_of_biopsies": 1,
                "has_atypical_hyperplasia": "no",
                "age_at_menarche": 12,
                "age_at_first_birth": 28,
                "num_first_degree_relatives": 1
            }
        }