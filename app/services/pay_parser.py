import re
from typing import Tuple, Dict, Any

def parse_compensation(text: str, default_tier: str = "Mid-Tier ($15-$30)") -> Dict[str, Any]:
    """
    Parses compensation from text or applies intelligent heuristics.
    Returns {
        "compensation": "$25 - $40/hr",
        "comp_min": 25.0,
        "comp_max": 40.0,
        "comp_unit": "hr",
        "tier": "Expert ($30-$100+)"
    }
    """
    if not text:
        return _fallback_tier(default_tier)

    # Search for hourly patterns like $25/hr, $25 - $50/hour, $30 to $45 an hour
    hourly_range = re.search(r'\$\s*(\d+(?:\.\d{1,2})?)\s*(?:-|to|–)\s*\$?\s*(\d+(?:\.\d{1,2})?)\s*(?:/(?:hr|hour)|per\s*hour|an\s*hour)', text, re.I)
    if hourly_range:
        min_val = float(hourly_range.group(1))
        max_val = float(hourly_range.group(2))
        return _format_comp(min_val, max_val, "hr")

    single_hourly = re.search(r'\$\s*(\d+(?:\.\d{1,2})?)\s*(?:/(?:hr|hour)|per\s*hour|an\s*hour)', text, re.I)
    if single_hourly:
        val = float(single_hourly.group(1))
        return _format_comp(val, val, "hr")

    # Search for task patterns like $2-$5 per task, $0.50/task
    task_match = re.search(r'\$\s*(\d+(?:\.\d{1,2})?)\s*(?:-|to|–)?\s*\$?\s*(\d+(?:\.\d{1,2})?)?\s*(?:/(?:task|hit|item)|per\s*(?:task|hit|item))', text, re.I)
    if task_match:
        min_v = float(task_match.group(1))
        max_v = float(task_match.group(2)) if task_match.group(2) else min_v
        tier = "Microtask ($2-$15)"
        return {
            "compensation": f"${min_v:.2f} - ${max_v:.2f}/task" if max_v != min_v else f"${min_v:.2f}/task",
            "comp_min": min_v,
            "comp_max": max_v,
            "comp_unit": "task",
            "tier": tier
        }

    # Annual salary patterns like $80,000 - $120,000
    annual_match = re.search(r'\$\s*(\d{2,3}(?:,\d{3})+)\s*(?:-|to|–)\s*\$?\s*(\d{2,3}(?:,\d{3})+)', text)
    if annual_match:
        min_v = float(annual_match.group(1).replace(",", ""))
        max_v = float(annual_match.group(2).replace(",", ""))
        # Convert to equivalent hourly estimate (assuming 2000 hrs/yr)
        approx_hr_min = round(min_v / 2000, 1)
        approx_hr_max = round(max_v / 2000, 1)
        tier = "Expert ($30-$100+)" if approx_hr_max >= 30 else "Mid-Tier ($15-$30)"
        return {
            "compensation": f"${approx_hr_min:.0f} - ${approx_hr_max:.0f}/hr (${min_v/1000:.0f}k-${max_v/1000:.0f}k/yr)",
            "comp_min": approx_hr_min,
            "comp_max": approx_hr_max,
            "comp_unit": "hr",
            "tier": tier
        }

    return _fallback_tier(default_tier)

def _format_comp(min_v: float, max_v: float, unit: str) -> Dict[str, Any]:
    if max_v >= 30 or min_v >= 30:
        tier = "Expert ($30-$100+)"
    elif max_v <= 15 and min_v <= 15:
        tier = "Microtask ($2-$15)"
    else:
        tier = "Mid-Tier ($15-$30)"

    comp_str = f"${min_v:.0f} - ${max_v:.0f}/{unit}" if min_v != max_v else f"${min_v:.0f}/{unit}"
    return {
        "compensation": comp_str,
        "comp_min": min_v,
        "comp_max": max_v,
        "comp_unit": unit,
        "tier": tier
    }

