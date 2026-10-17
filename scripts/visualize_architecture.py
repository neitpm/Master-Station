"""
scripts/visualize_architecture.py
Generates high-resolution 3D volumetric tensor block diagrams for Master-Station:
1. docs/figures/1_stationos_architecture_3d.png
2. docs/figures/2_ai_engine_integration_3d.png
3. docs/figures/3_alert_and_forecast_flow_3d.png

Canvas: 16x10 inches, 300 DPI.
Clear distinction:
- YOLOv8n line crossing detector (AI Inference)
- Acoustic PD HSV Hotspot (Rule-based color space processing)
- Snap7 S7 PLC poller (Industrial Telemetry)
"""

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

THEMES = {
    "camera": ["#0284C7", "#38BDF8", "#0369A1"],      # Cyan / Sky
    "preprocess": ["#475569", "#94A3B8", "#334155"],  # Slate Gray
    "ai_engine": ["#7C3AED", "#A78BFA", "#6D28D9"],   # Purple
    "backend": ["#4F46E5", "#818CF8", "#3730A3"],     # Indigo
    "ui": ["#DB2777", "#F472B6", "#9D174D"],          # Rose / Pink
    "plc": ["#059669", "#34D399", "#047857"],         # Emerald Green
    "dark_bg": "#0B1120",
    "card_bg": "#1E293B",
    "card_border": "#334155",
    "text_white": "#F8FAFC",
    "text_muted": "#94A3B8",
    "text_yellow": "#FEF08A"
}

def draw_3d_block(ax, x, y, w, h, depth=0.35, theme="backend", label="", sublabel="", tensor_shape="", desc=""):
    front_c, top_c, side_c = THEMES[theme]
    dx = depth * 0.7
    dy = depth * 0.7

    side_pts = [[x + w, y], [x + w + dx, y + dy], [x + w + dx, y + h + dy], [x + w, y + h]]
    ax.add_patch(Polygon(side_pts, closed=True, facecolor=side_c, edgecolor="#0F172A", lw=1.2, zorder=2))

    top_pts = [[x, y + h], [x + dx, y + h + dy], [x + w + dx, y + h + dy], [x + w, y + h]]
    ax.add_patch(Polygon(top_pts, closed=True, facecolor=top_c, edgecolor="#0F172A", lw=1.2, zorder=2))

    front_pts = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
    ax.add_patch(Polygon(front_pts, closed=True, facecolor=front_c, edgecolor="#0F172A", lw=1.2, zorder=3))

    cx = x + w / 2.0
    cy = y + h / 2.0

    if label:
        ax.text(cx, cy + h * 0.22, label, ha="center", va="center", color=THEMES["text_white"], fontsize=9.5, fontweight="bold", zorder=4)
    if sublabel:
        ax.text(cx, cy + h * 0.02, sublabel, ha="center", va="center", color="#F1F5F9", fontsize=8.0, zorder=4)
    if tensor_shape:
        ax.text(cx, cy - h * 0.22, tensor_shape, ha="center", va="center", color=THEMES["text_yellow"], fontsize=8.0, fontweight="bold", family="monospace", zorder=4)
    if desc:
        ax.text(cx + dx/2, y - 0.35, desc, ha="center", va="top", color=THEMES["text_muted"], fontsize=7.8, zorder=4)

