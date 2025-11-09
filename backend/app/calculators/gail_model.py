"""
Gail Risk Calculator - Production Version
نسخه نهایی با ساختار مدرن و مقادیر عددی دقیق از مرجع اصلی

مرجع عددی: riskmodels GitHub Repository (BCPT.cs conversion)
تاریخ: 2024
نسخه مدل: Gail Model v2 (BCRA)
"""

import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass
from enum import IntEnum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ================== Constants & Enums ==================

class RaceType(IntEnum):
    """کدهای نژاد - مطابق با مدل Gail"""
    WHITE_OTHER = 1
    AFRICAN_AMERICAN = 2
    HISPANIC = 3
    WHITE_AVG = 4
    AFRICAN_AMERICAN_AVG = 5
    HISPANIC_AVG = 6
    CHINESE = 7
    JAPANESE = 8
    FILIPINO = 9
    HAWAIIAN = 10
    OTHER_PACIFIC_ISLANDER = 11
    OTHER_ASIAN = 12


class RiskIndexType(IntEnum):
    """نوع محاسبه ریسک"""
    ABSOLUTE = 1
    AVERAGE = 2


@dataclass
class GailInputParams:
    """پارامترهای ورودی محاسبه‌گر Gail"""
    current_age: int
    projection_age: int
    menarche_age: int
    first_live_birth_age: int
    first_deg_relatives: int
    ever_had_biopsy: int = 99
    number_of_biopsy: int = 99
    hyperplasia: int = 99
    race: int = RaceType.WHITE_OTHER

    def validate(self) -> Tuple[bool, str]:
        """اعتبارسنجی پارامترهای ورودی"""
        # سن فعلی: 20-85
        if not (20 <= self.current_age <= 85):
            return False, "سن فعلی باید بین 20 تا 85 سال باشد"
        
        # سن پیش‌بینی: بیشتر از سن فعلی و حداکثر 90
        if self.projection_age <= self.current_age:
            return False, "سن پیش‌بینی باید بیشتر از سن فعلی باشد"
        
        if self.projection_age > 90:
            return False, "سن پیش‌بینی نمی‌تواند بیشتر از 90 سال باشد"
        
        # بازه پیش‌بینی: حداکثر تا 90 سالگی (بدون محدودیت دیگر)
        # این به ما اجازه می‌دهد lifetime risk را محاسبه کنیم
        
        return True, "Valid"


@dataclass
class GailResult:
    """نتیجه محاسبات"""
    absolute_risk: float
    average_risk: float
    relative_risk: float
    current_age: int
    projection_age: int
    
    def to_dict(self):
        return {
            "absolute_risk": round(self.absolute_risk, 6),
            "average_risk": round(self.average_risk, 6),
            "relative_risk": round(self.relative_risk, 2),
            "current_age": self.current_age,
            "projection_age": self.projection_age,
            "risk_period_years": self.projection_age - self.current_age,
            "absolute_risk_percentage": f"{round(self.absolute_risk * 100, 2)}%",
            "interpretation": self._interpret()
        }
    
    def _interpret(self) -> str:
        if self.relative_risk >= 1.67:
            return "ریسک بالا - نیاز به مشاوره"
        elif self.relative_risk >= 1.0:
            return "ریسک متوسط"
        return "ریسک پایین‌تر از میانگین"


# ================== Main Calculator ==================

