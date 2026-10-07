import os
from tracker import VideoTracker
from events import EventEngine
from query_engine import QueryEngine
from evidence import create_evidence_clip

def test_full_pipeline():
    video_path = "data/test_video.mp4"
    print("Loading tracker...")
    tracker = VideoTracker('yolov8n.pt')
    
    print("Processing video...")
    obs, meta = tracker.process_video(video_path, sample_rate_fps=3)
    print(f"Observations: {len(obs)}, Meta: {meta}")
    
    print("Extracting events...")
    roi = {"x_min": 100, "y_min": 100, "x_max": 800, "y_max": 600}
    engine = EventEngine(roi=roi, stop_threshold=10, move_threshold=15, time_gap_threshold=2.0)
    events = engine.extract_events(obs)
    print(f"Extracted {len(events)} events.")
    
    print("Querying...")
    qe = QueryEngine(events)
    res = qe.parse_query("What happened in chronological order?")
    print("Order result:", res['status'])
    
    # Try evidence creation
    if events:
        try:
            create_evidence_clip(video_path, 0.0, 1.0, "evidence/clips/test_clip.mp4")
            print("Evidence clip created successfully.")
        except Exception as e:
            print("Failed to create evidence clip:", e)
    else:
        print("No events to create evidence for.")
        # Test it anyway
        create_evidence_clip(video_path, 0.0, 1.0, "evidence/clips/test_clip.mp4")
        print("Evidence clip created successfully (forced).")

if __name__ == "__main__":
    test_full_pipeline()