def draw_3d_arrow(ax, x1, y1, x2, y2, color="#38BDF8", text=""):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(facecolor=color, edgecolor=color, width=1.8, headwidth=6, headlength=7, shrink=0.06), zorder=5)
    if text:
        ax.text((x1 + x2)/2, (y1 + y2)/2 + 0.25, text, ha="center", va="center", color="#FFFFFF", fontsize=7.5, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", facecolor=THEMES["card_bg"], edgecolor=THEMES["card_border"], alpha=0.95), zorder=6)


# Figure 1: StationOS Overall Architecture
def generate_fig1():
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor(THEMES["dark_bg"])
    ax.set_facecolor(THEMES["dark_bg"])
    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.5, 9.5)
    ax.axis("off")

    ax.text(8.0, 8.8, "StationOS Platform Central Orchestration Architecture", ha="center", va="center",
            color=THEMES["text_white"], fontsize=18, fontweight="bold")
    ax.text(8.0, 8.35, "Industrial PLC Polling + Edge AI Ingestion -> C# .NET 8 Backend -> SignalR Hub -> React Electron Dashboard",
            ha="center", va="center", color=THEMES["text_muted"], fontsize=10.5)

    stages = [
        {"x": 0.5, "w": 2.6, "h": 2.8, "theme": "plc", "label": "Siemens S7 PLC", "sub": "Snap7 Worker", "shape": "DB Read Loop", "desc": "Socket communication\nBreaker & Busbar stats"},
        {"x": 4.2, "w": 2.8, "h": 2.8, "theme": "backend", "label": "StationOS.Api", "sub": "C# ASP.NET Core", "shape": ".NET 8 WebApi", "desc": "REST API Controller\nEF Core (SQLite/Postgres)"},
        {"x": 8.0, "w": 2.8, "h": 2.8, "theme": "ai_engine", "label": "Python ai_engine", "sub": "Auxiliary Daemon", "shape": "Port 8000 TCP", "desc": "go2rtc WebRTC Relay\nYOLOv8n Line Crossing"},
        {"x": 11.8, "w": 2.6, "h": 2.8, "theme": "backend", "label": "SignalR Hub", "sub": "RealtimeHub.cs", "shape": "WebSocket Push", "desc": "Sub-second telemetry\nAlert broadcast"},
        {"x": 14.8, "w": 1.4, "h": 2.8, "theme": "ui", "label": "HMI UI", "sub": "React 18", "shape": "Electron", "desc": "Dynamic SLD"}
    ]

    for s in stages:
        draw_3d_block(ax, s["x"], 3.2, s["w"], s["h"], theme=s["theme"],
                      label=s["label"], sublabel=s["sub"], tensor_shape=s["shape"], desc=s["desc"])

    draw_3d_arrow(ax, 3.1, 4.6, 4.2, 4.6)
    draw_3d_arrow(ax, 7.0, 4.6, 8.0, 4.6)
    draw_3d_arrow(ax, 10.8, 4.6, 11.8, 4.6)
    draw_3d_arrow(ax, 14.4, 4.6, 14.8, 4.6)

    fig.savefig(OUTPUT_DIR / "1_stationos_architecture_3d.png", dpi=300)
    plt.close(fig)
    print("Master-Station: Generated 1_stationos_architecture_3d.png")


