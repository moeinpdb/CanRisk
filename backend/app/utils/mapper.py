"""
Questionnaire to Model Input Mapper
تبدیل پاسخ‌های پرسشنامه به ورودی مدل Gail

CRITICAL: این mappingها مستقیماً از منطق BCPT.cs و BCPTConvert.cs کپی شده‌اند
"""

from typing import Optional, Dict, Any
from app.models.questionnaire import PatientQuestionnaire


class QuestionnaireMapper:
    """
    Mapper برای تبدیل پرسشنامه NCI به ورودی مدل Gail
    
    این کلاس تبدیلات دقیق مطابق با BCPTConvert.cs را انجام می‌دهد
    """
    
    @staticmethod
    def map_menarche_age(age_at_menarche: int) -> int:
        """
        Map سن قاعدگی به کد Gail
        
        Gail coding:
            0: 14 or older
            1: 12-13
            2: 7-11
        
        Args:
            age_at_menarche: سن واقعی قاعدگی (7-17)
        
        Returns:
            کد Gail (0, 1, 2)
        """
        if age_at_menarche >= 14:
            return 0
        elif 12 <= age_at_menarche <= 13:
            return 1
        else:  # 7-11
            return 2
    
    @staticmethod
    def map_first_birth_age(
        age_at_first_birth: Optional[int],
        current_age: int
    ) -> int:
        """
        Map سن اولین زایمان به کد Gail
        
        Gail coding:
            0: < 20 or unknown
            1: 20-24
            2: 25-29 or no children
            3: >= 30
        
        Args:
            age_at_first_birth: سن واقعی زایمان (None = بدون فرزند)
            current_age: سن فعلی (برای validation)
        
        Returns:
            کد Gail (0, 1, 2, 3)
        """
        if age_at_first_birth is None:
            # بدون فرزند
            return 2
        
        if age_at_first_birth < 20:
            return 0
        elif 20 <= age_at_first_birth < 25:
            return 1
        elif 25 <= age_at_first_birth < 30:
            return 2
        else:  # >= 30
            return 3
    
    @staticmethod
    def map_biopsy_status(ever_had_biopsy: str) -> int:
        """
        Map وضعیت بیوپسی به کد Gail
        
        Gail coding:
            0: No
            1: Yes
            99: Unknown
        
        Args:
            ever_had_biopsy: "yes", "no", "unknown"
        
        Returns:
            کد Gail (0, 1, 99)
        """
        mapping = {
            "no": 0,
            "yes": 1,
            "unknown": 99
        }
        return mapping.get(ever_had_biopsy.lower(), 99)
    
    @staticmethod
    def map_number_of_biopsies(
        ever_had_biopsy: str,
        number_of_biopsies: Optional[int]
    ) -> int:
        """
        Map تعداد بیوپسی‌ها به کد Gail
        
        Gail coding:
            0: None
            1: One
            2: Two or more
            99: Unknown
        
        این منطق مطابق با BCPTConvert.NumberOfBiopsy() است
        
        Args:
            ever_had_biopsy: وضعیت بیوپسی
            number_of_biopsies: تعداد واقعی (اگر مشخص باشد)
        
        Returns:
            کد Gail (0, 1, 2, 99)
        """
        biopsy_status = QuestionnaireMapper.map_biopsy_status(ever_had_biopsy)
        
        # اگر بیوپسی نداشته
        if biopsy_status == 0:
            return 0
        
        # اگر نامشخص
        if biopsy_status == 99:
            return 99
        
        # اگر بیوپسی داشته (biopsy_status == 1)
        if number_of_biopsies is None:
            # اگر گفته بیوپسی داشته ولی تعداد نگفته -> فرض یکی
            return 1
        elif number_of_biopsies == 1:
            return 1
        elif 2 <= number_of_biopsies <= 30:
            return 2
        else:
            # out of range -> فرض نامشخص
            return 99
    
    @staticmethod
    def map_hyperplasia(
        has_atypical_hyperplasia: str,
        ever_had_biopsy: str
    ) -> int:
        """
        Map وضعیت هایپرپلازیا به کد Gail
        
        Gail coding:
            0: No
            1: Yes
            99: Unknown or no biopsy
        
        مطابق BCPTConvert.Hyperplasia()
        
        Args:
            has_atypical_hyperplasia: "yes", "no", "unknown"
            ever_had_biopsy: وضعیت بیوپسی
        
        Returns:
            کد Gail (0, 1, 99)
        """
        # اگر بیوپسی نداشته، هایپرپلازیا نامشخص است
        if ever_had_biopsy == "no":
            return 99
        
        mapping = {
            "no": 0,
            "yes": 1,
            "unknown": 99
        }
        return mapping.get(has_atypical_hyperplasia.lower(), 99)
    
    @staticmethod
    def map_relatives(num_first_degree_relatives: int, race: int) -> int:
        """
        Map تعداد بستگان به کد Gail
        
        Gail coding:
            0: None
            1: One
            2: Two or more (برای نژادهای 1-6)
            1: Two or more (برای نژادهای آسیایی 7-12 - محدودیت مدل)
        
        Args:
            num_first_degree_relatives: تعداد واقعی
            race: کد نژاد (برای تصمیم‌گیری درباره 2+)
        
        Returns:
            کد Gail (0, 1, 2)
        """
        if num_first_degree_relatives == 0:
            return 0
        elif num_first_degree_relatives == 1:
            return 1
        elif num_first_degree_relatives >= 2:
            # برای نژادهای آسیایی (7-12)، مدل فقط 0 و 1 را پشتیبانی می‌کند
            if race >= 7:
                return 1  # cap at 1
            else:
                return 2  # برای نژادهای دیگر
        else:
            return 0  # fallback
    
    @staticmethod
    def map_race(race: int, sub_race: Optional[int]) -> int:
        """
        Map نژاد و زیرنژاد به کد نهایی Gail
        
        Gail race codes:
            1: White/Other
            2: African American
            3: Hispanic
            4-6: (average woman variants)
            7: Chinese
            8: Japanese
            9: Filipino
            10: Hawaiian
            11: Other Pacific Islander
            12: Other Asian
        
        Args:
            race: نژاد اصلی (1-5 در questionnaire)
            sub_race: زیرنژاد آسیایی (7-12)
        
        Returns:
            کد نژاد نهایی برای Gail (1-12)
        """
        # اگر زیرنژاد آسیایی مشخص شده
        if sub_race is not None and 7 <= sub_race <= 12:
            return sub_race
        
        # اگر نژاد اصلی "Asian/Pacific Islander" (4) است ولی زیرنژاد مشخص نشده
        # -> از "Other Asian" (12) استفاده کن
        if race == 4 and sub_race is None:
            return 12  # Other Asian as default
        
        # برای سایر نژادها
        return race
    
    @classmethod
    def questionnaire_to_gail_input(
        cls,
        questionnaire: PatientQuestionnaire
    ) -> Dict[str, Any]:
        """
        تبدیل کامل پرسشنامه به ورودی مدل Gail
        
        این متد تمام تبدیلات را انجام می‌دهد و یک dictionary
        آماده برای GailInputParams برمی‌گرداند
        
        Args:
            questionnaire: پرسشنامه تکمیل شده
        
        Returns:
            دیکشنری حاوی پارامترهای ورودی Gail
        """
        
        # تعیین نژاد نهایی
        final_race = cls.map_race(questionnaire.race, questionnaire.sub_race)
        
        # تعداد بستگان با در نظر گرفتن نژاد
        first_deg_relatives_code = cls.map_relatives(
            questionnaire.num_first_degree_relatives,
            final_race
        )
        
        return {
            "current_age": questionnaire.age,
            "projection_age": questionnaire.age + 5,  # 5-year risk
            "menarche_age": cls.map_menarche_age(questionnaire.age_at_menarche),
            "first_live_birth_age": cls.map_first_birth_age(
                questionnaire.age_at_first_birth,
                questionnaire.age
            ),
            "first_deg_relatives": first_deg_relatives_code,
            "ever_had_biopsy": cls.map_biopsy_status(questionnaire.ever_had_biopsy),
            "number_of_biopsy": cls.map_number_of_biopsies(
                questionnaire.ever_had_biopsy,
                questionnaire.number_of_biopsies
            ),
            "hyperplasia": cls.map_hyperplasia(
                questionnaire.has_atypical_hyperplasia,
                questionnaire.ever_had_biopsy
            ),
            "race": final_race
        }
    
    @staticmethod
    def get_race_name_fa(race_code: int) -> str:
        """
        دریافت نام فارسی نژاد
        
        Args:
            race_code: کد نژاد Gail (1-12)
        
        Returns:
            نام فارسی
        """
        race_names = {
            1: "سفیدپوست/سایر",
            2: "آفریقایی-آمریکایی",
            3: "اسپانیایی‌تبار/لاتین",
            4: "سفیدپوست میانگین",
            5: "آفریقایی-آمریکایی میانگین",
            6: "اسپانیایی‌تبار میانگین",
            7: "چینی",
            8: "ژاپنی",
            9: "فیلیپینی",
            10: "هاوایی",
            11: "سایر جزایر اقیانوس آرام",
            12: "سایر آسیایی"
        }
        return race_names.get(race_code, "نامشخص")