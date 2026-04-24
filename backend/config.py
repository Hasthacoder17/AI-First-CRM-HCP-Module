import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "gemma2-9b-it"
API_BASE_URL = "http://localhost:8000"