# Figure 2: AI Engine Integration (YOLO vs HSV vs Telemetry)
def generate_fig2():
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor(THEMES["dark_bg"])
    ax.set_facecolor(THEMES["dark_bg"])
    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.5, 9.5)
    ax.axis("off")

    ax.text(8.0, 8.8, "Master-Station Python ai_engine Analytics Taxonomy", ha="center", va="center",
            color=THEMES["text_white"], fontsize=18, fontweight="bold")
    ax.text(8.0, 8.35, "Clear Architectural Separation: Deep Learning Inference vs Heuristic Computer Vision vs Video Relay",
            ha="center", va="center", color=THEMES["text_muted"], fontsize=10.5)

    stages = [
        {"x": 0.5, "w": 3.4, "h": 4.6, "theme": "ai_engine",
         "label": "Line Crossing Detector", "sub": "services/detection/line_detector.py", "shape": "yolov8n.pt (AI Inference)",
         "desc": "Paradigm: Deep Learning (YOLOv8)\nClasses: person (0), car (2)\nTracker: ByteTrack (persist=True)\nOutput: Bounding boxes & line crossings"},

        {"x": 5.8, "w": 3.4, "h": 4.6, "theme": "camera",
         "label": "Acoustic PD Analyzer", "sub": "services/detection/pd_region_analyzer.py", "shape": "Rule-Based (Non-Neural)",
         "desc": "Paradigm: Heuristic HSV Thresholding\nFilter: cv2.inRange (Red/Orange band)\nMorphology: cv2.morphologyEx\nOutput: Sound hotspot (cx, cy, area)"},

        {"x": 11.2, "w": 3.4, "h": 4.6, "theme": "backend",
         "label": "Thermal Forecaster", "sub": "services/thermal/thermal_forecaster.py", "shape": "Ordinary Least Squares",
         "desc": "Paradigm: Linear Extrapolation\nAlgorithm: np.linalg.lstsq\nInput: Rolling history CSV buffer\nOutput: 5-minute scalar projection"}
    ]

    for s in stages:
        draw_3d_block(ax, s["x"], 2.2, s["w"], s["h"], depth=0.45, theme=s["theme"],
                      label=s["label"], sublabel=s["sub"], tensor_shape=s["shape"], desc=s["desc"])

    fig.savefig(OUTPUT_DIR / "2_ai_engine_integration_3d.png", dpi=300)
    plt.close(fig)
    print("Master-Station: Generated 2_ai_engine_integration_3d.png")


# Figure 3: Alert & Forecast Flow
def generate_fig3():
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor(THEMES["dark_bg"])
    ax.set_facecolor(THEMES["dark_bg"])
    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.5, 9.5)
    ax.axis("off")

    ax.text(8.0, 8.8, "Cross-Node Ingestion Flow: Alerts, Forecasts & SLD Updates", ha="center", va="center",
            color=THEMES["text_white"], fontsize=18, fontweight="bold")
    ax.text(8.0, 8.35, "Jetson Edge Node -> REST Ingestion -> Rule Engine Evaluator -> Realtime Hub -> Desktop UI",
            ha="center", va="center", color=THEMES["text_muted"], fontsize=10.5)

    stages = [
        {"x": 0.5, "w": 2.8, "h": 2.8, "theme": "camera", "label": "Edge AI Alerts", "sub": "AI-Thermal-detect", "shape": "JSON Payloads", "desc": "POST /api/person-detection\nPOST /api/prediction"},
        {"x": 4.4, "w": 2.8, "h": 2.8, "theme": "backend", "label": "Ingestion Controller", "sub": "StationOS.Api", "shape": "REST Endpoints", "desc": "Schema validation\nPayload timestamp sync"},
        {"x": 8.3, "w": 2.8, "h": 2.8, "theme": "backend", "label": "Rule Engine Worker", "sub": "StationOS.Workers", "shape": "Evaluation Cycle", "desc": "Health Index (0-100%)\nTemperature threshold check"},
        {"x": 12.2, "w": 2.8, "h": 2.8, "theme": "ui", "label": "Interactive HMI", "sub": "Electron Shell", "shape": "React 18 SLD", "desc": "Visual alarm banners\nRealtime node coloring"}
    ]

    for s in stages:
        draw_3d_block(ax, s["x"], 3.2, s["w"], s["h"], theme=s["theme"],
                      label=s["label"], sublabel=s["sub"], tensor_shape=s["shape"], desc=s["desc"])

    draw_3d_arrow(ax, 3.3, 4.6, 4.4, 4.6)
    draw_3d_arrow(ax, 7.2, 4.6, 8.3, 4.6)
    draw_3d_arrow(ax, 11.1, 4.6, 12.2, 4.6)

    fig.savefig(OUTPUT_DIR / "3_alert_and_forecast_flow_3d.png", dpi=300)
    plt.close(fig)
    print("Master-Station: Generated 3_alert_and_forecast_flow_3d.png")

if __name__ == "__main__":
    generate_fig1()
    generate_fig2()
    generate_fig3()
    print("Master-Station: All 3 3D figures generated successfully.")
