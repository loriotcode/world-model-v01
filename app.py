"""
app.py — World Model v0.1 (UI premium stable)
"""

import os
import sys
import time
import html as _html
from pathlib import Path

import streamlit as st
import pandas as pd

# --- Configuration Streamlit (OBLIGATOIRE EN PREMIER) ---
st.set_page_config(
    page_title="World Model v0.1",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Chemin racine ---
_PROJECT_ROOT = str(Path(__file__).resolve().parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# --- Imports locaux ---
from models.world3 import run_all_scenarios, SCENARIOS
from models.planetary import load_boundaries, get_status_counts, STATUS_LABELS
from utils.charts import (
    chart_trajectories,
    chart_dashboard,
    chart_planetary_boundaries,
    chart_planetary_boundaries_as_bars,
)
from services.claude_api import analyse_scenario, extract_summary
from utils.logging_config import configure_logging

# --- Logging ---
configure_logging()

# --- Session State ---
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = False
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = []

# --- CSS PREMIUM SAFE ---
st.markdown("""
<style>
:root {
  --bg: #f8f5f0;
  --panel: #ffffff;
  --border: #d1c7b7;
  --text: #2d3748;
}

.stApp {
  background-color: var(--bg);
  color: var(--text);
}

section[data-testid="stSidebar"] {
  background-color: #f0eae2;
  border-right: 1px solid var(--border);
}

.hero {
  background: linear-gradient(135deg, #f9f7f3, #f0eae2);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 26px;
  margin-bottom: 20px;
  text-align: center;
}

.card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}

.status-card {
  padding: 10px 14px;
  border-radius: 10px;
  margin: 6px 0;
  background: #f9f7f3;
  border-left: 4px solid var(--border);
}

.status-safe { border-left-color: #4a7c59; }
.status-exceeded { border-left-color: #d68910; }
.status-critical { border-left-color: #a8323e; }

.metric-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px;
}

.footer {
  margin-top: 40px;
  padding-top: 10px;
  font-size: 0.8em;
  color: #718096;
  text-align: center;
}
</style>
""", unsafe_allow_html=True)

# --- Cache ---
@st.cache_data(ttl=3600)
def get_simulations():
    return run_all_scenarios()

@st.cache_data(ttl=3600)
def get_boundaries():
    return load_boundaries()

results = get_simulations()
boundaries = get_boundaries()
counts = get_status_counts(boundaries)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🌍 World Model")
    st.toggle("Mode mobile", key="is_mobile")
    st.divider()

    page = st.radio(
        "Navigation",
        ["🏠 Vue d'ensemble", "📈 Scénarios", "🌐 Limites planétaires", "🤖 Analyse IA"],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("**Scénarios**")
    for key, sc in SCENARIOS.items():
        st.markdown(
            f"<div style='display:flex;gap:8px;align-items:center'>"
            f"<div style='width:10px;height:10px;border-radius:50%;background:{sc['color']}'></div>"
            f"<span style='font-size:0.85em'>{_html.escape(sc['label'])}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

# --- PAGE : HOME ---
if page == "🏠 Vue d'ensemble":
    st.markdown("""
    <div class="hero">
        <h2>🌍 World Model v0.1</h2>
        <p>Simulation systémique · World3 · Limites planétaires · IA</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    bau_2050 = results["BAU"][results["BAU"]["year"] == 2050].iloc[0]
    sw_2050 = results["SW"][results["SW"]["year"] == 2050].iloc[0]

    col1.metric("Limites", f"{counts['exceeded'] + counts['critical']}/9", delta=f"{counts['critical']} critiques", delta_color="inverse")
    col2.metric("Population", f"{bau_2050['population']:.1f} Md")
    col3.metric("Ressources", f"{bau_2050['resources']*100:.0f}%", delta=f"{(bau_2050['resources']-1)*100:.0f}%", delta_color="inverse")
    col4.metric("HDI", f"{sw_2050['hdi']:.2f}/{bau_2050['hdi']:.2f}", delta=f"+{(sw_2050['hdi']-bau_2050['hdi']):.2f}")

    st.markdown("---")

    if st.session_state.is_mobile:
        var = st.selectbox("Variable", ["population", "resources", "pollution", "capital"])
        fig = chart_trajectories(results, var, is_mobile=True)
    else:
        fig = chart_dashboard(results, is_mobile=False)

    st.plotly_chart(fig, use_container_width=True, config={"responsive": True, "displayModeBar": False})

# --- PAGE : LIMITES ---
elif page == "🌐 Limites planétaires":
    col1, col2, col3 = st.columns(3)
    col1.metric("Safe", counts["safe"])
    col2.metric("Exceeded", counts["exceeded"])
    col3.metric("Critical", counts["critical"])

    if st.session_state.is_mobile:
        fig = chart_planetary_boundaries_as_bars(boundaries, is_mobile=True)
    else:
        fig = chart_planetary_boundaries(boundaries, is_mobile=False)

    st.plotly_chart(fig, use_container_width=True, config={"responsive": True, "displayModeBar": False})

    for b in boundaries:
        label, _ = STATUS_LABELS[b["status"]]
        css = f"status-{b['status']}"
        st.markdown(f"<div class='status-card {css}'><b>{b['name']}</b> — {label}</div>", unsafe_allow_html=True)

# --- PAGE : SCENARIOS ---
elif page == "📈 Scénarios":
    variable = st.selectbox(
        "Variable",
        ["population", "resources", "pollution", "capital", "life_expectancy", "food_per_capita", "hdi"]
    )

    scenarios = st.multiselect(
        "Scénarios",
        list(SCENARIOS.keys()),
        default=list(SCENARIOS.keys())
    )

    if scenarios:
        filtered = {k: results[k] for k in scenarios}
        fig = chart_trajectories(filtered, variable, is_mobile=st.session_state.is_mobile)
        st.plotly_chart(fig, use_container_width=True, config={"responsive": True, "displayModeBar": False})

# --- PAGE : IA ---
elif page == "🤖 Analyse IA":
    selected = st.selectbox("Scénario", list(SCENARIOS.keys()))

    now = time.time()
    last = st.session_state.get("last_api_call", 0)

    if now - last < 10:
        st.warning("Attendez 10s entre les analyses")

    if st.button("Analyser"):
        st.session_state["last_api_call"] = time.time()
        df = results[selected]
        summary = extract_summary(df, selected)
        analysis = analyse_scenario(selected, summary)
        st.markdown(f"<div class='card'>{analysis}</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<div class='footer'>World Model v0.1 · 2026</div>", unsafe_allow_html=True)
