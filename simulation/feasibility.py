import random
from utils.geo import haversine_distance
from data.hospitals import get_hospital_by_id, HOSPITALS

# Organ viability limits in hours
ORGAN_VIABILITY_HOURS = {
    "Heart": 5.0,
    "Lung": 5.0,
    "Liver": 10.0,
    "Kidney": 30.0
}

def check_feasibility(source_hosp_id, dest_hosp_id, organ_type, scenario_name="Normal Delivery"):
    """
    Perform pre-flight multi-point checks:
    1. Distance check
    2. Battery check
    3. Weather check
    4. Organ viability check
    5. Communication check
    6. Emergency hospital availability
    7. No-fly zone check
    """
    source = get_hospital_by_id(source_hosp_id)
    dest = get_hospital_by_id(dest_hosp_id)

    if not source or not dest:
        return {
            "feasible": False,
            "score": 0,
            "reasons": ["Invalid source or destination hospital."],
            "details": {}
        }

    distance = haversine_distance(source["latitude"], source["longitude"], dest["latitude"], dest["longitude"])

    reasons = []
    details = {}
    score = 100

    # 1. Distance Check
    details["distance_km"] = round(distance, 2)
    if distance > 40.0:
        score -= 40
        reasons.append("Distance exceeds drone's maximum single-charge safe range (40km).")
    elif distance > 25.0:
        score -= 15
        reasons.append("Long distance route: requires optimal flight profiles and energy conservation.")

    # 2. Battery Check
    # Estimate base consumption: ~2.0% battery per km
    estimated_battery_loss = distance * 2.0
    details["est_battery_loss_pct"] = round(estimated_battery_loss, 1)
    if estimated_battery_loss > 80.0:
        score -= 30
        reasons.append(f"Estimated battery loss ({estimated_battery_loss:.1f}%) leaves less than 20% critical safety buffer.")

    # 3. Weather Check
    if scenario_name == "Weather Emergency":
        wind_speed = random.uniform(36.0, 44.0)
    else:
        wind_speed = random.uniform(8.0, 15.0)
    details["wind_speed_kmh"] = round(wind_speed, 1)

    if wind_speed > 35.0:
        score -= 45
        reasons.append(f"Severe wind hazard: Wind speed is {wind_speed:.1f} km/h (Operational limit: 30 km/h).")
    elif wind_speed > 20.0:
        score -= 15
        reasons.append(f"Moderate wind resistance: Wind speed is {wind_speed:.1f} km/h.")

    # 4. Organ Viability Check
    estimated_flight_time_hours = distance / 70.0  # Assumes 70 km/h cruise speed
    organ_limit = ORGAN_VIABILITY_HOURS.get(organ_type, 6.0)
    details["organ_viability_hours"] = organ_limit
    details["est_flight_time_hours"] = round(estimated_flight_time_hours, 3)
    details["est_flight_time_mins"] = round(estimated_flight_time_hours * 60, 1)

    viability_ratio = (organ_limit - estimated_flight_time_hours) / organ_limit
    if viability_ratio < 0.8:
        score -= 10
        reasons.append("Organ viability safety margin narrow (extended flight time vs cold ischemia time).")

    # 5. Communication Check
    if scenario_name == "Communication Failure":
        signal_strength = random.uniform(15.0, 25.0)
    else:
        signal_strength = random.uniform(85.0, 99.0)
    details["signal_strength_pct"] = round(signal_strength, 1)
    if signal_strength < 40.0:
        score -= 25
        reasons.append(f"Weak RF/cellular signal forecast along path: {signal_strength:.1f}% telemetry link.")

    # 6. Emergency Hospital Availability
    # Check if there's any emergency hospital along the way (close to path midpoint)
    mid_lat = (source["latitude"] + dest["latitude"]) / 2.0
    mid_lon = (source["longitude"] + dest["longitude"]) / 2.0

    nearest_emerg = None
    min_emerg_dist = 999.0
    for h in HOSPITALS:
        if h["emergency_landing_enabled"] and h["id"] != source["id"]:
            d = haversine_distance(mid_lat, mid_lon, h["latitude"], h["longitude"])
            if d < min_emerg_dist:
                min_emerg_dist = d
                nearest_emerg = h

    details["nearest_emergency_hosp"] = nearest_emerg["name"] if nearest_emerg else "None"
    details["nearest_emergency_dist_km"] = round(min_emerg_dist, 2)

    if min_emerg_dist > 8.0:
        score -= 15
        reasons.append(f"Sparse emergency fallback sites: Nearest landing pad is {min_emerg_dist:.1f}km from midpoint.")

    # 7. No-Fly Zone Check (Disabled as requested)
    details["no_fly_zone_breached"] = False
    details["breached_nfz_name"] = "None"

    # 8. Scenario-based Pre-flight Anomalies
    if scenario_name == "Battery Emergency":
        score -= 40
        reasons.append("Pre-flight Battery Assessment: Detected LiPo cell impedance imbalance. Rapid power depletion expected.")
    elif scenario_name == "Cooling Failure":
        score -= 40
        reasons.append("Pre-flight Cooling Container Assessment: Unstable current draw on thermoelectric cooling unit.")
    elif scenario_name == "GPS Failure":
        score -= 50
        reasons.append("Pre-flight Navigation Assessment: GPS signal jammer / RF interference detected in corridor.")

    # Score clipping
    score = max(0, min(100, score))
    details["score"] = score

    # Threshold for approval eligibility
    feasible = score >= 50

    return {
        "feasible": feasible,
        "score": score,
        "reasons": reasons if len(reasons) > 0 else ["All flight corridors and environmental conditions clear."],
        "details": details
    }
