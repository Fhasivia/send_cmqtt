import paho.mqtt.client as paho
import time
import streamlit as st
import json
import platform

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MQTT Control Panel",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;900&family=Share+Tech+Mono&display=swap');

:root {
    --cyan:      #00f5ff;
    --green:     #00ff88;
    --red:       #ff2d55;
    --blue-dark: #050d1a;
    --mid:       #0a1628;
    --glass:     rgba(0,245,255,0.04);
    --border:    rgba(0,245,255,0.15);
    --glow-c:    0 0 20px rgba(0,245,255,0.4);
    --glow-g:    0 0 20px rgba(0,255,136,0.4);
    --glow-r:    0 0 20px rgba(255,45,85,0.4);
}

html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 30% 0%, #071a30 0%, #050d1a 55%, #000 100%) !important;
    color: #cde8ff !important;
    font-family: 'Share Tech Mono', monospace !important;
}
[data-testid="stHeader"] { background: transparent !important; }

/* scanlines */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed; inset: 0;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 2px,
        rgba(0,245,255,0.015) 2px, rgba(0,245,255,0.015) 4px
    );
    pointer-events: none; z-index: 0;
}

.block-container {
    max-width: 700px !important;
    padding: 2rem 2rem !important;
    position: relative; z-index: 1;
}

/* ── Typography ── */
h1 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 900 !important;
    font-size: clamp(1.5rem, 4vw, 2.3rem) !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    background: linear-gradient(90deg, var(--cyan) 0%, #7df9ff 45%, var(--green) 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin-bottom: 0 !important;
}
h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.3em !important;
    color: var(--cyan) !important;
    text-transform: uppercase !important;
    opacity: 0.7;
}
p, .stMarkdown p {
    font-family: 'Share Tech Mono', monospace !important;
    color: #6a9ab8 !important;
    font-size: 0.85rem !important;
}

/* ── Divider ── */
hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1rem 0 !important; }

/* ── HUD card ── */
.hud-card {
    background: linear-gradient(135deg, rgba(0,245,255,0.04), rgba(5,13,26,0.95));
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.4rem 1.8rem;
    margin: 0.8rem 0;
    box-shadow: var(--glow-c);
    position: relative; overflow: hidden;
}
.hud-card::before {
    content: "";
    position: absolute; top:0; left:0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--cyan), var(--green));
}
.hud-card-label {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.6rem;
    letter-spacing: 0.35em;
    color: var(--cyan);
    opacity: 0.6;
    margin-bottom: 0.7rem;
    text-transform: uppercase;
}

/* ── Accent lines ── */
.accent-bar {
    display: grid; grid-template-columns: 1fr 1fr; gap: 3px; margin-bottom: 1rem;
}
.accent-bar span { height: 2px; display: block; }
.accent-bar span:nth-child(1) { background: linear-gradient(90deg, var(--cyan), transparent); }
.accent-bar span:nth-child(2) { background: linear-gradient(270deg, var(--green), transparent); }

/* ── Status info chip ── */
.info-chip {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(0,245,255,0.06);
    border: 1px solid rgba(0,245,255,0.2);
    border-radius: 3px;
    padding: 4px 12px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #4a9ab8;
    letter-spacing: 0.1em;
}
.dot-pulse {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 6px var(--green);
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.25} }

