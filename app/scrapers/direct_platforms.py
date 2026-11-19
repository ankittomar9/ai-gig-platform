from typing import List, Dict, Any
from app.scrapers.base import BaseScraper
from app.services.pay_parser import parse_compensation, detect_category, detect_interview_type

DIRECT_PLATFORM_POSTS = [
    # --- Microtask Tier ($2-$15) ---
    {
        "id": "direct_clickworker_uhrs",
        "platform": "Clickworker",
        "company": "Clickworker",
        "title": "AI Model Feedback & UHRS Search Evaluator",
        "url": "https://www.clickworker.com/clickworker/",
        "compensation": "$5 - $15/hr",
        "comp_min": 5.0,
        "comp_max": 15.0,
        "comp_unit": "hr",
        "tier": "Microtask ($2-$15)",
        "category": "Generalist",
        "location": "Global / Remote",
        "requires_interview": "No Interview / Direct",
        "description": "Evaluate AI responses, search engine accuracy, image labeling, and categorization. Direct qualification assessments with immediate task availability."
    },
    {
        "id": "direct_prolific_eval",
        "platform": "Prolific",
        "company": "Prolific",
        "title": "Human AI Interaction & Behavioral Data Contributor",
        "url": "https://www.prolific.com/participants",
        "compensation": "$8 - $16/hr",
        "comp_min": 8.0,
        "comp_max": 16.0,
        "comp_unit": "hr",
        "tier": "Microtask ($2-$15)",
        "category": "Generalist",
        "location": "Remote",
        "requires_interview": "No Interview / Direct",
        "description": "Participate in human-in-the-loop AI studies, red-teaming games, and user preference evaluations for frontier research labs."
    },
    {
        "id": "direct_oneforma_linguistics",
        "platform": "OneForma",
        "company": "OneForma (Centific)",
        "title": "Multilingual AI Data Collector & Transcriber",
        "url": "https://jobs.oneforma.com/",
        "compensation": "$10 - $18/hr",
        "comp_min": 10.0,
        "comp_max": 18.0,
        "comp_unit": "hr",
        "tier": "Microtask ($2-$15)",
        "category": "Multilingual",
        "location": "Remote",
        "requires_interview": "Automated Test",
        "description": "Collection and verification of multilingual audio, speech transcription, and LLM translation benchmarking. Involves brief automated language tests."
    },
    {
        "id": "direct_telus_rater",
        "platform": "Telus International",
        "company": "Telus AI",
        "title": "Personalized Internet & AI Search Assessor",
        "url": "https://www.telusinternational.com/careers/ai-community",
        "compensation": "$12 - $17/hr",
        "comp_min": 12.0,
        "comp_max": 17.0,
        "comp_unit": "hr",
        "tier": "Microtask ($2-$15)",
        "category": "Generalist",
        "location": "Remote",
        "requires_interview": "Automated Test",
        "description": "Evaluate online search results, relevance of AI generated answers, and web content quality according to rigorous evaluation guidelines."
    },

    # --- Mid-Tier ($15-$30) ---
    {
        "id": "direct_dataannotation_core",
        "platform": "DataAnnotation.tech",
        "company": "DataAnnotation",
        "title": "Core AI Evaluator & Creative Prompt Specialist",
        "url": "https://www.dataannotation.tech/",
        "compensation": "$20 - $25/hr",
        "comp_min": 20.0,
        "comp_max": 25.0,
        "comp_unit": "hr",
        "tier": "Mid-Tier ($15-$30)",
        "category": "Writing & RLHF",
        "location": "Remote (US/UK/CA/AU/NZ/Global)",
        "requires_interview": "Automated Test",
        "description": "Work with cutting-edge AI models. Compare responses, write creative stories, evaluate factual correctness, and craft complex conversational prompts."
    },
    {
        "id": "direct_dataannotation_coding",
        "platform": "DataAnnotation.tech",
        "company": "DataAnnotation",
        "title": "Software Engineering & Code Evaluation Specialist",
        "url": "https://www.dataannotation.tech/",
        "compensation": "$40 - $45/hr",
        "comp_min": 40.0,
        "comp_max": 45.0,
        "comp_unit": "hr",
        "tier": "Expert ($30-$100+)",
        "category": "Coding",
        "location": "Remote",
        "requires_interview": "Automated Test",
        "description": "Write code to solve complex algorithmic tasks, debug code written by AI models, and write test suites in Python, JavaScript, and other languages."
    },
    {
        "id": "direct_mindrift_tutor",
        "platform": "Mindrift",
        "company": "Mindrift",
        "title": "AI Content Writer & Technical AI Tutor",
        "url": "https://mindrift.ai/become-a-writer",
        "compensation": "$15 - $28/hr",
        "comp_min": 15.0,
        "comp_max": 28.0,
        "comp_unit": "hr",
        "tier": "Mid-Tier ($15-$30)",
        "category": "Writing & RLHF",
        "location": "Remote",
        "requires_interview": "Automated Test",
        "description": "Craft high-quality prompts and answers, verify factual accuracy, and teach AI models how to formulate clear, logical explanations."
    },
    {
        "id": "direct_alignerr_expert",
        "platform": "Alignerr",
        "company": "Alignerr (Labelbox)",
        "title": "Domain Expert AI Alignerr (STEM, Coding & Writing)",
        "url": "https://www.alignerr.com/",
        "compensation": "$25 - $60/hr",
        "comp_min": 25.0,
        "comp_max": 60.0,
        "comp_unit": "hr",
        "tier": "Expert ($30-$100+)",
        "category": "Coding",
        "location": "Remote",
        "requires_interview": "Automated Test",
        "description": "Work on RLHF and model alignment across technical domains including software engineering, advanced mathematics, physics, and linguistics."
    },

    # --- Expert Tier ($30-$100+) ---
    {
        "id": "direct_micro1_ai_dev",
        "platform": "Micro1",
        "company": "Micro1",
        "title": "Senior AI Prompt & Code Evaluator (Global)",
        "url": "https://www.micro1.ai/jobs",
        "compensation": "$30 - $70/hr",
        "comp_min": 30.0,
        "comp_max": 70.0,
        "comp_unit": "hr",
        "tier": "Expert ($30-$100+)",
        "category": "Coding",
        "location": "Remote (Worldwide)",
        "requires_interview": "AI Interview",
        "description": "Curate and evaluate complex software datasets for world-leading foundation model labs. Involves an AI video technical interview powered by Micro1's platform."
    },
    {
        "id": "direct_mercor_ai_specialist",
        "platform": "Mercor",
        "company": "Mercor",
        "title": "Frontier AI Benchmark & Evaluation Engineer",
        "url": "https://jobs.ashbyhq.com/mercor",
        "compensation": "$40 - $120/hr",
        "comp_min": 40.0,
        "comp_max": 120.0,
        "comp_unit": "hr",
        "tier": "Expert ($30-$100+)",
        "category": "Coding",
        "location": "Remote",
        "requires_interview": "AI Interview",
        "description": "Develop and execute complex benchmarks for next-generation generative AI models. Includes Mercor's signature 20-minute automated video AI technical interview."
    }
]

class DirectPlatformScraper(BaseScraper):
    def __init__(self):
        super().__init__("Direct AI Platforms")

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        return DIRECT_PLATFORM_POSTS
