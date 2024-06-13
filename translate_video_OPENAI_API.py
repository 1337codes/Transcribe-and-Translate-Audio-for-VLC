import whisper
import ffmpeg
import os
import openai

# Set your OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'

def extract_audio(video_path):
    audio_path = "audio.wav"
    ffmpeg.input(video_path).output(audio_path, **{'q:a': 0, 'map': 'a'}).run()
    return audio_path

def save_to_srt(transcription, srt_file):
    with open(srt_file, "w", encoding="utf-8") as f:
        for i, segment in enumerate(transcription['segments']):
            start = segment['start']
            end = segment['end']
            text = segment['text']
            start_time = format_timestamp(start)
            end_time = format_timestamp(end)
            f.write(f"{i+1}\n{start_time} --> {end_time}\n{text}\n\n")

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds * 1000) % 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def translate_text(text, target_language):
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
    # Prompt for the video file
    video_path = input("Enter the path to the video file: ")
    if not os.path.exists(video_path):
        print("Video file does not exist.")
        return

    # Prompt for the translation language
    language = input("Enter the language code for translation (e.g., nl for Dutch, fr for French): ")

    # Extract audio from video
    print("Extracting audio from video...")
    audio_path = extract_audio(video_path)

    # Load the Whisper model
    print("Loading the Whisper model...")
    model = whisper.load_model("large")

    # Transcribe the audio file
    print("Transcribing the audio...")
    result = model.transcribe(audio_path)

    # Translate each segment using OpenAI ChatGPT
    print("Translating the transcription...")
    for segment in result['segments']:
        segment['text'] = translate_text(segment['text'], language)

    # Save the translation to a subtitle file in SRT format
    srt_file = "subtitles.srt"
    save_to_srt(result, srt_file)

    print(f"Subtitle file saved as {srt_file}")

if __name__ == "__main__":
    main()
