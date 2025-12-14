"""
FastAPI backend for Nissan chatbot/voicebot.
Provides REST and WebSocket endpoints for chat and voice interactions.
"""

import os
import io
import json
import base64
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
import httpx

load_dotenv()

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default: Rachel

# Store active threads (in production, use Redis or database)
active_threads: dict[str, str] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("Starting Nissan Chatbot API...")
    if not ASSISTANT_ID:
        print("WARNING: OPENAI_ASSISTANT_ID not set. Run 'python assistant.py --setup' first.")
    yield
    print("Shutting down...")


app = FastAPI(
    title="Nissan Chatbot API",
    description="Backend API for Nissan knowledge bot with chat and voice support",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: list[str] = []


class TTSRequest(BaseModel):
    text: str
    voice_id: str | None = None


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "assistant_configured": bool(ASSISTANT_ID),
        "voice_configured": bool(DEEPGRAM_API_KEY and ELEVENLABS_API_KEY),
    }


# Chat endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message and get a response."""
    if not ASSISTANT_ID:
        raise HTTPException(status_code=500, detail="Assistant not configured")

    # Get or create thread
    session_id = request.session_id or os.urandom(16).hex()
    if session_id not in active_threads:
        thread = openai_client.beta.threads.create()
        active_threads[session_id] = thread.id

    thread_id = active_threads[session_id]

    # Add message to thread
    openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=request.message,
    )

    # Run assistant
    run = openai_client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID,
    )

    if run.status != "completed":
        raise HTTPException(status_code=500, detail=f"Run failed: {run.status}")

    # Get response
    messages = openai_client.beta.threads.messages.list(
        thread_id=thread_id,
        order="desc",
        limit=1,
    )

    response_text = ""
    sources = []

    if messages.data:
        for content in messages.data[0].content:
            if content.type == "text":
                response_text = content.text.value
                # Extract citations/sources if present
                if hasattr(content.text, "annotations"):
                    for annotation in content.text.annotations:
                        if hasattr(annotation, "file_citation"):
                            sources.append(annotation.file_citation.file_id)

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        sources=sources,
    )


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream a chat response."""
    import asyncio
    import queue
    import threading

    if not ASSISTANT_ID:
        raise HTTPException(status_code=500, detail="Assistant not configured")

    # Get or create thread
    session_id = request.session_id or os.urandom(16).hex()
    if session_id not in active_threads:
        thread = openai_client.beta.threads.create()
        active_threads[session_id] = thread.id

    thread_id = active_threads[session_id]

    # Add message to thread
    openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=request.message,
    )

    # Use a queue to pass chunks from sync thread to async generator
    chunk_queue: queue.Queue = queue.Queue()

    def run_stream():
        """Run OpenAI stream in a thread and put chunks in queue."""
        try:
            with openai_client.beta.threads.runs.stream(
                thread_id=thread_id,
                assistant_id=ASSISTANT_ID,
            ) as stream:
                for text in stream.text_deltas:
                    chunk_queue.put(f"data: {json.dumps({'text': text, 'session_id': session_id})}\n\n")
            chunk_queue.put("data: [DONE]\n\n")
        finally:
            chunk_queue.put(None)  # Signal completion

    # Start streaming in background thread
    thread = threading.Thread(target=run_stream)
    thread.start()

    async def generate():
        """Async generator that reads from queue."""
        while True:
            # Check queue with small timeout to stay responsive
            try:
                chunk = chunk_queue.get(timeout=0.01)
                if chunk is None:
                    break
                yield chunk
            except queue.Empty:
                await asyncio.sleep(0.01)
                continue

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# Voice endpoints
@app.post("/voice/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe audio to text using Deepgram."""
    if not DEEPGRAM_API_KEY:
        raise HTTPException(status_code=500, detail="Deepgram not configured")

    audio_bytes = await audio.read()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.deepgram.com/v1/listen",
            params={
                "model": "nova-2",
                "smart_format": "true",
                "punctuate": "true",
            },
            headers={
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": audio.content_type or "audio/webm",
            },
            content=audio_bytes,
            timeout=30.0,
        )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Transcription failed")

    result = response.json()
    transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]

    return {"transcript": transcript}


