import json
import urllib.request
import urllib.error
from typing import Optional
import os

def query_ollama(markdown_content: str, model: str = "llama3") -> Optional[str]:
    """Sends the extracted Markdown to Ollama and returns the response."""
    print(f"Sending data to Ollama (model: {model})...")
    url = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
    
    prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()
        
    format_path = os.path.join(os.path.dirname(__file__), "bill_format.json")
    with open(format_path, "r", encoding="utf-8") as f:
        json_format = f.read()
    
    # Prompt for Ollama - explicitly requesting a JSON structure
    prompt = prompt_template.replace("{json_format}", json_format).replace("{markdown_content}", markdown_content)
    
    data = {
        "model": model,
        "prompt": prompt,
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
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response")
    except urllib.error.HTTPError as e:
        error_message = e.read().decode('utf-8')
        print(f"❌ Ollama HTTP Error {e.code}: {e.reason}")
        print(f"Ollama response: {error_message}")
        print(f"Make sure you have pulled the model '{model}' (e.g., 'ollama pull {model}').")
        return None
    except urllib.error.URLError as e:
        print(f"❌ Failed to connect to Ollama: {e.reason}")
        print("Make sure Ollama is running locally (e.g., 'ollama serve').")
        return None
    except Exception as e:
        print(f"❌ Error querying Ollama: {e}")
        return None
