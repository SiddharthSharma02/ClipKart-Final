# ClipKart - YouTube Shorts Creator

ClipKart is a Python web application that automatically downloads YouTube videos and creates vertical short-form videos (1080x1920) with captions from the first 45 seconds. The output videos are optimized for platforms like TikTok, Instagram Reels, or YouTube Shorts.

## ✨ Features

- **Simple Extraction**: Takes the first 45 seconds of any YouTube video
- **Vertical Format Conversion**: Transforms landscape videos to vertical (9:16 aspect ratio)
- **Automatic Captions**: Adds captions using speech recognition
- **User-friendly Interface**: Dark-themed web interface with progress tracking
- **Customizable Settings**: Control output format and caption options
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
3. Choose output format (MP4 or MKV)
4. Enable/disable captions as needed
5. Click "Create Short" and wait for processing to complete
6. Download your short video when ready

## 🔍 How It Works

1. The application downloads the specified YouTube video
2. It takes the first 45 seconds of the video
3. The video is cropped to vertical format (9:16 aspect ratio)
4. Speech recognition extracts dialogue for captions
5. The final video is assembled and exported

## 📂 Project Structure

- `app.py` - Flask web application
- `youtube_short_creator_enhanced.py` - Core video processing logic
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, and images
- `downloads/` - Temporary storage for downloaded videos
- `output/` - Final destination for processed shorts

## ⚠️ Note

This tool is for personal use only. Respect copyright and terms of service for all platforms. 