def _fallback_tier(tier: str) -> Dict[str, Any]:
    if "Microtask" in tier:
        return {"compensation": "$5 - $15/hr", "comp_min": 5.0, "comp_max": 15.0, "comp_unit": "hr", "tier": "Microtask ($2-$15)"}
    elif "Expert" in tier:
        return {"compensation": "$35 - $75+/hr", "comp_min": 35.0, "comp_max": 75.0, "comp_unit": "hr", "tier": "Expert ($30-$100+)"}
    else:
        return {"compensation": "$18 - $30/hr", "comp_min": 18.0, "comp_max": 30.0, "comp_unit": "hr", "tier": "Mid-Tier ($15-$30)"}

def detect_category(title: str, description: str = "") -> str:
    content = f"{title} {description}".lower()
    
    # Coding
    if any(k in content for k in ["code", "coding", "software", "python", "developer", "engineer", "java", "c++", "typescript", "debugger", "fullstack", "backend"]):
        return "Coding"
    # Math & Reasoning
    if any(k in content for k in ["math", "mathematics", "physics", "quantitative", "reasoning", "logic", "algebra", "calculus", "science"]):
        return "Math & Reasoning"
    # Multilingual
    if any(k in content for k in ["bilingual", "translator", "translation", "spanish", "hindi", "french", "german", "japanese", "arabic", "multilingual", "linguist"]):
        return "Multilingual"
    # Writing & RLHF
    if any(k in content for k in ["rlhf", "prompt", "writer", "writing", "editor", "creative writing", "content evaluation", "llm trainer", "evaluator", "fact-check"]):
        return "Writing & RLHF"
    
    return "Generalist"

def detect_interview_type(title: str, description: str, platform: str) -> str:
    content = f"{title} {description} {platform}".lower()
    
    if "mercor" in platform.lower() or "ai interview" in content or "video interview" in content:
        return "AI Interview"
    if "micro1" in platform.lower() or "hackerrank" in content or "assessment" in content or "screening test" in content or "coding test" in content:
        return "Automated Test"
    if "prolific" in platform.lower() or "clickworker" in platform.lower() or "direct onboarding" in content or "instant signup" in content:
        return "No Interview / Direct"
    if "interview" in content and "round" in content:
        return "Human Interview"
    
    # Default for AI annotation & training gigs is an AI/Automated screening assessment
    return "AI Interview"

SENIOR_KEYWORDS = [
    "senior", "sr.", "sr ", "staff", "principal", "lead", "director", "head of",
    "vp", "vice president", "architect", "engineering manager", "lead engineer",
    "distinguished", "founding engineer"
]

ENTRY_KEYWORDS = [
    "junior", "entry", "associate", "intern", "apprentice", "trainee", "early career",
    "no experience", "entry-level", "fresh"
]

DIRECT_TASK_PLATFORMS = [
    "outlier", "remotasks", "alignerr", "dataannotation", "mindrift", "clickworker",
    "prolific", "telus", "oneforma", "appen"
]

