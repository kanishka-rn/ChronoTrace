
# 🔎 ChronoTrace AI

### Evidence-Grounded Temporal Video Intelligence

> **Understand what happened. Know when it happened. Prove it with evidence.**

ChronoTrace AI is an **evidence-grounded temporal video reasoning system** that transforms video into a structured timeline of entities, events, and temporal relationships.

Instead of treating video as a collection of frames or asking an LLM to guess what happened, ChronoTrace builds a **Temporal Event Graph (TEG)** from detected and tracked entities, performs deterministic temporal reasoning, and provides the exact video evidence supporting its answers.

---

## 🚀 Why ChronoTrace?

Traditional video AI systems often answer:

> **"What is happening in this video?"**

ChronoTrace focuses on a harder question:

> **"What happened, when did it happen, in what order, and can you prove it?"**

For example:

**Question**

> What happened before the person exited?

**ChronoTrace**

```text
Person #3

STOP  →  00:11.2
  ↓
MOVE  →  00:14.6
  ↓
EXIT  →  00:16.3
```

**Answer**

> Person #3 stopped before exiting.

**Evidence**

> `00:11.2 → 00:16.3`

The user can then inspect the supporting video evidence.

---

# 🧠 Core Concept

ChronoTrace converts:

```text
Video
  ↓
Frame Sampling
  ↓
Object Detection
  ↓
Persistent Tracking
  ↓
Event Extraction
  ↓
Temporal Event Graph
  ↓
Temporal Reasoning
  ↓
Evidence Retrieval
  ↓
Explainable Answer
```

The core principle is:

> **Every answer should be connected to an observable event and a timestamp.**

---

# ✨ Key Features

## 🎥 Multiple Video Sources

ChronoTrace can work with:

- Local video uploads
- YouTube URLs
- Instagram URLs where the media is publicly accessible and technically retrievable

If a platform restricts automated access, the system provides a fallback to direct video upload.

---

## 👁️ Object Detection

Uses **YOLO** for detecting objects and people in video frames.

The system records:

- object class
- confidence
- bounding box
- timestamp
- persistent track ID

---

## 🏃 Persistent Object Tracking

Uses **ByteTrack** to maintain object identities across frames.

Instead of treating every detection independently:

```text
Frame 1 → Person
Frame 2 → Person
Frame 3 → Person
```

ChronoTrace maintains:

```text
Person #7
   ↓
Frame 1
   ↓
Frame 2
   ↓
Frame 3
```

This enables reasoning about what a specific entity did over time.

---

# ⏱️ Temporal Event Extraction

ChronoTrace converts observations into meaningful events such as:

- `APPEAR`
- `DISAPPEAR`
- `ENTER`
- `EXIT`
- `MOVE`
- `STOP`

Example:

```text
00:02.4  APPEAR
00:03.1  ENTER
00:06.7  MOVE
00:11.2  STOP
00:14.6  MOVE
00:16.3  EXIT
```

---

# 🔗 Temporal Event Graph

Events are connected into a structured temporal graph.

Example:

```text
APPEAR
   ↓
ENTER
   ↓
MOVE
   ↓
STOP
   ↓
MOVE
   ↓
EXIT
```

The graph allows ChronoTrace to reason about:

- BEFORE
- AFTER
- BETWEEN
- DURING
- OVERLAPS
- DURATION
- COUNT
- ORDER

---

# 🧠 Deterministic Temporal Reasoning

ChronoTrace does **not** depend on an LLM to invent temporal relationships.

For example:

```text
STOP @ 11.2s
EXIT @ 16.3s
```

The system deterministically establishes:

```text
STOP BEFORE EXIT
```

This makes temporal answers more explainable and auditable.

---

# 💬 Ask the Video

Users can ask temporal questions such as:

### Temporal

```text
What happened before the person exited?

What happened after the person entered?

What happened between the two events?

What happened first?
```

### Duration

```text
How long was the person stationary?
```

### Counting

```text
How many people entered?

How many times did the person enter?
```

### Current State

```text
How many people are currently visible?

How many people are moving?

How many people are stationary?
```

### Track-Based

```text
What did Person #3 do?

How long was Person #3 present?

When did Person #3 exit?
```

---

# 🎯 Evidence-Grounded Answers

ChronoTrace doesn't stop at an answer.

Each important answer can include:

```text
Answer
   ↓
Relevant Events
   ↓
Timestamp
   ↓
Temporal Reasoning
   ↓
Evidence Clip
```

Example:

```text
Question:
How long was Person #3 stationary?

Answer:
3.4 seconds

Start:
00:11.2

End:
00:14.6

Evidence:
00:09.2 → 00:16.6
```

---

# 📹 Evidence Clips

ChronoTrace generates video clips around important events.

Evidence is validated before being shown to the user.

The goal is simple:

> **Don't ask the user to trust the AI. Show them the evidence.**

---

# 📊 Video Quality Analysis

ChronoTrace evaluates input video quality before analysis.

Metrics can include:

- resolution
- FPS
- blur/sharpness
- brightness
- contrast
- visual degradation
- detection confidence

