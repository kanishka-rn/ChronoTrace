class TemporalGraph:
    def __init__(self, events):
        self.events = sorted(events, key=lambda e: e['start'])
        
    def find_before(self, target_event, max_time_diff=None):
        results = []
        for e in self.events:
            if e['id'] == target_event['id']:
                continue
            if e['end'] <= target_event['start']:
                if max_time_diff is None or (target_event['start'] - e['end'] <= max_time_diff):
                    results.append(e)
        return results

    def find_after(self, target_event, max_time_diff=None):
        results = []
        for e in self.events:
            if e['id'] == target_event['id']:
                continue
            if e['start'] >= target_event['end']:
                if max_time_diff is None or (e['start'] - target_event['end'] <= max_time_diff):
                    results.append(e)
        return results

    def find_between(self, start_event, end_event):
        results = []
        start_time = start_event['end']
        end_time = end_event['start']
        
        for e in self.events:
            if e['id'] in [start_event['id'], end_event['id']]:
                continue
            if e['start'] >= start_time and e['end'] <= end_time:
                results.append(e)
        return results

    def filter_events(self, obj_type=None, event_type=None):
        filtered = self.events
        if obj_type:
            filtered = [e for e in filtered if e['object'].lower() == obj_type.lower()]
        if event_type:
            filtered = [e for e in filtered if e['type'].lower() == event_type.lower()]
        return filtered
