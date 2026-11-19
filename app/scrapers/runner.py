import asyncio
from typing import List, Dict, Any
from app.scrapers.ashby import AshbyScraper
from app.scrapers.greenhouse import GreenhouseScraper
from app.scrapers.lever import LeverScraper
from app.scrapers.direct_platforms import DirectPlatformScraper
from app.services.matcher import calculate_match_score
from app.services.pay_parser import extract_experience_years, check_location_and_language
from app.database import get_user_profile, save_or_update_jobs

async def run_full_scan() -> Dict[str, Any]:
    scrapers = [
        AshbyScraper(),
        GreenhouseScraper(),
        LeverScraper(),
        DirectPlatformScraper()
    ]

    tasks = [s.fetch_jobs() for s in scrapers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_jobs: List[Dict[str, Any]] = []
    scraped_counts: Dict[str, int] = {}

    for s, res in zip(scrapers, results):
        if isinstance(res, list):
            all_jobs.extend(res)
            scraped_counts[s.name] = len(res)
        else:
            print(f"Scraper {s.name} failed: {res}")
            scraped_counts[s.name] = 0

    # Retrieve user profile for scoring
    profile = get_user_profile()
    user_skills = profile.get("skills", [])
    user_resume = profile.get("resume_text", "")

    # Calculate match scores and experience levels
    for job in all_jobs:
        score, matching = calculate_match_score(
            job.get("title", ""),
            job.get("description", ""),
            user_skills,
            user_resume
        )
        job["match_score"] = score
        job["matching_skills"] = matching

        exp_data = extract_experience_years(
            job.get("title", ""),
            job.get("description", ""),
            job.get("company", "")
        )
        job["min_exp_years"] = exp_data["min_exp"]
        job["max_exp_years"] = exp_data["max_exp"]
        job["exp_label"] = exp_data["label"]

        loc_data = check_location_and_language(
            job.get("title", ""),
            job.get("location", ""),
            job.get("description", "")
        )
        job["is_india_eligible"] = 1 if loc_data["is_india_eligible"] else 0
        job["location_status"] = loc_data["location_status"]
        job["language_status"] = loc_data["language_status"]

    # Save to database
    save_or_update_jobs(all_jobs)

    return {
        "status": "success",
        "total_jobs": len(all_jobs),
        "breakdown": scraped_counts
    }
