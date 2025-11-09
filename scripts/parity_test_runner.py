"""
Parity Test Runner
اسکریپت برای اجرای تست‌های تطبیق و تولید گزارش

این اسکریپت:
1. تست‌های parity را اجرا می‌کند
2. نتایج را در فایل CSV ذخیره می‌کند
3. گزارش خلاصه تولید می‌کند
"""

import sys
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.calculators.gail_model import create_calculator, GailInputParams


def run_parity_tests() -> List[Dict]:
    """
    اجرای مجموعه تست‌های parity
    
    Returns:
        لیست نتایج تست‌ها
    """
    
    calculator = create_calculator()
    
    test_cases = [
        {
            "name": "Original Example (Age 35, White, Hyperplasia)",
            "params": {
                "current_age": 35,
                "projection_age": 40,
                "menarche_age": 2,
                "first_live_birth_age": 0,
                "first_deg_relatives": 0,
                "ever_had_biopsy": 1,
                "number_of_biopsy": 1,
                "hyperplasia": 1,
                "race": 1
            }
        },
        {
            "name": "Age 45, White, Average Risk",
            "params": {
                "current_age": 45,
                "projection_age": 50,
                "menarche_age": 1,
                "first_live_birth_age": 1,
                "first_deg_relatives": 0,
                "ever_had_biopsy": 0,
                "number_of_biopsy": 0,
                "hyperplasia": 99,
                "race": 1
            }
        },
        {
            "name": "Age 50, African American",
            "params": {
                "current_age": 50,
                "projection_age": 55,
                "menarche_age": 1,
                "first_live_birth_age": 1,
                "first_deg_relatives": 1,
                "ever_had_biopsy": 0,
                "number_of_biopsy": 0,
                "hyperplasia": 99,
                "race": 2
            }
        },
        {
            "name": "Age 45, Hispanic, High Risk",
            "params": {
                "current_age": 45,
                "projection_age": 50,
                "menarche_age": 0,
                "first_live_birth_age": 3,
                "first_deg_relatives": 2,
                "ever_had_biopsy": 1,
                "number_of_biopsy": 2,
                "hyperplasia": 0,
                "race": 3
            }
        },
        {
            "name": "Age 40, Chinese",
            "params": {
                "current_age": 40,
                "projection_age": 45,
                "menarche_age": 1,
                "first_live_birth_age": 1,
                "first_deg_relatives": 0,
                "ever_had_biopsy": 0,
                "number_of_biopsy": 0,
                "hyperplasia": 99,
                "race": 7
            }
        },
    ]
    
    results = []
    
    print("🧪 Running Parity Tests...")
    print("=" * 80)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['name']}")
        print("-" * 80)
        
        try:
            params = GailInputParams(**case['params'])
            result = calculator.calculate_full_risk(params)
            
            test_result = {
                "test_name": case['name'],
                "current_age": params.current_age,
                "projection_age": params.projection_age,
                "race": params.race,
                "absolute_risk": result.absolute_risk,
                "average_risk": result.average_risk,
                "relative_risk": result.relative_risk,
                "absolute_risk_pct": result.absolute_risk * 100,
                "status": "PASS",
                "error": None
            }
            
            print(f"   ✅ Absolute Risk: {result.absolute_risk:.6f} ({result.absolute_risk*100:.3f}%)")
            print(f"   📊 Average Risk:  {result.average_risk:.6f}")
            print(f"   📈 Relative Risk: {result.relative_risk:.2f}x")
            
        except Exception as e:
            test_result = {
                "test_name": case['name'],
                "current_age": case['params'].get('current_age'),
                "projection_age": case['params'].get('projection_age'),
                "race": case['params'].get('race'),
                "absolute_risk": None,
                "average_risk": None,
                "relative_risk": None,
                "absolute_risk_pct": None,
                "status": "FAIL",
                "error": str(e)
            }
            
            print(f"   ❌ FAILED: {str(e)}")
        
        results.append(test_result)
    
    return results


def save_results_to_csv(results: List[Dict], output_path: Path):
    """ذخیره نتایج در CSV"""
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        if not results:
            return
        
        fieldnames = list(results[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n💾 Results saved to: {output_path}")


def print_summary(results: List[Dict]):
    """چاپ خلاصه نتایج"""
    
    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = total - passed
    
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total}")
    print(f"✅ Passed:   {passed}")
    print(f"❌ Failed:   {failed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if failed > 0:
        print("\n⚠️  Failed Tests:")
        for r in results:
            if r['status'] == 'FAIL':
                print(f"  - {r['test_name']}: {r['error']}")


def main():
    """Main entry point"""
    
    # Run tests
    results = run_parity_tests()
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent.parent / "test_results"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"parity_test_results_{timestamp}.csv"
    save_results_to_csv(results, output_file)
    
    # Print summary
    print_summary(results)


if __name__ == "__main__":
    main()
