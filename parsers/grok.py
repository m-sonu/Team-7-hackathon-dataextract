import os
import json
import logging
import requests
from typing import Dict, Any, Optional

from parsers.base import BaseParser

logger = logging.getLogger("Harateko-Tanuki")

class GrokParser(BaseParser):
    def __init__(self, model: str):
        super().__init__(model)
        self.api_key = os.getenv("GROK_API_KEY")
        self.api_url = os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions")

    def parse(self, markdown_content: str, prompt_template: str, json_format: str) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            logger.error("GROK_API_KEY is missing from environment variables.")
            return None

        prompt = prompt_template.replace("{json_format}", json_format).replace("{markdown_content}", markdown_content)

        system_prompt = "You are a specialized bill parsing assistant. Respond ONLY with valid JSON. Extract specific JSON format required for our invoice parsing (Merchant, Date, Amount, Tax, Registration Number)."

        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0,
            "max_tokens": 4000,
            "response_format": {"type": "json_object"}
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=body)
            response.raise_for_status()

            response_body = response.json()
            ai_message = response_body["choices"][0]["message"]["content"]

            logger.debug(f"Grok Raw Output -> {ai_message}")

            if ai_message:
                return self.extract_json(ai_message)
            return None

        except requests.exceptions.HTTPError as e:
            logger.error(f"Grok HTTPError: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error querying Grok API: {e}")
            return None
