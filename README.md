# StoryTelling Videos API

A FastAPI-based backend for generating viral short-form video scripts (TikTok/YouTube Shorts) using LLMs via OpenRouter, and storing them in MongoDB.
- The prompt should generate 2 people having conversation. One person asking the questions and understanding it while another is an expertise in that subject.
- AI voice should be implemented.
The project is designed for full automation—no manual voice recording or editing required.

## Features

- **Script Generation:** Generates engaging, conversational scripts for short-form videos using LLMs.
- **Database Storage:** Stores generated scripts with metadata in MongoDB.
- **REST API:** Endpoints for generating, retrieving, and listing stories.
- **Logging:** Colorful console and file logging for easy debugging.
- **Configurable:** Environment-based settings via `.env` and Pydantic.
- **Voice Synthesis:** Automatically generate voiceovers from scripts.
- **Video Assembly:** Combine voiceovers with visuals for fully automated video creation.

## Planned Automation

- **Publishing:** (Future) Direct upload to TikTok/YouTube Shorts.

## Getting Started

### Prerequisites

- Python 3.12
- MongoDB instance
- OpenRouter API key

