FROM python:3.11-slim

WORKDIR /app

# Install system libs for Docling & OCR
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "parse_bill:app", "--host", "0.0.0.0", "--port", "8000"]