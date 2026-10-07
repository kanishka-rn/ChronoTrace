import os
import json
from events import EventEngine, get_observation_center
from query_engine import QueryEngine
from accuracy_validator import evaluate_ground_truth
from scene_state import get_scene_state, get_person_journey

def test_ground_truth_accuracy():
    ground_truth = {"events": [{"type": "ENTER", "start": 0.5, "end": 0.5}, {"type": "STOP", "start": 1.2, "end": 1.8}, {"type": "EXIT", "start": 2.4, "end": 2.4}]}
    predicted_events = [
        {"id": "1", "type": "APPEAR", "track_id": 1, "start": 0.0, "end": 0.0, "object": "person"},
        {"id": "2", "type": "ENTER", "track_id": 1, "start": 0.6, "end": 0.6, "object": "person"},
        {"id": "3", "type": "STOP", "track_id": 1, "start": 1.2, "end": 1.8, "object": "person"},
        {"id": "4", "type": "EXIT", "track_id": 1, "start": 2.4, "end": 2.4, "object": "person"}
    ]
    metrics = evaluate_ground_truth(predicted_events, ground_truth)
    assert metrics is not None
    assert metrics['precision'] > 0.7
    assert metrics['timestamp_mae'] < 0.2
    print("[PASS] Ground truth accuracy")

def test_query_engine_expanded():
    predicted_events = [
        {"id": "1", "type": "APPEAR", "track_id": 1, "start": 0.0, "end": 0.0, "object": "person"},
        {"id": "3", "type": "STOP", "track_id": 1, "start": 1.2, "end": 1.8, "object": "person"},
    ]
    obs = [{"timestamp": 0.0, "track_id": 1, "class_name": "person", "confidence": 0.9, "center": [100, 100], "bbox": [50, 50, 150, 150]}]
    engine = QueryEngine(predicted_events, obs)
    
    res = engine.parse_query("currently moving", 1.5)
    assert res['intent'] == 'CURRENT_STATE'
    print("[PASS] Expanded Query Engine - CURRENT_STATE")
    
def test_scene_state():
    predicted_events = [
        {"id": "1", "type": "APPEAR", "track_id": 1, "start": 0.0, "end": 0.0, "object": "person"},
        {"id": "2", "type": "STOP", "track_id": 1, "start": 1.0, "end": 5.0, "object": "person"},
        {"id": "3", "type": "DISAPPEAR", "track_id": 1, "start": 10.0, "end": 10.0, "object": "person"},
    ]
    scene = get_scene_state(2.0, [], predicted_events)
    assert scene['people_count'] == 1
    assert scene['stationary_count'] == 1
    print("[PASS] Scene State calculations")

def test_person_journey():
    predicted_events = [
        {"id": "1", "type": "APPEAR", "track_id": 1, "start": 0.0, "end": 0.0, "object": "person"},
        {"id": "2", "type": "MOVE", "track_id": 1, "start": 1.0, "end": 5.0, "object": "person"},
        {"id": "3", "type": "STOP", "track_id": 1, "start": 5.0, "end": 8.0, "object": "person"},
    ]
    journey = get_person_journey(1, predicted_events)
    assert journey['total_presence'] == 8.0
    assert journey['moving_duration'] == 4.0
    assert journey['stationary_duration'] == 3.0
    print("[PASS] Person Journey logic")

def test_get_observation_center():
    obs_full = {
        "timestamp": 5.0,
        "track_id": 1,
        "class_name": "person",
        "confidence": 0.9,
        "bbox": [100, 100, 200, 300],
        "center": [150, 200]
    }
    assert get_observation_center(obs_full) == (150.0, 200.0)
    
    obs_fallback = {
        "timestamp": 5.0,
        "track_id": 1,
        "class_name": "person",
        "confidence": 0.9,
        "bbox": [100, 100, 200, 300]
    }
    assert get_observation_center(obs_fallback) == (150.0, 200.0)
    
    obs_old = {
        "timestamp": 5.0,
        "track_id": 1,
        "class_name": "person",
        "confidence": 0.9,
        "center_x": 150,
        "center_y": 200
    }
    assert get_observation_center(obs_old) == (150.0, 200.0)
    
    obs_empty = {
        "timestamp": 5.0,
        "track_id": 1,
        "class_name": "person",
        "confidence": 0.9
    }
    assert get_observation_center(obs_empty) is None
    
    # Check that event extraction handles this gracefully
    engine = EventEngine()
    events = engine.extract_events([obs_full, obs_fallback, obs_old, obs_empty])
    assert len(events) > 0
    print("[PASS] observation center extraction logic and graceful degradation")

if __name__ == "__main__":
    test_ground_truth_accuracy()
    test_query_engine_expanded()
    test_scene_state()
    test_person_journey()
    test_get_observation_center()
    print("All master-level tests PASSED.")
