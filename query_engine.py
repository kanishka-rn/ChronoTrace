from temporal_graph import TemporalGraph
from scene_state import get_scene_state, get_person_journey
import re

class QueryEngine:
    def __init__(self, events, observations=None):
        self.graph = TemporalGraph(events)
        self.events = events
        self.observations = observations
        
    def parse_query(self, query: str, current_timestamp=0.0):
        query = query.lower()
        
        # CURRENT STATE QUERIES
        if "currently" in query or "now" in query:
            scene = get_scene_state(current_timestamp, self.observations, self.events)
            if "moving" in query:
                return {"status": "success", "intent": "CURRENT_STATE", "answer": f"There are currently {scene['moving_count']} moving entities.", "confidence": 1.0}
            if "stationary" in query:
                return {"status": "success", "intent": "CURRENT_STATE", "answer": f"There are currently {scene['stationary_count']} stationary entities.", "confidence": 1.0}
            if "people" in query or "person" in query:
                return {"status": "success", "intent": "CURRENT_STATE", "answer": f"There are currently {scene['people_count']} people visible.", "confidence": 1.0}
            if "object" in query:
                return {"status": "success", "intent": "CURRENT_STATE", "answer": f"There are currently {scene['object_count']} objects visible.", "confidence": 1.0}
            return {"status": "success", "intent": "CURRENT_STATE", "answer": f"Scene contains {scene['people_count']} people and {scene['object_count']} objects.", "confidence": 1.0}
                
        # HISTORICAL
        if "chronological order" in query:
            return self._handle_order()
        
        if "how long" in query or "duration" in query:
            if "stationary" in query or "stop" in query:
                return self._handle_duration("STOP")
                
        if "how many times" in query or "how many people" in query or "count" in query:
            if "enter" in query:
                return self._handle_count("ENTER")
            if "exit" in query:
                return self._handle_count("EXIT")
            if "appear" in query:
                return self._handle_count("APPEAR")
                
        if "before" in query:
            if "exit" in query:
                target_events = self.graph.filter_events(event_type="EXIT")
                if target_events: return self._handle_before(target_events[0])
                    
        if "after" in query:
            if "enter" in query:
                target_events = self.graph.filter_events(event_type="ENTER")
                if target_events: return self._handle_after(target_events[-1])
                
        if "between" in query:
            enters = self.graph.filter_events(event_type="ENTER")
            exits = self.graph.filter_events(event_type="EXIT")
            if enters and exits:
                return self._handle_between(enters[0], exits[-1])

        return {"status": "insufficient_evidence", "reason": "Query not supported or events not found."}

    def _handle_order(self):
        return {"status": "success", "intent": "ORDER", "answer_events": self.graph.events, "timestamps": [(e['start'], e['end']) for e in self.graph.events], "confidence": 1.0}

    def _handle_duration(self, event_type):
        events = self.graph.filter_events(event_type=event_type)
        if not events: return {"status": "insufficient_evidence"}
        total_duration = sum([e['end'] - e['start'] for e in events])
        return {"status": "success", "intent": "DURATION", "answer_events": events, "time_difference": total_duration, "timestamps": [(e['start'], e['end']) for e in events], "confidence": 1.0}

    def _handle_count(self, event_type):
        events = self.graph.filter_events(event_type=event_type)
        return {"status": "success", "intent": "COUNT", "answer_events": events, "count": len(events), "timestamps": [(e['start'], e['end']) for e in events], "confidence": 1.0}

    def _handle_before(self, target_event):
        before_events = self.graph.find_before(target_event)
        if not before_events: return {"status": "insufficient_evidence"}
        time_diff = target_event['start'] - before_events[-1]['end']
        return {"status": "success", "intent": "BEFORE", "target_event": target_event, "answer_events": before_events, "time_difference": time_diff, "timestamps": [(before_events[-1]['start'], before_events[-1]['end'])], "confidence": 1.0}

    def _handle_after(self, target_event):
        after_events = self.graph.find_after(target_event)
        if not after_events: return {"status": "insufficient_evidence"}
        time_diff = after_events[0]['start'] - target_event['end']
        return {"status": "success", "intent": "AFTER", "target_event": target_event, "answer_events": after_events, "time_difference": time_diff, "timestamps": [(after_events[0]['start'], after_events[0]['end'])], "confidence": 1.0}

    def _handle_between(self, start_event, end_event):
        between_events = self.graph.find_between(start_event, end_event)
        if not between_events: return {"status": "insufficient_evidence"}
        return {"status": "success", "intent": "BETWEEN", "target_event": [start_event, end_event], "answer_events": between_events, "time_difference": end_event['start'] - start_event['end'], "timestamps": [(e['start'], e['end']) for e in between_events], "confidence": 1.0}

