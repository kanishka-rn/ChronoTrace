import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    h2 = styles['Heading2']
    normal = styles['Normal']
    
    elements = []
    
    # 1. Executive Summary
    elements.append(Paragraph("CHRONOTRACE AI", title_style))
    elements.append(Paragraph("Evidence-Grounded Temporal Video Reasoning", styles['Heading3']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("1. Executive Summary", h2))
    exec_data = [
        ["Source", data.get("source_reference", "N/A")],
        ["Video duration", f"{data.get('video_duration', 0):.1f}s"],
        ["Resolution", f"{data.get('video_width', 0)}x{data.get('video_height', 0)}"],
        ["Processing status", "SUCCESS"],
        ["Overall Analysis Confidence", f"{data.get('overall_confidence', 0)*100:.1f}%"]
    ]
    t_exec = Table(exec_data, colWidths=[200, 300])
    t_exec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.silver),
        ('PADDING', (0, 0), (-1, -1), 6)
    ]))
    elements.append(t_exec)
    elements.append(Spacer(1, 15))
    
    # 3. Video Quality Assessment
    elements.append(Paragraph("3. Video Quality Assessment", h2))
    q = data.get("quality", {})
    qual_data = [
        ["Resolution Category", q.get("resolution_category", "N/A")],
        ["FPS Category", q.get("fps_category", "N/A")],
        ["Blur Category", q.get("blur_category", "N/A")],
        ["Brightness Category", q.get("brightness_category", "N/A")],
        ["Overall Quality", q.get("overall_category", "N/A")]
    ]
    t_qual = Table(qual_data, colWidths=[200, 300])
    t_qual.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.silver)]))
    elements.append(t_qual)
    elements.append(Spacer(1, 15))
    
    # 4. Processing Statistics
    elements.append(Paragraph("4. Processing Statistics", h2))
    stats = data.get("stats", {})
    stats_data = [
        ["Sampled Frames", str(stats.get("sampled_frames", 0))],
        ["Events Extracted", str(stats.get("events_count", 0))],
        ["Processing Time", f"{stats.get('processing_time', 0):.1f}s"]
    ]
    t_stats = Table(stats_data, colWidths=[200, 300])
    t_stats.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.silver)]))
    elements.append(t_stats)
    elements.append(Spacer(1, 15))
    
    # 6. Event Analysis
    elements.append(Paragraph("6. Event Analysis", h2))
    events = data.get("events", [])
    if events:
        event_table_data = [["ID", "Event", "Track", "Start", "End", "Confidence"]]
        for e in events[:20]: # Limit to 20 for brevity
            event_table_data.append([
                e['id'][:8], 
                e['type'], 
                str(e['track_id']), 
                f"{e['start']:.1f}", 
                f"{e['end']:.1f}", 
                f"{e.get('confidence',0):.2f}"
            ])
        t_events = Table(event_table_data)
        t_events.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.silver),
        ]))
        elements.append(t_events)
    else:
        elements.append(Paragraph("No events detected.", normal))
    
    elements.append(Spacer(1, 15))
    
    # 9. Accuracy Validation
    elements.append(Paragraph("9. Accuracy Validation", h2))
    acc = data.get("accuracy", None)
    if acc:
        acc_data = [
            ["Precision", f"{acc['precision']:.2f}"],
            ["Recall", f"{acc['recall']:.2f}"],
            ["F1 Score", f"{acc['f1']:.2f}"],
            ["Timestamp MAE", f"{acc['timestamp_mae']:.2f}s"]
        ]
        t_acc = Table(acc_data, colWidths=[200, 300])
        t_acc.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.silver)]))
        elements.append(t_acc)
    else:
        elements.append(Paragraph("Ground-truth accuracy was not calculated because no annotated ground truth was provided.", normal))
        
    elements.append(Spacer(1, 15))
    
    # 13. Final Conclusion
    elements.append(Paragraph("13. Final Conclusion", h2))
    elements.append(Paragraph(f"Analysis completed successfully with {len(events)} events found. Overall analysis confidence is {data.get('overall_confidence', 0)*100:.1f}%.", normal))
    
    doc.build(elements)
    return output_path
