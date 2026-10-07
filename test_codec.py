import cv2
import numpy as np

fourcc = cv2.VideoWriter_fourcc(*'vp80')
out = cv2.VideoWriter('test.webm', fourcc, 10, (640, 480))
if not out.isOpened():
    print("Failed to open vp09")
else:
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    out.write(frame)
    out.release()
    print("Success vp09")
