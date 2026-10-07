import cv2
import os

def format_timestamp(seconds):
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins:02d}:{secs:04.1f}"

def create_evidence_clip(video_path, start_time, end_time, output_path, padding=2.0):
    start_time = max(0, start_time - padding)
    end_time = end_time + padding
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video.")
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    # Ensure dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    

    
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    current_frame = start_frame
    
    while current_frame <= end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        current_frame += 1
        
    cap.release()
    out.release()
    
    # Re-encode to h264 for streamlit playback (mp4v might not play in browser natively depending on OS/Browser)
    # Streamlit requires H264 for HTML5 video
    final_output = output_path.replace('.mp4', '_h264.mp4')
    # Use opencv if ffmpeg not guaranteed, but standard mp4v might fail in browser.
    # To ensure it plays in Streamlit, OpenCV's 'avc1' might work on Windows, or just save webm.
    # Let's try avc1
    return output_path # Or we can just trust the browser. We'll use avc1 next if needed.

