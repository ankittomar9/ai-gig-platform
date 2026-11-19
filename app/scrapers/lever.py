import httpx
from typing import List, Dict, Any
from app.scrapers.base import BaseScraper
from app.services.pay_parser import parse_compensation, detect_category, detect_interview_type

LEVER_BOARDS = [
    {"slug": "appen", "company": "Appen", "default_tier": "Microtask ($2-$15)"}
]

class LeverScraper(BaseScraper):
    def __init__(self):
        super().__init__("Lever ATS")

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        results = []
        async with httpx.AsyncClient(timeout=10.0) as client:
            for board in LEVER_BOARDS:
                slug = board["slug"]
                company = board["company"]
                url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
                try:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        jobs = resp.json()
                        for j in jobs:
                            title = j.get("text", "").strip()
                            desc = j.get("descriptionPlain", "") or ""
                            location = j.get("country", "Remote") or "Remote"
                            apply_url = j.get("applyUrl") or j.get("hostedUrl") or ""

                            salary_range = j.get("salaryRange", {})
                            raw_comp = ""
                            if salary_range:
                                min_s = salary_range.get("min")
                                max_s = salary_range.get("max")
                                interval = salary_range.get("interval", "per-year")
                                if min_s and max_s:
                                    raw_comp = f"${min_s} - ${max_s} {interval}"

                            comp_info = parse_compensation(f"{raw_comp} {title} {desc}", board["default_tier"])
                            category = detect_category(title, desc)
                            interview_type = detect_interview_type(title, desc, company)

                            results.append({
                                "id": f"lever_{slug}_{j.get('id')}",
                                "platform": f"Lever ({company})",
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
                    print(f"Error fetching Lever {slug}: {e}")
        return results
