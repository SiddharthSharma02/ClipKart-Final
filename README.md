# ClipKart - YouTube Shorts Creator

ClipKart is a Python web application that automatically downloads YouTube videos, identifies the most interesting scenes, and creates vertical short-form videos (1080x1920) with captions. The output videos are optimized for platforms like TikTok, Instagram Reels, or YouTube Shorts and limited to 60 seconds.

## ✨ Features

- **Smart Scene Detection**: Automatically detects and selects the most engaging segments
- **Vertical Format Conversion**: Transforms landscape videos to vertical (9:16 aspect ratio)
- **Automatic Captions**: Adds captions using speech recognition
- **User-friendly Interface**: Dark-themed web interface with progress tracking
- **Customizable Settings**: Control duration, format, and caption options
- **Local Storage**: Save videos directly to your computer

## 🚀 Live Demo

Access the ClipKart app through the login page with an animated logo. You can:
- Create an account (for demo purposes)
- Login with existing credentials (for demo purposes) 
- Continue as a guest user to start creating shorts right away

## 🛠️ Installation

### Prerequisites

- Python 3.7+
- FFmpeg installed on your system

### Setup

1. Clone this repository
```bash
git clone https://github.com/SiddharthSharma02/ClipKart-Final.git
cd ClipKart-Final
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Flask web server:
```bash
python app.py
```

4. Open your browser and navigate to http://localhost:5000

## 🎬 How to Use

1. Log in or continue as a guest
2. Enter a YouTube URL in the input box
3. Set the desired duration (up to 60 seconds)
4. Choose output format (MP4 or MKV)
5. Enable/disable captions as needed
6. Click "Create Short" and wait for processing to complete
7. Download your short video when ready

## 🔍 How It Works

1. The script downloads the specified YouTube video
2. It detects scene changes and analyzes each scene for interest level based on:
   - Motion analysis
   - Visual complexity
   - Face detection
3. The best scenes are selected to fit within the time limit
4. Selected scenes are cropped to vertical format
5. Speech recognition extracts dialogue for captions
6. The final video is assembled and exported

## 📂 Project Structure

- `app.py` - Flask web application
- `youtube_short_creator_enhanced.py` - Core video processing logic
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, and images
- `downloads/` - Temporary storage for downloaded videos
- `output/` - Final destination for processed shorts

## ⚠️ Note

This tool is for personal use only. Respect copyright and terms of service for all platforms. 
This tool is for personal use only. Respect copyright and terms of service for all platforms. 