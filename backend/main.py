import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from pathlib import Path

load_dotenv()   
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise RuntimeError("API kljuc nije ucitan. Proverite da li .env fajl postoji, i dali se u njemu nalazi API kljuc.")

client = genai.Client(api_key=GEMINI_API_KEY)
app = FastAPI(title="Code Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Review(BaseModel):
    code: str
    language: str = "auto-detect"
    personality: str = "senioreng"

class ReviewResponse(BaseModel):
    review: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/review", response_model=ReviewResponse)
def review_code(body: Review):

    if not body.code.strip():
        raise HTTPException(status_code=400, detail="Kod ne sme biti prazan. Upisi kod za pregled")

    prompt_path = Path.cwd() / f"prompts/{body.personality}.txt"
    try:
        with open(prompt_path, 'r') as f:
            prompt=f.read()
    except FileNotFoundError as err:
        raise HTTPException(status_code=500, detail=f"Dati fajl prompt-a ne postoji. Originalna poruka: {err}")
    except OSError as err:
        raise HTTPException(status_code=500, detail=f"Doslo je do greske pri citanju fajla za prompt. Originalna poruka : {err}")

    if not prompt.strip():
        raise HTTPException(status_code=500, detail="Prompt je prazan, nije moguce nastaviti sa izvrsavanjem programa.")

    try:
        gemini_call = f"Language: {body.language}\n\nCode:\n```\n{body.code}\n```"
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config={"system_instruction": prompt},
            contents=gemini_call,
        )
        return ReviewResponse(review=response.text)
    except Exception as err:
        raise HTTPException(status_code=502, detail=f"Greska pri komunikaciji sa Gemini-jem. Originalna poruka: {err}")