from file_handler import get_input_file, save_outputs
from extractor import extract_markdown
from ollama_client import query_ollama
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    # 1. Get the file path
    input_path = get_input_file()
    if not input_path:
        return

    # 2. Extract Markdown using Docling
    markdown_content = extract_markdown(input_path)
    if not markdown_content:
        return

    # 3. Send Markdown to Ollama
    # You currently have 'qwen2.5-coder:14b' installed!
    model = os.getenv("AI_MODEL", "qwen2.5-coder:14b")
    ollama_response = query_ollama(markdown_content, model=model)

    # 4. Create and save outputs
    save_outputs(input_path, markdown_content, ollama_response)
    
    print("✨ SUCCESS!")

if __name__ == '__main__':
    main()