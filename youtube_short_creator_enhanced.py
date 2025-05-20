import logging
import tempfile
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, ColorClip, AudioFileClip
from pytubefix import YouTube
import numpy as np
import cv2
from google.cloud import videointelligence
import io
import time
import json
import logging
import os
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_youtube_video(url):
    logging.info(f"Downloading video from {url}...")
    #Getting the OS PATH
    temp_dir = tempfile.mkdtemp()

    #Checking if the URL is valid
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video_id}"

    yt = YouTube(url)

    # Add an event handler for on_progress_callback
    yt.register_on_progress_callback(lambda stream, chunk, bytes_remaining: 
                        logging.debug(f"Downloaded {stream.filesize - bytes_remaining} of {stream.filesize} bytes"))

    # Get the highest quality progressive stream
    streams = yt.streams.filter(progressive=True, file_extension='mp4')
    if not streams:
        raise ValueError("No suitable video streams found for this YouTube video.")
        
    video = streams.order_by('resolution').desc().first()

    if not video:
        raise ValueError("Could not find a suitable video format to download.")

    cap = caption.generate_srt_captions()
    cap.splitlines()
    











    # """
    # Download a YouTube video and return the path to the downloaded file
    # Handles errors and provides progress updates
    # """
    # logging.info(f"Downloading video from {url}...")
    
    # # Create a temporary directory to store the video
    # temp_dir = tempfile.mkdtemp()
    
    # try:
    #     # Validate the URL
    #     if not url or "youtube.com" not in url and "youtu.be" not in url:
    #         raise ValueError("Invalid YouTube URL. Please provide a valid YouTube video URL.")
        
    #     # Clean the URL (remove unnecessary parameters)
    #     if "youtube.com/watch?v=" in url:
    #         video_id = url.split("youtube.com/watch?v=")[1].split("&")[0]
    #         # url = f"https://www.youtube.com/watch?v={video_id}"
    #         url = video_id
    #     elif "youtu.be/" in url:
    #         video_id = url.split("youtu.be/")[1].split("?")[0]
    #         url = f"https://www.youtube.com/watch?v={video_id}"
            
    #     # Extract video ID to verify it exists
    #     try:
    #         yt = YouTube(url)
            
    #         # Add an event handler for on_progress_callback
    #         yt.register_on_progress_callback(lambda stream, chunk, bytes_remaining: 
    #                          logging.debug(f"Downloaded {stream.filesize - bytes_remaining} of {stream.filesize} bytes"))
            
    #         # Get the highest quality progressive stream
    #         streams = yt.streams.filter(progressive=True, file_extension='mp4')
    #         if not streams:
    #             raise ValueError("No suitable video streams found for this YouTube video.")
                
    #         video = streams.order_by('resolution').desc().first()
            
    #         if not video:
    #             raise ValueError("Could not find a suitable video format to download.")
            
    #         # Download the video with the title as the filename
    #         logging.info(f"Downloading: {yt.title} (Quality: {video.resolution}, Size: {video.filesize_mb:.1f}MB)")
    #         video_path = video.download(output_path=temp_dir)
            
    #         logging.info(f"Video downloaded to {video_path}")
    #         return video_path
    #     except Exception as e:
    #         if "HTTP Error 400" in str(e):
    #             raise ValueError(f"YouTube rejected the request. The video might be age-restricted, private, or unavailable in your region. Try a different video.")
    #         elif "Video unavailable" in str(e):
    #             raise ValueError(f"This video is unavailable. It might have been removed or set to private.")
    #         elif "This video is age restricted" in str(e):
    #             raise ValueError(f"This video is age-restricted and cannot be downloaded.")
    #         else:
    #             raise ValueError(f"Failed to download YouTube video: {str(e)}")
            
    # except Exception as e:
    #     logging.error(f"Error downloading YouTube video: {str(e)}")
    #     raise ValueError(f"Failed to download YouTube video: {str(e)}")

# def find_scenes_with_google_ai(video_path, output_json=None):
#     """
#     Analyze video using Google Video Intelligence API
#     Returns list of scenes with timestamps and labels
#     """
#     print("Starting Google Video Intelligence analysis...")
    
#     # Initialize the client
#     client = videointelligence.VideoIntelligenceServiceClient()
    
#     # Read the video file
#     with io.open(video_path, "rb") as f:
#         input_content = f.read()
    