Example:

```text
VIDEO QUALITY

Resolution       640 × 360
FPS              24
Sharpness        Low
Brightness       Good
Compression      High

Quality          LOW
```

Low-quality videos are not automatically rejected.

Instead, the system warns that visual reliability may be reduced.

---

# 🎯 Analysis Confidence

ChronoTrace distinguishes between:

### Analysis Confidence

An automatically calculated estimate based on factors such as:

- detection confidence
- tracking stability
- event consistency
- temporal consistency
- evidence quality
- video quality

and:

### Ground-Truth Accuracy

Measured only when an annotated ground-truth dataset is available.

This distinction is important.

> **Confidence is not the same as accuracy.**

ChronoTrace does not fabricate accuracy percentages for arbitrary videos.

---

# 📈 Accuracy Validation

When ground truth is available, ChronoTrace can evaluate:

- Precision
- Recall
- F1 Score
- Event accuracy
- Temporal query accuracy
- Timestamp error
- Mean Absolute Timestamp Error
- Median timestamp error
- Evidence accuracy
- Track continuity

Timestamp evaluation can include:

```text
Events within ±0.5 sec
Events within ±1.0 sec
Events within ±2.0 sec
```

---

# 🧪 Low-Quality Video Evaluation

ChronoTrace can be evaluated across different video qualities:

```text
Original
   ↓
720p
   ↓
480p
   ↓
360p
   ↓
240p
```

and potentially:

```text
Blurred
Darkened
Compressed
```

Performance can then be compared using actual benchmark results.

Example:

| Video | Event F1 | Timestamp MAE | Confidence |
|---|---:|---:|---:|
| 1080p | Measured | Measured | Measured |
| 720p | Measured | Measured | Measured |
| 480p | Measured | Measured | Measured |
| 360p | Measured | Measured | Measured |

> Values should only be populated from actual benchmark runs.

---

# 👤 Person Journey

ChronoTrace can represent the history of a persistent tracked entity.

Example:

```text
PERSON #7

00:03.2  ENTER
   ↓
00:04.8  MOVE
   ↓
00:09.1  INTERACT
   ↓
00:12.4  STOP
   ↓
00:15.7  MOVE
   ↓
00:17.2  EXIT
```

The system can derive:

- first appearance
- last appearance
- presence duration
- movement duration
- stationary duration
- event history
- associated objects

---

# 📦 Person ↔ Object Relationships

The Temporal Event Graph can represent relationships between entities.

For example:

```text
PERSON #7
    │
    ├── APPROACHED → BOX
    │
    ├── NEAR → BOX
    │
    └── INTERACTED_WITH → BOX
```

Relationships are only generated when supported by the implemented visual evidence rules.

---

# ⚠️ Anomaly Detection

ChronoTrace can identify configurable unusual events such as:

- restricted-area entry
- unusually long stationary periods
- sudden disappearance
- unexpected object disappearance
- sudden crowd increase
- repeated entry/exit patterns

Example:

```text
⚠ ANOMALY DETECTED

Person #8 entered restricted region.

Timestamp: 00:13.7
Confidence: 89%

Evidence available.
```

---

# 📊 Accuracy Lab

ChronoTrace can provide a dedicated evaluation dashboard containing:

```text
Detection F1
Event F1
Temporal Accuracy
Precision
Recall
Timestamp MAE
```

It can also compare different system versions:

```text
             V1       V2       Change

Event F1     --       --       --
Temporal     --       --       --
Timestamp    --       --       --
```

Previous-version values are only shown when an actual benchmark exists.

---

# 📄 Analysis Report

After processing, ChronoTrace can generate a PDF report containing:

- video metadata
- source information
- video quality
- detection statistics
- tracking statistics
- event timeline
- temporal relationships
- query results
- evidence
- confidence
- ground-truth accuracy
- version comparison
- anomalies
- limitations

The report is generated from the actual processing results.

---

# 🏗️ Architecture

```text
                    ┌───────────────────────┐
                    │   Video / Video URL   │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Video Acquisition   │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Video Quality       │
                    │      Analysis         │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │     YOLO Detection    │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   ByteTrack Tracking  │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Event Extraction    │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Temporal Event Graph  │
                    └───────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
          ┌──────────────────┐    ┌──────────────────┐
          │  Query Engine    │    │ Current Scene    │
          └────────┬─────────┘    └────────┬─────────┘
                   │                       │
                   └───────────┬───────────┘
                               ▼
                    ┌───────────────────────┐
                    │ Evidence Generation   │
                    └───────────┬───────────┘
                                │
                 ┌──────────────┼──────────────┐
                 ▼              ▼              ▼
          ┌────────────┐ ┌────────────┐ ┌────────────┐
          │ Confidence │ │  Accuracy  │ │ PDF Report │
          └────────────┘ └────────────┘ └────────────┘
```

---

# 🛠️ Technology Stack

## Computer Vision

- Python
- OpenCV
- Ultralytics YOLO
- ByteTrack
- NumPy
- Pandas

## Application

