# Video Translation and Subtitle Generator

This project uses OpenAI's Whisper model to translate a video into a specified language and generate subtitles in the SRT format. The generated subtitles can then be used in video players like VLC.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.6 or later
- `pip` (Python package installer)
- `ffmpeg`

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
Install the required dependencies:

sh
Copy code
pip install -r requirements.txt
Usage
Run the script:

sh
Copy code
python3 translate_video.py
Follow the prompts:

Enter the path to your video file.
Enter the language code for translation (e.g., nl for Dutch, fr for French).
Add subtitles to VLC:

Open VLC and play your video.
Go to Subtitle > Add Subtitle File...
Select the generated subtitles.srt file.
Example

Enter the path to the video file: /path/to/your/video.mp4
Enter the language code for translation (e.g., nl for Dutch, fr for French): nl
