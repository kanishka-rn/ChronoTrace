import cv2
import numpy as np
import os

def create_synthetic_video(output_path, duration=3.0, fps=10):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    width, height = 640, 480
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Simple circle moving
    for i in range(int(duration * fps)):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        x = min(width - 50, 50 + int(i * 10))
        cv2.circle(frame, (x, height // 2), 20, (0, 0, 255), -1)
        out.write(frame)
        
    out.release()
    print(f"Created video at {output_path}")

os.makedirs("data", exist_ok=True)
create_synthetic_video("data/test_video.mp4")
