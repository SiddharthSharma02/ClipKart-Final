import os
import time
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import tkinter as tk
from tkinter import filedialog
import uuid
import logging
import platform
import openai
from dotenv import load_dotenv
from collections import deque
import traceback

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Try importing the video processor module
try:
    import youtube_short_creator_enhanced as video_processor
    processor_available = True
except ImportError as e:
    print(f"Warning: Could not import video processor module: {e}")
    print("The application will run, but video processing functionality will be limited.")
    processor_available = False

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'output'  # Default folder
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB max upload size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Dictionary to store processing status
processing_tasks = {}

# Global variable to ensure Tkinter is only used in the main thread
main_thread = threading.current_thread()

# Add this after other global variables
chat_history = {}
MAX_HISTORY_LENGTH = 10

def process_video(task_id, url, output_path, format_type, duration=45, captions=True):
    """Process a YouTube video in the background and create a short from the first 45 seconds."""
    try:
        task = processing_tasks[task_id]
        task['status'] = 'processing'
        task['current_stage'] = 'Initializing'
        task['progress'] = 0
        
        logging.info(f"Processing task {task_id} with URL: {url}, Output: {output_path}, Format: {format_type}, Duration: {duration}, Captions: {captions}")
        
        # Ensure output directory exists
        try:
            os.makedirs(output_path, exist_ok=True)
        except (PermissionError, OSError) as e:
            logging.error(f"Cannot create output directory: {str(e)}")
            task['status'] = 'failed'
            task['error'] = f"Cannot create output directory: {str(e)}"
            return
        
        # Update task status periodically with stage information
        def update_progress(progress, stage=None, time_estimate=None):
            task['progress'] = progress
            if stage:
                task['current_stage'] = stage
            if time_estimate:
                task['time_estimate'] = time_estimate
            logging.info(f"Task {task_id} progress: {progress}% - Stage: {task['current_stage']}")
        
        # Track processing stages
        update_progress(0, 'Starting download', 'Calculating...')
        
        # Process the video
        if processor_available:
            # Generate output filename
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            output_file = os.path.join(output_path, f"short_{timestamp}.{format_type}")
            
            try:
                # Process the video with the simplified approach (first 45 seconds)
                video_processor.process_video(
                    url=url,
                    output_file=output_file,
                    duration=duration,
                    progress_callback=update_progress,
                    captions=captions
                )
                
                # Update task on completion
                task['status'] = 'completed'
                task['progress'] = 100
                task['file_path'] = output_file
                task['current_stage'] = 'Completed'
                task['time_estimate'] = 'Done!'
                
                # Generate download URL
                filename = os.path.basename(output_file)
                task['download_url'] = f'/download/{filename}'
                
                logging.info(f"Task {task_id} completed. Output file: {output_file}")
            except ValueError as e:
                # Handle specific ValueError (usually from YouTube download)
                task['status'] = 'failed'
                task['error'] = str(e)
                task['current_stage'] = 'Failed: download error'
                logging.error(f"Value error processing task {task_id}: {str(e)}")
            except Exception as e:
                task['status'] = 'failed'
                task['error'] = f"Processing error: {str(e)}"
                task['current_stage'] = 'Failed: processing error'
                logging.error(f"Error processing task {task_id}: {str(e)}")
                traceback.print_exc()
        else:
            task['status'] = 'failed'
            task['error'] = "Video processor is not available"
            task['current_stage'] = 'Failed: processor unavailable'
            logging.error("Video processor is not available")
    
    except Exception as e:
        # Handle any errors during processing
        logging.error(f"Error processing task {task_id}: {str(e)}")
        task = processing_tasks.get(task_id)
        if task:
            task['status'] = 'failed'
            task['error'] = str(e)
            task['current_stage'] = 'Failed: unexpected error'
        traceback.print_exc()

