import streamlit as st

st.set_page_config(
    page_title="SafeLife — AI Emergency Detection",
    page_icon="🆘",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stSidebar"] { background: #0f1117; }
.metric-card {
    background: linear-gradient(135deg, #1a1f2e, #0d1117);
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.hero-title { font-size: 2.8rem; font-weight: 800; color: #e53e3e; }
.hero-sub   { font-size: 1.2rem; color: #a0aec0; margin-top: 4px; }
.step-card {
    background: #1a1f2e;
    border-left: 4px solid #e53e3e;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.quote-box {
    background: #1a1f2e;
    border-left: 4px solid #e53e3e;
    border-radius: 8px;
    padding: 20px 24px;
    font-style: italic;
    color: #e2e8f0;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🆘 SafeLife")
    st.markdown("*AI-Powered Emergency Detection*")
    st.divider()
    st.page_link("app.py",                    label="🏠 Home")
    st.page_link("pages/1_live_monitor.py",   label="📡 Live Monitor")
    st.page_link("pages/2_analytics.py",      label="📊 Analytics")
    st.page_link("pages/3_simulation.py",     label="🎮 Simulation")
    st.page_link("pages/4_danger_map.py",     label="🗺️ Danger Map")
    st.page_link("pages/5_competitor.py",     label="📋 Comparison")
    st.divider()
    st.caption("SafeLife MVP — RSM Demo · Avqust 2026")

# Hero
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown('<p class="hero-title">🆘 SafeLife</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">When You Can\'t Call for Help, SafeLife Does It For You</p>', unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size:3rem">🆘</div>
        <div style="color:#fc8181;font-weight:700;font-size:1.4rem">MVP Demo</div>
        <div style="color:#a0aec0;font-size:0.85rem">Rəqəmsal Səhiyyə Mərkəzi</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Founder Story
st.markdown("### 💡 Niyə SafeLife?")
c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    <div class="quote-box">
    "Yanvar 2026. Piyada kimi qəzaya düçar oldum. Sürücü qaçdı. Tək qaldım.<br><br>
    Dostumun zəngi xilas etdi. Amma ya o zəng olmasaydı?<br><br>
    <strong style="color:#fc8181">SafeLife o gecə olmayan həlldir.</strong>"
    <br><br>
    <span style="color:#a0aec0">— Uğur Xəlilov, SafeLife Founder</span>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("#### Azərbaycanda Problem")
    st.markdown("""
    | | 2025 (DSK) |
    |---|---|
    | 🚨 Qəza | **1.252** |
    | 🤕 Yaralı | **1.026** |
    | 💀 Həlak | **689** |
    | 🚶 Piyada iştirakı | **41%** |
    | 👨 Həlak olanlar kişi | **77%** |
    """)
    st.error("**Gündə ~3,4 qəza. Hər dəqiqə önəmlidir.**")

st.divider()

# How it works
st.markdown("### ⚙️ Necə İşləyir?")
steps = [
    ("1", "Mod seç", "Piyada, Moto, Avtomobil — hər biri üçün fərqli həssaslıq"),
    ("2", "Sensorlar izləyir", "7 sensor arxa planda dayanmadan işləyir"),
    ("3", "Qəza aşkarlanır", "Çoxsiqnallı analiz — telefon düşməsi ilə qarışdırmır"),
    ("4", '"Yaxşısınızmı?"', "30 saniyəlik fasilə — yanlış alarm imkanı"),
    ("5", "Auto SOS", "Cavab yoxdursa GPS + tibbi məlumat göndərilir"),
    ("6", "Hamı bildirilir", "Yaxınlar + icma (500m) + ambulans eyni anda"),
]
cols = st.columns(3)
for i, (num, title, desc) in enumerate(steps):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="step-card">
            <div style="color:#e53e3e;font-weight:700">Step {num}</div>
            <div style="font-weight:600;color:#e2e8f0;margin:4px 0">{title}</div>
            <div style="color:#a0aec0;font-size:0.85rem">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# Key features
st.markdown("### 🏆 Əsas Üstünlüklər")
d1, d2, d3, d4 = st.columns(4)
with d1:
    st.markdown("""<div class="metric-card">
        <div style="font-size:2rem">👥</div>
        <div style="color:#63b3ed;font-weight:700">Community Rescue</div>
        <div style="color:#a0aec0;font-size:0.85rem">500m radiusda yaxın istifadəçilər</div>
    </div>""", unsafe_allow_html=True)
with d2:
    st.markdown("""<div class="metric-card">
        <div style="font-size:2rem">🏥</div>
        <div style="color:#68d391;font-weight:700">Xəstəxana Nav.</div>
        <div style="color:#a0aec0;font-size:0.85rem">Ən yaxın 3 xəstəxana + ETA</div>
    </div>""", unsafe_allow_html=True)
with d3:
    st.markdown("""<div class="metric-card">
        <div style="font-size:2rem">🩺</div>
        <div style="color:#f6ad55;font-weight:700">Tibbi ID</div>
        <div style="color:#a0aec0;font-size:0.85rem">Qan qrupu + allergiya ambulansa</div>
    </div>""", unsafe_allow_html=True)
with d4:
    st.markdown("""<div class="metric-card">
        <div style="font-size:2rem">🗺️</div>
        <div style="color:#fc8181;font-weight:700">Danger Map</div>
        <div style="color:#a0aec0;font-size:0.85rem">Şəhər qara nöqtə xəritəsi</div>
    </div>""", unsafe_allow_html=True)

st.divider()
st.markdown("### 🚀 Demo-ya başla")
c1, c2, c3 = st.columns(3)
with c1:
    st.page_link("pages/1_live_monitor.py", label="📡 Live Monitor — 7 sensor canlı")
with c2:
    st.page_link("pages/3_simulation.py",   label="🎮 Simulation — Qəza ssenarisi")
with c3:
    st.page_link("pages/4_danger_map.py",   label="🗺️ Danger Map — Baku hotspots")

    