#     # Configure the request
#     features = [
#         videointelligence.Feature.SHOT_CHANGE_DETECTION,
#         videointelligence.Feature.LABEL_DETECTION,
#         videointelligence.Feature.OBJECT_TRACKING,
#         videointelligence.Feature.SPEECH_TRANSCRIPTION
#     ]
    
#     speech_config = videointelligence.SpeechTranscriptionConfig(
#         language_code="en-US",
#         enable_automatic_punctuation=True,
#     )
    
#     video_context = videointelligence.VideoContext(
#         speech_transcription_config=speech_config
#     )
    
#     print("Sending video to Google for analysis (this may take several minutes)...")
    
#     # Start the asynchronous request
#     operation = client.annotate_video(
#         request={
#             "features": features,
#             "input_content": input_content,
#             "video_context": video_context,
#         }
#     )
    
#     print("Waiting for operation to complete...")
#     result = operation.result(timeout=300)  # 5-minute timeout
    
#     # Process shot changes (scene boundaries)
#     shot_changes = result.annotation_results[0].shot_annotations
#     scene_boundaries = []
#     for shot in shot_changes:
#         start_time = shot.start_time_offset.seconds + shot.start_time_offset.microseconds / 1000000
#         end_time = shot.end_time_offset.seconds + shot.end_time_offset.microseconds / 1000000
#         scene_boundaries.append((start_time, end_time))
    
#     # Process labels and objects for scene scoring
#     scene_data = []
#     for i, (start_time, end_time) in enumerate(scene_boundaries):
#         scene_info = {
#             'start': start_time,
#             'end': end_time,
#             'duration': end_time - start_time,
#             'labels': [],
#             'objects': [],
#             'speech': []
#         }
        
#         # Add labels for this time segment
#         for label in result.annotation_results[0].segment_label_annotations:
#             for segment in label.segments:
#                 seg_start = segment.segment.start_time_offset.seconds + segment.segment.start_time_offset.microseconds / 1000000
#                 seg_end = segment.segment.end_time_offset.seconds + segment.segment.end_time_offset.microseconds / 1000000
                
#                 # Check if this label overlaps with the scene
#                 if (seg_start <= end_time and seg_end >= start_time):
#                     scene_info['labels'].append({
#                         'description': label.entity.description,
#                         'confidence': segment.confidence
#                     })
        
#         # Add objects for this time segment
#         for obj in result.annotation_results[0].object_annotations:
#             for frame in obj.frames:
#                 frame_time = frame.time_offset.seconds + frame.time_offset.microseconds / 1000000
                
#                 # Check if this object appears in the scene
#                 if start_time <= frame_time <= end_time:
#                     if any(o['description'] == obj.entity.description for o in scene_info['objects']):
#                         continue  # Object already added
                        
#                     scene_info['objects'].append({
#                         'description': obj.entity.description,
#                         'confidence': frame.confidence
#                     })
        
#         # Add speech transcription if available
#         if hasattr(result.annotation_results[0], 'speech_transcriptions'):
#             for transcript in result.annotation_results[0].speech_transcriptions:
#                 for alternative in transcript.alternatives:
#                     for word in alternative.words:
#                         word_start = word.start_time.seconds + word.start_time.microseconds / 1000000
#                         word_end = word.end_time.seconds + word.end_time.microseconds / 1000000
                        
#                         # Check if this word is in the scene
#                         if start_time <= word_start <= end_time:
#                             if not scene_info['speech']:
#                                 scene_info['speech'] = alternative.transcript
#                             break
        
#         scene_data.append(scene_info)
    
#     # Save analysis to a JSON file if requested
#     if output_json:
#         with open(output_json, 'w') as f:
#             json.dump(scene_data, f, indent=2)
    
#     print(f"Google analysis complete. Found {len(scene_boundaries)} scenes.")
#     return scene_boundaries, scene_data

# def find_scenes(video_path):
#     """Fallback method to find scenes using local processing (PySceneDetect)"""
#     print("Using local scene detection...")
    
#     # Create video manager and scene manager
#     video_manager = VideoManager([video_path])
#     scene_manager = SceneManager()
#     scene_manager.add_detector(ContentDetector(threshold=30.0))
    
#     # Start video manager
#     video_manager.start()
    
#     # Detect scenes
#     scene_manager.detect_scenes(frame_source=video_manager)
    
#     # Get scene boundaries
#     scene_list = scene_manager.get_scene_list()
    
#     # Convert scene list to timestamp format
#     scene_boundaries = []
#     for scene in scene_list:
#         start_time = scene[0].get_seconds()
#         end_time = scene[1].get_seconds()
#         scene_boundaries.append((start_time, end_time))
    
