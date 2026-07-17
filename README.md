# Real-Time Digital Twin System for Autonomous Organ Transportation Using Medical Drones

A production-grade, state-of-the-art multi-dashboard simulation system representing an autonomous drone transport command center for moving human organs between donor and recipient hospitals in Chennai, India. 

Developed as a highly realistic, thread-safe, and interactive Digital Twin demonstration.

---

## 🚀 Features

### 1. Multi-Console Role Views
*   **Donor Hospital (Sender) Dashboard**: Select donor organs, calculate pre-flight route feasibility, check ischemia limits, and request launches.
*   **Control Center (Admin) Command Console**: Monitor active flights, visualize dynamic telemetry in real-time, inspect analytical Plotly graphs (Battery, Speed, Altitude, Cargo Temperature), map uavs on interactive Leaflet maps (Folium), and inject manual flight failures.
*   **Recipient Hospital (Receiver) Console**: Track incoming drones, monitor live ETA countdowns, check cold-chain cargo temperatures, and confirm safe payload handover.

### 2. Multi-Flight Background Simulation
*   Runs a thread-safe parallel simulation engine using standard Python threading. Drones navigate, deplete battery based on airspeed and winds, adjust altitudes, and drift in real time simultaneously, even when the browser is closed or refreshed.

### 3. Pre-Flight Feasibility Engine
*   Checks route distances, estimated battery depletion, wind hazards, organ survival times, communication strengths, emergency landing pads availability, and Chennai No-Fly Zone restrictions (like MAA Airport space). Computes a composite checklist score out of 100 before approval.

### 4. Autonomous Fault Detection & Rerouting
*   Drones auto-diagnose in-flight anomalies. Upon battery depletion (<20%), severe storms (>30 km/h winds), cooler breakdowns (>8°C), or telemetry drops, the autopilot triggers emergency protocols: locates the nearest compatible Chennai emergency helipad, recalculates path coordinates, alerts the control tower, and lands safely.

---

## 📂 Project Structure

```text
app.py                       # Main Streamlit entrance and role navigation
dashboards/
    sender.py                # Donor hospital dispatch booking interface
    admin.py                 # Central telemetry and map command center
    receiver.py              # Recipient hospital payload handover console
simulation/
    drone.py                 # Drone physics, battery loss, and state twin model
    telemetry.py             # Sliding-window telemetry record logger
    mission_manager.py       # Thread-safe central state and simulation clock
    scenarios.py             # Anomaly definitions (Normal, Storm, Power cell loss)
    emergency.py             # Emergency search and autopilot override protocols
    feasibility.py           # Pre-flight route and airspace checker
data/
    hospitals.py             # Chennai 25-hospital spatial coordinates dataset
utils/
    geo.py                   # Haversine distance and path interpolation
    notifications.py         # Rolling log event database
requirements.txt             # Python packages
README.md                    # Documentation
```

---

## 🛠️ Installation & Setup

Ensure Python 3.10+ is installed in your local system, then run:

```bash
# 1. Install required packages
pip install -r requirements.txt

# 2. Boot the command center
streamlit run app.py
```

Streamlit will launch and serve the application on your default local browser at `http://localhost:8501`.

---

## ⚙️ How to Test & Demonstrate

1.  **Quick-Seed Demonstration**: Open the sidebar and click **"⚡ Quick-Seed Demo Flights"**. This automatically creates three diverse flight paths:
    *   *Normal Delivery* (a flawless cruise)
    *   *Weather Emergency* (drone encounters severe winds and reroutes autonomously)
    *   *Battery Emergency* (simulates a cell drop mid-flight forcing emergency landing)
2.  **Approve Flights**: Switch to the **Control Center (Admin)**. Under *Pending Authorizations*, review the feasibility checklists and click **"✅ Approve Launch"** on each flight.
3.  **Real-Time Tracking**: Monitor the live map. Watch the drone icons move physical coordinates towards their targets. Watch the live 2x2 Plotly subplots update and the metric cards fluctuate dynamically.
4.  **Inject Failures**: Under the *Inject Physical Anomalies* box, select an active flight and trigger a **"Cooler Leak"** or **"Motor Burn"** to witness how the Digital Twin immediately reroutes to the closest emergency-landing pad on the map.
5.  **Confirm Handover**: Switch to the **Recipient Hospital (Receiver)** dashboard. Once a drone touches down, its status becomes `ORGAN_HANDOVER`. Click **"🤝 Confirm Delivery"** to log completed delivery and return the drone to base!

---

## ☁️ Production Deployment Guide

This system is fully ready for containerized production deployment.

### 1. Google Cloud Run (Recommended for Enterprise)

Google Cloud Run is a fully-managed serverless platform that automatically scales containerized applications.

#### Prerequisites
- A Google Cloud Platform (GCP) Account with an active project.
- The `gcloud` CLI installed locally and authenticated (`gcloud auth login`).
- Docker installed locally (if building images locally).

#### Step-by-Step Deployment Commands

Run these commands in your local shell at the project root directory:

```bash
# 1. Set your active GCP project ID
export PROJECT_ID="YOUR_GCP_PROJECT_ID"

# 2. Build and submit your Docker image to Google Container Registry (GCR)
gcloud builds submit --tag gcr.io/$PROJECT_ID/organ-drone-app

# 3. Deploy the container image to Google Cloud Run
gcloud run deploy organ-drone-app \
    --image gcr.io/$PROJECT_ID/organ-drone-app \
    --platform managed \
    --allow-unauthenticated \
    --region us-central1
```

#### How Port Binding & Configuration Works on Cloud Run:
- **Port Resolution**: Google Cloud Run dynamically injects a `PORT` environment variable (typically `8080`) at runtime. The Dockerfile starts the server via:
  ```bash
  streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0
  ```
  This overrides any local configuration and maps Streamlit directly to the platform's ingress port.
- **Headless Mode**: Ensured through the `--server.headless true` setting or `.streamlit/config.toml` to prevent Streamlit from attempting to launch a browser in the container background.
- **Health Checks**: Google Cloud Run automatically queries the container startup. A custom docker `HEALTHCHECK` command is configured in the `Dockerfile` to ping Streamlit's internal health check endpoint (`/_stcore/health`) to ensure seamless traffic routing.

---

### 2. Streamlit Community Cloud (Recommended for Demos)

Streamlit Community Cloud is a free hosting service directly integrated with GitHub.

#### Step-by-Step Instructions:
1. Push this workspace to a public GitHub repository.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **"New app"** and select your repository, branch (e.g., `main`), and main file path (`app.py`).
4. Click **"Deploy"**.
5. Streamlit Community Cloud will automatically detect `requirements.txt`, install all required packages, and serve the application publicly. No Dockerfile is required for this path.

---

### 3. Firebase App Hosting (Static Web & Serverless)

Firebase App Hosting natively targets modern web frameworks (Next.js, Angular, etc.). For specialized Python workloads like Streamlit:
- **Architecture recommendation**: It is highly recommended to deploy the Python container directly to **Google Cloud Run** using the provided `Dockerfile`. You can then map a Firebase Hosting custom domain or use Firebase Multi-Site configuration to reverse-proxy traffic to your Cloud Run service.

