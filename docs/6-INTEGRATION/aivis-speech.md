# AivisSpeech Integration for Open Notebook

Integrate AivisSpeech Engine for free, private, Japanese text-to-speech synthesis in Open Notebook.

---

## Overview

[AivisSpeech Engine](https://github.com/Aivis-Speech-Project/AivisSpeech-Engine) is an open-source Japanese speech synthesis engine based on VOICEVOX. This integration allows Open Notebook to use AivisSpeech for podcast generation and TTS features.

---

## Features

- **Free & Local** - No API costs, runs entirely on your machine
- **Japanese Native** - Optimized for Japanese text synthesis
- **Multiple Speakers** - Support for Mao (まお) and Kohaku (コハク) with various styles
- **Privacy-First** - Audio generation happens locally, no data sent to external services
- **OpenAI-Compatible** - Drop-in replacement for OpenAI's TTS API

---

## Prerequisites

1. **AivisSpeech Engine running** on port 10101
   ```bash
   docker run -d -p 10101:10101 ghcr.io/aivis-project/aivisspeech-engine:cpu-latest
   ```

2. **Open Notebook deployed** (Docker or local)

---

## Quick Start

### Step 1: Verify AivisSpeech Engine

```bash
# Check if AivisSpeech is running
curl http://localhost:10101/speakers

# Should return JSON with speaker list
```

### Step 2: Configure Open Notebook

Add environment variable to your Open Notebook deployment:

**Docker Compose:**
```yaml
services:
  open-notebook:
    environment:
      - AIVIS_API_ENDPOINT=http://host.docker.internal:10101
```

**Local Development:**
```bash
export AIVIS_API_ENDPOINT=http://localhost:10101
```

### Step 3: Add TTS Model in Open Notebook

1. Go to **Settings** → **Models**
2. In the **Text-to-Speech** section, click **Add Model**
3. Configure:
   - **Provider:** `openai_compatible`
   - **Base URL:** `http://localhost:10101/api/v1` (or your AivisSpeech endpoint)
   - **Model Name:** `aivis-speech`
   - **Display Name:** `AivisSpeech (Japanese)`
   - **API Key:** (leave empty)
4. Click **Save**

---

## Available Voices

### Kohaku (コハク)

| Voice ID | Style | Description |
|----------|-------|-------------|
| `kohaku_normal` | ノーマル | Standard tone |
| `kohaku_amama` | あまあま | Sweet/cute tone |
| `kohaku_setsunane` | せつなめ | Emotional/sentimental |
| `kohaku_nemutai` | ねむたい | Sleepy/relaxed tone |

### Mao (まお)

| Voice ID | Style | Description |
|----------|-------|-------------|
| `mao_normal` | ノーマル | Standard tone |
| `mao_futsuu` | ふつー | Casual tone |
| `mao_amama` | あまあま | Sweet/cute tone |
| `mao_ochitsuki` | おちつき | Calm/composed tone |
| `mao_karakai` | からかい | Teasing/playful tone |
| `mao_setsunane` | せつなめ | Emotional/sentimental |

---

## API Endpoints

### Generate Speech

```bash
POST /api/v1/audio/speech
Content-Type: application/json

{
  "input": "こんにちは、動画自動生成工場へようこそ！",
  "model": "aivis-speech",
  "voice": "kohaku_normal",
  "speed": 1.0
}
```

**Response:**
- Content-Type: `audio/wav`
- Body: Audio data in WAV format

### List Available Voices

```bash
GET /api/v1/audio/voices
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "kohaku_normal",
      "name": "ノーマル",
      "speaker": "コハク",
      "style_id": 1878365376
    }
  ]
}
```

### Health Check

```bash
GET /api/v1/audio/health
```

**Response:**
```json
{
  "status": "healthy",
  "provider": "aivis-speech",
  "endpoint": "http://127.0.0.1:10101"
}
```

---

## Speaker Profiles for Podcasts

Create speaker profiles in Open Notebook:

**Host (Kohaku Normal):**
- Name: `Host`
- Model: `aivis-speech`
- Voice: `kohaku_normal`
- Speed: `1.0`

**Guest (Mao Casual):**
- Name: `Guest`
- Model: `aivis-speech`
- Voice: `mao_futsuu`
- Speed: `1.0`

**Narrator (Kohaku Sweet):**
- Name: `Narrator`
- Model: `aivis-speech`
- Voice: `kohaku_amama`
- Speed: `0.9`

---

## Configuration Examples

### Docker Compose (Full Setup)

```yaml
version: '3.8'

services:
  aivis-speech:
    image: ghcr.io/aivis-project/aivisspeech-engine:cpu-latest
    container_name: aivis-speech-engine
    ports:
      - "10101:10101"
    restart: unless-stopped

  open-notebook:
    image: ghcr.io/lfnovo/open-notebook:latest
    ports:
      - "3000:3000"
    environment:
      - AIVIS_API_ENDPOINT=http://aivis-speech:10101
    depends_on:
      - aivis-speech
```

---

## Troubleshooting

### Connection Refused

**Problem:** Cannot connect to AivisSpeech Engine

**Solutions:**
1. Verify AivisSpeech container is running: `docker ps | grep aivis`
2. Test endpoint: `curl http://localhost:10101/speakers`
3. Check firewall rules
4. For Docker-to-Docker, use container name instead of `localhost`

### Voice Not Found

**Problem:** "Invalid voice_id" error

**Solutions:**
1. Check available voices: `GET /api/v1/audio/voices`
2. Ensure voice_id format: `speaker_style` (e.g., `kohaku_normal`)
3. Verify speaker and style combination exists in AivisSpeech

### Empty Audio

**Problem:** Audio file generated but no sound

**Solutions:**
1. Check input text encoding (UTF-8)
2. Ensure text is not empty or whitespace-only
3. Verify AivisSpeech Engine logs: `docker logs aivis-speech-engine`

### Slow Generation

**Problem:** Audio takes too long to generate

**Solutions:**
1. Use shorter text segments
2. Reduce concurrent requests
3. Consider GPU version of AivisSpeech Engine (if available)
4. Increase CPU allocation for AivisSpeech container

---

## Advanced Configuration

### Custom Voice Mapping

Edit `open_notebook/providers/aivis_speech.py` to add custom speakers:

```python
SPEAKERS = {
    "custom_speaker": {
        "style1": 1234567890,
        "style2": 1234567891,
    },
}
```

### Speed Adjustment

Adjust speech speed (0.5 to 2.0):

```python
await AivisSpeechTTSProvider.synthesize(
    text="こんにちは",
    voice="kohaku_normal",
    speed=1.2,  # 20% faster
)
```

---

## Comparison: AivisSpeech vs Cloud TTS

| Feature | AivisSpeech | OpenAI | ElevenLabs |
|---------|-------------|---------|------------|
| **Cost** | Free | $0.015/1K chars | $0.18-0.30/1K chars |
| **Language** | Japanese | Multi | Multi |
| **Privacy** | 100% local | Cloud | Cloud |
| **Latency** | Medium | Fast | Fast |
| **Quality** | Good | Excellent | Excellent |
| **Setup** | Moderate | Easy | Easy |
| **Offline** | ✅ Yes | ❌ No | ❌ No |

---

## Performance Tips

1. **Cache Audio** - Store generated audio files for reuse
2. **Batch Processing** - Generate multiple audio files in parallel
3. **Text Segmentation** - Split long text into paragraphs
4. **Resource Limits** - Set CPU/memory limits for AivisSpeech container

```yaml
services:
  aivis-speech:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

---

## Related

- [Local TTS Setup](../5-CONFIGURATION/local-tts.md) - General local TTS guide
- [Creating Podcasts](../3-USER-GUIDE/creating-podcasts.md) - Using TTS for podcasts
- [AI Providers](../5-CONFIGURATION/ai-providers.md) - Provider configuration

---

## License

This integration is part of Open Notebook and follows the same license.

AivisSpeech Engine is licensed under LGPL-3.0.
