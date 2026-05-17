FROM python:3.11-slim

WORKDIR /app

# Install system libs for Docling & OCR
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download docling ML models during build so the container works offline
RUN python -c "from docling.document_converter import DocumentConverter; DocumentConverter()"

COPY . .

# Ensure the logs directory exists
RUN mkdir -p /app/logs

CMD ["uvicorn", "parse_bill:app", "--host", "0.0.0.0", "--port", "8000"]