def open_folder_dialog():
    """
    Open a folder dialog and return the selected path
    Uses platform-specific approach when possible
    """
    if threading.current_thread() != main_thread:
        logging.error("Error: Folder dialogs must be opened from the main thread.")
        return None

    # Try platform-specific approach first (more reliable on Windows)
    system = platform.system()
    
    if system == 'Windows':
        try:
            # Try to import Windows-specific modules
            try:
                import win32com.client
            except ImportError:
                logging.warning("win32com module not found, skipping Windows-specific dialog")
                raise ImportError("win32com not available")
                
            # Use Windows-specific folder selection dialog
            shell = win32com.client.Dispatch("Shell.Application")
            folder = shell.BrowseForFolder(0, "Select Output Folder", 0, 0)
            
            if folder:
                folder_path = str(folder.self.path)
                logging.info(f"Selected folder using Windows API: {folder_path}")
                return folder_path
            return None
        except Exception as e:
            logging.warning(f"Windows folder dialog failed: {str(e)}, falling back to Tkinter")
    
    # Fallback to Tkinter for cross-platform support
    try:
        # On Windows, make sure the Tkinter window doesn't appear in the taskbar
        root = tk.Tk()
        root.withdraw()
        
        # Ensure the dialog appears on top of other windows
        try:
            # This works on Windows and Linux
            root.attributes('-topmost', True)
        except:
            pass  # Ignore errors on platforms where this doesn't work
        
        # Force focus to make sure dialog is visible (especially on Windows)
        root.focus_force()
        
        # Open the folder dialog
        folder_selected = filedialog.askdirectory(parent=root)
        
        # Clean up
        root.destroy()
        
        # Sometimes empty strings are returned when canceled
        if folder_selected == "":
            return None
            
        # Log success for debugging
        logging.info(f"Folder selected via Tkinter: {folder_selected}")
        return folder_selected
    except Exception as e:
        logging.error(f"Error opening folder dialog: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/navigation')
def navigation():
    return render_template('navigation.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/record')
def record():
    return render_template('record.html')

@app.route('/browse-folder', methods=['GET'])
def browse_folder():
    folder = open_folder_dialog()
    if folder:
        logging.info(f"Selected folder: {folder}")
        return jsonify({'success': True, 'folder': folder})
    else:
        # Create a default output folder as fallback
        default_folder = os.path.abspath('output')
        os.makedirs(default_folder, exist_ok=True)
        logging.warning(f"No folder selected, using default: {default_folder}")
        return jsonify({'success': True, 'folder': default_folder, 'default': True})

def sanitize_path(path):
    """
    Sanitize and validate file paths to ensure they're safe to use.
    """
    if not path:
        # If path is empty, use default 'output' directory
        return os.path.abspath('output')
    
    # Ensure the path is absolute
    abs_path = os.path.abspath(path)
    
    # Create the directory if it doesn't exist
    try:
        os.makedirs(abs_path, exist_ok=True)
        return abs_path
    except (PermissionError, OSError) as e:
        logging.error("Path validation error: %s", str(e))
        raise ValueError(f"Cannot use the specified path: {str(e)}")

@app.route('/process', methods=['POST'])
def process_video():
    try:
        # Check if a file was uploaded or a YouTube URL was provided
        uploaded_file = request.files.get('videoFile')
        youtube_url = request.form.get('youtubeUrl', '')
        
        logging.info("Process request - URL: %s, File: %s", youtube_url, 
                    uploaded_file.filename if uploaded_file and uploaded_file.filename else "None")
        
        # Extract other form data
        duration_str = request.form.get('duration', '30')
        format_type = request.form.get('format', 'mp4')
        output_path = request.form.get('output_path', '')
        captions = request.form.get('captions', 'true').lower() == 'true'
        
        # Sanitize and validate the output path
        output_path = sanitize_path(output_path or 'output')
        
        # Validate inputs
        if not youtube_url and (not uploaded_file or not uploaded_file.filename):
            return jsonify({'success': False, 'error': 'No video source provided. Please enter a YouTube URL or upload a file.'}), 400
            
        if format_type not in ['mp4', 'mov']:
            return jsonify({'success': False, 'error': f'Invalid format: {format_type}'}), 400
        
        try:
            duration = int(duration_str)
        except ValueError:
            logging.warning("Invalid duration value: %s, defaulting to 30", duration_str)
            duration = 30
        
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'status': 'processing',
            'progress': 0,
            'url': youtube_url,
            'file_path': None,
            'error': None,
            'captions': captions,
            'is_upload': bool(uploaded_file and uploaded_file.filename)
        }
        
        processing_tasks[task_id] = task
        
        # If it's a file upload, save the file first
        upload_path = None
        if uploaded_file and uploaded_file.filename:
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(output_path, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save the uploaded file
            filename = secure_filename(uploaded_file.filename)
            upload_path = os.path.join(upload_dir, f"{task_id}_{filename}")
            uploaded_file.save(upload_path)
            
            # Store the path in the task
            task['upload_path'] = upload_path
        
        # Start processing in a background thread
        threading.Thread(
            target=process_video_task,
            args=(task_id, youtube_url, upload_path, output_path, format_type, duration, captions),
            daemon=True
        ).start()
        
        return jsonify({'success': True, 'task_id': task_id})
    except Exception as e:
        logging.error("Error in process_video route: %s", str(e))
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

def process_video_task(task_id, url, upload_path, output_path, format_type, duration=30, captions=True):
    """Process a video in the background from either a YouTube URL or uploaded file."""
    try:
        task = processing_tasks[task_id]
        task['status'] = 'processing'
        task['current_stage'] = 'Initializing'
        task['progress'] = 0
        
        logging.info(f"Processing task {task_id} - URL: {url}, Upload path: {upload_path}, Output: {output_path}")
        
        # Ensure output directory exists
        try:
            os.makedirs(output_path, exist_ok=True)
        except (PermissionError, OSError) as e:
            logging.error(f"Cannot create output directory: {str(e)}")
            task['status'] = 'failed'
            task['error'] = f"Cannot create output directory: {str(e)}"
            return
        
        # Update task status periodically with stage information
        def update_progress(progress, stage=None, time_estimate=None):
            task['progress'] = progress
            if stage:
                task['current_stage'] = stage
            if time_estimate:
                task['time_estimate'] = time_estimate
            logging.info(f"Task {task_id} progress: {progress}% - Stage: {task['current_stage']}")
        
        # Generate output filename
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_file = os.path.join(output_path, f"short_{timestamp}.{format_type}")
        
        # Process the video based on source
        if processor_available:
            try:
                if upload_path:
                    # Process uploaded file
                    update_progress(10, 'Processing uploaded file', 'Calculating...')
                    video_processor.process_local_video(
                        video_path=upload_path,
                        output_file=output_file,
                        duration=duration,
                        progress_callback=update_progress,
                        captions=captions
                    )
                else:
                    # Process YouTube URL - Use the new implementation
                    update_progress(10, 'Starting download', 'Calculating...')
                    video_processor.create_short_from_youtube(
                        url=url,
                        output_file=output_file,
                        duration=duration,
                        progress_callback=update_progress,
                        captions=captions
                    )
                
                # Update task on completion
                task['status'] = 'completed'
                task['progress'] = 100
                task['file_path'] = output_file
                task['current_stage'] = 'Completed'
                task['time_estimate'] = 'Done!'
                
                # Generate download URL
                filename = os.path.basename(output_file)
                task['download_url'] = f'/download/{filename}'
                
                logging.info(f"Task {task_id} completed. Output file: {output_file}")
                
            except ValueError as e:
                # Handle specific ValueError
                task['status'] = 'failed'
                task['error'] = str(e)
                task['current_stage'] = 'Failed: processing error'
                logging.error(f"Value error processing task {task_id}: {str(e)}")
            
            except Exception as e:
                task['status'] = 'failed'
                task['error'] = f"Processing error: {str(e)}"
                task['current_stage'] = 'Failed: processing error'
                logging.error(f"Error processing task {task_id}: {str(e)}")
                traceback.print_exc()
                
            finally:
                # Clean up uploaded file if needed
                if upload_path and os.path.exists(upload_path):
                    try:
                        os.remove(upload_path)
                        logging.info(f"Removed temporary upload file: {upload_path}")
                    except Exception as e:
                        logging.warning(f"Could not remove upload file {upload_path}: {str(e)}")
        else:
            task['status'] = 'failed'
            task['error'] = "Video processor is not available"
            task['current_stage'] = 'Failed: processor unavailable'
            logging.error("Video processor is not available")
    
    except Exception as e:
        # Handle any errors during processing
        logging.error(f"Error processing task {task_id}: {str(e)}")
        task = processing_tasks.get(task_id)
        if task:
            task['status'] = 'failed'
            task['error'] = str(e)
            task['current_stage'] = 'Failed: unexpected error'
        traceback.print_exc()

@app.route('/status/<task_id>', methods=['GET'])
def check_status(task_id):
    task = processing_tasks.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    
    response = {
        'success': True,
        'status': task['status'],
        'progress': task['progress'],
        'current_stage': task.get('current_stage', ''),
        'time_estimate': task.get('time_estimate', 'Calculating...')
    }
    
    # Add additional info depending on status
    if task['status'] == 'completed':
        response['file_path'] = task['file_path']
        response['download_url'] = task.get('download_url', '')
    elif task['status'] == 'failed':
        response['error'] = task['error']
    
    return jsonify(response)

@app.route('/download/<filename>')
def download(filename):
    """
    Route to download processed videos
    """
    try:
        # Look for the task with this filename
        task_id = None
        file_path = None
        
        for task_id, task in processing_tasks.items():
            if task.get('file_path') and os.path.basename(task.get('file_path')) == filename:
                file_path = task.get('file_path')
                break
        
        if not file_path:
            # If not found in tasks, check the default output directory
            file_path = os.path.join('output', filename)
            if not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
                
        # Get the directory from the file path
        directory = os.path.dirname(file_path)
        
        # Check if directory exists
        if not os.path.exists(directory):
            return jsonify({'error': 'Directory not found'}), 404
            
        # Send the file for download
        logging.info(f"Sending file for download: {file_path}")
        return send_from_directory(directory, os.path.basename(file_path), as_attachment=True)
        
    except Exception as e:
        logging.error(f"Error in download route: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
            
        # Initialize or get chat history for this session
        if session_id not in chat_history:
            chat_history[session_id] = deque(maxlen=MAX_HISTORY_LENGTH)
            
        # Create a system message that sets the context for the AI
        system_message = """You are a content creation assistant for ClipKart, a YouTube Shorts creation tool. 
        Your role is to help users create better short-form content by providing:
        1. Video ideas and concepts
        2. Tips for engaging short-form content
        3. Suggestions for video editing and pacing
        4. Help with content strategy
        5. Advice on trending topics and formats
        
        Keep your responses:
        - Concise and practical
        - Focused on short-form video content
        - Actionable with specific tips
        - Friendly and encouraging
        - Formatted with bullet points or numbered lists when appropriate
        
        If the user asks about video processing or technical aspects of the tool, explain how ClipKart works:
        - It takes the first 45 seconds of any YouTube video
        - Converts it to vertical format (9:16)
        - Can add captions automatically
        - Supports MP4 and MOV output formats
        
        Always maintain a helpful and enthusiastic tone, and provide specific examples when possible."""
        
        # Prepare messages array with system message and chat history
        messages = [{"role": "system", "content": system_message}]
        
        # Add chat history
        for msg in chat_history[session_id]:
            messages.append(msg)
            
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Update chat history
        chat_history[session_id].append({"role": "user", "content": user_message})
        chat_history[session_id].append({"role": "assistant", "content": ai_response})
        
        return jsonify({
            'response': ai_response,
            'session_id': session_id
        })
        
    except openai.error.AuthenticationError:
        logging.error("OpenAI API authentication failed")
        return jsonify({'error': 'API authentication failed. Please check your API key.'}), 500
    except openai.error.RateLimitError:
        logging.error("OpenAI API rate limit exceeded")
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500

if __name__ == '__main__':
    print(f"ClipKart is running! Video processor is {'available' if processor_available else 'NOT available'}")
    app.run(debug=True) 