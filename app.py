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
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

# Global variable to prevent multiple dialog instances
dialog_active = False

# Global variable to ensure Tkinter is only used in the main thread
main_thread = threading.current_thread()

def ensure_output_dir(path):
    """Ensure the output directory exists"""
    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False
    return True

def process_video(task_id, url, output_path, format_type, duration=60, captions=True):
    """Process a YouTube video in the background and create a short."""
    try:
        task = processing_tasks[task_id]
        task['status'] = 'processing'
        task['current_stage'] = 'Initializing'
        
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
        def update_progress(progress, stage=None):
            task['progress'] = progress
            if stage:
                task['current_stage'] = stage
            logging.info(f"Task {task_id} progress: {progress}% - Stage: {task['current_stage']}")
        
        # Track processing stages
        update_progress(0, 'Starting download')
        
        # Process the video
        if processor_available:
            # Generate output filename
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            output_file = os.path.join(output_path, f"short_{timestamp}.{format_type}")
            
            try:
                # Process the video with enhanced progress tracking
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
                import traceback
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
        import traceback
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

@app.route('/home')
def home():
    return render_template('home.html')

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
        logging.info("Received form data: %s", request.form)
        
        # Extract form data
        url = request.form.get('url')
        duration_str = request.form.get('duration', '60')
        format_type = request.form.get('format', 'mp4')
        output_path = request.form.get('output_path', '')
        captions = request.form.get('captions', 'true').lower() == 'true'
        
        # Sanitize and validate the output path
        output_path = sanitize_path(output_path)
        
        logging.info("Extracted data - URL: %s, Duration: %s, Format: %s, Output Path: %s, Captions: %s", url, duration_str, format_type, output_path, captions)
        
        # Validate inputs
        if not url:
            return jsonify({'success': False, 'error': 'No URL provided'}), 400
            
        if format_type not in ['mp4', 'mkv']:
            return jsonify({'success': False, 'error': f'Invalid format: {format_type}'}), 400
        
        try:
            duration = int(duration_str)
        except ValueError:
            logging.warning("Invalid duration value: %s, defaulting to 60", duration_str)
            duration = 60
        
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'status': 'processing',
            'progress': 0,
            'url': url,
            'file_path': None,
            'error': None,
            'captions': captions
        }
        
        processing_tasks[task_id] = task
        
        # Start processing in a background thread
        threading.Thread(
            target=process_video,
            args=(task_id, url, output_path, format_type, duration, captions),
            daemon=True
        ).start()
        
        return jsonify({'success': True, 'task_id': task_id})
    except Exception as e:
        logging.error("Error in process_video route: %s", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/status/<task_id>', methods=['GET'])
def check_status(task_id):
    task = processing_tasks.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    
    response = {
        'success': True,
        'status': task['status'],
        'progress': task['progress'],
        'current_stage': task.get('current_stage', '')
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
    # Look for the task with this output file
    target_task = None
    for task_id, task in processing_tasks.items():
        if task.get('output_file') == filename:
            target_task = task
            break
    
    # If found, use its output directory, otherwise use default
    output_dir = target_task.get('output_dir', 'output') if target_task else 'output'
    
    return send_from_directory(output_dir, filename, as_attachment=True)

if __name__ == '__main__':
    print(f"ClipKart is running! Video processor is {'available' if processor_available else 'NOT available'}")
    app.run(debug=True) 