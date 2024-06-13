import os
import subprocess
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from openai import OpenAI
import whisper
from ratelimit import limits, sleep_and_retry
from tqdm import tqdm
import torch
import moviepy.editor as mp
import srt
from datetime import timedelta

# Constants
THREE_REQUESTS_PER_MINUTE = 3
ONE_MINUTE = 60

# Ensure the API key is set
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("Error: The OPENAI_API_KEY environment variable is not set.")
    exit(1)

client = OpenAI(api_key=api_key)

# Functions
@sleep_and_retry
@limits(calls=THREE_REQUESTS_PER_MINUTE, period=ONE_MINUTE)
def check_openai_api():
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "This is a test."}]
        )
        print("OpenAI API key is valid.")
        return True
    except Exception as e:
        print(f"OpenAI API key validation failed: {e}")
        return False

def install_whisper():
    print("Installing Whisper and dependencies...")
    commands = [
        ["pip", "install", "-U", "openai-whisper"],
        ["sudo", "apt", "update"],
        ["sudo", "apt", "install", "-y", "ffmpeg"]
    ]
    for command in commands:
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute {command}: {e}")
            exit(1)
    print("Whisper installation complete.")

def convert_video_to_audio(video_file, output_format='mp3'):
    video = mp.VideoFileClip(video_file)
    audio_file = video_file.replace(video_file.split('.')[-1], output_format)
    video.audio.write_audiofile(audio_file)
    return audio_file

def translate_with_whisper(file_path, model_size="base"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model(model_size).to(device)
    result = model.transcribe(file_path)
    return result

def translate_text(text, target_language):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Translate the following text to {target_language}."},
            {"role": "user", "content": text}
        ]
    )
    translated_text = response.choices[0].message['content'].strip()
    return translated_text

def select_video_file():
    Tk().withdraw()  # Close the root window
    file_path = askopenfilename(filetypes=[("Video files", "*.mp4 *.flv *.mkv *.avi *.mov")])
    return file_path

def create_srt(transcription, translated_text, output_file):
    segments = transcription['segments']
    subtitles = []
    for i, segment in enumerate(segments):
        start = timedelta(seconds=segment['start'])
        end = timedelta(seconds=segment['end'])
        content = translated_text[i] if i < len(translated_text) else ""
        subtitle = srt.Subtitle(index=i, start=start, end=end, content=content)
        subtitles.append(subtitle)
    srt_content = srt.compose(subtitles)
    with open(output_file, 'w') as f:
        f.write(srt_content)

def main():
    if check_openai_api():
        print("Using OpenAI API for translation.")
    else:
        print("Falling back to using Whisper for translation.")
        install_whisper()

    video_file = select_video_file()
    if not video_file:
        print("No video file selected. Exiting.")
        exit(1)

    print(f"Selected video file: {video_file}")
    
    print("Converting video to audio...")
    audio_file = convert_video_to_audio(video_file)
    print(f"Audio file created: {audio_file}")

    print("Transcribing audio with Whisper...")
    transcription = translate_with_whisper(audio_file, model_size="base")
    transcribed_text = transcription['text']
    segments = transcription['segments']
    print(f"Transcribed text: {transcribed_text}")

    target_language = input("Enter the target language for translation (e.g., 'Dutch', 'English'): ").strip()
    print(f"Translating text to {target_language}...")
    translated_text = translate_text(transcribed_text, target_language)
    print(f"Translated text: {translated_text}")

    srt_file = video_file.replace(video_file.split('.')[-1], 'srt')
    create_srt(transcription, translated_text.split('\n'), srt_file)
    print(f"Subtitle file created: {srt_file}")

if __name__ == "__main__":
    main()
