# StoryTelling Videos API

A fully automated FastAPI-based backend for generating viral short-form videos (TikTok/YouTube Shorts/Instagram Reels) from text prompts. The system generates engaging conversational scripts using LLMs, synthesizes natural AI voices, creates word-level subtitles, and assembles final videos—all without manual intervention.

## 🎯 Overview

This project automates the entire video creation pipeline:
1. **Story Generation** - LLM creates conversational scripts (interviewer + expert format)
2. **TTS Audio** - Kokoro synthesizes natural voices with GPU acceleration
3. **Word-Level Subtitles** - WhisperX generates precise word-timing SRT files
4. **Video Assembly** - MoviePy combines audio, subtitles, and stock footage
5. **Publishing** - Direct upload to TikTok (future integration)

**Zero manual work required** - from prompt to published video.

## ✨ Features

### Core Functionality
- **LLM-Powered Script Generation** - OpenRouter integration for diverse models (Claude, GPT-4, etc.)
- **Natural AI Voices** - Kokoro TTS with GPU acceleration for fast synthesis
- **Precise Word-Level Subtitles** - WhisperX with automatic alignment
- **Automated Video Creation** - MoviePy integration with stock video support
- **Complete REST API** - All features exposed as endpoints

### Performance & Architecture
- **GPU Acceleration** - CUDA support for TTS (Kokoro) and subtitle generation (WhisperX)
- **Lazy Model Loading** - Models loaded once and cached for efficiency
- **Smart Caching** - Skips regeneration if files already exist
- **Comprehensive Logging** - Colorful console + file logging with detailed pipeline tracking
- **MongoDB Integration** - Store stories and metadata

### Configuration
- **Environment-based Settings** - `.env` support via Pydantic
- **Flexible Voice Options** - Multiple Kokoro voices
- **Customizable Speech Speed** - Adjustable audio playback speed
- **Model Selection** - Choose whisper models (tiny, base, small, medium, large)

## 📋 API Endpoints

### Story & Content Generation
```
POST /stories/generate_script
  - Generate conversational scripts from topics
  - Stores in MongoDB
  - Returns: script_uuid, story_content

GET /stories/{script_uuid}
  - Retrieve stored story by UUID

GET /stories
  - List all stored stories
```

### Audio & Subtitles
```
POST /tts/generate_tts?script_uuid=<uuid>
  - Generate TTS audio from script
  - Output: final.wav
  - Device: GPU (if available)

POST /srt/generate_srt?script_uuid=<uuid>&model_name=tiny
  - Generate word-level SRT subtitles
  - Output: full_sub_words.srt
  - Device: GPU (if available)
```

### Video Generation
```
POST /videos/generate_video?script_uuid=<uuid>&stock_video_path=<optional>
  - Assemble final video with audio + subtitles
  - Output: {script_uuid}.mp4
  - Device: CPU (MoviePy limitation)
```

### Complete Pipeline
```
POST /pipeline/orchestrate?prompt=<topic>&model=<llm_model>&voice=am_liam&whisper_model=tiny&speed=1.0
  - End-to-end workflow in one call
  - Generates story → TTS → SRT → Video
  - Returns all file paths and content
```

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API Framework** | FastAPI | REST endpoints & async support |
| **LLM Integration** | OpenRouter | Access to multiple language models |
| **Text-to-Speech** | Kokoro (82M) | Natural voice synthesis |
| **Speech-to-Text** | WhisperX | Word-level subtitle generation |
| **Video Assembly** | MoviePy | Audio/video/subtitle compositing |
| **Database** | MongoDB | Script and metadata storage |
| **Acceleration** | PyTorch + CUDA | GPU support for ML models |
| **Logging** | Python logging | Detailed pipeline tracking |

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.12+
CUDA 12.x (optional, for GPU acceleration)
MongoDB instance
OpenRouter API key
```

### Installation

```bash
# Clone repository
git clone <repo-url>
cd storytelling_videos

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model for Kokoro
python -m spacy download en_core_web_sm
```

### Configuration

Create `.env` file:
```env
OPENROUTER_API_KEY=your_api_key_here
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=storytelling_videos
LOG_LEVEL=INFO
```

### Running the Server

```bash
# Development
uvicorn storytelling_videos.main:app --reload

# Production
uvicorn storytelling_videos.main:app --host 0.0.0.0 --port 8000
```

Server runs on `http://localhost:8000`

API documentation available at `http://localhost:8000/docs`

## 📁 Project Structure

