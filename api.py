import os
import time
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil

from tracker import VideoTracker
from events import EventEngine
from query_engine import QueryEngine
from scene_state import get_scene_state, get_person_journey
from video_downloader import download_video
from video_quality import analyze_video_quality
from accuracy_validator import calculate_analysis_confidence
from evidence import create_evidence_clip

app = FastAPI(title="ChronoTrace AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data", exist_ok=True)
os.makedirs("evidence/clips", exist_ok=True)

# In-memory database for hackathon purposes
DB = {}

tracker = VideoTracker('yolov8n.pt')
roi = {"x_min": 0, "y_min": 0, "x_max": 2000, "y_max": 2000}

class AnalyzeUrlRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    query: str
    timestamp: float = 0.0

def process_video_pipeline(video_path: str, source_type: str, source_reference: str):
    analysis_id = f"analysis_{int(time.time())}"
    
    # 1. Quality
    q_metrics = analyze_video_quality(video_path)
    
    # 2. Tracking
    observations, metadata = tracker.process_video(video_path, sample_rate_fps=5)
    metadata["sourceType"] = source_type
    
    # 3. Events
    event_engine = EventEngine(roi=roi)
    events = event_engine.extract_events(observations)
    
    # 4. Confidence
    overall_conf, conf_details = calculate_analysis_confidence(observations, events, q_metrics)
    
    DB[analysis_id] = {
        "id": analysis_id,
        "video_path": video_path,
        "source_reference": source_reference,
        "metadata": metadata,
        "quality": q_metrics,
        "observations": observations,
        "events": events,
        "confidence": {
            "overall": overall_conf,
            "details": conf_details
        }
    }
    
    return analysis_id

@app.post("/api/video/upload")
async def upload_video(file: UploadFile = File(...)):
    video_path = f"data/{file.filename}"
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    analysis_id = process_video_pipeline(video_path, "LOCAL", file.filename)
    return {"analysis_id": analysis_id}

@app.post("/api/video/url")
async def url_video(req: AnalyzeUrlRequest):
    success, dl_path, err_cat, user_msg, raw_err = download_video(req.url)
    if not success:
        raise HTTPException(status_code=400, detail=user_msg)
    
    source_type = "YOUTUBE" if "youtube" in req.url or "youtu.be" in req.url else "INSTAGRAM"
    analysis_id = process_video_pipeline(dl_path, source_type, req.url)
    return {"analysis_id": analysis_id}

@app.get("/api/analysis/{analysis_id}")
def get_analysis(analysis_id: str):
    if analysis_id not in DB:
        raise HTTPException(status_code=404, detail="Analysis not found")
    data = DB[analysis_id]
    
    # Extract unique tracks
    tracks = {}
    for e in data["events"]:
        tid = e["track_id"]
        if tid not in tracks:
            tracks[tid] = {
                "trackId": tid,
                "className": e["object"],
                "firstSeen": e["start"],
                "lastSeen": e["end"],
                "confidence": e.get("confidence", 1.0)
            }
        else:
            tracks[tid]["lastSeen"] = max(tracks[tid]["lastSeen"], e["end"])
            tracks[tid]["firstSeen"] = min(tracks[tid]["firstSeen"], e["start"])

    return {
        "id": data["id"],
        "metadata": data["metadata"],
        "quality": data["quality"],
        "confidence": {
            "detection": data["confidence"]["details"].get("detection_score", 0),
            "tracking": data["confidence"]["details"].get("tracking_score", 0),
            "event": data["confidence"]["details"].get("event_score", 0),
            "temporal": data["confidence"]["details"].get("temporal_score", 0),
            "evidence": data["confidence"]["details"].get("evidence_score", 0),
            "overall": data["confidence"]["overall"]
        },
        "stats": {
            "objectsCount": len(tracks),
            "tracksCount": len(tracks),
            "eventsCount": len(data["events"]),
            "relationsCount": len(data["events"]) * 1.5 # derived approximation for UI
        },
        "tracks": list(tracks.values())
    }

@app.get("/api/analysis/{analysis_id}/events")
def get_events(analysis_id: str):
    if analysis_id not in DB:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"events": DB[analysis_id]["events"]}

@app.get("/api/analysis/{analysis_id}/scene")
def get_scene(analysis_id: str, timestamp: float):
    if analysis_id not in DB:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    data = DB[analysis_id]
    scene = get_scene_state(timestamp, data["observations"], data["events"])
    
    return {
        "timestamp": timestamp,
        "peopleCount": scene["people_count"],
        "objectCount": scene["object_count"],
        "movingCount": scene["moving_count"],
        "stationaryCount": scene["stationary_count"]
    }

@app.post("/api/analysis/{analysis_id}/query")
def run_query(analysis_id: str, req: QueryRequest):
    if analysis_id not in DB:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    data = DB[analysis_id]
    engine = QueryEngine(data["events"], data["observations"])
    res = engine.parse_query(req.query, current_timestamp=req.timestamp)
    
    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
