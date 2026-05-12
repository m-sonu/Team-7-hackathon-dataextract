from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import re

class BaseParser(ABC):
    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    def parse(self, markdown_content: str, prompt_template: str, json_format: str) -> Optional[Dict[str, Any]]:
        """
        Parses the markdown content using the specific AI provider.
        Should return a dictionary containing the parsed JSON data.
        """
        pass
    
    def extract_json(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Utility method to extract JSON from a raw text response.
        """
        if not response_text:
            return None
            
        try:
            # First try direct parsing
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback to regex extraction
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    return {"error": "Found JSON-like structure but it was invalid", "raw": response_text}
            
        return {"error": "No JSON found in response", "raw": response_text}
