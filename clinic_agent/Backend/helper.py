import json
import pyttsx3
import soundfile as sf
import librosa
import numpy as np
import io
import asyncio


def make_json_safe(obj):
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        return str(obj)

# --- NEW: Helper function for pyttsx3 ---
def run_tts_and_save(engine: pyttsx3.Engine, text: str, file_path: str):
    """
    Synchronous function to run the TTS engine and save to a file.
    """
    engine.save_to_file(text, file_path)
    engine.runAndWait()

async def transcribe_audio(audio_bytes: bytes, stt_model) -> str:
    """
    Transcribes audio bytes to text using the provided Whisper model.
    """
    audio_as_np_array, sampling_rate = sf.read(io.BytesIO(audio_bytes))
    if audio_as_np_array.ndim > 1:
        audio_as_np_array = np.mean(audio_as_np_array, axis=1)
    if sampling_rate != 16000:
        audio_as_np_array = librosa.resample(y=audio_as_np_array, orig_sr=sampling_rate, target_sr=16000)
    audio_as_np_array = audio_as_np_array.astype(np.float32)
    transcription_result = stt_model.transcribe(audio_as_np_array, language="en", fp16=False)
    user_message = transcription_result.get("text", "").strip()
    return user_message

async def synthesize_speech(engine: pyttsx3.Engine, text: str, tmp_wav_path: str):
    """
    Synthesizes speech from text and saves it to a temporary WAV file asynchronously.
    """
    await asyncio.to_thread(run_tts_and_save, engine, text, tmp_wav_path) 