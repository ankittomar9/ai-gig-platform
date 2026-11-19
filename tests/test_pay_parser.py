import pytest
from app.services.pay_parser import check_location_and_language, parse_compensation

def test_india_gate_eligible_locations():
    test_cases = [
        "Ahmedabad, Gujarat",
        "Kolkata, WB, India",
        "Remote — India (West)",
        "Jaipur, Rajasthan",
        "Bengaluru, Karnataka, India",
        "Pune, Maharashtra",
        "Chandigarh, India",
        "Kochi, Kerala",
        "Remote, Worldwide",
        "Anywhere (Work from Home)"
    ]
    for loc in test_cases:
        res = check_location_and_language("Software Engineer", loc, "English documentation required")
        assert res["is_india_eligible"] is True, f"Failed for eligible location: {loc}"

def test_india_gate_ineligible_locations():
    test_cases = [
        "New York, NY",
        "San Francisco, CA",
        "Toronto, Ontario, Canada",
        "London, United Kingdom",
        "Berlin, Germany",
        "Tokyo, Japan",
        "On-site - Austin, TX"
    ]
    for loc in test_cases:
        res = check_location_and_language("Developer", loc, "English required")
        assert res["is_india_eligible"] is False, f"Expected ineligible for: {loc}"

def test_india_gate_language_filtering():
    # Foreign language required -> Ineligible
    res_german = check_location_and_language("German Content Reviewer", "Remote", "Must speak fluent German (C1)")
    assert res_german["is_india_eligible"] is False
    assert "German" in res_german["language_status"]

    res_japanese = check_location_and_language("Bilingual Japanese Annotator", "Remote", "Japanese native speaker")
    assert res_japanese["is_india_eligible"] is False
    assert "Japanese" in res_japanese["language_status"]

    # English and Hindi -> Eligible
    res_hindi = check_location_and_language("Hindi / English AI Evaluation Lead", "Remote, India", "Fluent in Hindi and English")
    assert res_hindi["is_india_eligible"] is True

def test_compensation_parsing_unlisted():
    # Titles without pay numbers must return 'Not listed' and 0 min/max
    titles_without_pay = [
        "Account Based Marketing Lead",
        "Data Annotation Specialist - Coding",
        "Prompt Engineer (Generalist)"
    ]
    for title in titles_without_pay:
        comp = parse_compensation(title)
        assert comp["compensation"] == "Not listed"
        assert comp["comp_min"] == 0.0
        assert comp["comp_max"] == 0.0
        assert comp["tier"] == "Pay Not Listed"

def test_compensation_parsing_valid():
    comp1 = parse_compensation("AI Evaluator ($25 - $40/hr)")
    assert comp1["comp_min"] == 25.0
    assert comp1["comp_max"] == 40.0
    assert comp1["comp_unit"] == "hr"
    assert comp1["tier"] == "Expert ($30-$100+)"

    comp2 = parse_compensation("Junior Annotator $12/hr")
    assert comp2["comp_min"] == 12.0
    assert comp2["comp_max"] == 12.0
    assert comp2["tier"] == "Microtask ($2-$15)"