#     video_manager.release()
#     return scene_boundaries

# def calculate_scene_interest(video_path, scene_boundaries, scene_data=None):
#     """
#     Calculate how interesting each scene is based on Google AI results and visual analysis
#     Returns a score for each scene
#     """
#     print("Calculating scene interest scores...")
    
#     video = VideoFileClip(video_path)
#     scene_scores = []
    
#     # If we have Google AI data, use it for enhanced scoring
#     if scene_data:
#         for i, scene_info in enumerate(scene_data):
#             start, end = scene_info['start'], scene_info['end']
            
#             # Base score
#             base_score = 0.5
            
#             # Duration factor - prefer scenes between 3-10 seconds
#             duration = end - start
#             duration_score = 1.0
#             if duration < 1.0:
#                 duration_score = 0.3
#             elif duration < 3.0:
#                 duration_score = 0.7
#             elif duration > 15.0:
#                 duration_score = 0.6
            
#             # Label score - reward scenes with interesting labels
#             interesting_keywords = [
#                 'action', 'dance', 'amazing', 'awesome', 'beautiful', 
#                 'exciting', 'funny', 'happy', 'interesting', 'dramatic',
#                 'emotional', 'shocking', 'surprising', 'highlight', 'event',
#                 'sports', 'game', 'music', 'performance', 'speech'
#             ]
            
#             label_score = 0.0
#             for label in scene_info['labels']:
#                 base_label_score = label['confidence']
#                 # Boost score for interesting labels
#                 for keyword in interesting_keywords:
#                     if keyword in label['description'].lower():
#                         base_label_score *= 1.5
#                 label_score = max(label_score, base_label_score)
            
#             # Object score - reward scenes with people, animals, or interesting objects
#             interesting_objects = [
#                 'person', 'people', 'face', 'dog', 'cat', 'animal',
#                 'car', 'vehicle', 'food', 'ball', 'sports equipment', 
#                 'musical instrument'
#             ]
            
#             object_score = 0.0
#             for obj in scene_info['objects']:
#                 base_obj_score = obj['confidence']
#                 # Boost score for interesting objects
#                 for keyword in interesting_objects:
#                     if keyword in obj['description'].lower():
#                         base_obj_score *= 1.5
#                 object_score = max(object_score, base_obj_score)
            
#             # Speech score - reward scenes with speech
#             speech_score = 0.5
#             if scene_info['speech']:
#                 speech_score = 1.0
            
#             # Calculate total score with weights
#             total_score = (
#                 base_score * 0.1 +
#                 duration_score * 0.2 +
#                 label_score * 0.3 +
#                 object_score * 0.3 +
#                 speech_score * 0.1
#             )
            
#             scene_scores.append(total_score)
#     else:
#         # Fallback to basic scoring if no Google AI data
#         for i, (start, end) in enumerate(scene_boundaries):
#             scene = video.subclip(start, end)
#             duration = end - start
            
#             # Simple motion detection on a few frames
#             frames = list(scene.iter_frames(fps=1))
#             motion_score = 0.5  # Default score
            
#             if len(frames) > 1:
#                 diffs = []
#                 for j in range(1, len(frames)):
#                     # Convert to grayscale and calculate difference
#                     prev_gray = cv2.cvtColor(frames[j-1], cv2.COLOR_RGB2GRAY)
#                     curr_gray = cv2.cvtColor(frames[j], cv2.COLOR_RGB2GRAY)
#                     diff = np.mean(cv2.absdiff(prev_gray, curr_gray))
#                     diffs.append(diff)
                
#                 # Normalize motion score
#                 if diffs:
#                     motion_score = min(1.0, sum(diffs) / (len(diffs) * 255))
            
#             # Duration factor
#             duration_score = 1.0
#             if duration < 1.0:
#                 duration_score = 0.3
#             elif duration < 3.0:
#                 duration_score = 0.7
#             elif duration > 15.0:
#                 duration_score = 0.6
            
#             # Calculate total score
#             total_score = motion_score * 0.7 + duration_score * 0.3
#             scene_scores.append(total_score)
    
#     return scene_scores

# def add_captions_to_clip(clip, scene_data):
#     """
#     Add captions to a video clip based on speech data from Google AI analysis
    
#     Args:
#         clip (VideoClip): The video clip to add captions to
#         scene_data (dict): Scene data containing speech information
        
