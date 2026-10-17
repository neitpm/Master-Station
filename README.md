# StationOS: Industrial Substation Monitoring & Edge-to-Station Orchestration Platform
### An Offline-Resilient SCADA Platform Integrating C# .NET 8 Backend Services, SignalR Real-Time Telemetry, Snap7 PLC Communication, and React/Electron Desktop HMI

[![Backend](https://img.shields.io/badge/.NET-8.0-512BD4.svg)](https://dotnet.microsoft.com/)
[![Frontend](https://img.shields.io/badge/React-18.0-61DAFB.svg)](https://react.dev/)
[![Electron](https://img.shields.io/badge/Electron-Desktop%20HMI-47848F.svg)](https://www.electronjs.org/)
[![PLC](https://img.shields.io/badge/PLC-Siemens%20S7%20(Snap7)-00646E.svg)](https://snap7.sourceforge.net/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](docs-project/commercialization_and_licensing.md)

---

## 1. Architectural Scope & Positioning

> **Important Notice on Role & System Boundaries:**  
> **Master-Station** is the **Central Station Orchestration, SCADA Integration, and Operator Interface Layer (StationOS)**.  
> It does not train core computer vision or deep time-series neural networks. Instead, it aggregates telemetry across industrial edge devices, ingests AI-generated safety events and temperature forecasts, evaluates multi-variable health rules, and interfaces directly with electrical switchgear via Siemens S7 PLCs.

Upstream Edge AI nodes providing computer vision and thermal forecasting:
👉 **[`AI-Thermal-detect`](https://github.com/neitpm/AI-Thermal-detect)** *(Edge AI Inference & Time-Series Engine)*  
👉 **[`Get-Thermal-Jetson-nano`](https://github.com/neitpm/Get-Thermal-Jetson-nano)** *(Radiometric Acquisition Daemon)*

---

## 2. Integrated Edge-to-Station Architecture

StationOS functions as an offline-resilient edge server running inside the substation control room:

```mermaid
flowchart TD
    subgraph Edge_AI_Nodes["1. UPSTREAM EDGE AI NODES (Jetson / Cameras)"]
        JETSON_DET["AI-Thermal-detect (yolo_detect.py)<br/>TensorRT FP16 PPE / Uniform Violations"]
        JETSON_FC["AI-Thermal-detect (timeseries_service)<br/>5-Minute Radiometric Temperature Forecasts"]
        RTSP_CAMS["Hikvision Bi-Spectrum & Optical Cameras<br/>Direct RTSP Streams"]
    end

    subgraph StationOS_Host["2. MASTER-STATION CENTRAL PLATFORM (Edge Server)"]
        subgraph Media_Relay["Media Subsystem"]
            GO2RTC["go2rtc Relay Gateway (:1984 / :8554)<br/>Low-Latency WebRTC / MSE Transcoding (<100ms)"]
            AI_ENG["Python ai_engine (:8000)<br/>• Line Crossing Detector (yolov8n.pt - AI Inference)<br/>• Acoustic PD Analyzer (HSV Hotspot - Heuristic Computer Vision)"]
        end

        subgraph Core_Backend["Core Backend (StationOS.Api C# .NET 8 :5000)"]
            REST["REST Endpoints (/api/person-detection, /api/prediction)"]
            HUB["SignalR Realtime WebSocket Hub (RealtimeHub.cs)"]
            SNAP7["Snap7 Background Worker (Siemens S7 PLC Poller)"]
            RULE["Rule Evaluation Worker (Multi-Condition Health Scorer)"]
            DB[(SQLite / PostgreSQL via EF Core)]
        end

        subgraph Client_Layer["Operator Presentation"]
            HMI["React 18 + Electron Desktop Client<br/>• Dynamic SVG Single Line Diagram (SLD)<br/>• Interactive Thermal Zone Annotator<br/>• Sub-second Multi-Camera Matrix"]
        end
    end

    JETSON_DET -->|"POST /api/person-detection"| REST
    JETSON_FC -->|"POST /api/prediction"| REST
    RTSP_CAMS --> GO2RTC
    GO2RTC --> AI_ENG
    AI_ENG -->|"Event Webhooks"| REST

    REST --> DB
    SNAP7 --> DB
    RULE --> DB
    RULE --> HUB
    REST --> HUB
    GO2RTC -->|"WebRTC Video"| HMI
    HUB -->|"SignalR Events"| HMI
```

---

## 3. High-Resolution 3D Volumetric Architecture Figures

Below is the suite of isometric 3D volumetric tensor block diagrams illustrating StationOS platform subsystems:

#### Figure 1: StationOS Platform Central Orchestration Architecture
*Industrial PLC polling, edge AI event ingestion, C# ASP.NET Core .NET 8 backend routing, SignalR broadcasting, and React/Electron desktop HMI.*
![StationOS Architecture 3D](docs/figures/1_stationos_architecture_3d.png)

#### Figure 2: Master-Station Python ai_engine Analytics Taxonomy
*Explicit architectural separation between deep learning object tracking (`line_detector.py`), heuristic HSV hotspot extraction (`pd_region_analyzer.py`), and linear extrapolation.*
![AI Engine Integration 3D](docs/figures/2_ai_engine_integration_3d.png)

#### Figure 3: Cross-Node Ingestion Flow: Alerts, Forecasts & SLD Updates
*Telemetry progression from Jetson Edge nodes into backend REST controllers, rule evaluation workers, and real-time interactive SVG single-line diagrams.*
![Alert and Forecast Flow 3D](docs/figures/3_alert_and_forecast_flow_3d.png)

---

## 4. Subsystem Technical Overview

### A. Backend Core (C# ASP.NET Core .NET 8)
- **High-Performance Ingestion:** Exposes strongly typed endpoints receiving structured JSON payloads from edge detectors (`/api/person-detection`) and forecasters (`/api/prediction`).
- **Industrial PLC Integration (`StationOS.Workers`):** Continuous background polling of Siemens S7-300/1200/1500 PLCs using native socket connections via **Snap7** to read circuit breaker states, busbar voltages, and active power.
- **Dynamic Equipment Health Scorer:** Evaluates multi-parameter heuristics combining electrical current, thermal spot temperatures, and partial discharge acoustic intensity to compute a real-time asset health index (0–100%).
- **Offline Hardware Licensing:** Enforces cryptographic node-locked license keys generated from motherboard and CPU Hardware IDs (`LicenseController.cs`).

### B. Python AI Engine Auxiliary Service (`ai_engine/`)
- Runs as an independent microservice on port `8000`:
  1. **Line Crossing Monitor (`line_detector.py`):** Uses an official pretrained `yolov8n.pt` with ByteTrack to trigger boundary-crossing alarms when personnel cross virtual lines. *(Neural AI Inference)*
  2. **Partial Discharge Acoustic Analyzer (`pd_region_analyzer.py`):** Analyzes video feeds from acoustic imaging cameras; identifies discharge acoustic energy hotspots via HSV color-space thresholding (red/orange spectrum) and correlates coordinates with equipment boundaries. *(Heuristic Image Processing / Non-Neural)*
  3. **Local Linear Extrapolator (`thermal_forecaster.py`):** Provides a lightweight fallback ordinary least-squares extrapolation directly from local CSV buffers.

### C. Frontend HMI (React 18 + Electron)
- **Dynamic Single Line Diagram (SLD):** Interactive vector graphic engine rendering electrical nodes, busbars, and transformers, dynamically updating colors based on real-time voltage and breaker statuses.
- **Low-Latency Video Streaming:** Bypasses sluggish HTTP MJPEG pipelines by consuming direct WebRTC streams transcoded by the internal `go2rtc` daemon.

---

## 5. Repository Structure

```
Master-Station/
├── scripts/
│   └── visualize_architecture.py # 3D volumetric diagram generation script
├── docs/figures/                 # 300 DPI isometric volumetric architecture figures
├── backend/
│   ├── StationOS.Api/          # ASP.NET Core .NET 8 Web API & SignalR Hubs
│   ├── StationOS.Data/         # Entity Framework Core DbContext and Migrations
│   ├── StationOS.Services/     # Business logic, hardware licensing, and health scorer
│   ├── StationOS.Workers/      # Background daemons: Snap7 poller, rule engine
│   └── StationOS.sln           # Visual Studio solution file
├── ai_engine/
│   ├── api/routes.py           # FastAPI routes for stream control and alerts
│   ├── services/acoustic/      # Acoustic Partial Discharge analysis logic (HSV)
│   ├── services/detection/     # YOLOv8 virtual line crossing detector (AI)
│   └── services/thermal/       # Thermal ISAPI matrix parser and local forecaster
├── frontend/                   # React 18 + Vite + TailwindCSS Electron application
├── docs-project/               # Detailed technical specifications and architecture docs
├── start-all.bat               # Windows all-in-one launch script
└── start-all.sh                # Linux all-in-one launch script
```

---

## 6. Deployment & Execution

### Prerequisites
- .NET 8.0 SDK & Runtime.
- Node.js 18+ & npm.
- Python 3.10 with OpenCV.

### Launching Full Station Stack
```bash
# On Windows environments:
start-all.bat

# On Linux environments:
chmod +x start-all.sh
./start-all.sh
```
The platform automatically binds the backend API to `http://localhost:5000`, the AI Engine to `http://localhost:8000`, and launches the Electron desktop monitoring shell.
