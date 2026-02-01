"""
AivisSpeech OpenAI-Compatible TTS API Router

Provides OpenAI-compatible /v1/audio/speech endpoint
for integration with Open Notebook's existing TTS infrastructure.
"""

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
import loguru

from open_notebook.providers.aivis_speech import AivisSpeechTTSProvider


router = APIRouter(prefix="/v1/audio", tags=["tts"])


class SpeechRequest(BaseModel):
    """OpenAI-compatible speech request"""

    input: str = Field(..., description="Text to synthesize")
    model: str = Field(default="aivis-speech", description="Model name (ignored, always AivisSpeech)")
    voice: str = Field(
        default="kohaku_normal",
        description="Voice ID (format: speaker_style, e.g., kohaku_normal, mao_amama)",
    )
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed")


@router.post("/speech")
async def create_speech(request: SpeechRequest):
    """
    Generate speech using AivisSpeech Engine

    OpenAI-compatible endpoint for text-to-speech synthesis.
    Returns audio in WAV format.

    **Voices available:**
    - kohaku_normal (コハク・ノーマル)
    - kohaku_amama (コハク・あまあま)
    - kohaku_setsunane (コハク・せつなめ)
    - kohaku_nemutai (コハク・ねむたい)
    - mao_normal (まお・ノーマル)
    - mao_futsuu (まお・ふつー)
    - mao_amama (まお・あまあま)
    - mao_ochitsuki (まお・おちつき)
    - mao_karakai (まお・からかい)
    - mao_setsunane (まお・せつなめ)
    """
    try:
        # Validate input
        if not request.input or len(request.input.strip()) == 0:
            raise HTTPException(status_code=400, detail="Input text cannot be empty")

        if len(request.input) > 5000:
            raise HTTPException(status_code=400, detail="Input text too long (max 5000 characters)")

        loguru.logger.info(f"TTS request: voice={request.voice}, length={len(request.input)}")

        # Synthesize audio
        audio_data = await AivisSpeechTTSProvider.synthesize(
            text=request.input,
            voice=request.voice,
            speed=request.speed,
        )

        # Return WAV audio
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f'attachment; filename="speech_{request.voice}.wav"',
                "X-Model-Used": "aivis-speech",
                "X-Voice-Used": request.voice,
            },
        )

    except ValueError as e:
        loguru.logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        loguru.logger.error(f"TTS generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate speech")


@router.get("/voices")
async def list_voices():
    """List available AivisSpeech voices"""
    try:
        voices = await AivisSpeechTTSProvider.get_available_voices()
        return {
            "object": "list",
            "data": voices,
        }
    except Exception as e:
        loguru.logger.error(f"Failed to list voices: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve voices")


@router.get("/health")
async def health_check():
    """Check AivisSpeech Engine health"""
    is_healthy = await AivisSpeechTTSProvider.health_check()

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "provider": "aivis-speech",
        "endpoint": "http://127.0.0.1:10101",
    }