#     Returns:
#         VideoClip: Clip with captions added
#     """
#     # If no speech data is available, return the original clip
#     if not scene_data or 'speech' not in scene_data or not scene_data['speech']:
#         print("No speech data available for captions")
#         return clip
    
#     speech_text = scene_data['speech']
    
#     # Create text clip with modern caption styling
#     text_clip = TextClip(
#         speech_text,
#         font='Arial-Bold',
#         fontsize=32,
#         color='white',
#         bg_color='black',
#         align='center',
#         method='caption',
#         size=(clip.w * 0.8, None)  # Width at 80% of video width with auto height
#     )
    
#     # Position the text at the bottom with padding
#     text_clip = text_clip.set_position(('center', 'bottom')).set_duration(clip.duration)
    
#     # Add a semi-transparent background for better readability
#     text_bg = TextClip(
#         " " * len(speech_text),
#         font='Arial-Bold',
#         fontsize=32,
#         bg_color='black',
#         color='black',
#         align='center',
#         method='caption',
#         size=(clip.w * 0.8, None)
#     ).set_opacity(0.6).set_position(('center', 'bottom')).set_duration(clip.duration)
    
#     # Composite the clips (background, video, text)
#     return CompositeVideoClip([clip, text_bg, text_clip])

# def create_vertical_video(video_path, selected_scenes, output_path, add_captions=True):
#     """
#     Create a vertical video from selected scenes with captions
    
#     Args:
#         video_path (str): Path to the input video
#         selected_scenes (list): List of (start_time, end_time) tuples for selected scenes
#         output_path (str): Path to save the output video
#         add_captions (bool): Whether to add captions to the video
        
#     Returns:
#         str: Path to the output video file
#     """
#     print("Creating vertical video with captions...")
    
#     # Load the video
#     video = VideoFileClip(video_path)
    
#     # Extract scene clips and add captions
#     clips = []
#     for i, (start_time, end_time, scene_data) in enumerate(selected_scenes):
#         # Extract the scene
#         scene_clip = video.subclip(start_time, end_time)
        
#         # Convert to vertical format (9:16 aspect ratio)
#         scene_height = scene_clip.h
#         target_width = int(scene_height * 9 / 16)
        
#         # Create a background clip (black)
#         bg_clip = ColorClip(size=(target_width, scene_height), color=(0, 0, 0))
#         bg_clip = bg_clip.set_duration(scene_clip.duration)
        
#         # Center crop and resize the video
#         if scene_clip.w > target_width:
#             # Calculate the crop window
#             x_center = scene_clip.w / 2
#             x1 = int(max(0, x_center - target_width / 2))
#             # Crop the video
#             scene_clip = scene_clip.crop(x1=x1, width=target_width)
#         else:
#             # Scale the video to fit the target width
#             scene_clip = scene_clip.resize(width=target_width)
        
#         # Set the position to center
#         scene_clip = scene_clip.set_position('center')
        
#         # Create a composite clip
#         composite_clip = CompositeVideoClip([bg_clip, scene_clip])
        
#         # Add captions if available and requested
#         if add_captions and scene_data and 'speech' in scene_data:
#             composite_clip = add_captions_to_clip(composite_clip, scene_data)
        
#         clips.append(composite_clip)
    
#     # Concatenate all clips
#     final_clip = concatenate_videoclips(clips)
    
#     # Write the output file
#     final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
    
#     # Close all clips to free resources
#     final_clip.close()
#     for clip in clips:
#         clip.close()
#     video.close()
    
#     return output_path

# def select_best_scenes(scene_boundaries, scene_scores, target_duration, include_scene_data=None):
#     """
#     Select the best scenes based on scores to fit the target duration
    
#     Args:
#         scene_boundaries (list): List of (start_time, end_time) tuples for scenes
#         scene_scores (list): List of scores for each scene
#         target_duration (int): Target duration in seconds
#         include_scene_data (list): Optional data about each scene for captions
        
#     Returns:
#         list: List of selected scenes with (start_time, end_time, scene_data) tuples
#     """
#     print(f"Selecting best scenes for {target_duration} second video...")
    
#     # Sort scenes by score (highest first)
#     scene_indices = sorted(range(len(scene_scores)), key=lambda i: scene_scores[i], reverse=True)
    
#     # Calculate durations for each scene
#     scene_durations = [scene_boundaries[i][1] - scene_boundaries[i][0] for i in range(len(scene_boundaries))]
    
#     # Select scenes until we reach the target duration
#     selected_scenes = []
#     current_duration = 0
    
