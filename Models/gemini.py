# gemini.py
import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()  # Carga el .env que tienes en la carpeta

gemini_api_key = os.getenv("GEMINI_API_KEY")

gemini_llm = LLM(
    model="gemini-2.0-flash",
    api_key=gemini_api_key,
    temperature=0.0
)