- Streamlit

## Optional Frontend

- React
- TypeScript
- Tailwind CSS
- shadcn/ui

## Reporting

- ReportLab

## Optional Natural Language Layer

- Gemini / compatible LLM

The LLM is an **optional explanation layer**, not the source of truth for events or timestamps.

---

# 📁 Project Structure

The exact structure may evolve, but the core system follows this pattern:

```text
ChronoTrace/
│
├── app.py
├── video_processor.py
├── tracker.py
├── events.py
├── temporal_graph.py
├── query_engine.py
├── evidence.py
├── accuracy_validator.py
├── video_quality.py
├── report_generator.py
├── test_engine.py
│
├── models/
├── data/
├── evidence/
├── benchmarks/
│
├── frontend/              # Optional React frontend
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── hooks/
│       └── types/
│
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd ChronoTrace
```

## 2. Create a Python environment

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

## 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

If the environment has network timeout issues:

```bash
python -m pip install -r requirements.txt --default-timeout=300 --retries=10
```

---

# ▶️ Run ChronoTrace

```bash
streamlit run app.py
```

The application will open in your browser.

---

# 🎥 Using ChronoTrace

### Option 1 — Local Video

1. Open ChronoTrace.
2. Select **Upload Local Video**.
3. Upload a supported video.
4. Analyze the video.
5. Inspect events and tracks.
6. Ask temporal questions.
7. View evidence.
8. Generate the analysis report.

### Option 2 — YouTube

1. Select **YouTube URL**.
2. Paste a publicly accessible video URL.
3. Fetch the video.
4. Analyze it.

### Option 3 — Instagram

1. Select **Instagram URL**.
2. Paste an accessible public media URL.
3. Fetch the video.
4. Analyze it.

> Automated access to third-party platforms can be restricted. When a URL cannot be retrieved, direct video upload can be used instead.

---

# 🧪 Testing

Run the test suite:

```bash
python test_engine.py
```

Syntax validation:

```bash
python -m py_compile app.py tracker.py video_processor.py events.py temporal_graph.py query_engine.py evidence.py
```

For real-world validation, use a controlled video with known events.

Example:

```text
00:00  Empty scene
00:05  Person enters
00:10  Person moves
00:15  Person stops
00:20  Person interacts with object
00:25  Person moves
00:30  Person exits
```

Then compare detected events against the ground truth.

---

# 🔬 Research & Evaluation Principle

ChronoTrace separates three concepts:

```text
                 VIDEO
                   │
          ┌────────┴────────┐
          ▼                 ▼
     MODEL OUTPUT       GROUND TRUTH
          │                 │
          ▼                 ▼
    CONFIDENCE          ACCURACY
```

### Confidence

"What does the system believe based on the available visual evidence?"

### Accuracy

"How closely did the system match a known ground truth?"

This prevents unsupported claims such as:

> "The AI is 95% accurate."

Instead:

> "On the evaluated benchmark, ChronoTrace achieved an event F1 score of X%."

---

# 🎯 Design Philosophy

ChronoTrace is built around five principles:

### 1. Evidence First

Every important answer should have supporting evidence.

### 2. Temporal First

Video understanding is treated as a sequence of events rather than isolated frames.

### 3. Deterministic Reasoning

Temporal relationships should be computed from structured events whenever possible.

### 4. Explainability

The system should show how an answer was derived.

### 5. Honest Evaluation

Confidence and accuracy are never conflated, and benchmark results are never fabricated.

---

# 🏆 Example Demo Questions

Try asking:

```text
What happened before the person exited?

What happened after the person entered?

How long was the person stationary?

How many people entered?

Who entered first?

Who stayed the longest?

How many people are currently visible?

How many people are currently moving?

What did Person #3 do?

When did Person #3 exit?

Who interacted with the box?
```

---

# 🔮 Future Improvements

Potential future work includes:

- improved multi-object interaction reasoning
- stronger occlusion handling
- more robust cross-camera tracking
- richer scene graphs
- advanced anomaly detection
- audio/event fusion
- larger benchmark datasets
- improved low-quality video robustness
- real-time streaming analysis
- scalable deployment

---

# ⚠️ Limitations

ChronoTrace's performance depends on:

- video resolution
- lighting
- camera angle
- object size
- occlusion
- motion blur
- frame rate
- detector performance
- tracking stability

Third-party video platforms may also restrict automated media access.

Low-quality videos can still be processed, but their analysis confidence may be lower.

---

# 🤝 Contributing

Contributions are welcome.

A typical workflow:

```bash
git checkout -b feature/your-feature
```

Make your changes, add tests, and verify that the existing temporal reasoning pipeline still works.

Then submit a pull request.

---

# 📜 License

Add your project's chosen license here.

For example:

```text
MIT License
```

if the repository is intended to use MIT licensing.

---

# 👨‍💻 Project

**ChronoTrace AI**

### Evidence-Grounded Temporal Video Intelligence

> **Every event. Every timestamp. Every piece of evidence.**

Built for temporal video understanding, reasoning, and evidence-based analysis.
