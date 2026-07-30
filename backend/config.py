import os
from dotenv import load_dotenv
load_dotenv()

# ── Environment
USE_GROQ = os.getenv("USE_GROQ", "false").lower() == "true"

# ── Models based on provider
if USE_GROQ:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    EXTRACTION_MODEL = "openai/gpt-oss-20b"
    VALIDATION_MODEL = "openai/gpt-oss-20b"
    MODEL= "llama-3.1-8b-instant"
else:
    OLLAMA_HOST = "http://localhost:11434"
    EXTRACTION_MODEL = "qwen3:latest"
    VALIDATION_MODEL = "qwen3:latest"
    MODEL="qwen3:latest"

# ── Output directory
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
