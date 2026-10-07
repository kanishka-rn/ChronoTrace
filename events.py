import uuid

def generate_event_id(type_name):
    return f"{type_name}_{str(uuid.uuid4())[:8]}"

def get_observation_center(obs):
    center = obs.get("center")
    if center is not None:
        return float(center[0]), float(center[1])
    bbox = obs.get("bbox")
    if bbox is not None and len(bbox) >= 4:
        x1, y1, x2, y2 = bbox[:4]
        return ((float(x1) + float(x2)) / 2.0, (float(y1) + float(y2)) / 2.0)
    # backward compatibility for old cached data
    if "center_x" in obs and "center_y" in obs:
        return float(obs["center_x"]), float(obs["center_y"])
    return None

class EventEngine:
    def __init__(self, roi=None, stop_threshold=10, move_threshold=15, time_gap_threshold=2.0, interaction_distance=50):
        # ROI is a dictionary: {"x_min": 0, "y_min": 0, "x_max": 1000, "y_max": 1000}
        self.roi = roi
        self.stop_threshold = stop_threshold # pixels
        self.move_threshold = move_threshold # pixels
        self.time_gap_threshold = time_gap_threshold # seconds before track disappears
        self.interaction_distance = interaction_distance
        
    def in_roi(self, x, y):
        if not self.roi:
            return False
        return (self.roi['x_min'] <= x <= self.roi['x_max'] and 
                self.roi['y_min'] <= y <= self.roi['y_max'])

    def _create_event(self, type_name, tid, obj_class, start, end, conf=1.0, extra=None):
        ev = {
            "id": generate_event_id(type_name),
            "type": type_name,
            "track_id": tid,
            "object": obj_class,
            "start": start,
            "end": end,
            "confidence": conf,
            "evidence_quality": 1.0 # default
        }
        if extra:
            ev.update(extra)
        return ev

    def extract_events(self, observations):
        events = []
        if not observations:
            return events
            
        tracks = {}
        for obs in observations:
            tid = obs['track_id']
            if tid not in tracks:
                tracks[tid] = []
            tracks[tid].append(obs)
            
        for tid, track_obs in tracks.items():
            track_obs.sort(key=lambda x: x['timestamp'])
            obj_class = track_obs[0].get('class_name', 'unknown')
            
            # APPEAR
            events.append(self._create_event("APPEAR", tid, obj_class, track_obs[0]['timestamp'], track_obs[0]['timestamp'], track_obs[0].get('confidence', 1.0)))
            
            c0 = get_observation_center(track_obs[0])
            was_in_roi = False
            if c0:
                was_in_roi = self.in_roi(c0[0], c0[1]) if self.roi else False
                if was_in_roi:
                    events.append(self._create_event("ENTER", tid, obj_class, track_obs[0]['timestamp'], track_obs[0]['timestamp'], track_obs[0].get('confidence', 1.0)))
            
            state = "UNKNOWN"
            state_start = track_obs[0]['timestamp']
            last_pos = c0
            
            for i in range(1, len(track_obs)):
                obs = track_obs[i]
                prev_obs = track_obs[i-1]
                
                curr_pos = get_observation_center(obs)
                if curr_pos is None:
                    continue
                    
                dist = 0
                if last_pos is not None:
                    dist = ((curr_pos[0] - last_pos[0])**2 + (curr_pos[1] - last_pos[1])**2)**0.5
                else:
                    last_pos = curr_pos
                
                # Check Time Gap
                if obs['timestamp'] - prev_obs['timestamp'] > self.time_gap_threshold:
                    if state in ["STOP", "MOVE"]:
                        events.append(self._create_event(state, tid, obj_class, state_start, prev_obs['timestamp']))
                    state = "UNKNOWN"
                    events.append(self._create_event("DISAPPEAR", tid, obj_class, prev_obs['timestamp'], prev_obs['timestamp'], prev_obs['confidence']))
                    events.append(self._create_event("APPEAR", tid, obj_class, obs['timestamp'], obs['timestamp'], obs['confidence']))
                    state_start = obs['timestamp']
                    
                # ROI logic
                if self.roi:
                    currently_in_roi = self.in_roi(curr_pos[0], curr_pos[1])
                    if currently_in_roi and not was_in_roi:
                        events.append(self._create_event("ENTER", tid, obj_class, obs['timestamp'], obs['timestamp'], obs['confidence']))
                    elif not currently_in_roi and was_in_roi:
                        events.append(self._create_event("EXIT", tid, obj_class, obs['timestamp'], obs['timestamp'], obs['confidence']))
                    was_in_roi = currently_in_roi
                
                # State logic
                if dist < self.stop_threshold:
                    new_state = "STOP"
                elif dist > self.move_threshold:
                    new_state = "MOVE"
                else:
                    new_state = state # within deadband, keep state
                
                if new_state != state and new_state != "UNKNOWN":
                    if state in ["STOP", "MOVE"]:
                        # Close old state
                        events.append(self._create_event(state, tid, obj_class, state_start, prev_obs['timestamp']))
                    state = new_state
                    state_start = obs['timestamp']
                    last_pos = curr_pos
                    
            # Close final state
            if state in ["STOP", "MOVE"]:
                events.append(self._create_event(state, tid, obj_class, state_start, track_obs[-1]['timestamp']))
                
            # DISAPPEAR
            events.append(self._create_event("DISAPPEAR", tid, obj_class, track_obs[-1]['timestamp'], track_obs[-1]['timestamp'], track_obs[-1]['confidence']))
            
        # Object-Person Interactions
        # Very simple: if a person is STOPPED and an object (not person) is nearby.
        # Alternatively, DETECTED_NEAR for overlapping centers.
        for e1 in events:
            if e1['type'] not in ['STOP', 'MOVE']: continue
            if e1['object'] != 'person': continue
            
            # Find objects that exist during e1's time
            for e2 in events:
                if e2['type'] not in ['STOP', 'MOVE']: continue
                if e2['object'] == 'person': continue
                
                # Check overlap in time
                overlap_start = max(e1['start'], e2['start'])
                overlap_end = min(e1['end'], e2['end'])
                if overlap_end > overlap_start:
                    # They overlap in time. Are they close?
                    # We'd ideally check trajectory distances, but since we don't have bounding boxes in events directly,
                    # we will just extract them if needed, or we just rely on a simple heuristic if we had bounding boxes here.
                    # Since we don't have bboxes in `e1`, we skip deep physical checks for this MVP version to preserve determinism.
                    # A true implementation would query the `observations` list.
                    pass 

        events.sort(key=lambda x: x['start'])
        return events
