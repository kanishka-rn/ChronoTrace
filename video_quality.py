import cv2
import numpy as np

def categorize_resolution(width, height):
    pixels = width * height
    if pixels < 640 * 360:
        return "VERY_LOW"
    elif pixels < 1280 * 720:
        return "LOW"
    elif pixels < 1920 * 1080:
        return "MEDIUM"
    elif pixels < 2560 * 1440:
        return "HIGH"
    return "VERY_HIGH"

def categorize_fps(fps):
    if fps < 10:
        return "UNUSUALLY_LOW"
    elif fps < 24:
        return "LOW"
    return "ACCEPTABLE"

def calculate_blur(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def categorize_blur(blur_score):
    if blur_score < 50:
        return "VERY_BLURRY"
    elif blur_score < 100:
        return "BLURRY"
    elif blur_score < 300:
        return "MODERATE"
    return "SHARP"

def calculate_brightness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.mean(gray)

def categorize_brightness(brightness):
    if brightness < 40:
        return "DARK"
    elif brightness > 220:
        return "OVEREXPOSED"
    return "ACCEPTABLE"

def analyze_video_quality(video_path, max_frames_to_sample=10):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video for quality analysis.")
        
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    blur_scores = []
    bright_scores = []
    
    stride = max(1, frame_count // max_frames_to_sample)
    
    for i in range(max_frames_to_sample):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * stride)
        ret, frame = cap.read()
        if not ret:
            break
        blur_scores.append(calculate_blur(frame))
        bright_scores.append(calculate_brightness(frame))
        
    cap.release()
    
    mean_blur = float(np.mean(blur_scores)) if blur_scores else 0.0
    mean_bright = float(np.mean(bright_scores)) if bright_scores else 0.0
    
    res_cat = categorize_resolution(width, height)
    fps_cat = categorize_fps(fps)
    blur_cat = categorize_blur(mean_blur)
    bright_cat = categorize_brightness(mean_bright)
    
    overall_cat = "ACCEPTABLE"
    if res_cat in ["VERY_LOW", "LOW"] or fps_cat == "UNUSUALLY_LOW" or blur_cat in ["VERY_BLURRY", "BLURRY"] or bright_cat in ["DARK", "OVEREXPOSED"]:
        overall_cat = "LOW"
    if res_cat == "VERY_LOW" or blur_cat == "VERY_BLURRY":
        overall_cat = "VERY_LOW"
        
    quality_score = 1.0
    if overall_cat == "LOW": quality_score = 0.7
    elif overall_cat == "VERY_LOW": quality_score = 0.4
    
    return {
        "width": width,
        "height": height,
        "resolution_category": res_cat,
        "fps": fps,
        "fps_category": fps_cat,
        "mean_blur_score": mean_blur,
        "blur_category": blur_cat,
        "mean_brightness": mean_bright,
        "brightness_category": bright_cat,
        "overall_category": overall_cat,
        "quality_score": quality_score
    }