def extract_experience_years(title: str, description: str = "", company: str = "") -> Dict[str, Any]:
    """
    Extracts minimum years of experience and eligibility from job title and description.
    Returns:
    {
        "min_exp": int,
        "max_exp": int,
        "label": str,
        "is_fits_resume": bool (True if min_exp <= 3)
    }
    """
    t_lower = title.lower()
    c_lower = company.lower()
    full = f"{title} {description}".lower()

    # 1. Direct Senior keywords in Title
    if any(k in t_lower for k in ["staff", "principal", "director", "head of", "vp", "architect", "distinguished"]):
        return {"min_exp": 7, "max_exp": 12, "label": "7+ yrs (Staff/Lead)", "is_fits_resume": False}

    if any(k in t_lower for k in ["senior", "sr.", "sr "]):
        return {"min_exp": 5, "max_exp": 8, "label": "5+ yrs (Senior)", "is_fits_resume": False}

    if any(k in t_lower for k in ["lead", "manager"]):
        return {"min_exp": 5, "max_exp": 8, "label": "5+ yrs (Lead)", "is_fits_resume": False}

    # 2. Check for explicit range in text, e.g. "3-5 years", "minimum 4 years"
    range_match = re.search(r'(?:minimum|at least)?\s*(\d+)\+?\s*(?:-|to|–)\s*(\d+)\s*(?:years?|yrs?)(?:\s*of)?\s*(?:experience|exp)?', full)
    if range_match:
        min_v = int(range_match.group(1))
        max_v = int(range_match.group(2))
        if 1 <= min_v <= 15 and max_v <= 20:
            return {
                "min_exp": min_v,
                "max_exp": max_v,
                "label": f"{min_v}-{max_v} yrs",
                "is_fits_resume": min_v <= 3
            }

    single_match = re.search(r'(?:minimum|at least)?\s*(\d+)\+?\s*(?:years?|yrs?)(?:\s*of)?\s*(?:experience|exp)?', full)
    if single_match:
        val = int(single_match.group(1))
        if 1 <= val <= 15:
            label = f"{val}+ yrs" if val >= 4 else f"{val} yrs"
            return {
                "min_exp": val,
                "max_exp": val + 2,
                "label": label,
                "is_fits_resume": val <= 3
            }

    # 3. Check for Entry / Junior / Associate
    if any(k in t_lower for k in ENTRY_KEYWORDS):
        return {"min_exp": 0, "max_exp": 2, "label": "0-2 yrs (Entry/Junior)", "is_fits_resume": True}

    # 4. Direct Task / Evaluation / RLHF Platforms
    if any(k in c_lower for k in DIRECT_TASK_PLATFORMS) or any(k in t_lower for k in ["evaluator", "annotator", "trainer", "tutor", "rater", "contributor", "reviewer"]):
        return {"min_exp": 0, "max_exp": 2, "label": "0-2 yrs (Assessment Based)", "is_fits_resume": True}

    # 5. Default mid-level IC (Software Engineer, Analyst, Operations)
    return {"min_exp": 2, "max_exp": 3, "label": "1-3 yrs (Mid-Level)", "is_fits_resume": True}

NON_INDIA_LOCATION_PATTERNS = [
    r'\bsan francisco\b', r'\bsf\b', r'\bnew york\b', r'\bnyc\b', r'\btoronto\b',
    r'\bseattle\b', r'\blondon\b', r'\bunited states\b', r'\bus only\b', r'\busa\b',
    r'\bcanada\b', r'\bparis\b', r'\bfrance\b', r'\bberlin\b', r'\bgermany\b',
    r'\btokyo\b', r'\bjapan\b', r'\bkorea\b', r'\bsingapore\b', r'\bdubai\b',
    r'\bsaudi arabia\b', r'\briyadh\b', r'\bstockholm\b', r'\bsweden\b', r'\bottawa\b',
    r'\bhouston\b', r'\bhalifax\b', r'\bmiddle east\b', r'\beurope\b', r'\bmexico\b',
    r'\bchile\b', r'\bargentina\b', r'\bcolombia\b', r'\bperu\b', r'\bcosta rica\b',
    r'\bqatar\b', r'\bdoha\b', r'\bunited arab emirates\b', r'\buae\b', r'\bnigeria\b',
    r'\baustralia\b', r'\buk\b', r'\bnetherlands\b', r'\bamsterdam\b', r'\bboston\b',
    r'\baustin\b', r'\bchicago\b', r'\blos angeles\b', r'\bsan diego\b', r'\bwashington\b',
    r'\bdc\b', r'\bcolorado springs\b', r'\bdayton\b', r'\btampa\b', r'\bhuntsville\b',
    r'\bdetroit\b', r'\bkuwait\b', r'\bpalo alto\b', r'\bplano\b', r'\btexas\b',
    r'\bcalifornia\b', r'\bcolorado\b', r'\bhawaii\b', r'\bhonolulu\b', r'\bomaha\b',
    r'\bmiami\b', r'\bflorida\b', r'\bmanila\b', r'\bphilippines\b', r'\bbrazil\b',
    r'\bsão paulo\b', r'\bmercor hq\b', r'\b181 fremont\b', r'\bst\. louis\b',
    r'^(us|jp|qa|pe|my|mx|mm|cr|co|cl|cf|cd|bh|ar|ae)$'
]

