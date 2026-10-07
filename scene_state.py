def get_scene_state(timestamp, observations, events):
    """
    Returns the deterministic state of the scene at a given timestamp.
    """
    # Active tracks at this timestamp
    active_obs = {}
    
    # We find the closest observation for each track that is near this timestamp.
    # A track is active if there is an observation within a small threshold (e.g., 1.0s)
    # OR if the timestamp falls between its APPEAR and DISAPPEAR events.
    
    # Better: Use events to determine what is currently present.
    # An entity is present if timestamp is between APPEAR and DISAPPEAR.
    # Since we can have multiple APPEAR/DISAPPEAR per track, we check active intervals.
    
    active_tracks = set()
    for e in events:
        if e['type'] == 'APPEAR' and e['start'] <= timestamp:
            active_tracks.add(e['track_id'])
        elif e['type'] == 'DISAPPEAR' and e['start'] <= timestamp:
            if e['track_id'] in active_tracks:
                active_tracks.remove(e['track_id'])
                
    # Now we know which tracks are active. Let's find their current state (STOP/MOVE)
    track_states = {}
    for tid in active_tracks:
        track_states[tid] = {"state": "UNKNOWN", "object": "unknown"}
        
    for e in events:
        if e['start'] <= timestamp <= e['end']:
            if e['track_id'] in track_states:
                track_states[e['track_id']]['object'] = e['object']
                if e['type'] in ['STOP', 'MOVE']:
                    track_states[e['track_id']]['state'] = e['type']
                    
    # Compile summary
    people = 0
    objects = 0
    moving = 0
    stationary = 0
    
    for tid, info in track_states.items():
        if info['object'] == 'person':
            people += 1
        else:
            objects += 1
            
        if info['state'] == 'MOVE':
            moving += 1
        elif info['state'] == 'STOP':
            stationary += 1
            
    return {
        "timestamp": timestamp,
        "people_count": people,
        "object_count": objects,
        "moving_count": moving,
        "stationary_count": stationary,
        "active_tracks": track_states
    }

def get_person_journey(track_id, events):
    """
    Summarize a track's journey.
    """
    track_events = [e for e in events if e['track_id'] == track_id]
    if not track_events:
        return None
        
    first_seen = track_events[0]['start']
    last_seen = track_events[-1]['end']
    
    moving_duration = sum([e['end'] - e['start'] for e in track_events if e['type'] == 'MOVE'])
    stationary_duration = sum([e['end'] - e['start'] for e in track_events if e['type'] == 'STOP'])
    
    return {
        "track_id": track_id,
        "object": track_events[0]['object'],
        "first_seen": first_seen,
        "last_seen": last_seen,
        "total_presence": last_seen - first_seen,
        "moving_duration": moving_duration,
        "stationary_duration": stationary_duration,
        "events": track_events
    }
