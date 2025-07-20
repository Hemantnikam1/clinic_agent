from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils.agentworkflow import app as agent_app
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def make_json_safe(obj):
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        return str(obj)

@app.post('/text')
async def text_service(request: Request):
    data = await request.json()
    message = data.get("message")
    session_id = data.get("session_id")
    result = await agent_app.ainvoke({"message": message, "session_id": session_id})
    return JSONResponse(content={"response": make_json_safe(result)})

@app.post('/voice')
async def voice_service():
    return JSONResponse(content={"message": "You reached voice service"}) 