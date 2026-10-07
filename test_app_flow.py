import time
import json
from tracker import VideoTracker
from events import EventEngine
from video_quality import analyze_video_quality
from accuracy_validator import calculate_analysis_confidence
from temporal_graph import TemporalGraph
from query_engine import QueryEngine

def test_full_flow(video_path):
    print(f"Testing full flow on {video_path}")
    tracker = VideoTracker('yolov8n.pt')
    
    q_metrics = analyze_video_quality(video_path)
    print("Quality metrics done")
    
    observations, metadata = tracker.process_video(video_path, sample_rate_fps=15) # higher sample rate to get ~559
    print(f"Tracking done: {len(observations)} observations")
    
    roi = {"x_min": 0, "y_min": 0, "x_max": 2000, "y_max": 2000}
    event_engine = EventEngine(roi=roi)
    events = event_engine.extract_events(observations)
    print(f"Event extraction done: {len(events)} events")
    
    overall_conf, conf_details = calculate_analysis_confidence(observations, events, q_metrics)
    print(f"Confidence done: {overall_conf}")
    
    graph = TemporalGraph(events)
    print(f"Graph done: {len(graph.events)} nodes")
    
    engine = QueryEngine(events, observations)
    res = engine.parse_query("currently moving", current_timestamp=5.0)
    print(f"Query done: {res['intent']}")

if __name__ == "__main__":
    test_full_flow("data/dl_11999b32.mp4")
