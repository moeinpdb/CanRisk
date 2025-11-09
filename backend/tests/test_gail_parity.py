"""
Parity Tests for Gail Calculator
تست تطبیق با مقادیر مرجع NCI/R BCRA

این فایل خروجی‌های محاسبه‌گر را با مقادیر مرجع مقایسه می‌کند
"""

import pytest
import numpy as np
from typing import Dict, List, Tuple

from app.calculators.gail_model import create_calculator, GailInputParams


class TestGailParity:
    """تست‌های تطبیق (parity) با مقادیر مرجع"""
    
    @pytest.fixture(scope="class")
    def calculator(self):
        """Calculator instance برای تمام تست‌ها"""
        return create_calculator()
    
    def test_example_1_original(self, calculator):
        """
        Test Case 1: مثال اصلی از کد مرجع
        
        Input:
          - Age: 35 -> 40
          - Menarche: 2 (7-11)
          - First Birth: 0 (<20)
          - Relatives: 0
          - Biopsy: 1
          - Hyperplasia: Yes (1.82)
          - Race: 1 (White)
        
        Expected: (باید با مرجع تطبیق داده شود)
        """
        params = GailInputParams(
            current_age=35,
            projection_age=40,
            menarche_age=2,
            first_live_birth_age=0,
            first_deg_relatives=0,
            ever_had_biopsy=1,
            number_of_biopsy=1,
            hyperplasia=1,
            race=1
        )
        
        result = calculator.calculate_full_risk(params)
        
        # Assertions
        assert 0 <= result.absolute_risk <= 1, "Absolute risk باید بین 0 و 1 باشد"
        assert 0 <= result.average_risk <= 1, "Average risk باید بین 0 و 1 باشد"
        assert result.relative_risk > 0, "Relative risk باید مثبت باشد"
        
        # Log برای بررسی دستی
        print(f"\n📊 Test Case 1 Results:")
        print(f"  Absolute Risk: {result.absolute_risk:.6f} ({result.absolute_risk*100:.3f}%)")
        print(f"  Average Risk:  {result.average_risk:.6f}")
        print(f"  Relative Risk: {result.relative_risk:.2f}")
    
    def test_age_50_african_american(self, calculator):
        """
        Test Case 2: African American woman
        
        بررسی محاسبات برای نژاد African American
        """
        params = GailInputParams(
            current_age=50,
            projection_age=55,
            menarche_age=1,  # 12-13
            first_live_birth_age=1,  # 20-24
            first_deg_relatives=1,
            ever_had_biopsy=0,
            number_of_biopsy=0,
            hyperplasia=99,
            race=2  # African American
        )
        
        result = calculator.calculate_full_risk(params)
        
        assert 0 <= result.absolute_risk <= 1
        assert result.relative_risk > 0
        
        print(f"\n📊 Test Case 2 (African American):")
        print(f"  Absolute Risk: {result.absolute_risk:.6f}")
        print(f"  Relative Risk: {result.relative_risk:.2f}")
    
    def test_hispanic_with_biopsies(self, calculator):
        """
        Test Case 3: Hispanic woman with multiple biopsies
        """
        params = GailInputParams(
            current_age=45,
            projection_age=50,
            menarche_age=0,  # 14+
            first_live_birth_age=2,  # 25-29
            first_deg_relatives=2,  # 2+
            ever_had_biopsy=1,
            number_of_biopsy=2,  # 2+
            hyperplasia=0,  # No hyperplasia
            race=3  # Hispanic
        )
        
        result = calculator.calculate_full_risk(params)
        
        assert result.absolute_risk > 0
        assert result.relative_risk > 0
        
        print(f"\n📊 Test Case 3 (Hispanic, high risk factors):")
        print(f"  Absolute Risk: {result.absolute_risk:.6f}")
        print(f"  Relative Risk: {result.relative_risk:.2f}")
    
    def test_asian_chinese(self, calculator):
        """
        Test Case 4: Chinese woman
        """
        params = GailInputParams(
            current_age=40,
            projection_age=45,
            menarche_age=1,
            first_live_birth_age=1,
            first_deg_relatives=0,
            ever_had_biopsy=0,
            number_of_biopsy=0,
            hyperplasia=99,
            race=7  # Chinese
        )
        
        result = calculator.calculate_full_risk(params)
        
        assert result.absolute_risk > 0
        
        print(f"\n📊 Test Case 4 (Chinese):")
        print(f"  Absolute Risk: {result.absolute_risk:.6f}")
        print(f"  Relative Risk: {result.relative_risk:.2f}")
    
    def test_consistency_absolute_vs_average(self, calculator):
        """
        بررسی consistency بین absolute و average risk
        
        relative_risk باید برابر باشد با absolute_risk / average_risk
        """
        params = GailInputParams(
            current_age=55,
            projection_age=60,
            menarche_age=1,
            first_live_birth_age=1,
            first_deg_relatives=1,
            ever_had_biopsy=1,
            number_of_biopsy=1,
            hyperplasia=0,
            race=1
        )
        
        result = calculator.calculate_full_risk(params)
        
        # محاسبه relative risk از absolute و average
        calculated_relative = result.absolute_risk / result.average_risk if result.average_risk > 0 else 0
        
        # باید تقریباً برابر باشد
        assert abs(calculated_relative - result.relative_risk) < 0.01, \
            f"Relative risk inconsistency: {calculated_relative:.4f} vs {result.relative_risk:.4f}"
        
        print(f"\n✅ Consistency check passed")
        print(f"  Relative (calculated): {calculated_relative:.4f}")
        print(f"  Relative (returned):   {result.relative_risk:.4f}")
    
    @pytest.mark.parametrize("age,projection", [
        (35, 40),
        (45, 50),
        (55, 60),
        (65, 70),
        (75, 80),
    ])
    def test_age_progression(self, calculator, age, projection):
        """
        تست برای رنج‌های مختلف سنی
        
        بررسی که محاسبات برای تمام سنین کار می‌کند
        """
        params = GailInputParams(
            current_age=age,
            projection_age=projection,
            menarche_age=1,
            first_live_birth_age=1,
            first_deg_relatives=0,
            ever_had_biopsy=0,
            number_of_biopsy=0,
            hyperplasia=99,
            race=1
        )
        
        result = calculator.calculate_full_risk(params)
        
        assert 0 <= result.absolute_risk <= 1
        assert result.relative_risk > 0
        
        print(f"\n📊 Age {age}-{projection}: Abs={result.absolute_risk:.6f}, Rel={result.relative_risk:.2f}")
    
    def test_boundary_age_35(self, calculator):
        """تست مرز پایینی سنی (35)"""
        params = GailInputParams(
            current_age=35,
            projection_age=40,
            menarche_age=1,
            first_live_birth_age=1,
            first_deg_relatives=0,
            ever_had_biopsy=0,
            number_of_biopsy=0,
            hyperplasia=99,
            race=1
        )
        
        result = calculator.calculate_full_risk(params)
        assert result.absolute_risk > 0
    
    def test_boundary_age_85(self, calculator):
        """تست مرز بالایی سنی (85)"""
        params = GailInputParams(
            current_age=85,
            projection_age=90,
            menarche_age=1,
            first_live_birth_age=1,
            first_deg_relatives=0,
            ever_had_biopsy=0,
            number_of_biopsy=0,
            hyperplasia=99,
            race=1
        )
        
        result = calculator.calculate_full_risk(params)
        assert result.absolute_risk >= 0
    
    def test_all_races(self, calculator):
        """
        تست تمام نژادها
        
        بررسی که محاسبات برای تمام 12 نژاد کار می‌کند
        """
        race_names = {
            1: "White/Other",
            2: "African American",
            3: "Hispanic",
            7: "Chinese",
            8: "Japanese",
            9: "Filipino",
            10: "Hawaiian",
            11: "Other Pacific Islander",
            12: "Other Asian"
        }
        
        print(f"\n📊 Testing all races:")
        
        for race_code, race_name in race_names.items():
            params = GailInputParams(
                current_age=45,
                projection_age=50,
                menarche_age=1,
                first_live_birth_age=1,
                first_deg_relatives=1 if race_code >= 7 else 1,  # Asian cap at 1
                ever_had_biopsy=0,
                number_of_biopsy=0,
                hyperplasia=99,
                race=race_code
            )
            
            result = calculator.calculate_full_risk(params)
            
            assert 0 <= result.absolute_risk <= 1, f"Race {race_name} failed"
            assert result.relative_risk > 0, f"Race {race_name} failed"
            
            print(f"  {race_name:25s}: Abs={result.absolute_risk:.6f}, Rel={result.relative_risk:.2f}")