@app.post("/voice/synthesize")
async def synthesize_speech(request: TTSRequest):
    """Convert text to speech using ElevenLabs."""
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ElevenLabs not configured")

    voice_id = request.voice_id or ELEVENLABS_VOICE_ID

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "text": request.text,
                "model_id": "eleven_turbo_v2_5",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True,
                },
            },
            timeout=30.0,
        )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Speech synthesis failed")

    return StreamingResponse(
        io.BytesIO(response.content),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=response.mp3"},
    )


@app.post("/voice/synthesize/stream")
async def synthesize_speech_stream(request: TTSRequest):
    """Stream text-to-speech audio."""
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ElevenLabs not configured")

    voice_id = request.voice_id or ELEVENLABS_VOICE_ID

    async def generate():
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream",
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "text": request.text,
                    "model_id": "eleven_turbo_v2_5",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    },
                },
                timeout=60.0,
            ) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(generate(), media_type="audio/mpeg")


# WebSocket for real-time voice chat
@app.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time voice chat."""
    await websocket.accept()

    session_id = os.urandom(16).hex()
    thread = openai_client.beta.threads.create()
    active_threads[session_id] = thread.id

    try:
        while True:
            # Receive audio data
            data = await websocket.receive_json()

            if data.get("type") == "audio":
                # Decode base64 audio
                audio_bytes = base64.b64decode(data["audio"])

                # Transcribe with Deepgram
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.deepgram.com/v1/listen",
                        params={"model": "nova-2", "smart_format": "true"},
                        headers={
                            "Authorization": f"Token {DEEPGRAM_API_KEY}",
                            "Content-Type": "audio/webm",
                        },
                        content=audio_bytes,
                    )

                if response.status_code != 200:
                    await websocket.send_json({"type": "error", "message": "Transcription failed"})
                    continue

                result = response.json()
                transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]

                if not transcript.strip():
                    continue

                # Send transcript to client
                await websocket.send_json({"type": "transcript", "text": transcript})

                # Get AI response
                openai_client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=transcript,
                )

                run = openai_client.beta.threads.runs.create_and_poll(
                    thread_id=thread.id,
                    assistant_id=ASSISTANT_ID,
                )

                if run.status == "completed":
                    messages = openai_client.beta.threads.messages.list(
                        thread_id=thread.id,
                        order="desc",
                        limit=1,
                    )

                    if messages.data:
                        response_text = ""
                        for content in messages.data[0].content:
                            if content.type == "text":
                                response_text = content.text.value

                        # Send text response
                        await websocket.send_json({"type": "response", "text": response_text})

                        # Synthesize and send audio
                        async with httpx.AsyncClient() as client:
                            tts_response = await client.post(
                                f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
                                headers={
                                    "xi-api-key": ELEVENLABS_API_KEY,
                                    "Content-Type": "application/json",
                                },
                                json={
                                    "text": response_text,
                                    "model_id": "eleven_turbo_v2_5",
                                },
                            )

                        if tts_response.status_code == 200:
                            audio_base64 = base64.b64encode(tts_response.content).decode()
                            await websocket.send_json({
                                "type": "audio",
                                "audio": audio_base64,
                            })

            elif data.get("type") == "end":
                break

    except WebSocketDisconnect:
        pass
    finally:
        # Cleanup
        if session_id in active_threads:
            del active_threads[session_id]


# Session management
@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session."""
    if session_id in active_threads:
        del active_threads[session_id]
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Session not found")


@app.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """Get chat history for a session."""
    if session_id not in active_threads:
        raise HTTPException(status_code=404, detail="Session not found")

    thread_id = active_threads[session_id]
    messages = openai_client.beta.threads.messages.list(
        thread_id=thread_id,
        order="asc",
    )

    history = []
    for msg in messages.data:
        content = ""
        for c in msg.content:
            if c.type == "text":
                content = c.text.value

        history.append({
            "role": msg.role,
            "content": content,
            "created_at": msg.created_at,
        })

    return {"history": history}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
