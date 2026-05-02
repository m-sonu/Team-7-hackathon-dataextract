import sys
import os
from typing import Optional

def get_input_file() -> Optional[str]:
    """Retrieves and validates the input file path from command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: uv run python parse_bill.py <path_to_bill>")
        return None

    input_path = sys.argv[1]

    if not os.path.exists(input_path):
        print(f"Error: File not found at {input_path}")
        return None
        
    return input_path

def save_outputs(input_path: str, markdown_content: str, ollama_response: Optional[str]) -> None:
    """Saves the Markdown and Ollama response to the filesystem."""
    base_name = os.path.basename(input_path)
    file_name_without_ext = os.path.splitext(base_name)[0]

    md_dir = os.getenv("MD_OUTPUT_DIR", "md_output")
    json_dir = os.getenv("JSON_OUTPUT_DIR", "json_output")
    
    os.makedirs(md_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)

    md_filename = os.path.join(md_dir, f"{file_name_without_ext}.md")
    response_filename = os.path.join(json_dir, f"{file_name_without_ext}_response.json")

    # Save Markdown (Best for LLMs)
    with open(md_filename, "w", encoding='utf-8') as f:
        f.write(markdown_content)
    print(f"📄 Markdown for AI: {md_filename}")

    # Save Ollama response if available
    if ollama_response:
        with open(response_filename, "w", encoding='utf-8') as f:
            f.write(ollama_response)
        print(f"🤖 Ollama Response: {response_filename}")
