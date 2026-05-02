from typing import Optional
from docling.document_converter import DocumentConverter

def extract_markdown(input_path: str) -> Optional[str]:
    """Uses Docling to convert the document at the given path to Markdown."""
    print(f"Tanuki is sniffing: {input_path}...")
    try:
        converter = DocumentConverter()
        result = converter.convert(input_path)
        return result.document.export_to_markdown()
    except Exception as e:
        print(f"❌ Error during document conversion: {e}")
        return None
