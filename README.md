# AI-Powered Video Transcript Summarizer with Timestamps

This project automates the process of extracting subtitles from YouTube videos, formatting them with timestamps, and generating concise AI-powered summaries. It leverages advanced natural language processing models like **ChatGPT** to deliver meaningful insights into video content without requiring a full watch-through.

---

## Features

- Extracts subtitles (manual or auto-generated) from YouTube videos.
- Formats subtitles with accurate timestamps in `[hh:mm:ss - hh:mm:ss]` format.
- Summarizes the key points in the video while preserving timestamps.
- Supports multiple languages (e.g., English, auto-generated English).
- Flexible AI integration with OpenAI’s GPT models for summarization.

---

## Tech Stack

- **Python**: Core language.
- **pytube**: Extracts video details and metadata.
- **youtube-transcript-api**: Fetches video subtitles.
- **OpenAI API**: For AI-driven summarization (using GPT-3.5 or GPT-4).
- **Transformers**: Optional, for local summarization using Hugging Face models.

---

## Installation

### Prerequisites

1. **Python 3.8+**
2. Required Python libraries:
   ```bash
   pip install pytube youtube-transcript-api openai
3. Don't forget about OpenAI API key