#     for i in scene_indices:
#         start_time, end_time = scene_boundaries[i]
#         duration = scene_durations[i]
        
#         # Skip very short scenes (less than 1 second)
#         if duration < 1.0:
#             continue
            
#         # Add the scene if it doesn't exceed the target duration too much
#         if current_duration + duration <= target_duration * 1.1:  # Allow 10% extra
#             # Include scene data if available
#             scene_data = None
#             if include_scene_data and i < len(include_scene_data):
#                 scene_data = include_scene_data[i]
                
#             selected_scenes.append((start_time, end_time, scene_data))
#             current_duration += duration
            
#             # Break if we've reached the target duration
#             if current_duration >= target_duration:
#                 break
    
#     # Sort selected scenes by time (start_time)
#     selected_scenes.sort(key=lambda x: x[0])
    
#     print(f"Selected {len(selected_scenes)} scenes with total duration of {current_duration:.1f} seconds")
#     return selected_scenes

# def analyze_video(url, output_path, format='mp4', duration=60):
#     """
#     Full pipeline: download, analyze, and create a vertical short from a YouTube video
#     """
#     # Download the video
#     video_path = download_youtube_video(url)
    
#     try:
#         # Try Google AI analysis first
#         scene_boundaries, scene_data = find_scenes_with_google_ai(video_path)
#     except Exception as e:
#         print(f"Google AI analysis failed: {e}. Using fallback method.")
#         scene_boundaries = find_scenes(video_path)
#         scene_data = None
    
#     # Calculate interest scores
#     scene_scores = calculate_scene_interest(video_path, scene_boundaries, scene_data)
    
#     # Select the best scenes
#     selected_scenes = select_best_scenes(scene_boundaries, scene_scores, duration, scene_data)
    
#     # Create the final video
#     output_filename = f"clipkart_{int(time.time())}.{format}"
#     output_path_full = os.path.join(output_path, output_filename)
#     create_vertical_video(video_path, selected_scenes, output_path_full, add_captions=True)
    
#     return output_path_full

# def generate_captions_with_whisper(video_path, progress_callback=None):
#     """
#     Generate captions using OpenAI's Whisper model
    
#     Args:
#         video_path (str): Path to the video file
#         progress_callback (function): Optional callback to report progress
        
#     Returns:
#         list: List of caption dictionaries with text, start and end times
#     """
#     try:
#         import whisper
        
#         if progress_callback:
#             progress_callback(72, "Extracting audio for captions")
        
#         # Extract audio from video to a temporary file
#         temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
#         temp_audio_path = temp_audio.name
#         temp_audio.close()
        
#         # Extract audio using moviepy
#         audio_clip = AudioFileClip(video_path)
#         audio_clip.write_audiofile(temp_audio_path, verbose=False, logger=None)
#         audio_clip.close()
        
#         if progress_callback:
#             progress_callback(75, "Generating captions with Whisper")
        
#         # Load Whisper model (using the smallest model for speed)
#         model = whisper.load_model("tiny")
        
#         # Transcribe audio
#         result = model.transcribe(temp_audio_path)
        
#         # Format captions
#         captions = []
#         for segment in result["segments"]:
#             caption = {
#                 "text": segment["text"].strip(),
#                 "start": segment["start"],
#                 "end": segment["end"]
#             }
#             captions.append(caption)
        
#         # Clean up temporary file
#         os.remove(temp_audio_path)
        
#         return captions
#     except Exception as e:
#         print(f"Error generating captions with Whisper: {e}")
#         return []

# def process_video(url, output_file='short_video.mp4', duration=30, progress_callback=None, captions=True):
#     """
#     Process a YouTube video to create a short-form clip with the first 30 seconds
#     Simplified version with faster processing
    
#     Args:
#         url (str): YouTube URL to process
#         output_file (str): Path to save the output file
#         duration (int): Target duration in seconds (default: 30)
#         progress_callback (function): Optional callback to report progress percentage
#         captions (bool): Whether to add captions to the video (simplified in this version)
        
#     Returns:
#         str: Path to the output video file
#     """
#     try:
#         # Report starting progress
#         if progress_callback:
#             progress_callback(5, "Starting download")
        
#         # Download the video
#         video_path = download_youtube_video(url)
#         if not video_path:
#             raise ValueError("Failed to download video")
            
#         if progress_callback:
#             progress_callback(30, "Download complete")
            
#         # Load the video
#         logging.info(f"Loading video from {video_path}")
#         if progress_callback:
#             progress_callback(40, "Loading video")
            
