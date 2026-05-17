import traceback
import logging
from typing import Optional
from docling.document_converter import DocumentConverter

logger = logging.getLogger("Harateko-Tanuki")

def extract_markdown(input_path: str, converter: DocumentConverter) -> Optional[str]:
    """Uses Docling to convert the document at the given path to Markdown."""
    print(f"Tanuki is sniffing: {input_path}...")
    try:
        result = converter.convert(input_path)
        return result.document.export_to_markdown()
    except Exception as e:
        logger.error(f"Failed to extract markdown from {input_path}: {e}\n{traceback.format_exc()}")
        return None
