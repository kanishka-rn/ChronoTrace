import yt_dlp
import os
import uuid
import time
import cv2

def categorize_error(err_msg):
    err_msg = err_msg.lower()
    if "private video" in err_msg or "private" in err_msg:
        return "VIDEO_PRIVATE", "The platform reports that the video is private."
    elif "sign in" in err_msg or "login" in err_msg or "authentication" in err_msg:
        return "LOGIN_REQUIRED", "The platform reports that the video requires authentication."
    elif "unavailable" in err_msg or "not found" in err_msg or "404" in err_msg:
        return "VIDEO_UNAVAILABLE", "The video is unavailable or does not exist."
    elif "age restricted" in err_msg or "age-restricted" in err_msg:
        return "AGE_RESTRICTED", "The video is age-restricted."
    elif "geo restricted" in err_msg or "region" in err_msg or "country" in err_msg:
        return "REGION_RESTRICTED", "The video is geo-restricted in this region."
    elif "timeout" in err_msg or "timed out" in err_msg:
        return "DOWNLOAD_TIMEOUT", "Network timeout while downloading the video. Please retry."
    elif "network" in err_msg or "connection" in err_msg:
        return "NETWORK_ERROR", "A network or connection error occurred."
    elif "unsupported" in err_msg or "extractor" in err_msg:
        return "UNSUPPORTED_URL", "The provided URL is not supported by the downloader."
    elif "blocked" in err_msg or "captcha" in err_msg or "bot" in err_msg or "http error 403" in err_msg or "http error 429" in err_msg:
        return "PLATFORM_BLOCKED", "Unable to download this video because the platform temporarily restricted automated access."
    else:
        return "DOWNLOADER_ERROR", "An unexpected error occurred during download."

def validate_video_file(filepath):
    if not os.path.exists(filepath):
        return False, "File does not exist."
    if os.path.getsize(filepath) == 0:
        return False, "File size is 0 bytes."
        
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        return False, "OpenCV could not open the video file."
        
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    cap.release()
    
    if duration <= 0:
        return False, "Video duration/frame count is invalid."
    if width <= 0 or height <= 0:
        return False, "Video dimensions are invalid."
        
    return True, "Valid video."

def download_video(url, output_dir="data", max_retries=2):
    """
    Downloads video from YouTube, Instagram or supported URLs using yt-dlp.
    Returns (success, video_path, error_category, user_message, raw_error)
    """
    os.makedirs(output_dir, exist_ok=True)
    temp_id = str(uuid.uuid4())[:8]
    output_template = os.path.join(output_dir, f"dl_{temp_id}.%(ext)s")
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]/bestvideo/best',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
    }
    
    attempt = 0
    while attempt <= max_retries:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Determine filepath
                if 'requested_downloads' in info and info['requested_downloads']:
                    filepath = info['requested_downloads'][0]['filepath']
                else:
                    filepath = ydl.prepare_filename(info)
                    
                # Handle possible extension mismatch from merge_output_format
                if not os.path.exists(filepath):
                    base, ext = os.path.splitext(filepath)
                    if os.path.exists(base + ".mkv"): filepath = base + ".mkv"
                    elif os.path.exists(base + ".webm"): filepath = base + ".webm"
                    elif os.path.exists(base + ".mp4"): filepath = base + ".mp4"
                
                is_valid, val_msg = validate_video_file(filepath)
                if not is_valid:
                    return False, None, "VALIDATION_ERROR", f"Downloaded file is invalid: {val_msg}", val_msg
                    
                return True, filepath, "SUCCESS", "Download successful.", None
                
        except yt_dlp.utils.DownloadError as e:
            err_msg = str(e)
            cat, msg = categorize_error(err_msg)
            
            # Decide if we should retry
            if cat in ["DOWNLOAD_TIMEOUT", "NETWORK_ERROR"] and attempt < max_retries:
                attempt += 1
                time.sleep(2)
                continue
                
            return False, None, cat, msg, err_msg
            
        except Exception as e:
            err_msg = str(e)
            return False, None, "UNKNOWN_ERROR", "An unknown error occurred.", err_msg
            
    return False, None, "DOWNLOAD_TIMEOUT", "Exceeded maximum retries due to timeouts.", "Max retries reached"
