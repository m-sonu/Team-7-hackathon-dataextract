import json
import os
import urllib.request
import urllib.error
import logging
from typing import Dict, Any, Optional

from parsers.base import BaseParser

logger = logging.getLogger("Harateko-Tanuki")

class OllamaParser(BaseParser):
    def parse(self, markdown_content: str, prompt_template: str, json_format: str) -> Optional[Dict[str, Any]]:
        url = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/chat")
        
        prompt = prompt_template.replace("{json_format}", json_format).replace("{markdown_content}", markdown_content)
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a specialized bill parsing assistant. Respond ONLY with valid JSON."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "stream": False,
            "format": "json"
        }
        
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                raw_body = response.read().decode('utf-8')
                result = json.loads(raw_body)
                
                ai_message = result.get("message", {}).get("content")
                logger.debug(f"Ollama Raw Output -> {ai_message}")
                
                if ai_message:
                    return self.extract_json(ai_message)
                return None
                
        except urllib.error.HTTPError as e:
            error_message = e.read().decode('utf-8')
            logger.error(f"Ollama HTTP Error {e.code}: {e.reason}")
            logger.error(f"Ollama response: {error_message}")
            return None
        except urllib.error.URLError as e:
            logger.error(f"Failed to connect to Ollama: {e.reason}")
            return None
        except Exception as e:
            logger.error(f"Error querying Ollama: {e}")
            return None
