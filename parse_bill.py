import os
import shutil
import tempfile
import re
import json
import time
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
from extractor import extract_markdown
from parsers import ParserFactory
from dotenv import load_dotenv
from docling.document_converter import DocumentConverter

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/extraction.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Harateko-Tanuki")

app = FastAPI(title="Harateko Tanuki Bill Parser API")
converter = DocumentConverter()

@app.post("/api/parse")
async def parse_bill(file: UploadFile = File(...)):
    total_start_time = time.time()
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
        
    # Create a temporary file to save the upload
    _, ext = os.path.splitext(file.filename)
    fd, temp_path = tempfile.mkstemp(suffix=ext)
    
    try:
        # Save the uploaded file
        with os.fdopen(fd, 'wb') as f:
            shutil.copyfileobj(file.file, f)
            
        # Extract Markdown using Docling
        logger.info(f"Starting markdown extraction for: {file.filename}")
        docling_start = time.time()
        markdown_content = extract_markdown(temp_path, converter)
        docling_end = time.time()
        docling_duration = docling_end - docling_start
        
        if not markdown_content:
            logger.error(f"Failed to extract markdown from {file.filename}")
            raise HTTPException(status_code=500, detail="Failed to extract markdown from document")
            
        logger.info(f"Markdown extraction completed in {docling_duration:.2f} seconds")
        
        # Save the extracted markdown to a file
        # md_filename = f"{os.path.splitext(file.filename)[0]}.md"
        # md_path = os.path.join("extracted_md", md_filename)
        # with open(md_path, "w", encoding="utf-8") as f:
        #     f.write(markdown_content)
        # logger.info(f"Extracted markdown saved to: {md_path}")
            
        # Load prompt and format for the parser
        prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
            
        format_path = os.path.join(os.path.dirname(__file__), "bill_format.json")
        with open(format_path, "r", encoding="utf-8") as f:
            json_format = f.read()
            
        # Initialize the parser from the factory
        parser = ParserFactory.get_parser()
        
        short_markdown = markdown_content[:4000] if markdown_content else ""
    
        ai_start = time.time()
        # Parse the JSON response directly using the selected AI provider
        parsed_data = parser.parse(short_markdown, prompt_template, json_format)
        ai_end = time.time()
        ai_duration = ai_end - ai_start
        
        if not parsed_data:
            parsed_data = {"error": "AI returned empty or invalid response"}
            
        total_duration = time.time() - total_start_time
        logger.info(f"AI parsing completed in {ai_duration:.2f} seconds")
        logger.info(f"Total processing completed in {total_duration:.2f} seconds")

        return {
            "status": "success",
            "filename": file.filename,
            "timings": {
                "markdown_extraction_seconds": round(docling_duration, 2),
                "ai_parsing_seconds": round(ai_duration, 2),
                "total_seconds": round(total_duration, 2)
            },
            "data": parsed_data
        }
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    # Start the server if run directly
    uvicorn.run("parse_bill:app", host="0.0.0.0", port=8000, reload=True)