from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseScraper(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        pass