#         clip = VideoFileClip(video_path)
        
#         # Take the first 30 seconds (or duration)
#         if clip.duration > duration:
#             if progress_callback:
#                 progress_callback(50, "Trimming video")
#             clip = clip.subclip(0, duration)
        
#         if progress_callback:
#             progress_callback(60, "Creating vertical format")
            
#         # Convert to vertical format (9:16 aspect ratio)
#         # Calculate crop dimensions to achieve 9:16 ratio
#         target_aspect = 9/16  # vertical aspect ratio
        
#         # Get original dimensions
#         w, h = clip.size
        
#         # Calculate new width to achieve target aspect ratio
#         new_w = int(h * target_aspect)
        
#         # Center crop
#         if new_w < w:
#             # Crop width to achieve vertical aspect ratio
#             x1 = (w - new_w) // 2
#             x2 = x1 + new_w
#             cropped_clip = clip.crop(x1=x1, y1=0, x2=x2, y2=h)
#         else:
#             # If video is already narrower than 9:16, add black bars
#             cropped_clip = clip
            
#         if progress_callback:
#             progress_callback(70, "Processing completed")
            
#         # Add captions if requested
#         if captions:
#             # Generate captions using Whisper
#             caption_data = generate_captions_with_whisper(video_path, progress_callback)
            
#             if caption_data:
#                 # Create TextClip objects for each caption
#                 txt_clips = []
                
#                 for caption in caption_data:
#                     txt_clip = TextClip(
#                         caption["text"], 
#                         fontsize=24, 
#                         color='white',
#                         bg_color='rgba(0,0,0,0.5)',
#                         stroke_color='black',
#                         stroke_width=1,
#                         method='caption',
#                         size=(cropped_clip.w - 40, None),
#                         font='Arial-Bold'
#                     )
                    
#                     # Position at the bottom and set time
#                     txt_clip = txt_clip.set_position(('center', 'bottom')).set_start(caption["start"]).set_duration(caption["end"] - caption["start"])
#                     txt_clips.append(txt_clip)
                
#                 # Add all caption clips to the video
#                 final_clip = CompositeVideoClip([cropped_clip] + txt_clips)
#             else:
#                 # Fallback if captions generation fails
#                 final_clip = cropped_clip
#         else:
#             final_clip = cropped_clip
            
#         if progress_callback:
#             progress_callback(85, "Exporting video")
        
#         # Export the final video
#         logging.info(f"Exporting video to {output_file}")
#         final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
        
#         if progress_callback:
#             progress_callback(100, "Complete")
            
#         return output_file
        
#     except Exception as e:
#         logging.error(f"Error processing video: {e}")
#         raise e

# def process_local_video(video_path, output_file='short_video.mp4', duration=30, progress_callback=None, captions=True):
#     """
#     Process a local video file to create a short-form clip
    
#     Args:
#         video_path (str): Path to the local video file
#         output_file (str): Path to save the output file
#         duration (int): Target duration in seconds (default: 30)
#         progress_callback (function): Optional callback to report progress percentage
#         captions (bool): Whether to add captions to the video
        
#     Returns:
#         str: Path to the output video file
#     """
#     try:
#         if not os.path.exists(video_path):
#             raise ValueError(f"Video file not found: {video_path}")
            
#         # Report starting progress
#         if progress_callback:
#             progress_callback(10, "Loading video file")
        
#         logging.info(f"Processing local video: {video_path}")
            
#         # Load the video
#         clip = VideoFileClip(video_path)
        
#         if progress_callback:
#             progress_callback(30, "Video loaded successfully")
            
#         # Take the first 30 seconds (or duration)
#         if clip.duration > duration:
#             if progress_callback:
#                 progress_callback(40, "Trimming video")
#             clip = clip.subclip(0, duration)
        
#         if progress_callback:
#             progress_callback(50, "Creating vertical format")
            
#         # Convert to vertical format (9:16 aspect ratio)
#         # Calculate crop dimensions to achieve 9:16 ratio
#         target_aspect = 9/16  # vertical aspect ratio
        
#         # Get original dimensions
#         w, h = clip.size
        
#         # Calculate new width to achieve target aspect ratio
#         new_w = int(h * target_aspect)
        
#         # Center crop
#         if new_w < w:
#             # Crop width to achieve vertical aspect ratio
#             x1 = (w - new_w) // 2
#             x2 = x1 + new_w
#             cropped_clip = clip.crop(x1=x1, y1=0, x2=x2, y2=h)
#         else:
#             # If video is already narrower than 9:16, add black bars
#             cropped_clip = clip
            
