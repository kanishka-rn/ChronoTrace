import os
from tracker import VideoTracker
from events import EventEngine
from accuracy_validator import evaluate_ground_truth, calculate_analysis_confidence
from video_quality import analyze_video_quality
from video_downloader import download_video
from report_generator import generate_pdf_report
import json

def test_v2_features():
    print("Testing Video Quality Analysis...")
    q = analyze_video_quality("data/test_video.mp4")
    print("Quality Metrics:", q)
    assert 'resolution_category' in q
    assert 'blur_category' in q
    assert 'quality_score' in q
    print("[PASS] Quality Analysis")
    
    print("Testing Local Video Processing...")
    tracker = VideoTracker('yolov8n.pt')
    obs, meta = tracker.process_video("data/test_video.mp4")
    print(f"Observations: {len(obs)}")
    
    engine = EventEngine()
    events = engine.extract_events(obs)
    
    print("Testing Confidence Calculation...")
    conf, details = calculate_analysis_confidence(obs, events, q)
    print(f"Confidence: {conf:.2f}")
    assert isinstance(conf, float)
    print("[PASS] Confidence Calculation")
    
    print("Testing Ground Truth Evaluation...")
    with open("data/ground_truth.json", "r") as f:
        gt = json.load(f)
    metrics = evaluate_ground_truth(events, gt)
    print("Metrics:", metrics)
    print("[PASS] Ground Truth Evaluation")
    
    print("Testing PDF Generation...")
    report_data = {
        "source_reference": "test_video.mp4",
        "video_duration": meta['duration'],
        "video_width": meta['resolution'][0],
        "video_height": meta['resolution'][1],
        "overall_confidence": conf,
        "quality": q,
        "stats": {"sampled_frames": len(obs), "events_count": len(events), "processing_time": 2.5},
        "events": events,
        "accuracy": metrics
    }
    pdf_path = generate_pdf_report(report_data, "reports/test_report.pdf")
    assert os.path.exists(pdf_path)
    print("[PASS] PDF Generation")
    
    print("Testing YouTube URL Download...")
    # Testing a short creative commons video or similar
    # We will just verify it fails gracefully if restricted or downloads correctly.
    # We will use a known safe URL or a dummy URL to see if it handles failure correctly.
    success, path, err_cat, user_msg, raw_err = download_video("https://www.youtube.com/watch?v=nonexistent123")
    print("URL Download Result:", success, err_cat)
    # It should fail gracefully
    assert not success
    print("[PASS] URL Download Graceful Failure")
    
    print("All End-to-End V2 Tests Finished.")

if __name__ == "__main__":
    test_v2_features()
