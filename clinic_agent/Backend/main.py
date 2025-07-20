from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from utils.agentworkflow import app as agent_app
import json
import whisper
import os
import io
import soundfile as sf
import librosa
import numpy as np
import pyttsx3
import tempfile
import asyncio
from helper import make_json_safe, run_tts_and_save, transcribe_audio, synthesize_speech

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stt_model = None
try:
    print("Loading Whisper STT model...")
    stt_model = whisper.load_model("small")
    print("Whisper STT model loaded successfully.")
except Exception as e:
    print(f"Error loading Whisper STT model: {e}")

tts_engine = None
try:
    print("Initializing pyttsx3 TTS engine...")
    tts_engine = pyttsx3.init()
    print("pyttsx3 TTS engine initialized.")
except Exception as e:
    print(f"Error initializing pyttsx3 engine: {e}")


@app.post('/text')
async def text_service(request: Request):
    data = await request.json()
    message = data.get("message")
    session_id = data.get("session_id")
    agent_persona = data.get("agent_persona")
    result = await agent_app.ainvoke({"message": message, "session_id": session_id, "agent_persona": agent_persona})
    return JSONResponse(content={"response": make_json_safe(result)})



@app.post('/voice')
async def voice_service(audio: UploadFile = File(...), session_id: str = Form(None), agent_persona: str = Form(None)):
    """
    Receives an audio file, transcribes it, sends the text to an agent,
    then converts the agent's final response back into speech.
    """
    if not stt_model:
        return JSONResponse(status_code=500, content={"error": "Speech-to-Text model is not available."})
    if not tts_engine:
        return JSONResponse(status_code=500, content={"error": "Text-to-Speech engine is not available."})

    try:
        # --- Part 1: Speech-to-Text ---
        audio_bytes = await audio.read()
        user_message = await transcribe_audio(audio_bytes,stt_model)
        print(f"Transcription successful: '{user_message}'")

        if not user_message:
            return JSONResponse(status_code=400, content={"error": "Transcription resulted in empty text."})

        # --- Part 2: Get response from Agent ---
        print(f"Sending message to agent: '{user_message}'")
        agent_result = await agent_app.ainvoke({"message": user_message, "session_id": session_id, "agent_persona": agent_persona})
        safe_agent_result = make_json_safe(agent_result)

        # Extract the final response text
        final_response_text = safe_agent_result.get("final_response", "")
        if not final_response_text:
            # Fallback in case the structure is nested under 'response'
            if isinstance(safe_agent_result.get("response"), dict):
                final_response_text = safe_agent_result.get("response", {}).get("final_response", "")

        print(f"Agent final response: '{final_response_text}'")
        if not final_response_text:
            return JSONResponse(status_code=500, content={"error": "Agent did not provide a final response."})

        # --- Part 3: Text-to-Speech using pyttsx3 ---
        print(f"Converting agent response to audio with pyttsx3...")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
            tmp_wav_path = tmp_wav.name

        await synthesize_speech(tts_engine, final_response_text, tmp_wav_path)

        with open(tmp_wav_path, "rb") as f:
            wav_buffer = io.BytesIO(f.read())

        os.unlink(tmp_wav_path)

        wav_buffer.seek(0)
        return StreamingResponse(
            wav_buffer,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=response_speech.wav"}
        )

    except Exception as e:
        print(f"Error during voice processing: {e}")
        return JSONResponse(status_code=500, content={"error": f"Failed to process audio. Error: {str(e)}"})
