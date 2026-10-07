from tracker import VideoTracker
import os

tracker = VideoTracker()
for f in os.listdir("data"):
    if f.endswith(".mp4"):
        print(f"Testing {f}")
        try:
            obs, meta = tracker.process_video(f"data/{f}")
            print(f"File {f}: {len(obs)} observations, {meta['duration']}s")
            
            # Check if event extraction works
            from events import EventEngine
            engine = EventEngine()
            events = engine.extract_events(obs)
            print(f"Events extracted: {len(events)}")
            
            # temporal graph
            from temporal_graph import TemporalGraph
            graph = TemporalGraph(events)
            print(f"Graph created: {len(graph.events)} nodes")
        except Exception as e:
            print(f"Error on {f}: {e}")
