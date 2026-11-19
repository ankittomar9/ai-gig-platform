import httpx
from typing import List, Dict, Any
from app.scrapers.base import BaseScraper
from app.services.pay_parser import parse_compensation, detect_category, detect_interview_type

GREENHOUSE_BOARDS = [
    {"slug": "scaleai", "company": "Scale AI", "default_tier": "Expert ($30-$100+)"},
    {"slug": "turing", "company": "Turing", "default_tier": "Expert ($30-$100+)"},
    {"slug": "invisible", "company": "Invisible Technologies", "default_tier": "Mid-Tier ($15-$30)"},
    {"slug": "remotasks", "company": "Outlier", "default_tier": "Mid-Tier ($15-$30)"}
]

class GreenhouseScraper(BaseScraper):
    def __init__(self):
        super().__init__("Greenhouse ATS")

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        results = []
        async with httpx.AsyncClient(timeout=10.0) as client:
            for board in GREENHOUSE_BOARDS:
                slug = board["slug"]
                company = board["company"]
                url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
                try:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        data = resp.json()
                        jobs = data.get("jobs", [])
                        for j in jobs:
                            title = j.get("title", "").strip()
                            loc_dict = j.get("location", {})
                            location = loc_dict.get("name", "Remote") if isinstance(loc_dict, dict) else "Remote"
                            apply_url = j.get("absolute_url") or f"https://boards.greenhouse.io/{slug}/jobs/{j.get('id')}"

                            comp_info = parse_compensation(title)
                            category = detect_category(title, "")
                            interview_type = detect_interview_type(title, "", company)

                            results.append({
                                "id": f"gh_{slug}_{j.get('id')}",
                                "platform": f"Greenhouse ({company})",
                                "title": title,
                                "company": company,
                                "url": apply_url,
                                "compensation": comp_info["compensation"],
                                "comp_min": comp_info["comp_min"],
                                "comp_max": comp_info["comp_max"],
                                "comp_unit": comp_info["comp_unit"],
                                "tier": comp_info["tier"],
                                "category": category,
                                "location": location,
                                "requires_interview": interview_type,
                                "description": f"Position: {title} at {company}. Apply directly at {apply_url}."
                            })
                except Exception as e:
                    print(f"Error fetching Greenhouse {slug}: {e}")
        return results
