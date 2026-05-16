import os
import logging

from parsers.base import BaseParser
from parsers.ollama import OllamaParser
from parsers.bedrock import BedrockParser
from parsers.grok import GrokParser

logger = logging.getLogger("Harateko-Tanuki")

class ParserFactory:
    @staticmethod
    def get_parser() -> BaseParser:
        provider = os.getenv("AI_PROVIDER", "ollama").lower()

        if provider == "bedrock":
            model = os.getenv("BEDROCK_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0")
            logger.info(f"Using Bedrock parser with model: {model}")
            return BedrockParser(model)
        elif provider == "grok":
            model = os.getenv("GROK_MODEL", "grok-3")
            logger.info(f"Using Grok parser with model: {model}")
            return GrokParser(model)
        elif provider == "ollama":
            model = os.getenv("AI_MODEL", "qwen2.5-coder:14b")
            logger.info(f"Using Ollama parser with model: {model}")
            return OllamaParser(model)
        else:
            logger.warning(f"Unknown provider '{provider}', falling back to Ollama")
            model = os.getenv("AI_MODEL", "qwen2.5-coder:14b")
            return OllamaParser(model)
