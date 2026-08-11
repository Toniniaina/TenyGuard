from typing import Optional
from app.models.detection import ProfanityCategory, SeverityLevel


class LLMService:
    """
    Service wrapping LLM integration for contextual analysis of Malagasy expressions.
    """

    def __init__(self, api_key: str = "", model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name

    def analyze_context(self, phrase: str, surrounding_text: str = "") -> dict:
        """
        Skeleton method: Sends prompt to LLM to evaluate if a phrase is vulgar/insulting in context.
        """
        return {
            "category": ProfanityCategory.NEUTRAL,
            "severity": SeverityLevel.LOW,
            "confidence": 0.5,
            "explanation": "Skeleton response - no live API call made yet."
        }