FOREIGN_LANGUAGES = [
    'spanish', 'german', 'french', 'japanese', 'chinese', 'mandarin', 'cantonese',
    'arabic', 'portuguese', 'italian', 'russian', 'korean', 'dutch', 'vietnamese',
    'turkish', 'polish', 'ukrainian', 'swedish', 'danish', 'norwegian', 'finnish',
    'hebrew', 'thai', 'indonesian', 'malay', 'igbo', 'yoruba', 'tagalog', 'swahili',
    'persian', 'farsi', 'czech', 'greek', 'hungarian', 'romanian'
]

def check_location_and_language(title: str, location: str, description: str = "") -> Dict[str, Any]:
    """
    Evaluates whether a candidate residing in India who speaks English and Hindi
    is eligible to apply for this job.
    Returns:
    {
        "is_india_eligible": bool,
        "location_status": str,
        "language_status": str
    }
    """
    t_low = title.lower()
    l_low = (location or "").lower().strip()
    d_low = (description or "").lower()

    # 1. Foreign Language Check (Reject if role title explicitly targets a foreign non-English/non-Hindi language)
    for fl in FOREIGN_LANGUAGES:
        if re.search(r'\b' + fl + r'\b', t_low):
            return {
                "is_india_eligible": False,
                "location_status": location or "Unknown",
                "language_status": f"Foreign: {fl.title()} Required"
            }

    # 2. Location Check
    # A. Explicit India locations (Bangalore, Chennai, Hyderabad, Remote India, etc.)
    if any(k in l_low for k in ['india', 'bengaluru', 'bangalore', 'hyderabad', 'mumbai', 'delhi', 'noida', 'gurgaon', 'pune', 'chennai', 'karnataka', 'telangana']):
        return {
            "is_india_eligible": True,
            "location_status": "India (Local/Remote)",
            "language_status": "English / Hindi Eligible"
        }

    # B. Global Remote keywords (Worldwide, Global Remote, Anywhere)
    if any(k in l_low for k in ['worldwide', 'global', 'anywhere', 'remote (worldwide)', 'remote (global)', 'global / remote', 'global - remote', 'remote - non-us']):
        return {
            "is_india_eligible": True,
            "location_status": "Global Remote",
            "language_status": "English / Hindi Eligible"
        }

    # C. Open Remote check (Check description for US-only / Canada-only restrictions)
    if l_low in ['remote', 'remote / flexible', '']:
        if any(r in d_low for r in ['us only', 'must reside in the united states', 'us work authorization', 'u.s. citizens', 'canada only', 'must be based in the us', 'authorized to work in the us']):
            return {
                "is_india_eligible": False,
                "location_status": "US-Restricted Remote",
                "language_status": "English / Hindi Eligible"
            }
        return {
            "is_india_eligible": True,
            "location_status": "Open Remote",
            "language_status": "English / Hindi Eligible"
        }

    # D. Disqualify known non-India locations (San Francisco, Toronto, NYC, London, etc.)
    for pat in NON_INDIA_LOCATION_PATTERNS:
        if re.search(pat, l_low):
            return {
                "is_india_eligible": False,
                "location_status": f"Ineligible Location: {location}",
                "language_status": "English / Hindi Eligible"
            }

    return {
        "is_india_eligible": False,
        "location_status": f"Ineligible Location: {location}",
        "language_status": "English / Hindi Eligible"
    }

