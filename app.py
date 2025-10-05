# app.py
import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import ask_agent

app = FastAPI(title="City Situation Agent", version="0.1.0")

# --- CORS ---
# Dla dev: zezwól na localhost:3000 (Next.js). Możesz podać wiele originów oddzielonych przecinkami.
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    max_age=600,  # cache preflight
)

# --- Schemy ---
class ChatIn(BaseModel):
    message: str

class ChatOut(BaseModel):
    answer: str

# --- Endpoints ---
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatOut)
async def chat(body: ChatIn):
    try:
        # ask_agent jest async wg Twojego przykładu; jeśli kiedyś będzie sync,
        # możesz użyć: answer = await asyncio.to_thread(ask_agent, body.message)
        answer = await ask_agent(body.message)
        if not isinstance(answer, str):
            answer = str(answer)
        return ChatOut(answer=answer.strip() or "Brak odpowiedzi.")
    except Exception as e:
        # Ładny błąd dla klienta, bez wycieku stacktrace
        raise HTTPException(status_code=500, detail="Agent nie odpowiada lub wystąpił błąd.") from e

# Uwaga:
# - CORSMiddleware automatycznie obsługuje OPTIONS /chat (zwróci 200),
#   więc nie trzeba tworzyć osobnej trasy @app.options("/chat").
# - Uruchom: uvicorn app:app --host 0.0.0.0 --port 5050 --reload
# - Konfiguracja originów: ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