# ========== Known Reference Values Test ==========

class TestKnownReferenceValues:
    """
    تست با مقادیر شناخته شده از مراجع
    
    TODO: این مقادیر را از R BCRA یا NCI tool دریافت و وارد کنید
    """
    
    REFERENCE_CASES: List[Dict] = [
        # Example format (uncomment and fill with real values):
        # {
        #     "name": "NCI Example 1",
        #     "input": {
        #         "current_age": 40,
        #         "projection_age": 45,
        #         "menarche_age": 1,
        #         "first_live_birth_age": 2,
        #         "first_deg_relatives": 0,
        #         "ever_had_biopsy": 0,
        #         "number_of_biopsy": 0,
        #         "hyperplasia": 99,
        #         "race": 1
        #     },
        #     "expected": {
        #         "absolute_risk": 0.0123,  # Example value
        #         "tolerance": 0.0001
        #     }
        # },
    ]
    
    @pytest.fixture(scope="class")
    def calculator(self):
        return create_calculator()
    
    # ✅ تغییر اینجا: شرط skipif را اضافه کردیم
    @pytest.mark.skipif(
        len(REFERENCE_CASES) == 0,
        reason="No reference values provided yet"
    )
    @pytest.mark.parametrize("case", REFERENCE_CASES or [{}], ids=lambda c: c.get("name", "unnamed"))
    def test_reference_case(self, calculator, case):
        """تست با مقادیر مرجع"""
        
        if not case:  # اگر خالی بود skip کن
            pytest.skip("No test cases defined")
        
        params = GailInputParams(**case["input"])
        result = calculator.calculate_full_risk(params)
        
        expected = case["expected"]["absolute_risk"]
        tolerance = case["expected"].get("tolerance", 0.0001)
        
        diff = abs(result.absolute_risk - expected)
        
        assert diff <= tolerance, \
            f"{case['name']}: Expected {expected:.6f}, got {result.absolute_risk:.6f}, diff={diff:.6f}"
        
        print(f"\n✅ {case['name']} passed: {result.absolute_risk:.6f} (expected {expected:.6f})")


# ========== Run tests ========== 

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
