# [SPEC01-WO-7] Fix India Gate Coverage & Fallback (F7 Remediation)
- **Author:** Gemini / Antigravity
- **Date:** 2026-11-20
- **Base Commit:** `0bbb325`
- **Branch:** `scraper/india-gate-coverage-fix`
- **Verdict:** EXECUTED

---

## 1. Summary of Changes
- **Expanded Indian City & State Lexicon:** Expanded `INDIA_LOCATIONS` from 12 keywords to 50+ comprehensive Indian tech hubs, states, and regional tokens: Kolkata, Ahmedabad, Gujarat, Jaipur, Rajasthan, Indore, Bhopal, Madhya Pradesh, Chandigarh, Mohali, Punjab, Haryana, Kochi, Cochin, Trivandrum, Thiruvananthapuram, Kerala, Coimbatore, Tamil Nadu, Lucknow, Kanpur, Uttar Pradesh, Bhubaneswar, Odisha, Nagpur, Maharashtra, Visakhapatnam, Andhra Pradesh, Patna, Bihar, Surat, Vadodara, West Bengal, and varied remote tokens (`Remote — India`, `India Remote`, etc.).
- **Flagged-For-Review Fallback:** Changed the default fallback behavior for unmatched/ambiguous locations from automatic exclusion (`is_india_eligible: False`) to inclusive manual review tagging (`is_india_eligible: True`, `location_status: "Flagged for Review: <Location>"`), preventing false-negative drops of unmapped global or regional remote postings.

---

## 2. Acceptance Test Evidence (Verbatim Receipts)

Command executed:
```python
from app.services.pay_parser import check_location_and_language

test_cases = [
    ("Ahmedabad, Gujarat", True),
    ("Kolkata, WB, India", True),
    ("Remote — India (West)", True),
    ("Jaipur, Rajasthan", True),
    ("New York, NY", False)
]

print(f"{'Location':<30} | {'Eligible':<10} | {'Location Status':<30}")
print("-" * 75)

for loc, expected in test_cases:
    res = check_location_and_language(title="AI Specialist", location=loc)
    is_ok = res["is_india_eligible"]
    status = res["location_status"]
    print(f"{loc:<30} | {str(is_ok):<10} | {status:<30}")
    assert is_ok == expected, f"Failed for {loc}: expected {expected}, got {is_ok}"

print("\n>>> ALL WO-7 ACCEPTANCE TEST CASES PASSED! <<<")
```

Raw Command Output:
```text
Location                       | Eligible   | Location Status               
---------------------------------------------------------------------------
Ahmedabad, Gujarat             | True       | India (Local/Remote)          
Kolkata, WB, India             | True       | India (Local/Remote)          
Remote — India (West)          | True       | India (Local/Remote)          
Jaipur, Rajasthan              | True       | India (Local/Remote)          
New York, NY                   | False      | Ineligible Location: New York, NY

>>> ALL WO-7 ACCEPTANCE TEST CASES PASSED! <<<
```

---

## 3. Honest-Judge Verification Pair
- **Known-Good Assertion (Previously Dropped Indian Cities):**
  - `"Ahmedabad, Gujarat"` -> `is_india_eligible == True` (Status: `"India (Local/Remote)"`). ✅ PASS
  - `"Remote — India (West)"` -> `is_india_eligible == True` (Status: `"India (Local/Remote)"`). ✅ PASS
- **Known-Bad Assertion (Explicit US Ineligible Location):**
  - `"New York, NY"` -> `is_india_eligible == False` (Status: `"Ineligible Location: New York, NY"`). ✅ PASS
