from events import EventEngine
from query_engine import QueryEngine

def test_pipeline():
    observations = [
        # Frame 0 - Appear out of ROI
        {"timestamp": 0.0, "track_id": 1, "class_name": "person", "confidence": 0.9, "center_x": 50, "center_y": 50},
        # Frame 1 - Move out of ROI
        {"timestamp": 0.3, "track_id": 1, "class_name": "person", "confidence": 0.9, "center_x": 70, "center_y": 70},
        # Frame 2 - Enter ROI
        {"timestamp": 0.6, "track_id": 1, "class_name": "person", "confidence": 0.9, "center_x": 150, "center_y": 150},
        # Frame 3 - Move in ROI
        {"timestamp": 0.9, "track_id": 1, "class_name": "person", "confidence": 0.9, "center_x": 170, "center_y": 170},
        # Frame 4 - Stop in ROI
        {"timestamp": 1.2, "track_id": 1, "class_name": "person", "confidence": 0.9, "center_x": 171, "center_y": 171},
        # Frame 5 - Stop in ROI
        {"timestamp": 1.5, "track_id": 1, "class_name": "person", "confidence": 0.9, "center_x": 171, "center_y": 172},
        # Frame 6 - Stop in ROI
        {"timestamp": 1.8, "track_id": 1, "class_name": "person", "confidence": 0.9, "center_x": 172, "center_y": 171},
        # Frame 7 - Move in ROI
        {"timestamp": 2.1, "track_id": 1, "class_name": "person", "confidence": 0.9, "center_x": 200, "center_y": 200},
        # Frame 8 - Exit ROI
        {"timestamp": 2.4, "track_id": 1, "class_name": "person", "confidence": 0.9, "center_x": 50, "center_y": 50},
        # Frame 9 - Disappear (no more observations)
    ]
    
    roi = {"x_min": 100, "y_min": 100, "x_max": 300, "y_max": 300}
    engine = EventEngine(roi=roi, stop_threshold=5, move_threshold=10, time_gap_threshold=2.0)
    events = engine.extract_events(observations)
    
    print("--- EXTRACTED EVENTS ---")
    for e in events:
        print(f"{e['type']} ({e['start']:.1f} - {e['end']:.1f})")
        
    qe = QueryEngine(events)
    
    print("\n--- QUERY: How long did the person remain stationary? ---")
    res = qe.parse_query("How long did the person remain stationary?")
    print(res)
    
    print("\n--- QUERY: What happened before the person exited? ---")
    res = qe.parse_query("What happened before the person exited?")
    print(res)

if __name__ == "__main__":
    test_pipeline()
