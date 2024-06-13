# Video Translation and Subtitle Generator

Translate videos to subtitles using Whisper and OpenAI GPT-4.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set API key: `export OPENAI_API_KEY="your-api-key"`
3. Run: `python3 translate_video.py`

This script will allow you to:

Select a video file
Convert the video to an audio file
Transcribe the audio using Whisper
Translate the transcribed text to a chosen language using OpenAI API
Export the translated text to a .srt file for subtitles

**OFFLINE mode when disabling internet**
