from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from transformers import pipeline
from TTS.api import TTS
import whisper
import os

app = FastAPI()

# Carica modelli leggeri
whisper_model = whisper.load_model("tiny")
llm = pipeline("text-generation", model="distilgpt2")  # Sostituisci con Mistral 7B
tts = TTS(model_name="tts_models/en/ljspeech/vits")

class CommandRequest(BaseModel):
    command: str
    mode: str

@app.post("/process")
async def process_command(request: CommandRequest):
    try:
        # Elabora comando con LLM
        prompt = (
            f"Rispondi in modo adatto ai bambini: {request.command}" if request.mode == "child"
            else f"Rispondi in modo maturo e naturale: {request.command}"
        )
        response = llm(prompt, max_length=50, num_return_sequences=1)[0]["generated_text"]

        # Determina espressione
        expression = "happy" if "felice" in response.lower() else "neutral"

        # Genera audio TTS
        audio_path = f"output_{request.mode}.wav"
        speaker = "p225" if request.mode == "child" else "p230"  # VCTK voci
        tts.tts_to_file(
            text=response,
            file_path=audio_path,
            speaker_wav=f"/vctk/{speaker}.wav" if os.path.exists(f"/vctk/{speaker}.wav") else None
        )

        # URL audio
        audio_url = f"https://your-app.onrender.com/audio/{audio_path}"

        return {
            "text": response,
            "expression": expression,
            "audio_url": audio_url,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    if os.path.exists(filename):
        return FileResponse(filename)
    raise HTTPException(status_code=404, detail="File non trovato")
