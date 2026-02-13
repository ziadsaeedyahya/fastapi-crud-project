from abc import ABC, abstractmethod
from typing import Any, Dict

class LLMBaseClient(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Base method to be implemented by all LLM clients"""
        pass