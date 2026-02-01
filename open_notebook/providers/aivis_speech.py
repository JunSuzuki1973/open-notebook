"""
AivisSpeech TTS Provider for Open Notebook

Integrates AivisSpeech Engine for Japanese text-to-speech synthesis.
"""

import os
from typing import Any, Dict, List, Optional
import httpx
from loguru import logger


class AivisSpeechTTSProvider:
    """AivisSpeech Engine TTS provider"""

    BASE_URL = os.getenv("AIVIS_API_ENDPOINT", "http://127.0.0.1:10101")

    # Speaker mappings for AivisSpeech
    SPEAKERS = {
        "mao": {
            "normal": 888753760,
            "futsuu": 888753761,
            "amama": 888753762,
            "ochitsuki": 888753763,
            "karakai": 888753764,
            "setsunane": 888753765,
        },
        "kohaku": {
            "normal": 1878365376,
            "amama": 1878365377,
            "setsunane": 1878365378,
            "nemutai": 1878365379,
        },
    }

    @classmethod
    async def get_available_voices(cls) -> List[Dict[str, Any]]:
        """Get available voices from AivisSpeech Engine"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{cls.BASE_URL}/speakers", timeout=10.0)
                response.raise_for_status()
                speakers = response.json()

                voices = []
                for speaker in speakers:
                    for style in speaker.get("styles", []):
                        voices.append({
                            "id": f"{speaker['name']}_{style['name']}",
                            "name": style["name"],
                            "speaker": speaker["name"],
                            "style_id": style["id"],
                        })

                logger.info(f"Found {len(voices)} voices in AivisSpeech")
                return voices

        except Exception as e:
            logger.error(f"Failed to get AivisSpeech voices: {e}")
            return []

    @classmethod
    def parse_voice_id(cls, voice_id: str) -> Optional[tuple[str, str]]:
        """Parse voice_id into speaker and style"""
        # Expected format: "speaker_style" or "speaker_style_ja"
        for speaker_name, styles in cls.SPEAKERS.items():
            for style_name in styles.keys():
                if voice_id.startswith(f"{speaker_name}_{style_name}"):
                    return speaker_name, style_name
        return None

    @classmethod
    async def synthesize(
        cls,
        text: str,
        voice: str = "kohaku_normal",
        speed: float = 1.0,
    ) -> bytes:
        """
        Synthesize speech using AivisSpeech Engine

        Args:
            text: Input text to synthesize
            voice: Voice ID in format "speaker_style" (e.g., "kohaku_normal")
            speed: Speech speed (0.5 to 2.0)

        Returns:
            Audio data as bytes (WAV format)

        Raises:
            ValueError: If voice_id is invalid
            httpx.HTTPError: If API request fails
        """
        # Parse voice_id
        parsed = cls.parse_voice_id(voice)
        if not parsed:
            raise ValueError(
                f"Invalid voice_id '{voice}'. "
                f"Expected format: 'speaker_style' (e.g., 'kohaku_normal')"
            )

        speaker_name, style_name = parsed
        style_id = cls.SPEAKERS[speaker_name][style_name]

        logger.info(f"Synthesizing with {speaker_name} ({style_name}), style_id={style_id}")

        try:
            async with httpx.AsyncClient() as client:
                # Step 1: Create AudioQuery
                query_params = {"speaker": style_id, "text": text}
                query_response = await client.post(
                    f"{cls.BASE_URL}/audio_query",
                    params=query_params,
                    timeout=30.0,
                )
                query_response.raise_for_status()
                audio_query = query_response.json()

                # Adjust speed if needed
                if speed != 1.0:
                    audio_query["speedScale"] = speed

                # Step 2: Synthesize audio
                synth_response = await client.post(
                    f"{cls.BASE_URL}/synthesis",
                    params={"speaker": style_id},
                    json=audio_query,
                    timeout=60.0,
                )
                synth_response.raise_for_status()

                audio_data = synth_response.content
                logger.info(f"Synthesized {len(audio_data)} bytes of audio")
                return audio_data

        except httpx.HTTPError as e:
            logger.error(f"AivisSpeech API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during synthesis: {e}")
            raise

    @classmethod
    async def health_check(cls) -> bool:
        """Check if AivisSpeech Engine is accessible"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{cls.BASE_URL}/speakers", timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False


# Helper function for OpenAI-compatible API
async def openai_compatible_speech(
    input: str,
    voice: str = "kohaku_normal",
    speed: float = 1.0,
) -> bytes:
    """
    OpenAI-compatible TTS function

    Maps to AivisSpeech synthesize method for integration
    with existing Open Notebook TTS infrastructure.
    """
    return await AivisSpeechTTSProvider.synthesize(
        text=input,
        voice=voice,
        speed=speed,
    )
