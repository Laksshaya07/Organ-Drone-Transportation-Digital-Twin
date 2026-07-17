import streamlit as st
import pandas as pd
from data.hospitals import HOSPITALS, get_hospital_by_id
from simulation.feasibility import ORGAN_VIABILITY_HOURS
from utils.navigation import safe_rerun

def render_sender_dashboard(mission_manager):
    st.markdown("<h2 style='text-align: center; color: #ffffff; font-weight: 700; letter-spacing: -0.02em;'>Donor Hospital Dispatch Console</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a1a1aa; font-size: 0.95rem; margin-bottom: 20px;'>Initiate and track cold-chain human organ transports via the autonomous drone logistics network.</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # Grid columns
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("📋 Create Organ Dispatch Request")
        
        # Form fields
        hosp_names_ids = [(h["name"], h["id"]) for h in HOSPITALS]
        
        source_name = st.selectbox(
            "Donor Hospital (Source)",
            options=[h[0] for h in hosp_names_ids],
            index=0,
            key="src_hosp"
        )
        source_id = next(h[1] for h in hosp_names_ids if h[0] == source_name)
        
        dest_options = [h[0] for h in hosp_names_ids if h[0] != source_name]
        dest_name = st.selectbox(
            "Recipient Hospital (Destination)",
            options=dest_options,
            index=1,
            key="dst_hosp"
        )
        dest_id = next(h[1] for h in hosp_names_ids if h[0] == dest_name)
        
        col_org, col_pri = st.columns(2)
        with col_org:
            organ_type = st.selectbox(
                "Organ Type",
                options=list(ORGAN_VIABILITY_HOURS.keys()),
                index=0
            )
            # Display organ survival helper text
            viab_h = ORGAN_VIABILITY_HOURS[organ_type]
            st.caption(f"Ischemia Limit: **{viab_h:.0f} hours**")
            
        with col_pri:
            priority = st.selectbox(
                "Priority Level",
                options=["CRITICAL", "HIGH", "MEDIUM"],
                index=0
            )
            
        scenario_name = st.selectbox(
            "Simulated Flight Scenario",
            options=[
                "Normal Delivery",
                "Battery Emergency",
                "Weather Emergency",
                "Cooling Failure",
                "GPS Failure",
                "Communication Failure"
            ],
            help="Choose a scenario to test different behaviors of the Digital Twin autopilot.",
            index=0
        )
        
        if st.button("🚀 Create Mission", use_container_width=True):
            with st.spinner("Analyzing routes and checking weather..."):
                m_id = mission_manager.create_mission(source_id, dest_id, organ_type, priority, scenario_name)
                st.success(f"Request {m_id} successfully registered! Feasibility score compiled.")
                safe_rerun()
                
    with col2:
        st.subheader("📡 Active Despatches & Feasibility Scores")
        
        all_missions = mission_manager.get_all_missions()
        sender_missions = [m for m in all_missions if m["status"] not in ["MISSION_COMPLETED", "REJECTED_BY_ADMIN"]]
        
        if not sender_missions:
            st.info("No active dispatch requests in progress. Create a request in the left panel.")
        else:
            for m in reversed(sender_missions):
                status = m["status"]
                score = m["feasibility_score"]
                
                # Setup visual color badge for status
                status_color = "#3B82F6"  # Blue
                if "REJECTED" in status:
                    status_color = "#EF4444"  # Red
                elif "EMERGENCY" in status:
                    status_color = "#F59E0B"  # Orange
                elif status in ["ORGAN_HANDOVER", "LANDED"]:
                    status_color = "#10B981"  # Green
                    
                st.markdown(f"""
                <div style="background-color: #121214; padding: 15px; border-radius: 8px; border-left: 6px solid {status_color}; margin-bottom: 12px; border-top: 1px solid #27272a; border-right: 1px solid #27272a; border-bottom: 1px solid #27272a;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: bold; font-size: 1.1em; color: #ffffff;">Mission: {m['id']}</span>
                        <span style="background-color: {status_color}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold;">{status}</span>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.9em; color: #a1a1aa;">
                        <strong style="color: #fafafa;">Organ:</strong> {m['organ_type']} | <strong style="color: #fafafa;">Priority:</strong> {m['priority']}<br/>
                        <strong style="color: #fafafa;">Route:</strong> {m['source_name']} → {m['dest_name']}<br/>
                        <strong style="color: #fafafa;">Scenario:</strong> <span style="color: #3b82f6;">{m['scenario_name']}</span><br/>
                    </div>
                    <div style="margin-top: 10px; display: flex; align-items: center; justify-content: space-between; background-color: #18181b; padding: 8px; border-radius: 4px; border: 1px solid #27272a;">
                        <span style="font-weight: 500; font-size: 0.85em; color: #d4d4d8;">Feasibility Assessment:</span>
                        <span style="font-weight: bold; color: {'#10B981' if score >= 70 else '#EF4444' if score < 50 else '#F59E0B'};">{score}/100</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Expandable checklist
                with st.expander(f"🔍 Route Feasibility Checklist for {m['id']}"):
                    det = m["feasibility_details"]["details"]
                    st.write(f"📏 **Calculated Distance:** {det['distance_km']} km")
                    st.write(f"🔋 **Est. Battery Expenditure:** {det['est_battery_loss_pct']}%")
                    st.write(f"💨 **Forecast Winds:** {det['wind_speed_kmh']} km/h")
                    st.write(f"📍 **Emergency Pads Nearby:** {det['nearest_emergency_hosp']} ({det['nearest_emergency_dist_km']} km away)")
                    
                    st.write("**Assessment Verdicts:**")
                    for r in m["feasibility_details"]["reasons"]:
                        st.markdown(f"- {r}")

    st.divider()
    
    # Notifications section for Sender
    st.subheader("🔔 Sender Notifications Logs")
    notifs = mission_manager.notifier.get_all()
    if notifs:
        for n in notifs[:10]:
            if n["mission_id"] != "SYSTEM" and n["mission_id"] in [m["id"] for m in sender_missions]:
                icon = "ℹ️"
                if n["type"] == "success":
                    icon = "✅"
                elif n["type"] == "warning":
                    icon = "⚠️"
                elif n["type"] == "danger":
                    icon = "🚨"
                st.markdown(f"**[{n['timestamp']}]** {icon} {n['message']}")
    else:
        st.write("No dispatch telemetry notifications logged yet.")