```
storytelling_videos/
├── core/                          # Configuration & initialization
│   ├── config_core.py            # Pydantic settings from .env
│   ├── loggings.py               # Logger setup
│   ├── mongodb_core.py           # MongoDB connection
│   └── openrouter_core.py        # OpenRouter client initialization
│
├── models/                        # Data models
│   ├── database_schema.py        # MongoDB schemas
│   └── __init__.py               # Pydantic models
│
├── repositories/                  # Database access
│   └── mongodb_repo.py           # MongoDB CRUD operations
│
├── services/                      # Business logic
│   ├── openrouter_service.py     # LLM story generation
│   ├── voice_kokoro_service.py   # TTS synthesis (GPU)
│   ├── whisperx_service.py       # SRT generation (GPU)
│   ├── video_gen_service.py      # Video assembly (CPU)
│   ├── pipeline_service.py       # Orchestration logic
│   └── preprocess_text_service.py # Text preprocessing
│
├── routers/                       # API endpoints
│   ├── _base.py                  # Router registration
│   ├── orchestrate_router.py     # Complete pipeline endpoint
│   ├── kokoro_tts_router.py      # TTS endpoint
│   ├── srt_router.py             # SRT generation endpoint
│   ├── video_gen_router.py       # Video generation endpoint
│   └── mongo_router.py           # Story CRUD endpoints
│
└── main.py                        # FastAPI application entry point
```

## 💻 Usage Examples

### 1. Complete Pipeline (Recommended)

```bash
curl -X POST "http://localhost:8000/pipeline/orchestrate?prompt=Why%20is%20the%20sky%20blue&model=claude-3.5-sonnet&voice=am_liam&whisper_model=tiny"
```

Response:
```json
{
  "status": "success",
  "script_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "story_content": "Interviewer: Why is the sky blue?...",
  "audio_path": "/saved_audio_kokoro/.../final.wav",
  "srt_path": "/saved_audio_kokoro/.../full_sub_words.srt",
  "video_path": "/output/550e8400-e29b-41d4-a716-446655440000.mp4"
}
```

### 2. Step-by-Step Pipeline

```bash
# Step 1: Generate story
curl -X POST "http://localhost:8000/stories/generate_script?topic=machine%20learning"

# Step 2: Generate TTS
curl -X POST "http://localhost:8000/tts/generate_tts?script_uuid=<uuid>"

# Step 3: Generate SRT
curl -X POST "http://localhost:8000/srt/generate_srt?script_uuid=<uuid>"

# Step 4: Generate video
curl -X POST "http://localhost:8000/videos/generate_video?script_uuid=<uuid>"
```

## ⚙️ Performance Optimization

### GPU vs CPU Usage

| Component | Recommended | Speed Improvement |
|-----------|-------------|-------------------|
| **Kokoro TTS** | GPU | 3-5x faster |
| **WhisperX SRT** | GPU | 4-8x faster |
| **MoviePy Video** | CPU | N/A (no GPU support) |

**Result:** ~60% faster pipeline with GPU

### Caching Strategy

- **Audio files** - Cached as `final.wav`, skips regeneration
- **SRT files** - Cached as `full_sub_words.srt`, skips transcription
- **Models** - Lazy-loaded and cached in memory (loaded once)
- **GPU memory** - Cleared between major steps for efficiency

## 📊 File Structure

Generated files organized by script_uuid:

```
saved_audio_kokoro/
└── {script_uuid}/
    ├── final.wav              # Generated TTS audio
    └── full_sub_words.srt     # Word-level subtitles

output/
└── {script_uuid}.mp4          # Final video

mongodb/
└── stories collection         # Script metadata & content
```

## 🔧 Configuration Options

### OpenRouter Models

Available via OpenRouter (update in API calls):
- `claude-3.5-sonnet`
- `gpt-4-turbo`
- `gemini-2.0-flash`
- Many others...

### Kokoro Voices

- `am_liam` (default)
- `af_sarah`
- `am_michael`
- `af_luna`

### Whisper Models

- `tiny` (fastest, lower accuracy)
- `base`
- `small`
- `medium`
- `large` (slowest, highest accuracy)

## 🚧 Planned Features

- [ ] **TikTok Direct Upload** - Automated publishing
- [ ] **Multi-platform Support** - YouTube Shorts, Instagram Reels
- [ ] **Analytics Dashboard** - Video performance tracking
- [ ] **Batch Processing** - Generate multiple videos in parallel
- [ ] **Advanced Scheduling** - Schedule posts for optimal engagement
- [ ] **Custom Branding** - Logo, watermarks, intro/outro sequences
- [ ] **A/B Testing** - Auto-generate variants for comparison

## 📝 Logging

Logs are stored in `logs` directory with both console and file output:

```
logs/
├── app.log                       # Main application log
```

Enable debug logging via `.env`:
```env
LOG_LEVEL=DEBUG
```

## 🐛 Troubleshooting

### GPU Not Detected
```python
# Check CUDA availability
import torch
print(torch.cuda.is_available())  # Should return True
print(torch.cuda.get_device_name(0))
```

### MongoDB Connection Issues
```bash
# Verify MongoDB is running
mongosh --eval "db.adminCommand('ping')"
```

### Out of Memory
- Reduce batch size in WhisperX settings
- Use smaller Whisper model (`tiny` instead of `large`)
- Process videos sequentially instead of parallel

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please ensure:
- Code follows existing style
- All endpoints documented
- GPU/CPU usage optimized
- Comprehensive logging added

## 📞 Support

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ for automated content creation**
