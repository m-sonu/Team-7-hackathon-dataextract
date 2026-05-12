import os
import json
import logging
import requests
from typing import Dict, Any, Optional

from parsers.base import BaseParser

logger = logging.getLogger("Harateko-Tanuki")

class BedrockParser(BaseParser):
    def __init__(self, model: str):
        # Override with BEDROCK_MODEL_ID if it exists, otherwise use the passed model
        model_id = os.getenv("BEDROCK_MODEL_ID", model)
        super().__init__(model_id)
        self.api_key = os.getenv("BEDROCK_API_KEY")
        self.region = os.getenv("AWS_REGION", "us-east-1")

    def parse(self, markdown_content: str, prompt_template: str, json_format: str) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            logger.error("BEDROCK_API_KEY is missing from environment variables.")
            return None

        prompt = prompt_template.replace("{json_format}", json_format).replace("{markdown_content}", markdown_content)
        
        # Ensure explicitly requesting the correct JSON format in system prompt
        system_prompt = "You are a specialized bill parsing assistant. Respond ONLY with valid JSON. Extract specific JSON format required for our invoice parsing (Merchant, Date, Amount, Tax, Registration Number)."
        
        # Bedrock Amazon Nova payload structure
        body = {
            "system": [
                {
                    "text": system_prompt
                }
            ],
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "max_new_tokens": 4000,
                "temperature": 0.0
            }
        }

        url = f"https://bedrock-runtime.{self.region}.amazonaws.com/model/{self.model}/invoke"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            
            response_body = response.json()
            
            # Nova response format: output.message.content[0].text
            ai_message = ""
            if "output" in response_body and "message" in response_body["output"]:
                message_content = response_body["output"]["message"].get("content", [])
                if len(message_content) > 0:
                    ai_message = message_content[0].get("text", "")
                
            logger.debug(f"Bedrock Nova Raw Output -> {ai_message}")
            
            if ai_message:
                return self.extract_json(ai_message)
            return None
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Bedrock HTTPError: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error querying Bedrock via API: {e}")
            return None
