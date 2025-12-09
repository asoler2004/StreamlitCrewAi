# gemini.py
import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()  # Carga el .env que tienes en la carpeta

gemini_api_key = os.getenv("GEMINI_API_KEY")

# print("en gemini.py: " + gemini_api_key)

# print(gemini_api_key)

gemini_llm = LLM(
    model="gemini-2.5-flash",
    api_key=gemini_api_key,
    temperature=0.0
)