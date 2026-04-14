from flask import Flask, request, jsonify
from flask_cors import CORS
from pytubefix import YouTube
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins != "*":
    allowed_origins = [origin.strip() for origin in allowed_origins.split(",")]

CORS(app, resources={r"/*": {"origins": allowed_origins}})


import ffmpeg

def download_video(url, resolution):
    try:
        yt = YouTube(url)
        out_dir = f"./downloads/{yt.video_id}"
        os.makedirs(out_dir, exist_ok=True)

        # 1. Try progressive streams (Video + Audio combined, usually up to 720p)
        stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=resolution).first()
        
        if stream:
            print(f"Downloading progressive stream: {resolution}")
            stream.download(output_path=out_dir)
            return True, None
        
        # 2. Try adaptive streams (High quality video only, needs merging with audio)
        video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', resolution=resolution, type="video").first()
        
        if video_stream:
            print(f"Downloading adaptive video stream: {resolution}")
            audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()
            
            if not audio_stream:
                return False, "Could not find a suitable audio stream for merging."

            # Download video and audio files separately
            video_path = video_stream.download(output_path=out_dir, filename_prefix="video_")
            audio_path = audio_stream.download(output_path=out_dir, filename_prefix="audio_")
            
            # Merge files using ffmpeg
            output_filename = f"{yt.title} {resolution}.mp4".replace("/", "_").replace("\\", "_")
            output_path = os.path.join(out_dir, output_filename)
            
            try:
                video_input = ffmpeg.input(video_path)
                audio_input = ffmpeg.input(audio_path)
                ffmpeg.output(video_input, audio_input, output_path, vcodec='copy', acodec='aac', strict='experimental').overwrite_output().run(quiet=True)
                
                # Cleanup temporary files
                os.remove(video_path)
                os.remove(audio_path)
                return True, None
            except ffmpeg.Error as e:
                return False, f"FFmpeg merge failed. Ensure FFmpeg is installed on your system. Error: {str(e)}"
        
        return False, f"Resolution {resolution} not found in progressive or adaptive streams."

    except Exception as e:
        return False, str(e)

def get_video_info(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.first()
        video_info = {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "description": yt.description,
            "publish_date": yt.publish_date,
        }
        return video_info, None
    except Exception as e:
        return None, str(e)

def is_valid_youtube_url(url):
    pattern = r"^(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+(&\S*)?$"
    return re.match(pattern, url) is not None

import threading
import uuid

# Task tracking
tasks = {}

def download_video_task(task_id, url, resolution):
    tasks[task_id] = {"status": "downloading", "message": "Download started"}
    try:
        success, error_message = download_video(url, resolution)
        if success:
            tasks[task_id] = {"status": "completed", "message": f"Video with resolution {resolution} downloaded successfully."}
        else:
            tasks[task_id] = {"status": "failed", "error": error_message}
    except Exception as e:
        tasks[task_id] = {"status": "failed", "error": str(e)}

@app.route('/download/<resolution>', methods=['POST'])
def download_by_resolution(resolution):
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400
    
    task_id = str(uuid.uuid4())
    thread = threading.Thread(target=download_video_task, args=(task_id, url, resolution))
    thread.start()
    
    return jsonify({
        "task_id": task_id,
        "message": "Download started in the background.",
        "status_url": f"/status/{task_id}"
    }), 202

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found."}), 404
    return jsonify(task), 200

@app.route('/video_info', methods=['POST'])
def video_info():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400
    
    video_info, error_message = get_video_info(url)
    
    if video_info:
        return jsonify(video_info), 200
    else:
        return jsonify({"error": error_message}), 500


@app.route('/available_resolutions', methods=['POST'])
def available_resolutions():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400
    
    try:
        yt = YouTube(url)
        progressive_resolutions = list(set([
            stream.resolution 
            for stream in yt.streams.filter(progressive=True, file_extension='mp4')
            if stream.resolution
        ]))
        all_resolutions = list(set([
            stream.resolution 
            for stream in yt.streams.filter(file_extension='mp4')
            if stream.resolution
        ]))
        return jsonify({
            "progressive": sorted(progressive_resolutions),
            "all": sorted(all_resolutions)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    app.run(host='0.0.0.0', port=port, debug=debug)