#         if progress_callback:
#             progress_callback(60, "Format conversion completed")
            
#         # Add captions if requested
#         if captions:
#             if progress_callback:
#                 progress_callback(70, "Generating captions")
                
#             # Generate captions using Whisper
#             caption_data = generate_captions_with_whisper(video_path, progress_callback)
            
#             if caption_data:
#                 # Create TextClip objects for each caption
#                 txt_clips = []
                
#                 for caption in caption_data:
#                     txt_clip = TextClip(
#                         caption["text"], 
#                         fontsize=24, 
#                         color='white',
#                         bg_color='rgba(0,0,0,0.5)',
#                         stroke_color='black',
#                         stroke_width=1,
#                         method='caption',
#                         size=(cropped_clip.w - 40, None),
#                         font='Arial-Bold'
#                     )
                    
#                     # Position at the bottom and set time
#                     txt_clip = txt_clip.set_position(('center', 'bottom')).set_start(caption["start"]).set_duration(caption["end"] - caption["start"])
#                     txt_clips.append(txt_clip)
                
#                 # Add all caption clips to the video
#                 final_clip = CompositeVideoClip([cropped_clip] + txt_clips)
#             else:
#                 # Fallback if captions generation fails
#                 final_clip = cropped_clip
#         else:
#             final_clip = cropped_clip
            
#         if progress_callback:
#             progress_callback(80, "Exporting video")
        
#         # Export the final video
#         logging.info(f"Exporting video to {output_file}")
#         final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
        
#         if progress_callback:
#             progress_callback(100, "Complete")
            
#         # Clean up
#         clip.close()
#         if final_clip != cropped_clip:
#             cropped_clip.close()
#         final_clip.close()
            
#         return output_file
        
#     except Exception as e:
#         logging.error(f"Error processing local video: {e}")
#         raise e

# if __name__ == "__main__":
#     # Example usage
#     url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
#     output_path = "output"
#     analyze_video(url, output_path, format='mp4', duration=60) 

