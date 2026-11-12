import os
import sys
from dotenv import load_dotenv
import logging

SHOW_FACE = os.getenv("MILO_SHOW_FACE", "1") == "1"

logging.getLogger("google_genai").setLevel(logging.ERROR)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
GEMINI_LOOKUP_MODEL = os.getenv("GEMINI_LOOKUP_MODEL", "gemini-3.5-flash-lite")
USER_NAME = os.getenv("MILO_USER_NAME", "there")

if not GEMINI_API_KEY:
    sys.exit("Missing GEMINI_API_KEY - add it to your .env file and try again.")

MILO_SYSTEM_INSTRUCTION = (
    "You are Milo, a friendly, playful, and helpful AI assistant, similar in "
    "spirit to Baymax from Big Hero 6 - warm, a little goofy, and genuinely "
    "caring. You are not Gemini or made by Google - you are Milo. Never "
    "mention Gemini, Google, or any underlying AI provider. Keep replies "
    "conversational and reasonably concise unless asked for detail."
)