import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

MODES = {
    "Pedestrian": {"accel_thresh": 2.5, "speed_thresh": 15, "sensitivity": 0.85},
    "Motorcycle": {"accel_thresh": 4.0, "speed_thresh": 80, "sensitivity": 0.90},
    "Vehicle":    {"accel_thresh": 5.0, "speed_thresh": 120, "sensitivity": 0.80},
}

SCENARIOS = {
    "Normal walking":      {"accel": 1.1, "gyro": 0.3, "baro": 0.01, "light": 0.9, "mag": 0.1, "noise": 0.15, "accident": False},
    "Normal riding":       {"accel": 2.1, "gyro": 1.2, "baro": 0.05, "light": 0.7, "mag": 0.3, "noise": 0.2,  "accident": False},
    "Dropped phone":       {"accel": 3.8, "gyro": 2.5, "baro": 0.08, "light": 0.1, "mag": 0.2, "noise": 0.3,  "accident": False},
    "Pedestrian accident": {"accel": 8.5, "gyro": 5.2, "baro": 0.25, "light": 0.05,"mag": 0.8, "noise": 0.4,  "accident": True},
    "Motorcycle crash":    {"accel": 12.0,"gyro": 9.8, "baro": 0.40, "light": 0.02,"mag": 1.2, "noise": 0.5,  "accident": True},
    "Car collision":       {"accel": 15.0,"gyro": 7.5, "baro": 0.55, "light": 0.03,"mag": 1.8, "noise": 0.6,  "accident": True},
}

def generate_realtime_frame(scenario_name, t, mode="Pedestrian"):
    s = SCENARIOS[scenario_name]
    n = s["noise"]
    accel = max(0, s["accel"] + np.random.normal(0, n * s["accel"]))
    gyro  = max(0, s["gyro"]  + np.random.normal(0, n * s["gyro"]))
    gps   = max(0, (accel * 3.6) + np.random.normal(0, 2))
    mic   = max(0, min(100, (accel * 6) + np.random.normal(0, 5)))
    baro  = max(0, s["baro"]  + np.random.normal(0, 0.01))
    light = max(0, min(1, s["light"] + np.random.normal(0, 0.05)))
    mag   = max(0, s["mag"]   + np.random.normal(0, 0.05))
    thresh = MODES[mode]["accel_thresh"]
    risk_raw = (
        (accel / (thresh * 2)) * 35 +
        (gyro  / 10)           * 25 +
        (mic   / 100)          * 15 +
        (baro  / 0.6)          * 10 +
        (1 - light)            * 10 +
        (mag   / 2.0)          * 5
    )
    risk = min(100, max(0, risk_raw + np.random.normal(0, 3)))
    return {
        "time": t,
        "accelerometer": round(accel, 3),
        "gyroscope":     round(gyro, 3),
        "gps_speed":     round(gps, 1),
        "microphone":    round(mic, 1),
        "barometer":     round(baro, 4),
        "light_sensor":  round(light, 3),
        "magnetometer":  round(mag, 3),
        "risk_score":    round(risk, 1),
        "scenario":      scenario_name,
        "accident":      s["accident"],
    }

def generate_history(n_events=200):
    rows = []
    base = datetime.now() - timedelta(days=30)
    for i in range(n_events):
        t = base + timedelta(minutes=random.randint(0, 43200))
        sc = random.choices(list(SCENARIOS.keys()), weights=[30,20,15,15,10,10])[0]
        mode = random.choice(list(MODES.keys()))
        frame = generate_realtime_frame(sc, t, mode)
        frame["mode"] = mode
        rows.append(frame)
    return pd.DataFrame(rows).sort_values("time").reset_index(drop=True)

def generate_stream(scenario_name, n_frames=60, mode="Pedestrian"):
    frames = []
    base = datetime.now()
    for i in range(n_frames):
        t = base + timedelta(seconds=i * 0.5)
        frames.append(generate_realtime_frame(scenario_name, t, mode))
    return pd.DataFrame(frames)

BAKU_HOTSPOTS = [
    {"lat": 40.3729, "lon": 49.8404, "zone": "Nizami küçəsi",        "incidents": 45, "severity": "high"},
    {"lat": 40.3791, "lon": 49.8527, "zone": "28 May metro",          "incidents": 62, "severity": "high"},
    {"lat": 40.4017, "lon": 49.8607, "zone": "Gənclik metro",         "incidents": 38, "severity": "high"},
    {"lat": 40.3662, "lon": 49.8353, "zone": "Sahil metro",           "incidents": 19, "severity": "low"},
    {"lat": 40.3503, "lon": 49.8434, "zone": "Bayıl",                 "incidents": 22, "severity": "medium"},
    {"lat": 40.4676, "lon": 49.8222, "zone": "Binəqədi",              "incidents": 28, "severity": "medium"},
    {"lat": 40.3614, "lon": 49.7997, "zone": "Biləcəri",              "incidents": 17, "severity": "low"},
    {"lat": 40.4675, "lon": 50.0467, "zone": "Heydar Əliyev Hava Limanı", "incidents": 31, "severity": "medium"},
]

COMPETITORS = {
    "Feature": [
        "Pedestrian Mode","Motorcycle Mode","Works on any phone",
        "Multi-sensor analysis","Unconscious user scenario",
        "Phone separation detection","Manual SOS button",
        "AI severity analysis","Free tier available",
        "Hospital navigation","Medical ID to ambulance",
        "Community rescue (500m)","7-sensor detection",
    ],
    "SafeLife":      ["✅","✅","✅","✅","✅","✅","✅","✅","✅","✅","✅","✅","✅"],
    "RealRider SOS": ["❌","✅","✅","❌","❌","❌","✅","❌","✅","❌","❌","❌","❌"],
    "Detecht":       ["✅","✅","✅","✅","✅","❌","✅","❌","❌","❌","❌","❌","❌"],
    "SOSmart":       ["✅","❌","✅","❌","❌","❌","✅","❌","✅","❌","❌","❌","❌"],
}

