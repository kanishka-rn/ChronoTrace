CONFIDENCE_WEIGHTS = {
    "detection": 0.25,
    "tracking": 0.20,
    "event": 0.20,
    "temporal": 0.15,
    "evidence": 0.10,
    "video_quality": 0.10
}

def calculate_analysis_confidence(observations, events, quality_metrics):
    """
    Calculate automated analysis confidence transparently based on metrics.
    """
    if not observations:
        return 0.0, {}
        
    # Detection Score
    avg_conf = sum(o['confidence'] for o in observations) / len(observations)
    detection_score = avg_conf
    
    # Tracking Score (simple metric based on track continuity - few tracks is better than many fragmented)
    unique_tracks = len(set(o['track_id'] for o in observations))
    expected_tracks = max(1, unique_tracks) # naive, but let's assume highly fragmented if ratio is off
    # We can measure fragmentation by average observations per track.
    # Higher is better, capped at 1.0
    avg_obs_per_track = len(observations) / expected_tracks
    tracking_score = min(1.0, avg_obs_per_track / 10.0) 
    
    # Event Score (average confidence of events, fallback to 1.0 if none)
    if events:
        event_score = sum(e.get('confidence', 0.5) for e in events) / len(events)
    else:
        event_score = 0.5 # Unknown/neutral
        
    # Temporal & Evidence are assumed high if events exist and graph connects them well.
    # We use 0.9 as placeholder.
    temporal_score = 0.9 if len(events) > 1 else 0.5
    evidence_score = 0.9
    
    # Video Quality
    quality_score = quality_metrics.get("quality_score", 1.0)
    
    overall = (
        detection_score * CONFIDENCE_WEIGHTS['detection'] +
        tracking_score * CONFIDENCE_WEIGHTS['tracking'] +
        event_score * CONFIDENCE_WEIGHTS['event'] +
        temporal_score * CONFIDENCE_WEIGHTS['temporal'] +
        evidence_score * CONFIDENCE_WEIGHTS['evidence'] +
        quality_score * CONFIDENCE_WEIGHTS['video_quality']
    )
    
    details = {
        "detection_score": detection_score,
        "tracking_score": tracking_score,
        "event_score": event_score,
        "temporal_score": temporal_score,
        "evidence_score": evidence_score,
        "quality_score": quality_score
    }
    return overall, details

def evaluate_ground_truth(predicted_events, ground_truth):
    """
    Calculate Accuracy metrics against a ground_truth json.
    Returns precision, recall, f1, timestamp_mae.
    """
    if not ground_truth or 'events' not in ground_truth:
        return None
        
    gt_events = ground_truth['events']
    
    # Simple matching based on type and overlapping time
    matched_gt = set()
    matched_pred = set()
    errors = []
    
    for i, p_e in enumerate(predicted_events):
        best_match = None
        best_overlap = -1
        
        for j, g_e in enumerate(gt_events):
            if j in matched_gt:
                continue
                
            if p_e['type'] == g_e['type']:
                # overlap check
                overlap_start = max(p_e['start'], g_e['start'])
                overlap_end = min(p_e['end'], g_e['end'])
                overlap = max(0, overlap_end - overlap_start)
                
                if overlap > 0 or (p_e['start'] == p_e['end'] and p_e['start'] >= g_e['start']-1 and p_e['start'] <= g_e['end']+1):
                    if overlap > best_overlap:
                        best_overlap = overlap
                        best_match = j
                        
        if best_match is not None:
            matched_gt.add(best_match)
            matched_pred.add(i)
            # Calculate timestamp error (mean of start and end diff)
            g_e = gt_events[best_match]
            start_err = abs(p_e['start'] - g_e['start'])
            end_err = abs(p_e['end'] - g_e['end'])
            errors.append((start_err + end_err) / 2.0)
            
    tp = len(matched_pred)
    fp = len(predicted_events) - tp
    fn = len(gt_events) - tp
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    timestamp_mae = sum(errors) / len(errors) if errors else 0.0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "timestamp_mae": timestamp_mae
    }