def create_short_from_youtube(url, output_file='short_video.mp4', duration=45, progress_callback=None, captions=True):
    """
    Creates a short vertical video from a YouTube URL with captions
    Based on the test_editing.ipynb workflow
    
    Args:
        url (str): YouTube URL to process
        output_file (str): Path to save the output file
        duration (int): Target duration in seconds (default: 45)
        progress_callback (function): Optional callback to report progress percentage
        captions (bool): Whether to add captions to the video
        
    Returns:
        str: Path to the output video file
    """
    try:
        # Report starting progress
        if progress_callback:
            progress_callback(5, "Starting download")
        
        # Create temporary directory for processing
        temp_dir = os.path.dirname(output_file)
        if not temp_dir:
            temp_dir = "videos"
        
        os.makedirs(temp_dir, exist_ok=True)
        
        logging.info(f"Processing YouTube URL: {url}")
        logging.info(f"Output file: {output_file}")
        
        # Download the YouTube video
        yt = YouTube(url)
        
        if progress_callback:
            progress_callback(10, "Getting video information")
        
        # Download video and audio separately for best quality
        try:
            video_stream = yt.streams.filter(res="1080p", mime_type="video/mp4").first()
            if not video_stream:
                # Fallback to the highest resolution available
                video_stream = yt.streams.filter(mime_type="video/mp4").order_by('resolution').desc().first()
                
            audio_stream = yt.streams.filter(only_audio=True).first()
            
            if not video_stream or not audio_stream:
                raise ValueError("Could not find suitable video and audio streams.")
            
            if progress_callback:
                progress_callback(20, "Downloading video")
            
            # Download video and audio to temp directory
            video_path = os.path.join(temp_dir, "temp_video.mp4")
            audio_path = os.path.join(temp_dir, "temp_audio.mp4")
            
            video_stream.download(output_path=temp_dir, filename="temp_video.mp4")
            
            if progress_callback:
                progress_callback(30, "Downloading audio")
                
            audio_stream.download(output_path=temp_dir, filename="temp_audio.mp4")
            
            # Merge video and audio
            if progress_callback:
                progress_callback(40, "Merging video and audio")
                
            merged_path = os.path.join(temp_dir, "temp_merged.mp4")
            
            os.system(f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 "{merged_path}" -y -loglevel quiet')
            
            if progress_callback:
                progress_callback(50, "Processing captions")
            
            # Get captions
            caption_data = []
            try:
                # Try to get captions from YouTube
                try:
                    caption = yt.captions['a.en']
                except:
                    try:
                        caption = yt.captions.get_by_language_code('en')
                    except:
                        # Try other available captions
                        if yt.captions:
                            caption = list(yt.captions.values())[0]
                        else:
                            caption = None
                
                if caption and captions:
                    srt_captions = caption.generate_srt_captions()
                    
                    # Parse SRT captions
                    def parse_srt(srt_text):
                        blocks = srt_text.strip().split("\n\n")
                        parsed_captions = []
                        
                        for block in blocks:
                            lines = block.split("\n")
                            if len(lines) >= 3:
                                index = int(lines[0])
                                time_range = lines[1]
                                text = " ".join(lines[2:])
                                parsed_captions.append((index, time_range, text))
                        
                        return parsed_captions
                    
                    captions_list = parse_srt(srt_captions)
                    
                    # Convert time format from SRT to seconds
                    def srt_to_seconds(time_str):
                        h, m, s = time_str.split(":")
                        s, ms = s.split(",")
                        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
                    
                    formatted_captions = []
                    for index, time_range, text in captions_list:
                        start, end = time_range.split(" --> ")
                        start_time = srt_to_seconds(start)
                        end_time = srt_to_seconds(end)
                        formatted_captions.append((start_time, end_time, text))
                    
                    caption_data = formatted_captions
            except Exception as e:
                logging.warning(f"Error getting captions: {str(e)}")
                caption_data = []
            
            if progress_callback:
                progress_callback(60, "Creating short video")
            
            # Load the video
            video = VideoFileClip(merged_path)
            
            # Trim to desired duration
            if video.duration > duration:
                video = video.subclip(0, duration)
            
            # Create text clips for captions
            text_clips = []
            if captions and caption_data:
                for start, end, text in caption_data:
                    # Skip captions beyond the video duration
                    if start >= video.duration:
                        continue
                    
                    # Adjust end time if it exceeds video duration
                    if end > video.duration:
                        end = video.duration
                    
                    txt_clip = TextClip(
                        text, 
                        fontsize=40, 
                        color='white', 
                        bg_color='rgba(0,0,0,0.5)',
                        stroke_color='black',
                        stroke_width=1,
                        method='caption',
                        size=(video.w * 0.8, None),
                        font='Arial-Bold'
                    )
                    
                    txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(end - start).set_start(start)
                    text_clips.append(txt_clip)
            
            # Overlay text on video
            if text_clips:
                video_with_captions = CompositeVideoClip([video] + text_clips)
            else:
                video_with_captions = video
            
            if progress_callback:
                progress_callback(70, "Converting to vertical format")
            
            # Get original dimensions
            w, h = video_with_captions.size
            
            # Calculate crop dimensions for square (center crop)
            square_size = min(w, h)
            x_center = w // 2
            y_center = h // 2
            
            # Crop to square
            square_video = video_with_captions.crop(
                width=square_size,
                height=square_size,
                x_center=x_center,
                y_center=y_center
            )
            
            # Calculate padding to achieve 9:16 aspect ratio (vertical)
            target_width = 1080
            target_height = 1920
            scale_factor = target_width / square_size
            
            # Resize the square video to target width
            resized_video = square_video.resize(width=target_width)
            
            # Add black bars on top and bottom
            padding = (target_height - target_width) // 2
            video_with_bars = resized_video.margin(top=padding, bottom=padding, color=(0, 0, 0))
            
            if progress_callback:
                progress_callback(80, "Exporting final video")
            
            # Save the final video
            video_with_bars.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24)
            
            # Clean up temporary files
            for file_path in [video_path, audio_path, merged_path]:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
            
            if progress_callback:
                progress_callback(100, "Complete")
                
            return output_file
            
        except Exception as e:
            logging.error(f"Error processing video: {str(e)}")
            if progress_callback:
                progress_callback(0, f"Error: {str(e)}")
            raise e
            
    except Exception as e:
        logging.error(f"Error creating short from YouTube: {str(e)}")
        if progress_callback:
            progress_callback(0, f"Error: {str(e)}")
        raise e

def process_video(url, output_file='short_video.mp4', duration=45, progress_callback=None, captions=True):
    """
    Process a YouTube video to create a short.
    This is a wrapper around the create_short_from_youtube function for compatibility.
    """
    return create_short_from_youtube(url, output_file, duration, progress_callback, captions) 