/* ── Streamlit buttons ── */
.stButton > button {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.25em !important;
    text-transform: uppercase !important;
    border-radius: 3px !important;
    padding: 0.6rem 1.6rem !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

/* ON button — green */
div[data-testid="column"]:nth-child(1) .stButton > button {
    color: var(--green) !important;
    background: rgba(0,255,136,0.05) !important;
    border: 1px solid var(--green) !important;
    box-shadow: 0 0 14px rgba(0,255,136,0.25) !important;
}
div[data-testid="column"]:nth-child(1) .stButton > button:hover {
    background: rgba(0,255,136,0.12) !important;
    box-shadow: 0 0 28px rgba(0,255,136,0.5) !important;
}

/* OFF button — red */
div[data-testid="column"]:nth-child(2) .stButton > button {
    color: var(--red) !important;
    background: rgba(255,45,85,0.05) !important;
    border: 1px solid var(--red) !important;
    box-shadow: 0 0 14px rgba(255,45,85,0.25) !important;
}
div[data-testid="column"]:nth-child(2) .stButton > button:hover {
    background: rgba(255,45,85,0.12) !important;
    box-shadow: 0 0 28px rgba(255,45,85,0.5) !important;
}

/* Send analog button — cyan (3rd col or standalone) */
div[data-testid="column"]:nth-child(3) .stButton > button,
div[data-testid="stVerticalBlock"] > div:last-child .stButton > button {
    color: var(--cyan) !important;
    background: rgba(0,245,255,0.05) !important;
    border: 1px solid var(--cyan) !important;
    box-shadow: 0 0 14px rgba(0,245,255,0.25) !important;
}
div[data-testid="column"]:nth-child(3) .stButton > button:hover {
    background: rgba(0,245,255,0.12) !important;
    box-shadow: 0 0 28px rgba(0,245,255,0.5) !important;
}

/* ── Slider ── */
[data-testid="stSlider"] > div > div > div > div {
    background: var(--cyan) !important;
}
[data-testid="stSlider"] label {
    font-family: 'Share Tech Mono', monospace !important;
    color: #4a9ab8 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.08em !important;
}

/* ── Slider value readout ── */
.slider-value-box {
    background: rgba(0,245,255,0.05);
    border: 1px solid rgba(0,245,255,0.2);
    border-radius: 4px;
    padding: 0.7rem 1.2rem;
    margin-top: 0.5rem;
    display: flex; justify-content: space-between; align-items: center;
}
.slider-value-box .label {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.6rem; letter-spacing: 0.3em; color: #4a9ab8;
}
.slider-value-box .val {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem; font-weight: 700; color: var(--cyan);
    text-shadow: 0 0 12px rgba(0,245,255,0.6);
}

/* ── Footer ── */
.hud-footer {
    margin-top: 2rem;
    border-top: 1px solid rgba(0,245,255,0.08);
    padding-top: 0.8rem;
    display: flex; justify-content: space-between;
    font-size: 0.6rem; letter-spacing: 0.18em; color: #1e4060;
}
</style>
""", unsafe_allow_html=True)


# ─── ORIGINAL LOGIC (unchanged) ───────────────────────────────────────────────
values = 0.0
act1 = "OFF"

def on_publish(client, userdata, result):
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "157.230.214.127"
port   = 1883
client1 = paho.Client("LAURA")
client1.on_message = on_message


# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown('<div class="accent-bar"><span></span><span></span></div>', unsafe_allow_html=True)
st.title("MQTT CONTROL")

py_ver = platform.python_version()
st.markdown(f"""
<div style="display:flex; align-items:center; gap:12px; margin:0.5rem 0 1.2rem;">
    <span class="info-chip"><span class="dot-pulse"></span>CONNECTED</span>
    <span class="info-chip">BROKER: {broker}:{port}</span>
    <span class="info-chip">PY {py_ver}</span>
</div>
""", unsafe_allow_html=True)

# Original st.write for python version — kept
st.write("Versión de Python:", platform.python_version())

st.markdown("---")


# ─── DIGITAL OUTPUT CONTROL ───────────────────────────────────────────────────
st.markdown('<div class="hud-card">', unsafe_allow_html=True)
st.markdown('<div class="hud-card-label">▸ Control de salida digital — Topic: lauram</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="medium")

with col1:
    if st.button('⬤  ON'):
        act1 = "ON"
        client1 = paho.Client("LAURA")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": act1})
        ret = client1.publish("lauram", message)
    else:
        st.write('')

with col2:
    if st.button('⬤  OFF'):
        act1 = "OFF"
        client1 = paho.Client("LAURA")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": act1})
        ret = client1.publish("lauram", message)
    else:
        st.write('')

st.markdown('</div>', unsafe_allow_html=True)


# ─── ANALOG OUTPUT CONTROL ────────────────────────────────────────────────────
st.markdown('<div class="hud-card">', unsafe_allow_html=True)
st.markdown('<div class="hud-card-label">▸ Control de salida analógica — Topic: lauraa</div>', unsafe_allow_html=True)

values = st.slider('Selecciona el rango de valores', 0.0, 100.0)

st.markdown(f"""
<div class="slider-value-box">
    <span class="label">VALOR SELECCIONADO</span>
    <span class="val">{values:.1f} <span style="font-size:0.55rem; color:#4a9ab8;">/ 100.0</span></span>
</div>
""", unsafe_allow_html=True)

st.write('Values:', values)   # original st.write kept

st.markdown("<br>", unsafe_allow_html=True)

if st.button('⟶  Enviar valor analógico'):
    client1 = paho.Client("LAURA")
    client1.on_publish = on_publish
    client1.connect(broker, port)
    message = json.dumps({"Analog": float(values)})
    ret = client1.publish("lauraa", message)
else:
    st.write('')

st.markdown('</div>', unsafe_allow_html=True)


# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hud-footer">
    <span>MQTT://157.230.214.127:1883</span>
    <span>CLIENT: LAURA</span>
    <span>TOPICS: lauram · lauraa</span>
</div>
""", unsafe_allow_html=True)




