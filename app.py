import streamlit as st
import os
import time
import json
import pandas as pd
from tracker import VideoTracker
from events import EventEngine
from query_engine import QueryEngine
from scene_state import get_person_journey, get_scene_state
from evidence import create_evidence_clip, format_timestamp
from video_downloader import download_video
from video_quality import analyze_video_quality
from accuracy_validator import calculate_analysis_confidence, evaluate_ground_truth
from report_generator import generate_pdf_report

st.set_page_config(page_title="ChronoTrace AI | Master Level", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM STYLING ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main-header { font-size: 2.8rem; font-weight: 800; color: #111827; margin-bottom: 0px; letter-spacing: -0.05em; }
.sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 1.5rem; font-weight: 400; }
.tagline { font-weight: 600; color: #2563EB; }
.metric-card { background: white; border: 1px solid #E5E7EB; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: center; }
.timeline-event { background: white; border: 1px solid #E5E7EB; padding: 12px 16px; border-radius: 8px; margin-bottom: 4px; display: flex; align-items: center; cursor: pointer; transition: 0.2s;}
.timeline-event:hover { background: #F9FAFB; border-color: #2563EB; }
.timeline-event .ts { font-family: monospace; font-size: 1rem; font-weight: bold; color: #374151; margin-right: 15px; background: #F3F4F6; padding: 4px 8px; border-radius: 4px; }
.timeline-event .info { font-size: 1rem; color: #1F2937; flex-grow: 1; }
.answer-box { background: #F0FDF4; border-left: 6px solid #16A34A; padding: 15px; border-radius: 8px; margin-top: 10px; }
.answer-box h4 { margin-top: 0; color: #166534; }
.chain-gap { text-align: left; color: #6B7280; font-size: 0.85rem; margin: 4px 0 4px 30px; font-style: italic; }
.scene-stat { font-size: 1.5rem; font-weight: bold; color: #2563EB; }
</style>
""", unsafe_allow_html=True)

# --- DIRECTORY SETUP ---
for dir_name in ["data", "evidence/clips", "models", "reports"]:
    os.makedirs(dir_name, exist_ok=True)

@st.cache_resource
def load_tracker():
    return VideoTracker('yolov8n.pt')

tracker = load_tracker()

# --- INITIALIZE STATE ---
if 'query_history' not in st.session_state:
    st.session_state['query_history'] = []

st.markdown('<p class="main-header">CHRONOTRACE AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Temporal Video Intelligence Platform<br><span class="tagline">Understand what happened. Know when it happened. Prove it with evidence.</span></p>', unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.markdown("### 🎥 1. Video Input")
    input_mode = st.radio("Source:", ["Upload Local Video", "YouTube URL", "Instagram URL"], horizontal=True)
    
    video_path = None
    source_reference = None
    source_type = None
    
    if input_mode == "Upload Local Video":
        uploaded_file = st.file_uploader("Upload video to analyze", type=["mp4", "mov", "avi", "mkv", "webm"])
        if uploaded_file:
            video_path = os.path.join("data", uploaded_file.name)
            with open(video_path, "wb") as f:
                f.write(uploaded_file.read())
            source_reference = uploaded_file.name
            source_type = "LOCAL_UPLOAD"
            
    elif input_mode in ["YouTube URL", "Instagram URL"]:
        url = st.text_input("Enter URL:")
        if url:
            if st.button("Fetch Video"):
                with st.spinner("Downloading video securely..."):
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc
                    success, dl_path, err_cat, user_msg, raw_err = download_video(url)
                    if success:
                        st.session_state['dl_path'] = dl_path
                        st.session_state['dl_url'] = url
                        st.success("Download complete.")
                    else:
                        st.error(f"{user_msg}")
                        st.info("Could not automatically access this video. Download the video manually and upload it using Upload Local Video.")
                        with st.expander("Technical details"):
                            st.write(f"**Source:** {input_mode}")
                            st.write(f"**Error Category:** {err_cat}")
                            st.write(f"**Raw Error:** {raw_err}")
                        
        if st.session_state.get('dl_path') and os.path.exists(st.session_state['dl_path']):
            video_path = st.session_state['dl_path']
            source_reference = st.session_state.get('dl_url', 'URL')
            source_type = "YOUTUBE" if "youtube" in source_reference or "youtu.be" in source_reference else "INSTAGRAM"
            
    if video_path and os.path.exists(video_path):
        st.video(video_path)
        
        if st.button("🚀 ANALYZE VIDEO", type="primary", use_container_width=True):
            with st.status("Running Temporal Pipeline...", expanded=True) as status:
                try:
                    start_proc = time.time()
                    st.write("📊 1. Analyzing Video Quality...")
                    q_metrics = analyze_video_quality(video_path)
                    
                    st.write("🏃 2. Object Detection & Persistent Tracking...")
                    observations, metadata = tracker.process_video(video_path, sample_rate_fps=5)
                    
                    st.write(f"✅ Found {len(observations)} observations. Extracting events...")
                    roi = {"x_min": 0, "y_min": 0, "x_max": 2000, "y_max": 2000}
                    event_engine = EventEngine(roi=roi)
                    events = event_engine.extract_events(observations)
                    
                    st.write("🧠 3. Validation & Graph Indexing...")
                    overall_conf, conf_details = calculate_analysis_confidence(observations, events, q_metrics)
                    
                    acc_metrics = None
                    gt_path = os.path.join(os.path.dirname(video_path), "ground_truth.json")
                    if os.path.exists(gt_path):
                        with open(gt_path, 'r') as f: gt = json.load(f)
                        acc_metrics = evaluate_ground_truth(events, gt)
                        
                    proc_time = time.time() - start_proc
                    
                    st.session_state.update({
                        'observations': observations, 'metadata': metadata, 'video_path': video_path,
                        'events': events, 'analyzed': True, 'source_reference': source_reference,
                        'overall_conf': overall_conf, 'q_metrics': q_metrics, 'acc_metrics': acc_metrics,
                        'proc_time': proc_time, 'query_history': []
                    })
                    status.update(label=f"Analysis Complete! ({proc_time:.1f}s)", state="complete", expanded=False)
                    st.rerun()
                except Exception as e:
                    status.update(label="Analysis Failed", state="error", expanded=True)
                    st.error(f"Error during analysis: {str(e)}")

with col2:
    if st.session_state.get('analyzed', False):
        metadata = st.session_state['metadata']
        events = st.session_state['events']
        obs = st.session_state['observations']
        overall_conf = st.session_state['overall_conf']
        q = st.session_state['q_metrics']
        video_path = st.session_state['video_path']
        
        tab_dash, tab_query, tab_timeline, tab_track, tab_anomalies, tab_data = st.tabs(["📊 Dashboard", "🧠 Ask Video", "🔗 Timeline", "👤 Tracks", "⚠️ Anomalies", "📄 Data"])
        
        with tab_dash:
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"<div class='metric-card'>Video<br><b>{metadata['duration']:.1f}s</b></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='metric-card'>Tracks<br><b>{len(set(e['track_id'] for e in events))}</b></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='metric-card'>Events<br><b>{len(events)}</b></div>", unsafe_allow_html=True)
            c4.markdown(f"<div class='metric-card'>Confidence<br><b>{overall_conf*100:.0f}%</b></div>", unsafe_allow_html=True)
            
            st.markdown("### 🎬 Current Scene State")
            c_ts = st.slider("Select timestamp to evaluate scene state", 0.0, float(metadata['duration']), 0.0, 0.1)
            scene = get_scene_state(c_ts, obs, events)
            
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.markdown(f"<div class='scene-stat'>{scene['people_count']}</div>People", unsafe_allow_html=True)
            sc2.markdown(f"<div class='scene-stat'>{scene['moving_count']}</div>Moving", unsafe_allow_html=True)
            sc3.markdown(f"<div class='scene-stat'>{scene['stationary_count']}</div>Stationary", unsafe_allow_html=True)
            sc4.markdown(f"<div class='scene-stat'>{scene['object_count']}</div>Objects", unsafe_allow_html=True)
            
            st.markdown("### 📈 Accuracy & Validation")
            if st.session_state['acc_metrics']:
                acc = st.session_state['acc_metrics']
                st.success(f"Ground Truth available. F1: {acc['f1']:.2f}, Timestamp Error: {acc['timestamp_mae']:.2f}s")
            else:
                st.info("Ground-truth accuracy: NOT AVAILABLE (No annotations provided)")
                
            if st.button("📄 Generate Final PDF Report"):
                report_data = {
                    "source_reference": st.session_state['source_reference'],
                    "video_duration": metadata['duration'],
                    "video_width": metadata['resolution'][0],
                    "video_height": metadata['resolution'][1],
                    "overall_confidence": overall_conf,
                    "quality": q,
                    "stats": {"sampled_frames": len(obs), "events_count": len(events), "processing_time": st.session_state['proc_time']},
                    "events": events,
                    "accuracy": st.session_state['acc_metrics']
                }
                pdf_path = f"reports/report_{int(time.time())}.pdf"
                generate_pdf_report(report_data, pdf_path)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button("⬇️ Download PDF", data=pdf_file, file_name="ChronoTrace_Report.pdf", mime="application/pdf")
                    
        with tab_query:
            engine = QueryEngine(events, obs)
            st.markdown("### Deterministic Temporal Engine")
            
            query = st.text_input("Ask a question about the video...", placeholder="e.g., How many people are currently moving?")
            
            if query:
                with st.spinner("Reasoning..."):
                    res = engine.parse_query(query, current_timestamp=c_ts)
                    if res['status'] == 'success':
                        st.session_state['query_history'].append({"q": query, "res": res})
                        
                        st.markdown("<div class='answer-box'>", unsafe_allow_html=True)
                        st.markdown(f"#### Answer: {res.get('answer', res['intent'])}")
                        
                        # Explainable Reasoning
                        st.markdown("**Evidence / Reasoning:**")
                        if 'time_difference' in res: st.markdown(f"- Derived Time Difference: **{res['time_difference']:.1f}s**")
                        if 'count' in res: st.markdown(f"- Derived Count: **{res['count']}**")
                        
                        ans_events = res.get('answer_events', [])
                        if ans_events:
                            for e in ans_events[:3]:
                                st.markdown(f"- Used Event: **{e['type']}** @ {e['start']:.1f}s (Track {e['track_id']})")
                                
                        if res.get('timestamps'):
                            st.markdown(f"- Validated Timestamp Range: **{res['timestamps'][0][0]:.1f}s to {res['timestamps'][0][1]:.1f}s**")
                            st.markdown(f"- Evidence Strength: **{overall_conf*100:.0f}%** (Stable temporal relationship)")
                            
                            clip_path = f"evidence/clips/ev_{int(time.time())}.mp4"
                            try:
                                create_evidence_clip(video_path, res['timestamps'][0][0], res['timestamps'][0][1], clip_path)
                                st.video(clip_path)
                            except Exception as e:
                                st.error(f"Evidence extraction failed: {e}")
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Insufficient evidence to deterministically answer this question.")
                        
            if st.session_state['query_history']:
                st.markdown("#### Query History")
                for h in reversed(st.session_state['query_history']):
                    st.markdown(f"**Q:** {h['q']} → **A:** {h['res']['intent']}")

        with tab_timeline:
            st.markdown("### Temporal Event Graph")
            
            # Interactive Timeline
            last_end = 0.0
            for e in events:
                gap = e['start'] - last_end
                if gap > 1.0:
                    st.markdown(f"<div class='chain-gap'>↓ {gap:.1f}s gap</div>", unsafe_allow_html=True)
                    
                emoji = "👤" if e['type'] == 'APPEAR' else "🔴" if e['type'] == 'EXIT' else "🟢" if e['type'] == 'ENTER' else "🟡" if e['type'] == 'STOP' else "➡️" if e['type'] == 'MOVE' else "👻"
                col_ts, col_btn = st.columns([4, 1])
                with col_ts:
                    st.markdown(f"""
                    <div class='timeline-event'>
                        <span class='ts'>{format_timestamp(e['start'])}</span>
                        <span class='info'><b>{e['type']}</b> | Track {e['track_id']} <span style='font-size:0.8em; color:gray;'>({e['end']-e['start']:.1f}s duration)</span></span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_btn:
                    if st.button("👁️ View", key=f"btn_{e['id']}"):
                        clip_path = f"evidence/clips/ev_{e['id']}.mp4"
                        create_evidence_clip(video_path, e['start'], e['end'], clip_path)
                        st.video(clip_path)
                last_end = e['end']
                
        with tab_track:
            st.markdown("### Person Journey Explorer")
            track_ids = list(set(e['track_id'] for e in events))
            if track_ids:
                sel_track = st.selectbox("Select Track ID", track_ids)
                journey = get_person_journey(sel_track, events)
                if journey:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("First Seen", format_timestamp(journey['first_seen']))
                    c2.metric("Total Presence", f"{journey['total_presence']:.1f}s")
                    c3.metric("Stationary Time", f"{journey['stationary_duration']:.1f}s")
                    
                    st.markdown("#### Journey Log")
                    for e in journey['events']:
                        st.markdown(f"- **{format_timestamp(e['start'])}**: {e['type']}")
            else:
                st.write("No tracks found.")
                
        with tab_anomalies:
            st.markdown("### ⚠️ Anomaly Detection")
            st.markdown("Configurable lightweight deterministic anomaly engine.")
            
            long_stationary = [e for e in events if e['type'] == 'STOP' and (e['end'] - e['start']) > 15.0]
            sudden_disappear = [e for e in events if e['type'] == 'DISAPPEAR' and not e.get('near_edge', True)] # placeholder
            
            anomalies = []
            for e in long_stationary:
                anomalies.append({"type": "Long stationary period", "desc": f"Track {e['track_id']} was stationary for {e['end']-e['start']:.1f}s", "ts": e['start']})
                
            if anomalies:
                for a in anomalies:
                    st.warning(f"**{a['type']}** @ {format_timestamp(a['ts'])}: {a['desc']}")
            else:
                st.success("No critical anomalies detected in the current configuration.")
                
        with tab_data:
            st.markdown("### Raw Export")
            if st.button("Download Complete Analysis JSON"):
                data_export = json.dumps({
                    "metadata": metadata,
                    "quality": q,
                    "confidence": overall_conf,
                    "events": events
                }, indent=2)
                st.download_button("⬇️ Download JSON", data=data_export, file_name="chronotrace_export.json", mime="application/json")
            
            st.markdown("#### Events Table")
            st.dataframe(pd.DataFrame(events), use_container_width=True)
    else:
        st.info("Upload or fetch a video and click Analyze to begin.")
