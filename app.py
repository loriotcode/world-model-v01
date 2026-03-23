"""
app.py — World Model v0.1
Simulation World3 + Limites Planétaires + Analyse Claude AI
Thème : Ivoire/Papier recyclé avec graphiques bleu clair pâle
"""

import os
import sys
import time
import logging
import html as _html
import re
from pathlib import Path
import streamlit as st
import pandas as pd

# --- Configuration initiale ---
port = int(os.environ.get('PORT', 8080))
_PROJECT_ROOT = str(Path(__file__).resolve().parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# --- Imports locaux ---
from models.world3 import run_all_scenarios, SCENARIOS
from models.planetary import load_boundaries, get_status_counts, STATUS_LABELS
from utils.charts import chart_trajectories, chart_dashboard, chart_planetary_boundaries, chart_planetary_boundaries_as_bars
from services.claude_api import analyse_scenario, extract_summary
from utils.logging_config import configure_logging

# --- Logging ---
configure_logging()

# --- Détection mobile (solution native sécurisée) ---
if "is_mobile" not in st.session_state:
    user_agent = st.experimental_get_query_params().get("user_agent", [""])[0]
    # Validation stricte du user_agent pour éviter les injections
    if not re.match(r'^[a-zA-Z0-9\s\-\(\)\.,;:!?/]+$', user_agent):
        user_agent = ""
    st.session_state.is_mobile = bool(re.search(r"(android|ios|iphone|ipad|mobile)", user_agent.lower()))

# --- Initialisation des états de session ---
if "mobile_guidance_shown" not in st.session_state:
    st.session_state.mobile_guidance_shown = False
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = []

# --- CSS personnalisé (thème ivoire/bleu clair) ---
st.markdown("""
<style>
  /* Fond global — ivoire clair */
  .stApp {
    background-color: #f8f5f0;
    color: #2d3748;
  }
  /* Sidebar — papier recyclé */
  section[data-testid="stSidebar"] {
    background-color: #f0eae2;
    border-right: 1px solid #d1c7b7;
  }
  /* Métriques — fond blanc cassé */
  div[data-testid="metric-container"] {
    background-color: #ffffff;
    border: 1px solid #d1c7b7;
    border-radius: 8px;
    padding: 12px 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }
  /* Cards status — fond ivoire */
  .status-card {
    padding: 10px 14px;
    border-radius: 8px;
    margin: 4px 0;
    font-size: 0.9em;
    background-color: #f9f7f3;
    border-left: 3px solid #d1c7b7;
  }
  .status-safe     { border-left-color: #4a7c59; background-color: rgba(74, 124, 89, 0.05); }
  .status-exceeded { border-left-color: #d68910; background-color: rgba(214, 137, 16, 0.05); }
  .status-critical { border-left-color: #a8323e; background-color: rgba(168, 50, 62, 0.05); }
  /* Hero — fond texturé */
  .hero {
    background: linear-gradient(135deg, #f9f7f3 0%, #f0eae2 100%);
    border: 1px solid #d1c7b7;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  }
  /* Section headers — terre cuite */
  .section-title {
    font-size: 1.1em;
    font-weight: 600;
    color: #4a5568;
    margin: 8px 0 4px 0;
    border-bottom: 1px solid #d1c7b7;
    padding-bottom: 4px;
  }
  /* Analyse AI box — blanc avec bordure */
  .ai-output {
    background: #ffffff;
    border: 1px solid #d1c7b7;
    border-radius: 10px;
    padding: 20px;
    margin-top: 12px;
    line-height: 1.7;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }
  /* Footer — ivoire clair */
  .footer {
    text-align: center;
    color: #718096;
    font-size: 0.8em;
    margin-top: 40px;
    padding: 16px;
    border-top: 1px solid #e2e8f0;
    background-color: #f8f5f0;
  }
  /* Guidage pour les graphiques */
  .graph-guide {
    background-color: #f0eae2;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 16px;
    border-left: 3px solid #d68910;
  }
</style>
""", unsafe_allow_html=True)

# --- Cache des données ---
@st.cache_data(ttl=3600)
def get_simulations():
    return run_all_scenarios()

@st.cache_data(ttl=3600)
def get_boundaries():
    return load_boundaries()

# --- Chargement des données ---
results = get_simulations()
boundaries = get_boundaries()
counts = get_status_counts(boundaries)

# --- Config page ---
st.set_page_config(
    page_title="World Model v0.1",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Modal de guidage mobile (version Streamlit native sécurisée) ---
if st.session_state.get("is_mobile", False) and not st.session_state.mobile_guidance_shown:
    with st.expander("📱 Conseils pour mobile (cliquez pour ouvrir)", expanded=True):
        st.warning("""
        Pour une expérience optimale :
        - Tournez votre appareil en **mode paysage**.
        - Sélectionnez une variable à la fois en mode portrait.
        - Utilisez deux doigts pour zoomer.
        """)
        if st.button("Compris !"):
            st.session_state.mobile_guidance_shown = True
            st.rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🌍 World Model v0.1")
    st.markdown("*Simulation systèmes Terre*")
    st.divider()
    page = st.radio(
        "Navigation",
        ["🏠 Vue d'ensemble", "📈 Scénarios", "🌐 Limites planétaires", "🤖 Analyse IA"],
        label_visibility="collapsed"
    )
    st.divider()
    # Légende scénarios
    st.markdown("**Scénarios**")
    for key, sc in SCENARIOS.items():
        color = sc["color"]
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;margin:4px 0'>"
            f"<div style='width:12px;height:12px;border-radius:50%;background:{color};flex-shrink:0'></div>"
            f"<span style='font-size:0.85em;color:#cbd5e0'>{_html.escape(sc['label'].split('(')[0].strip())}</span>"
            f"</div>",
            unsafe_allow_html=True
        )
    st.divider()
    st.markdown(
        "<div style='font-size:0.75em;color:#4a5568'>"
        "Basé sur Meadows et al.<br><i>Limits to Growth</i> (1972)<br>"
        "Rockström et al. (2009, 2023)<br><br>"
        "World Model v0.1 — 2026"
        "</div>",
        unsafe_allow_html=True
    )

# --- PAGE : VUE D'ENSEMBLE ---
if page == "🏠 Vue d'ensemble":
    st.markdown("""
    <div class="hero">
        <h1 style="font-size:2em;margin:0;color:#2d3748">🌍 World Model v0.1</h1>
        <p style="color:#4a5568;margin:8px 0 0 0;font-size:1.05em">
            Simulation des trajectoires planétaires 1970–2100 · Limites planétaires · Analyse IA
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Métriques globales
    col1, col2, col3, col4 = st.columns(4)
    bau_2050 = results["BAU"][results["BAU"]["year"] == 2050].iloc[0]
    sw_2050  = results["SW"][results["SW"]["year"] == 2050].iloc[0]
    with col1:
        st.metric("Limites planétaires dépassées", f"{counts['exceeded'] + counts['critical']}/9",
                  delta=f"{counts['critical']} critiques", delta_color="inverse")
    with col2:
        st.metric("Population 2050 (BAU)", f"{bau_2050['population']:.1f} Md",
                  delta=f"↑ vs {results['BAU'][results['BAU']['year']==2026].iloc[0]['population']:.1f} Md (2026)")
    with col3:
        st.metric("Ressources 2050 (BAU)", f"{bau_2050['resources']*100:.0f}%",
                  delta=f"{(bau_2050['resources']-1)*100:.0f}%", delta_color="inverse")
    with col4:
        st.metric("HDI 2050 — SW vs BAU",
                  f"{sw_2050['hdi']:.2f} / {bau_2050['hdi']:.2f}",
                  delta=f"+{(sw_2050['hdi']-bau_2050['hdi']):.2f} avec transition", delta_color="normal")

    st.markdown("---")

    # --- TRAJECTOIRES (adaptatif portrait/paysage) ---
    st.markdown("### Trajectoires — 4 variables core")
    if st.session_state.get("is_mobile", False):
        st.markdown("""
        <div class="graph-guide">
        📱 <b>Conseil</b> : Tournez votre appareil en mode paysage pour une meilleure visualisation,
        ou sélectionnez une variable ci-dessous.
        </div>
        """, unsafe_allow_html=True)
        selected_var = st.selectbox(
            "Variable à afficher (mode portrait)",
            options=["population", "resources", "pollution", "capital"],
            format_func=lambda x: {
                "population": "Population (Md)",
                "resources": "Ressources (%)",
                "pollution": "Pollution",
                "capital": "Capital industriel"
            }[x]
        )
        st.plotly_chart(
            chart_trajectories(results, selected_var, is_mobile=st.session_state.get("is_mobile", False)),
            use_container_width=True,
            config={
                "responsive": True,
                "displayModeBar": False,
                "scrollZoom": True
            }
        )
    else:  # desktop
        st.plotly_chart(
            chart_dashboard(results, is_mobile=st.session_state.get("is_mobile", False)),
            use_container_width=True,
            config={"responsive": True}
        )

    # --- CONTEXTE ---
    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Qu'est-ce que ce modèle ?")
        st.markdown("""
        **World Model v0.1** est une simulation des grands systèmes Terre basée sur les équations
        du modèle World3 (Meadows et al., *Limits to Growth*, 1972).
        Il modélise les interactions entre **4 stocks planétaires** :
        - 👥 Population mondiale
        - 🏭 Capital industriel
        - ☠️ Pollution globale
        - ⛏️ Ressources non-renouvelables
        """)
    with col_b:
        st.markdown("### Les 3 scénarios")
        for key, sc in SCENARIOS.items():
            color = sc["color"]
            st.markdown(
                f"<div class='status-card' style='border-left-color:{color};background:rgba(0,0,0,0.2)'>"
                f"<b style='color:{color}'>{_html.escape(sc['label'])}</b><br>"
                f"<span style='color:#a0aec0;font-size:0.88em'>{_html.escape(sc['description'])}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("""
    <div class="footer">
        Modèle simplifié à des fins de démonstration.
        Sources : Meadows et al. (1972, 2004) · Stockholm Resilience Centre (2023) · Rockström et al. (2009)
    </div>
    """, unsafe_allow_html=True)

# --- PAGE : LIMITE PLANÉTAIRES (adaptatif) ---
elif page == "🌐 Limites planétaires":
    st.markdown("## 🌐 Les 9 limites planétaires")
    st.markdown("*Rockström et al. (2009) · Stockholm Resilience Centre (2023)*")

    # Compteurs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Zone sûre", counts["safe"])
    with col2:
        st.metric("⚠️ Dépassée", counts["exceeded"])
    with col3:
        st.metric("🔴 Critique", counts["critical"])

    st.markdown("---")

    # Graphique adaptatif
    if st.session_state.get("is_mobile", False):
        st.markdown("""
        <div class="graph-guide">
        📱 <b>Conseil</b> : Tournez votre appareil en mode paysage pour voir le graphique radar,
        ou consultez le barplot ci-dessous.
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(
            chart_planetary_boundaries_as_bars(boundaries, is_mobile=st.session_state.get("is_mobile", False)),
            use_container_width=True,
            config={"responsive": True, "displayModeBar": False}
        )
    else:
        st.plotly_chart(
            chart_planetary_boundaries(boundaries, is_mobile=st.session_state.get("is_mobile", False)),
            use_container_width=True,
            config={"responsive": True}
        )

    # Détail des limites
    st.markdown("### Détail des 9 limites")
    for b in boundaries:
        label, color = STATUS_LABELS[b["status"]]
        css_class = {"safe": "status-safe", "exceeded": "status-exceeded", "critical": "status-critical"}.get(b["status"], "status-safe")
        st.markdown(
            f"<div class='status-card {css_class}'>"
            f"<b>{_html.escape(b['name'])}</b> &nbsp; <span style='font-size:0.85em'>{_html.escape(label)}</span>"
            f"<br><span style='color:#a0aec0;font-size:0.85em'>{_html.escape(b['description'])}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

# --- PAGE : ANALYSE IA ---
elif page == "🤖 Analyse IA":
    st.markdown("## 🤖 Analyse IA — Powered by Claude")
    st.markdown("Sélectionnez un scénario pour recevoir une analyse structurée.")

    # Sélection du scénario
    selected_scenario = st.selectbox(
        "Scénario à analyser",
        options=list(SCENARIOS.keys()),
        format_func=lambda x: SCENARIOS[x]["label"]
    )
    sc = SCENARIOS[selected_scenario]
    st.markdown(
        f"<div class='status-card' style='border-left-color:{sc['color']};background:rgba(0,0,0,0.2)'>"
        f"<b style='color:{sc['color']}'>{_html.escape(sc['label'])}</b><br>"
        f"<span style='color:#a0aec0;font-size:0.88em'>{_html.escape(sc['description'])}</span>"
        f"</div>",
        unsafe_allow_html=True
    )

    # Bouton d'analyse
    now = time.time()
    last_call = st.session_state.get("last_api_call", 0)
    cooldown = 10
    btn_disabled = (now - last_call) < cooldown
    remaining = max(0, int(cooldown - (now - last_call)))

    if btn_disabled:
        st.warning(f"⏳ Analyse disponible dans {remaining}s...")

    if st.button(
        f"🤖 Analyser le scénario {selected_scenario} avec Claude",
        type="primary",
        disabled=btn_disabled
    ):
        st.session_state["last_api_call"] = time.time()
        with st.spinner("Claude analyse les trajectoires..."):
            df_selected = results[selected_scenario]
            summary = extract_summary(df_selected, selected_scenario)
            analysis = analyse_scenario(selected_scenario, summary)
            st.markdown(
                f"<div class='ai-output'>{analysis}</div>",
                unsafe_allow_html=True
            )
            # Mise à jour de l'historique (limité à 10 entrées)
            if len(st.session_state.last_analysis) >= 10:
                st.session_state.last_analysis.pop(0)
            st.session_state.last_analysis.append({
                "scenario": selected_scenario,
                "time": time.strftime("%H:%M:%S")
            })

    # Historique des analyses
    if st.session_state.last_analysis:
        st.markdown("---")
        st.markdown("### 📊 Historique des analyses")
        for i, analysis in enumerate(reversed(st.session_state.last_analysis[-3:])):  # 3 dernières
            st.markdown(
                f"<div class='status-card' style='border-left-color: #d68910; margin-bottom: 8px;'>"
                f"<b>Analyse {len(st.session_state.last_analysis)-i}</b> : "
                f"<span style='color: #2d3748;'>{analysis['scenario']} — {analysis['time']}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.info(
        "💡 **Configuration requise** : Ajoutez votre clé `ANTHROPIC_API_KEY` dans le fichier `.env` "
        "pour activer les analyses IA.",
        icon="ℹ️"
    )

# --- PAGE : SCÉNARIOS ---
elif page == "📈 Scénarios":
    st.markdown("## 📈 Exploration des scénarios")
    col_ctrl1, col_ctrl2 = st.columns([1, 2])
    with col_ctrl1:
        variable = st.selectbox(
            "Variable à afficher",
            options=["population", "resources", "pollution", "capital", "life_expectancy", "food_per_capita", "hdi"],
            format_func=lambda x: {
                "population": "Population (Md)",
                "resources": "Ressources (%)",
                "pollution": "Pollution",
                "capital": "Capital industriel",
                "life_expectancy": "Espérance de vie (ans)",
                "food_per_capita": "Nourriture/habitant",
                "hdi": "IDH"
            }[x]
        )
    with col_ctrl2:
        scenarios_shown = st.multiselect(
            "Scénarios à comparer",
            options=list(SCENARIOS.keys()),
            default=list(SCENARIOS.keys()),
            format_func=lambda x: SCENARIOS[x]["label"]
        )

    if not scenarios_shown:
        st.warning("Sélectionnez au moins un scénario.")
    else:
        filtered = {k: v for k, v in results.items() if k in scenarios_shown}
        st.plotly_chart(
            chart_trajectories(filtered, variable, is_mobile=st.session_state.get("is_mobile", False)),
            use_container_width=True,
            config={"responsive": True}
        )

    # Tableau comparatif
    st.markdown("---")
    st.markdown("### Tableau comparatif — années clés")
    years_display = [2026, 2035, 2050, 2075, 2100]
    tabs = st.tabs([SCENARIOS[k]["label"] for k in SCENARIOS])
    for tab, (key, sc) in zip(tabs, SCENARIOS.items()):
        with tab:
            df = results[key]
            rows = []
            for yr in years_display:
                r = df[df["year"] == yr].iloc[0]
                rows.append({
                    "Année": yr,
                    "Population (Md)": f"{r['population']:.2f}",
                    "Ressources (%)": f"{r['resources']*100:.0f}",
                    "Pollution": f"{r['pollution']:.3f}",
                    "Capital": f"{r['capital']:.3f}",
                    "HDI": f"{r['hdi']:.2f}",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
