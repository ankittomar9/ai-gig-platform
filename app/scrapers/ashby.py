import httpx
from typing import List, Dict, Any
from app.scrapers.base import BaseScraper
from app.services.pay_parser import parse_compensation, detect_category, detect_interview_type

ASHBY_BOARDS = [
    {"slug": "mercor", "company": "Mercor", "default_tier": "Expert ($30-$100+)"},
    {"slug": "surge-ai", "company": "Surge AI", "default_tier": "Mid-Tier ($15-$30)"},
    {"slug": "cohere", "company": "Cohere", "default_tier": "Expert ($30-$100+)"}
]

class AshbyScraper(BaseScraper):
    def __init__(self):
        super().__init__("Ashby ATS")

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        results = []
        async with httpx.AsyncClient(timeout=10.0) as client:
            for board in ASHBY_BOARDS:
                slug = board["slug"]
                company = board["company"]
                url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
                try:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        data = resp.json()
                        jobs = data.get("jobs", [])
                        for j in jobs:
                            title = j.get("title", "").strip()
                            desc = j.get("descriptionPlain", "") or ""
                            location = j.get("location", "Remote") or "Remote"
                            apply_url = j.get("jobUrl") or j.get("applyUrl") or f"https://jobs.ashbyhq.com/{slug}/{j.get('id')}"
                            
                            comp_info = parse_compensation(f"{title} {desc}", board["default_tier"])
                            category = detect_category(title, desc)
                            interview_type = detect_interview_type(title, desc, company)

                            results.append({
                                "id": f"ashby_{slug}_{j.get('id')}",
                                "platform": f"Ashby ({company})",
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
                                "description": desc[:1500]
                            })
                except Exception as e:
                    print(f"Error fetching Ashby {slug}: {e}")
        return results