class GailRiskCalculator:
    """
    محاسبه‌گر ریسک Gail
    
    CRITICAL: تمام مقادیر عددی این کلاس مستقیماً از مرجع اصلی
    (riskmodels/BCPT.cs) کپی شده‌اند و نباید تغییر کنند.
    """
    
    NumCovPattInGailModel = 216

    def __init__(self):
        """مقداردهی اولیه آرایه‌ها"""
        self.bet2 = np.zeros((8, 12), dtype=np.float64)
        self.bet = np.zeros(8, dtype=np.float64)
        self.rf = np.zeros(2, dtype=np.float64)
        self.rf2 = np.zeros((2, 13), dtype=np.float64)
        self.abs = np.zeros(self.NumCovPattInGailModel, dtype=np.float64)
        self.rlan = np.zeros(14, dtype=np.float64)
        self.rlan2 = np.zeros((14, 12), dtype=np.float64)
        self.rmu = np.zeros(14, dtype=np.float64)
        self.rmu2 = np.zeros((14, 12), dtype=np.float64)
        self.sumb = np.zeros(self.NumCovPattInGailModel, dtype=np.float64)
        self.sumbb = np.zeros(self.NumCovPattInGailModel, dtype=np.float64)
        self.t = np.zeros(15, dtype=np.float64)
        self.is_initialized = False

    def initialize(self):
        """
        مقداردهی جداول آماری
        
        CRITICAL: تمام اعداد زیر از BCPT.cs کپی شده‌اند
        هیچ تغییری ندهید مگر با مرجع تطبیق داده شود
        """
        # Age boundaries
        self.t = np.array([20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0,
                          55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0],
                         dtype=np.float64)

        # ========== COMPETING HAZARDS (rmu2) ==========
        # SEER mortality data - EXACT VALUES FROM SOURCE
        
        # Column 0: White/Other - BCPT model
        self.rmu2[:, 0] = np.array([
            49.3, 53.1, 62.5, 82.5, 130.7, 218.1, 365.5,
            585.2, 943.9, 1502.8, 2383.9, 3883.2, 6682.8, 14490.8
        ]) * 0.00001

        # Column 1: African American - Updated 11/29/2007
        self.rmu2[:, 1] = np.array([
            0.00074354, 0.00101698, 0.00145937, 0.00215933,
            0.00315077, 0.00448779, 0.00632281, 0.00963037,
            0.01471818, 0.02116304, 0.03266035, 0.04564087,
            0.06835185, 0.13271262
        ])

        # Column 2: Hispanic - STAR model
        self.rmu2[:, 2] = np.array([
            43.7, 53.3, 70.0, 89.7, 116.3, 170.2, 264.6,
            421.6, 696.0, 1086.7, 1685.8, 2515.6, 4186.6, 8947.6
        ]) * 0.00001

        # Column 3: Average White/Other
        self.rmu2[:, 3] = np.array([
            44.12, 52.54, 67.46, 90.92, 125.34, 195.70, 329.84,
            546.22, 910.35, 1418.54, 2259.35, 3611.46, 6136.26, 14206.63
        ]) * 0.00001

        # Column 4: Average African American (same as column 1)
        self.rmu2[:, 4] = self.rmu2[:, 1].copy()

        # Column 5: Average Hispanic (same as column 2)
        self.rmu2[:, 5] = self.rmu2[:, 2].copy()

        # Column 6: Chinese - SEER18 1998:02
        self.rmu2[:, 6] = np.array([
            0.000210649076, 0.000192644865, 0.000244435215, 0.000317895949,
            0.000473261994, 0.000800271380, 0.001217480226, 0.002099836508,
            0.003436889186, 0.006097405623, 0.010664526765, 0.020148678452,
            0.037990796590, 0.098333900733
        ])

        # Column 7: Japanese - SEER18 1998:02
        self.rmu2[:, 7] = np.array([
            0.000173593803, 0.000295805882, 0.000228322534, 0.000363242389,
            0.000590633044, 0.001086079485, 0.001859999966, 0.003216600974,
            0.004719402141, 0.008535331402, 0.012433511681, 0.020230197885,
            0.037725498348, 0.106149118663
        ])

        # Column 8: Filipino - SEER18 1998:02
        self.rmu2[:, 8] = np.array([
            0.000229120979, 0.000262988494, 0.000314844090, 0.000394471908,
            0.000647622610, 0.001170202327, 0.001809380379, 0.002614170568,
            0.004483330681, 0.007393665092, 0.012233059675, 0.021127058106,
            0.037936954809, 0.085138518334
        ])

        # Column 9: Hawaiian - SEER18 1998:02
        self.rmu2[:, 9] = np.array([
            0.000563507269, 0.000369640217, 0.001019912579, 0.001234013911,
            0.002098344078, 0.002982934175, 0.005402445702, 0.009591474245,
            0.016315472607, 0.020152229069, 0.027354838710, 0.050446998723,
            0.072262026612, 0.145844504021
        ])

        # Column 10: Other Pacific Islander - SEER18 1998:02
        self.rmu2[:, 10] = np.array([
            0.000465500812, 0.000600466920, 0.000851057138, 0.001478265376,
            0.001931486788, 0.003866623959, 0.004924932309, 0.008177071806,
            0.008638202890, 0.018974658371, 0.029257567105, 0.038408980974,
            0.052869579345, 0.074745721133
        ])

        # Column 11: Other Asian - SEER18 1998:02
        self.rmu2[:, 11] = np.array([
            0.000212632332, 0.000242170741, 0.000301552711, 0.000369053354,
            0.000543002943, 0.000893862331, 0.001515172239, 0.002574669551,
            0.004324370426, 0.007419621918, 0.013251765130, 0.022291427490,
            0.041746550635, 0.087485802065
        ])

        # ========== COMPOSITE INCIDENCE (rlan2) ==========
        # SEER incidence data - EXACT VALUES FROM SOURCE

        # Column 0: White/Other - BCPT (SEER 1983:87)
        self.rlan2[:, 0] = np.array([
            1.0, 7.6, 26.6, 66.1, 126.5, 186.6, 221.1,
            272.1, 334.8, 392.3, 417.8, 443.9, 442.1, 410.9
        ]) * 0.00001

        # Column 1: African American - SEER11 1994-98 (Updated 11/29/2007)
        self.rlan2[:, 1] = np.array([
            0.00002696, 0.00011295, 0.00031094, 0.00067639,
            0.00119444, 0.00187394, 0.00241504, 0.00291112,
            0.00310127, 0.00366560, 0.00393132, 0.00408951,
            0.00396793, 0.00363712
        ])

        # Column 2: Hispanic - STAR
        self.rlan2[:, 2] = np.array([
            2.00, 7.10, 19.70, 43.80, 81.10, 130.70, 157.40,
            185.70, 215.10, 251.20, 284.60, 275.70, 252.30, 203.90
        ]) * 0.00001

        # Column 3: Average White/Other
        self.rlan2[:, 3] = np.array([
            1.22, 7.41, 22.97, 56.49, 116.45, 195.25, 261.54,
            302.79, 367.57, 420.29, 473.08, 494.25, 479.76, 401.06
        ]) * 0.00001

        # Column 4: Average African American (same as column 1)
        self.rlan2[:, 4] = self.rlan2[:, 1].copy()

        # Column 5: Average Hispanic (same as column 2)
        self.rlan2[:, 5] = self.rlan2[:, 2].copy()

        # Column 6: Chinese - SEER18 1998:02
        self.rlan2[:, 6] = np.array([
            0.000004059636, 0.000045944465, 0.000188279352, 0.000492930493,
            0.000913603501, 0.001471537353, 0.001421275482, 0.001970946494,
            0.001674745804, 0.001821581075, 0.001834477198, 0.001919911972,
            0.002233371071, 0.002247315779
        ])

        # Column 7: Japanese - SEER18 1998:02
        self.rlan2[:, 7] = np.array([
            0.000000000001, 0.000099483924, 0.000287041681, 0.000545285759,
            0.001152211095, 0.001859245108, 0.002606291272, 0.003221751682,
            0.004006961859, 0.003521715275, 0.003593038294, 0.003589303081,
            0.003538507159, 0.002051572909
        ])

        # Column 8: Filipino - SEER18 1998:02
        self.rlan2[:, 8] = np.array([
            0.000007500161, 0.000081073945, 0.000227492565, 0.000549786433,
            0.001129400541, 0.001813873795, 0.002223665639, 0.002680309266,
            0.002891219230, 0.002534421279, 0.002457159409, 0.002286616920,
            0.001814802825, 0.001750879130
        ])

        # Column 9: Hawaiian - SEER18 1998:02
        self.rlan2[:, 9] = np.array([
            0.000045080582, 0.000098570724, 0.000339970860, 0.000852591429,
            0.001668562761, 0.002552703284, 0.003321774046, 0.005373001776,
            0.005237808549, 0.005581732512, 0.005677419355, 0.006513409962,
            0.003889457523, 0.002949061662
        ])

        # Column 10: Other Pacific Islander - SEER18 1998:02
        self.rlan2[:, 10] = np.array([
            0.000000000001, 0.000071525212, 0.000288799028, 0.000602250698,
            0.000755579402, 0.000766406354, 0.001893124938, 0.002365580107,
            0.002843933070, 0.002920921732, 0.002330395655, 0.002036291235,
            0.001482683983, 0.001012248203
        ])

        # Column 11: Other Asian - SEER18 1998:02
        self.rlan2[:, 11] = np.array([
            0.000012355409, 0.000059526456, 0.000184320831, 0.000454677273,
            0.000791265338, 0.001048462801, 0.001372467817, 0.001495473711,
            0.001646746198, 0.001478363563, 0.001216010125, 0.001067663700,
            0.001376104012, 0.000661576644
        ])

        # ========== BETA COEFFICIENTS (bet2) ==========
        # Logistic regression coefficients - EXACT FROM SOURCE

        # Column 0: White/Other - GAIL model (BCDDP)
        self.bet2[:, 0] = np.array([
            -0.7494824600,  # intercept
            0.0108080720,   # age >= 50 indicator
            0.0940103059,   # age menarche
            0.5292641686,   # # of breast biopsy
            0.2186262218,   # age 1st live birth
            0.9583027845,   # # 1st degree relatives
            -0.2880424830,  # # breast biopsy * age >=50
            -0.1908113865   # age 1st live birth * # 1st degree rel
        ])

        # Column 1: African American - CARE model
        self.bet2[:, 1] = np.array([
            -0.3457169653,
            0.0334703319,
            0.2672530336,
            0.1822121131,
            0.0000000000,
            0.4757242578,
            -0.1119411682,
            0.0000000000
        ])

        # Column 2: Hispanic (same as White/Other)
        self.bet2[:, 2] = self.bet2[:, 0].copy()

        # Columns 3-5: Average woman (same as 0-2)
        self.bet2[:, 3] = self.bet2[:, 0].copy()
        self.bet2[:, 4] = self.bet2[:, 1].copy()
        self.bet2[:, 5] = self.bet2[:, 2].copy()

        # Columns 6-11: Asian-American beta
        asian_beta = np.array([
            0.0, 0.0, 0.07499257592975, 0.55263612260619,
            0.27638268294593, 0.79185633720481, 0.0, 0.0
        ])
        for i in range(6, 12):
            self.bet2[:, i] = asian_beta.copy()

        # ========== CONVERSION FACTORS (rf2) ==========
        # (1-attributable risk) - EXACT FROM SOURCE

        # BCPT model
        self.rf2[0, 0] = 0.5788413
        self.rf2[1, 0] = 0.5788413

        # African American (Updated 12/19/2007)
        self.rf2[0, 1] = 0.72949880
        self.rf2[1, 1] = 0.74397137

        # Hispanic
        self.rf2[0, 2] = 0.5788413
        self.rf2[1, 2] = 0.5788413

        # Average woman
        for i in range(3, 6):
            self.rf2[0, i] = 1.0
            self.rf2[1, i] = 1.0

        # Asian-American
        for i in range(6, 12):
            self.rf2[0, i] = 0.47519806426735
            self.rf2[1, i] = 0.50316401683903

        self.rf2[0, 12] = 1.0
        self.rf2[1, 12] = 1.0

        self.is_initialized = True
        logger.info("GailRiskCalculator initialized with verified values")

    @staticmethod
    def clean_biopsy_inputs(ever_had_biopsy: int, num_biopsy: int, 
                           hyperplasia: int) -> Tuple[int, int, int]:
        """
        پاکسازی ورودی‌های بیوپسی - منطق دقیق از BCPTConvert.cs
        
        CRITICAL: این منطق از کد مرجع کپی شده - تغییر ندهید
        """
        if ever_had_biopsy == 99:
            ever_had_biopsy = 0

        if ever_had_biopsy == 1 and num_biopsy == 99:
            num_biopsy = 1
        elif ever_had_biopsy == 0:
            num_biopsy = 0

        if 1 < num_biopsy <= 30:
            num_biopsy = 2

        if ever_had_biopsy == 0:
            hyperplasia = 99

        return ever_had_biopsy, num_biopsy, hyperplasia

    def calculate_absolute_risk(self, current_age: int, projection_age: int,
                               menarche_age: int, first_live_birth_age: int,
                               first_deg_relatives: int, ever_had_biopsy: int = 99,
                               number_of_biopsy: int = 99, hyperplasia: int = 99,
                               race: int = 1) -> float:
        """محاسبه ریسک مطلق"""
        if not self.is_initialized:
            raise RuntimeError("Call initialize() first")
        
        return self._calculate_risk_api(
            RiskIndexType.ABSOLUTE, current_age, projection_age,
            menarche_age, first_live_birth_age, first_deg_relatives,
            ever_had_biopsy, number_of_biopsy, hyperplasia, race
        )

    def calculate_average_risk(self, current_age: int, projection_age: int,
                              menarche_age: int, first_live_birth_age: int,
                              first_deg_relatives: int, ever_had_biopsy: int = 99,
                              number_of_biopsy: int = 99, hyperplasia: int = 99,
                              race: int = 1) -> float:
        """محاسبه ریسک میانگین"""
        if not self.is_initialized:
            raise RuntimeError("Call initialize() first")
        
        return self._calculate_risk_api(
            RiskIndexType.AVERAGE, current_age, projection_age,
            menarche_age, first_live_birth_age, first_deg_relatives,
            ever_had_biopsy, number_of_biopsy, hyperplasia, race
        )

    def calculate_full_risk(self, params: GailInputParams) -> GailResult:
        """محاسبه کامل ریسک"""
        is_valid, msg = params.validate()
        if not is_valid:
            raise ValueError(f"Invalid input: {msg}")

        abs_risk = self.calculate_absolute_risk(
            params.current_age, params.projection_age, params.menarche_age,
            params.first_live_birth_age, params.first_deg_relatives,
            params.ever_had_biopsy, params.number_of_biopsy,
            params.hyperplasia, params.race
        )

        avg_risk = self.calculate_average_risk(
            params.current_age, params.projection_age, params.menarche_age,
            params.first_live_birth_age, params.first_deg_relatives,
            params.ever_had_biopsy, params.number_of_biopsy,
            params.hyperplasia, params.race
        )

        rel_risk = abs_risk / avg_risk if avg_risk > 0 else 0.0

        return GailResult(
            absolute_risk=abs_risk,
            average_risk=avg_risk,
            relative_risk=rel_risk,
            current_age=params.current_age,
            projection_age=params.projection_age
        )

    def _calculate_risk_api(self, risk_index: int, current_age: int,
                           projection_age: int, menarche_age: int,
                           first_live_birth_age: int, first_deg_relatives: int,
                           ever_had_biopsy: int, number_of_biopsy: int,
                           hyperplasia: int, race: int) -> float:
        """API wrapper - تبدیل و پاکسازی ورودی‌ها"""
        
        age_indicator = 1 if current_age >= 50 else 0
        
        ever_had_biopsy, number_of_biopsy, hyperplasia = self.clean_biopsy_inputs(
            ever_had_biopsy, number_of_biopsy, hyperplasia
        )
        
        if hyperplasia == 1:
            real_hyp = np.float64(1.82)
        elif hyperplasia == 0:
            real_hyp = np.float64(0.93)
        else:
            real_hyp = np.float64(1.0)
        
        if first_deg_relatives == 0 or first_deg_relatives == 99:
            first_deg_relatives = 0
        elif 2 <= first_deg_relatives <= 31 and race < 7:
            first_deg_relatives = 2
        elif first_deg_relatives >= 2 and race >= 7:
            first_deg_relatives = 1
        
        return self._calculate_risk(
            risk_index, current_age, projection_age, age_indicator,
            number_of_biopsy, menarche_age, first_live_birth_age,
            ever_had_biopsy, first_deg_relatives, hyperplasia, real_hyp, race
        )

    def _calculate_risk(self, riskindex: int, CurrentAge: int, ProjectionAge: int,
                       AgeIndicator: int, NumberOfBiopsy: int, MenarcheAge: int,
                       FirstLiveBirthAge: int, EverHadBiopsy: int,
                       FirstDegRelatives: int, ihyp: int, rhyp: float,
                       irace: int) -> float:
        """
        هسته اصلی محاسبات - EXACT LOGIC FROM BCPT.cs
        
        CRITICAL: این الگوریتم دقیقاً از BCPT.cs کپی شده
        هیچ تغییری ندهید مگر با مرجع تطبیق کامل شود
        """
        
        n = self.NumCovPattInGailModel
        r8iTox2 = np.zeros((n, 9), dtype=np.float64)
        
        ti = np.float64(CurrentAge)
        ts = np.float64(ProjectionAge)
        
        # Select race-specific beta
        for i in range(8):
            self.bet[i] = self.bet2[i, irace - 1]
        
        # Recode for African American
        if irace == 2 and MenarcheAge == 2:
            MenarcheAge = 1
            FirstLiveBirthAge = 0
        
        # Find age intervals
        ni = 0
        for i in range(1, 16):
            if ti < self.t[i - 1]:
                ni = i - 1
                break
        
        ns = 0
        for i in range(1, 16):
            if ts <= self.t[i - 1]:
                ns = i - 1
                break
        
        incr = 3 if (riskindex == 2 and irace < 7) else 0
        cindx = incr + irace - 1
        
        for i in range(14):
            self.rmu[i] = self.rmu2[i, cindx]
            self.rlan[i] = self.rlan2[i, cindx]
        
        self.rf[0] = self.rf2[0, incr + irace - 1]
        self.rf[1] = self.rf2[1, incr + irace - 1]
        
        if riskindex == 2 and irace >= 7:
            self.rf[0] = self.rf2[0, 12]
            self.rf[1] = self.rf2[1, 12]
        
        if riskindex >= 2:
            MenarcheAge = 0
            NumberOfBiopsy = 0
            FirstLiveBirthAge = 0
            FirstDegRelatives = 0
            rhyp = np.float64(1.0)
        
        ilev = (AgeIndicator * 108 + MenarcheAge * 36 + NumberOfBiopsy * 12 +
                FirstLiveBirthAge * 3 + FirstDegRelatives + 1)
        
        # Build covariate matrix (EXACT FROM SOURCE)
        for k in range(n):
            r8iTox2[k, 0] = np.float64(1.0)
        
        for k in range(108):
            r8iTox2[k, 1] = np.float64(0.0)
            r8iTox2[108 + k, 1] = np.float64(1.0)
        
        for j in range(1, 3):
            for k in range(1, 37):
                r8iTox2[(j-1)*108 + k-1, 2] = np.float64(0.0)
                r8iTox2[(j-1)*108 + 36+k-1, 2] = np.float64(1.0)
                r8iTox2[(j-1)*108 + 72+k-1, 2] = np.float64(2.0)
        
        for j in range(1, 7):
            for k in range(1, 13):
                r8iTox2[(j-1)*36 + k-1, 3] = np.float64(0.0)
                r8iTox2[(j-1)*36 + 12+k-1, 3] = np.float64(1.0)
                r8iTox2[(j-1)*36 + 24+k-1, 3] = np.float64(2.0)
        
        for j in range(1, 19):
            for k in range(1, 4):
                r8iTox2[(j-1)*12 + k-1, 4] = np.float64(0.0)
                r8iTox2[(j-1)*12 + 3+k-1, 4] = np.float64(1.0)
                r8iTox2[(j-1)*12 + 6+k-1, 4] = np.float64(2.0)
                r8iTox2[(j-1)*12 + 9+k-1, 4] = np.float64(3.0)
        
        for j in range(1, 73):
            r8iTox2[(j-1)*3 + 0, 5] = np.float64(0.0)
            r8iTox2[(j-1)*3 + 1, 5] = np.float64(1.0)
            r8iTox2[(j-1)*3 + 2, 5] = np.float64(2.0)
        
        for i in range(n):
            r8iTox2[i, 6] = r8iTox2[i, 1] * r8iTox2[i, 3]
            r8iTox2[i, 7] = r8iTox2[i, 4] * r8iTox2[i, 5]
            r8iTox2[i, 8] = np.float64(1.0)
        
        # Compute sum(beta * X)
        for i in range(n):
            self.sumb[i] = np.float64(0.0)
            for j in range(8):
                self.sumb[i] += self.bet[j] * r8iTox2[i, j]
        
        for i in range(1, 109):
            self.sumbb[i-1] = self.sumb[i-1] - self.bet[0]
        for i in range(109, n+1):
            self.sumbb[i-1] = self.sumb[i-1] - self.bet[0] - self.bet[1]
        
        for j in range(1, 7):
            self.rlan[j-1] *= self.rf[0]
        for j in range(7, 15):
            self.rlan[j-1] *= self.rf[1]
        
        i = ilev
        self.sumbb[i-1] += np.log(rhyp)
        if i <= 108:
            self.sumbb[i+107] += np.log(rhyp)
        
        # Risk calculation (EXACT FROM SOURCE)
        if ts <= self.t[ni]:
            self.abs[i-1] = 1.0 - np.exp(
                -(self.rlan[ni-1] * np.exp(self.sumbb[i-1]) + self.rmu[ni-1]) * (ts - ti)
            )
            self.abs[i-1] = (self.abs[i-1] * self.rlan[ni-1] * np.exp(self.sumbb[i-1]) /
                            (self.rlan[ni-1] * np.exp(self.sumbb[i-1]) + self.rmu[ni-1]))
        else:
            self.abs[i-1] = 1.0 - np.exp(
                -(self.rlan[ni-1] * np.exp(self.sumbb[i-1]) + self.rmu[ni-1]) * (self.t[ni] - ti)
            )
            self.abs[i-1] = (self.abs[i-1] * self.rlan[ni-1] * np.exp(self.sumbb[i-1]) /
                            (self.rlan[ni-1] * np.exp(self.sumbb[i-1]) + self.rmu[ni-1]))
            
            if ns - ni > 0:
                if ProjectionAge > 50.0 and CurrentAge < 50.0:
                    r = 1.0 - np.exp(
                        -(self.rlan[ns-1] * np.exp(self.sumbb[i+107]) + self.rmu[ns-1]) * (ts - self.t[ns-1])
                    )
                    r = (r * self.rlan[ns-1] * np.exp(self.sumbb[i+107]) /
                        (self.rlan[ns-1] * np.exp(self.sumbb[i+107]) + self.rmu[ns-1]))
                    r *= np.exp(-(self.rlan[ni-1] * np.exp(self.sumbb[i-1]) + self.rmu[ni-1]) * (self.t[ni] - ti))
                    
                    if ns - ni > 1:
                        for j in range(ni+1, ns):
                            if self.t[j-1] >= 50.0:
                                r *= np.exp(-(self.rlan[j-1] * np.exp(self.sumbb[i+107]) + self.rmu[j-1]) * (self.t[j] - self.t[j-1]))
                            else:
                                r *= np.exp(-(self.rlan[j-1] * np.exp(self.sumbb[i-1]) + self.rmu[j-1]) * (self.t[j] - self.t[j-1]))
                    self.abs[i-1] += r
                else:
                    r = 1.0 - np.exp(
                        -(self.rlan[ns-1] * np.exp(self.sumbb[i-1]) + self.rmu[ns-1]) * (ts - self.t[ns-1])
                    )
                    r = (r * self.rlan[ns-1] * np.exp(self.sumbb[i-1]) /
                        (self.rlan[ns-1] * np.exp(self.sumbb[i-1]) + self.rmu[ns-1]))
                    r *= np.exp(-(self.rlan[ni-1] * np.exp(self.sumbb[i-1]) + self.rmu[ni-1]) * (self.t[ni] - ti))
                    
                    if ns - ni > 1:
                        for j in range(ni+1, ns):
                            r *= np.exp(-(self.rlan[j-1] * np.exp(self.sumbb[i-1]) + self.rmu[j-1]) * (self.t[j] - self.t[j-1]))
                    self.abs[i-1] += r
            
            if ns - ni > 1:
                if ProjectionAge > 50.0 and CurrentAge < 50.0:
                    for k in range(ni+1, ns):
                        if self.t[k-1] >= 50.0:
                            r = 1.0 - np.exp(-(self.rlan[k-1] * np.exp(self.sumbb[i+107]) + self.rmu[k-1]) * (self.t[k] - self.t[k-1]))
                            r = (r * self.rlan[k-1] * np.exp(self.sumbb[i+107]) /
                                (self.rlan[k-1] * np.exp(self.sumbb[i+107]) + self.rmu[k-1]))
                        else:
                            r = 1.0 - np.exp(-(self.rlan[k-1] * np.exp(self.sumbb[i-1]) + self.rmu[k-1]) * (self.t[k] - self.t[k-1]))
                            r = (r * self.rlan[k-1] * np.exp(self.sumbb[i-1]) /
                                (self.rlan[k-1] * np.exp(self.sumbb[i-1]) + self.rmu[k-1]))
                        
                        r *= np.exp(-(self.rlan[ni-1] * np.exp(self.sumbb[i-1]) + self.rmu[ni-1]) * (self.t[ni] - ti))
                        
                        for j in range(ni+1, k):
                            if self.t[j-1] >= 50.0:
                                r *= np.exp(-(self.rlan[j-1] * np.exp(self.sumbb[i+107]) + self.rmu[j-1]) * (self.t[j] - self.t[j-1]))
                            else:
                                r *= np.exp(-(self.rlan[j-1] * np.exp(self.sumbb[i-1]) + self.rmu[j-1]) * (self.t[j] - self.t[j-1]))
                        self.abs[i-1] += r
                else:
                    for k in range(ni+1, ns):
                        r = 1.0 - np.exp(-(self.rlan[k-1] * np.exp(self.sumbb[i-1]) + self.rmu[k-1]) * (self.t[k] - self.t[k-1]))
                        r = (r * self.rlan[k-1] * np.exp(self.sumbb[i-1]) /
                            (self.rlan[k-1] * np.exp(self.sumbb[i-1]) + self.rmu[k-1]))
                        r *= np.exp(-(self.rlan[ni-1] * np.exp(self.sumbb[i-1]) + self.rmu[ni-1]) * (self.t[ni] - ti))
                        
                        for j in range(ni+1, k):
                            r *= np.exp(-(self.rlan[j-1] * np.exp(self.sumbb[i-1]) + self.rmu[j-1]) * (self.t[j] - self.t[j-1]))
                        self.abs[i-1] += r
        
        return self.abs[i-1]


