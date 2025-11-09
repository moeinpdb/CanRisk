"""
تست دستی API با Python requests
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_calculate_risk():
    """تست محاسبه ریسک"""
    
    url = f"{BASE_URL}/api/gail/calculate"
    
    # Case 1: زن 45 ساله با ریسک متوسط
    payload = {
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
    
    print("🧪 Testing /api/gail/calculate")
    print("=" * 80)
    print(f"📤 Request: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    response = requests.post(url, json=payload)
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Success!")
        print(f"\n📊 Results:")
        print(f"  Patient Age: {result['patient_info']['age']}")
        print(f"  Race: {result['patient_info']['race_name_fa']}")
        print(f"\n  5-Year Absolute Risk: {result['risk_assessment']['absolute_risk_5year']:.6f} ({result['risk_assessment']['absolute_risk_5year']*100:.2f}%)")
        print(f"  5-Year Average Risk:  {result['risk_assessment']['average_risk_5year']:.6f}")
        print(f"  5-Year Relative Risk: {result['risk_assessment']['relative_risk_5year']:.2f}x")
        print(f"\n  Risk Category: {result['risk_assessment']['risk_category']}")
        print(f"\n  Interpretation:\n    {result['risk_assessment']['interpretation_fa']}")
        print(f"\n  Recommendations:")
        for i, rec in enumerate(result['risk_assessment']['recommendations_fa'], 1):
            print(f"    {i}. {rec}")
    else:
        print(f"\n❌ Error!")
        print(f"  {response.text}")


def test_health():
    """تست health check"""
    print("\n\n🏥 Testing /api/health")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_info():
    """تست اطلاعات مدل"""
    print("\n\n📖 Testing /api/gail/info")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/api/gail/info")
    result = response.json()
    
    print(f"Model: {result['model_name']}")
    print(f"Version: {result['version']}")
    print(f"\nLimitations:")
    for lim in result['limitations']:
        print(f"  - {lim}")


def test_validation_error():
    """تست خطای validation"""
    print("\n\n⚠️  Testing Validation Error (Age < 35)")
    print("=" * 80)
    
    url = f"{BASE_URL}/api/gail/calculate"
    payload = {
        "has_breast_cancer_history": False,
        "has_genetic_mutation": "no",
        "age": 30,  # Invalid!
        "race": 1,
        "ever_had_biopsy": "no",
        "age_at_menarche": 12,
        "age_at_first_birth": 25,
        "num_first_degree_relatives": 0
    }
    
    response = requests.post(url, json=payload)
    
    print(f"Status: {response.status_code} (Expected: 400 or 422)")
    if response.status_code in [400, 422]:
        print("✅ Validation working correctly!")
        print(f"Error: {response.json()}")
    else:
        print("❌ Validation not working as expected")


if __name__ == "__main__":
    try:
        test_health()
        test_calculate_risk()
        test_info()
        test_validation_error()
        
        print("\n\n" + "=" * 80)
        print("✅ All manual tests completed!")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")