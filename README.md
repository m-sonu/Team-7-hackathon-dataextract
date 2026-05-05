# Harateko Tanuki

## Setup Instructions

This project uses Python. You can set up your local development environment using either the standard `venv` module (with `pip`) or using the modern, faster `uv` package manager.

### Option 1: Using `uv` (Recommended)

`uv` is an extremely fast Python package installer and resolver written in Rust.

1. **Install `uv`** (if you don't have it installed globally):
   - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh` or `brew install uv`
   - Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

2. **Create the virtual environment:**

   ```bash
   uv venv
   ```

3. **Activate the virtual environment:**
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```

4. **Install dependencies:**
   _(If you add a `requirements.txt` file later)_
   ```bash
   uv pip install -r requirements.txt
   ```

---

### Option 2: Using standard `venv` and `pip`

1. **Create the virtual environment:**

   ```bash
   python3 -m venv .venv
   ```

2. **Activate the virtual environment:**
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```

3. **Install dependencies:**
   _(If you add a `requirements.txt` file later)_
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Before running the scripts, you need to set up your environment variables. Copy the provided `.env.example` file to create your own `.env` file:

```bash
# On macOS/Linux
cp .env.example .env

# On Windows (PowerShell)
copy .env.example .env
```

Update the values in `.env` if necessary.

## Usage (API Server)

The project has been updated to run as a REST API server using **FastAPI**. 

### 1. Start the Server

Start the API server by running the script. If you get a `command not found: python` error, use `python3` or if you are using `uv`, use `uv run`:

```bash
# Using uv (Recommended)
uv run python parse_bill.py

# Or using the standard python command (make sure the virtual environment is activated)
python3 parse_bill.py
```

The server will start on `http://0.0.0.0:8000`.

### 2. Make an API Call from Another Project

You can now send files to this API from any other application (or using `curl`). 

**Endpoint:** `POST /api/parse`
**Body:** `multipart/form-data` with a field named `file` containing the file to be parsed.

**Example using `curl`:**
```bash
curl -X POST "http://localhost:8000/api/parse" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/your/image.jpg"
```

The API will extract the text, query the Ollama AI model, and return the parsed JSON data as a response.
