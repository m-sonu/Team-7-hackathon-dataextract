import os
import json
import logging
from typing import Dict, Any, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from parsers.base import BaseParser

logger = logging.getLogger("Harateko-Tanuki")

class BedrockParser(BaseParser):
    def __init__(self, model: str):
        model_id = os.getenv("BEDROCK_MODEL_ID", model)
        super().__init__(model_id)
        self.region = os.getenv("AWS_REGION", "us-east-1")
        # boto3 automatically picks up AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
        # env vars, or uses the IAM role attached to the EC2/ECS instance — no
        # manual key handling needed.
        self.client = boto3.client("bedrock-runtime", region_name=self.region)

    def parse(self, markdown_content: str, prompt_template: str, json_format: str) -> Optional[Dict[str, Any]]:
        prompt = prompt_template.replace("{json_format}", json_format).replace("{markdown_content}", markdown_content)

        system_prompt = "You are a specialized bill parsing assistant. Respond ONLY with valid JSON. Extract specific JSON format required for our invoice parsing (Merchant, Date, Amount, Tax, Registration Number)."

        body = {
            "system": [{"text": system_prompt}],
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ],
            "inferenceConfig": {
                "max_new_tokens": 4000,
                "temperature": 0.0,
            },
        }

        try:
            response = self.client.invoke_model(
                modelId=self.model,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )
            response_body = json.loads(response["body"].read())

            # Nova response format: output.message.content[0].text
            ai_message = ""
            if "output" in response_body and "message" in response_body["output"]:
                content = response_body["output"]["message"].get("content", [])
                if content:
                    ai_message = content[0].get("text", "")

            logger.debug(f"Bedrock Nova Raw Output -> {ai_message}")

            if ai_message:
                return self.extract_json(ai_message)
            return None

        except NoCredentialsError:
            logger.error("AWS credentials not found. Set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY or attach an IAM role.")
            return None
        except ClientError as e:
            code = e.response["Error"]["Code"]
            msg = e.response["Error"]["Message"]
            logger.error(f"Bedrock ClientError: {code} - {msg}")
            return None
        except Exception as e:
            logger.error(f"Error querying Bedrock: {e}")
            return None
