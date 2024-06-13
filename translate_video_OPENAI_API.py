import whisper
import ffmpeg
import os
import readline
from autocorrect import Speller
import glob
import time
import openai
import warnings

# Set your OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Suppress the specific warning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

def extract_audio(video_path):
    video_dir, video_name = os.path.split(video_path)
    audio_name = os.path.splitext(video_name)[0] + ".wav"
    audio_path = os.path.join(video_dir, audio_name)
    print(f"Extracting audio from the video to {audio_path}...")
    start_time = time.time()
    ffmpeg.input(video_path).output(audio_path, **{'q:a': 0, 'map': 'a'}).run()
    end_time = time.time()
    print(f"Audio extracted and saved to {audio_path}. Time taken: {end_time - start_time:.2f} seconds.")
    return audio_path

def save_to_srt(transcription, srt_file):
    print("Saving transcription to SRT file...")
    start_time = time.time()
    with open(srt_file, "w", encoding="utf-8") as f:
        for i, segment in enumerate(transcription['segments']):
            start = segment['start']
            end = segment['end']
            text = segment['text']
            start_time_code = format_timestamp(start)
            end_time_code = format_timestamp(end)
            f.write(f"{i+1}\n{start_time_code} --> {end_time_code}\n{text}\n\n")
    end_time = time.time()
    print(f"Transcription saved to {srt_file}. Time taken: {end_time - start_time:.2f} seconds.")

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds * 1000) % 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def complete_path(text, state):
    return (glob.glob(text + '*') + [None])[state]

def transcribe_audio(model, audio_path):
    print("Transcribing the audio...")
    start_time = time.time()
    result = model.transcribe(audio_path)
    end_time = time.time()
    print(f"Audio transcribed. Time taken: {end_time - start_time:.2f} seconds.")
    return result

def translate_text(text, target_language):
    print(f"Translating text to {target_language}...")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Translate the following text to {target_language}."},
            {"role": "user", "content": text}
        ]
    )
    translated_text = response.choices[0].message['content'].strip()
    return translated_text

def main():
    spell = Speller(lang='en')
    readline.set_completer(complete_path)
    readline.parse_and_bind('tab: complete')
    
    # Prompt for the video file
    video_path = input(f"Enter the path to the video file (current directory: {os.getcwd()}): ")
    corrected_video_path = spell(video_path)
    
    if not os.path.exists(corrected_video_path):
        print("Video file does not exist.")
        return
    
    # Prompt for the translation language
    language = input("Enter the language code for translation (e.g., nl for Dutch, fr for French, en for English): ")

    # Extract audio from video
    audio_path = extract_audio(corrected_video_path)

    try:
        # Load the Whisper model
        print("Loading the Whisper model (large)... This might take a while.")
        model = whisper.load_model("large")
    except MemoryError:
        print("MemoryError: Switching to smaller model...")
        model = whisper.load_model("small")

    # Transcribe the audio file
    result = transcribe_audio(model, audio_path)

    # Translate each segment using OpenAI ChatGPT
    for segment in result['segments']:
        segment['text'] = translate_text(segment['text'], language)

    # Save the translation to a subtitle file in SRT format
    video_dir, video_name = os.path.split(corrected_video_path)
    srt_file = os.path.join(video_dir, os.path.splitext(video_name)[0] + ".srt")
    save_to_srt(result, srt_file)

    print(f"Subtitle file saved as {srt_file}")

if __name__ == "__main__":
    main()