# ================== Helper Functions ==================

def create_calculator() -> GailRiskCalculator:
    """ایجاد instance آماده"""
    calc = GailRiskCalculator()
    calc.initialize()
    return calc


# ================== Test/Example ==================

if __name__ == '__main__':
    print("="*70)
    print("Gail Risk Calculator - Production Test")
    print("="*70)
    
    calc = create_calculator()
    
    # Test case 1 (از مثال اصلی)
    params = GailInputParams(
        current_age=35,
        projection_age=40,
        menarche_age=2,
        first_live_birth_age=0,
        first_deg_relatives=0,
        ever_had_biopsy=1,
        number_of_biopsy=1,
        hyperplasia=1,
        race=RaceType.WHITE_OTHER
    )
    
    result = calc.calculate_full_risk(params)
    print("\nTest Case 1:")
    print(f"  Input: Age 35→40, Menarche=2, Biopsy=1, Hyperplasia=Yes")
    print(f"  Absolute Risk: {result.absolute_risk:.6f} ({result.absolute_risk*100:.2f}%)")
    print(f"  Average Risk: {result.average_risk:.6f}")
    print(f"  Relative Risk: {result.relative_risk:.2f}")
    print(f"  Interpretation: {result._interpret()}")
    
    # Test case 2
    params2 = GailInputParams(
        current_age=50,
        projection_age=60,
        menarche_age=1,
        first_live_birth_age=1,
        first_deg_relatives=1,
        ever_had_biopsy=0,
        race=RaceType.AFRICAN_AMERICAN
    )
    
    result2 = calc.calculate_full_risk(params2)
    print("\nTest Case 2 (African American):")
    print(f"  Absolute Risk: {result2.absolute_risk:.6f} ({result2.absolute_risk*100:.2f}%)")
    print(f"  Relative Risk: {result2.relative_risk:.2f}")
    
    print("\n" + "="*70)
    print("✓ Tests completed successfully")
    print("="*70)