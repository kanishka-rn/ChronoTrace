import cv2
import numpy as np
from ultralytics import YOLO
import time

class VideoTracker:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = YOLO(model_path)
    
    def process_video(self, video_path, sample_rate_fps=3):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video {video_path}")
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        stride = max(1, int(fps / sample_rate_fps) if fps > 0 else 1)
        
        observations = []
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_idx % stride == 0:
                msec = cap.get(cv2.CAP_PROP_POS_MSEC)
                if msec > 0:
                    timestamp = msec / 1000.0
                else:
                    timestamp = frame_idx / fps if fps > 0 else 0.0
                
                results = self.model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False, classes=[0, 39, 41]) # person, bottle, cup (some objects for interaction)
                
                if results[0].boxes is not None and results[0].boxes.id is not None:
                    boxes = results[0].boxes.xyxy.cpu().numpy()
                    track_ids = results[0].boxes.id.cpu().numpy().astype(int)
                    confidences = results[0].boxes.conf.cpu().numpy()
                    classes = results[0].boxes.cls.cpu().numpy().astype(int)
                    
                    for box, track_id, conf, cls in zip(boxes, track_ids, confidences, classes):
                        x1, y1, x2, y2 = box
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2
                        
                        observations.append({
                            "timestamp": timestamp,
                            "track_id": track_id,
                            "class_name": self.model.names[cls],
                            "confidence": float(conf),
                            "bbox": [float(x1), float(y1), float(x2), float(y2)],
                            "center": [float(center_x), float(center_y)]
                        })
                        
            frame_idx += 1
            
        cap.release()
        
        metadata = {
            "filename": video_path.split("/")[-1].split("\\")[-1],
            "duration": duration,
            "fps": fps,
            "resolution": (width, height),
            "frame_count": frame_count
        }
        
        return observations, metadata
