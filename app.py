"""
app.py — World Model v0.1
Simulation World3 + Limites Planétaires + Analyse Claude AI
"""

import streamlit as st
import sys
import time
import logging
import html as _html
from pathlib import Path

# Path setup — ajout du répertoire du projet uniquement s'il n'est pas déjà présent
_PROJECT_ROOT = str(Path(__file__).resolve().parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from models.world3 import run_all_scenarios, SCENARIOS
from models.planetary import load_boundaries, get_status_counts, STATUS_LABELS
from utils.charts import chart_trajectories, chart_dashboard, chart_planetary_boundaries
import pandas as pd
from services.claude_api import analyse_scenario, extract_summary
from utils.logging_config import configure_logging

# Logging — configuré une fois au démarrage
configure_logging()

# ── Config page ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="World Model v0.1",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS custom ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
  /* Fond global */
  .stApp { background-color: #0e1117; }
  
  /* Sidebar */
  section[data-testid="stSidebar"] { background-color: #12151f; }
  
  /* Métriques */
  div[data-testid="metric-container"] {
    background-color: #1a1f2e;
    border: 1px solid #2a3040;
    border-radius: 8px;
    padding: 12px 16px;
  }
  
  /* Cards status */
  .status-card {
    padding: 10px 14px;
    border-radius: 8px;
    margin: 4px 0;
    font-size: 0.9em;
  }
  .status-safe     { background: rgba(39,174,96,0.15); border-left: 3px solid #27ae60; }
  .status-exceeded { background: rgba(230,126,34,0.15); border-left: 3px solid #e67e22; }
  .status-critical { background: rgba(231,76,60,0.15);  border-left: 3px solid #e74c3c; }
  
  /* Header hero */
  .hero {
    background: linear-gradient(135deg, #0e1117 0%, #1a1f2e 50%, #0e1117 100%);
    border: 1px solid #2a3040;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    text-align: center;
  }
  
  /* Section headers */
  .section-title {
    font-size: 1.1em;
    font-weight: 600;
    color: #a0aec0;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 8px 0 4px 0;
  }
  
  /* Analyse AI box */
  .ai-output {
    background: #1a1f2e;
    border: 1px solid #2d4a7a;
    border-radius: 10px;
    padding: 20px;
    margin-top: 12px;
    line-height: 1.7;
  }
  
  /* Badges scénario */
  .badge-bau  { color: #e74c3c; font-weight: 700; }
  .badge-bau2 { color: #e67e22; font-weight: 700; }
  .badge-sw   { color: #27ae60; font-weight: 700; }
  
  /* Footer */
  .footer {
    text-align: center;
    color: #4a5568;
    font-size: 0.8em;
    margin-top: 40px;
    padding: 16px;
    border-top: 1px solid #1a1f2e;
  }
</style>
""", unsafe_allow_html=True)


# ── Cache simulations ─────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_simulations():
    return run_all_scenarios()


@st.cache_data(ttl=3600)
def get_boundaries():
    return load_boundaries()


# ── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🌍 World Model v0.1")
    st.markdown("*Simulation systèmes Terre*")
    st.divider()

    # Navigation
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


# ── Chargement données ────────────────────────────────────────────────────────

results = get_simulations()
boundaries = get_boundaries()
counts = get_status_counts(boundaries)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE : VUE D'ENSEMBLE
# ══════════════════════════════════════════════════════════════════════════════

if page == "🏠 Vue d'ensemble":

    # Hero
    st.markdown("""
    <div class="hero">
        <h1 style="font-size:2em;margin:0;color:#e2e8f0">🌍 World Model v0.1</h1>
        <p style="color:#718096;margin:8px 0 0 0;font-size:1.05em">
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

    # Dashboard 4 variables
    st.markdown("### Trajectoires — 4 variables core")
    st.plotly_chart(chart_dashboard(results), use_container_width=True)

    # Contexte
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

        Ces stocks interagissent via des **boucles de rétroaction** positives et négatives 
        qui produisent des trajectoires divergentes selon les choix sociétaux.
        """)

    with col_b:
        st.markdown("### Les 3 scénarios")
        for key, sc in SCENARIOS.items():
            color = sc["color"]
            st.markdown(
                f"<div class='status-card' style='border-left-color:{color};background:rgba(0,0,0,0.2)'>"
                f"<b style='color:{color}'>{_html.escape(sc['label'])}</b><br>"
                f"<span style='color:#a0aec0;font-size:0.9em'>{_html.escape(sc['description'])}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("""
    <div class="footer">
        Modèle simplifié à des fins de démonstration. 
        Sources : Meadows et al. (1972, 2004) · Stockholm Resilience Centre (2023) · Rockström et al. (2009)
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE : SCÉNARIOS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📈 Scénarios":

    st.markdown("## 📈 Exploration des scénarios")

    col_ctrl1, col_ctrl2 = st.columns([1, 2])
    with col_ctrl1:
        variable = st.selectbox(
            "Variable à afficher",
            options=["population", "resources", "pollution", "capital",
                     "life_expectancy", "food_per_capita", "hdi"],
            format_func=lambda x: {
                "population": "Population (Md)",
                "resources": "Ressources non-renouvelables",
                "pollution": "Pollution globale",
                "capital": "Capital industriel",
                "life_expectancy": "Espérance de vie (ans)",
                "food_per_capita": "Nourriture par habitant",
                "hdi": "IDH approximatif",
            }[x]
        )

    with col_ctrl2:
        scenarios_shown = st.multiselect(
            "Scénarios à comparer",
            options=list(SCENARIOS.keys()),
            default=list(SCENARIOS.keys()),
            format_func=lambda x: SCENARIOS[x]["label"]
        )

    _VALID_VARIABLES = {"population", "resources", "pollution", "capital",
                         "life_expectancy", "food_per_capita", "hdi"}
    if not scenarios_shown:
        st.warning("Sélectionnez au moins un scénario.")
    elif variable not in _VALID_VARIABLES:
        st.error("Variable invalide.")
    else:
        filtered = {k: v for k, v in results.items() if k in scenarios_shown}
        st.plotly_chart(chart_trajectories(filtered, variable), use_container_width=True)

    st.markdown("---")

    # Tableau comparatif
    st.markdown("### Tableau comparatif — années clés")

    years_display = [2026, 2035, 2050, 2075, 2100]
    var_display = ["population", "resources", "pollution", "capital", "hdi"]
    var_labels  = ["Population (Md)", "Ressources", "Pollution", "Capital", "HDI"]

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
                    "Ressources": f"{r['resources']*100:.0f}%",
                    "Pollution": f"{r['pollution']:.3f}",
                    "Capital": f"{r['capital']:.3f}",
                    "HDI": f"{r['hdi']:.2f}",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.markdown(
                f"<div class='status-card' style='border-left-color:{sc['color']};background:rgba(0,0,0,0.2);margin-top:8px'>"
                f"<b style='color:{sc['color']}'>{_html.escape(sc['label'])}</b> — {_html.escape(sc['description'])}"
                f"</div>",
                unsafe_allow_html=True
            )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE : LIMITES PLANÉTAIRES
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🌐 Limites planétaires":

    st.markdown("## 🌐 Les 9 limites planétaires")
    st.markdown(
        "*Rockström et al. (2009) · Stockholm Resilience Centre (2023)*"
    )

    # Compteurs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Zone sûre", counts["safe"])
    with col2:
        st.metric("⚠️ Dépassée", counts["exceeded"])
    with col3:
        st.metric("🔴 Critique", counts["critical"])

    st.markdown("---")

    col_radar, col_list = st.columns([1.2, 1])

    with col_radar:
        st.plotly_chart(chart_planetary_boundaries(boundaries), use_container_width=True)

    with col_list:
        st.markdown("### Détail des 9 limites")
        for b in boundaries:
            label, color = STATUS_LABELS[b["status"]]
            # Whitelist css_class — b['status'] validé par load_boundaries() mais défense en profondeur
            _css_safe = {"safe": "status-safe", "exceeded": "status-exceeded", "critical": "status-critical"}
            css_class = _css_safe.get(b["status"], "status-safe")

            indicator_str = ""
            if b.get("safe_limit") and b.get("current"):
                indicator_str = (
                    f"<br><span style='color:#718096;font-size:0.82em'>"
                    f"Limite sûre : {b['safe_limit']} · Actuel : {b['current']} ({_html.escape(str(b['indicator']))})"
                    f"</span>"
                )

            st.markdown(
                f"<div class='status-card {css_class}'>"
                f"<b>{_html.escape(b['name'])}</b> &nbsp; <span style='font-size:0.85em'>{_html.escape(label)}</span>"
                f"{indicator_str}"
                f"<br><span style='color:#a0aec0;font-size:0.85em'>{_html.escape(b['description'])}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.markdown("""
    **Pourquoi c'est important pour World Model ?**
    
    Les 9 limites planétaires définissent l'**espace opératoire sûr** pour les civilisations humaines.
    7 sont aujourd'hui dépassées. Le modèle World3 simule les *conséquences dynamiques* de ces 
    dépassements sur un siècle — population, capital, pollution et ressources interagissent 
    en boucles de rétroaction qui peuvent mener au collapse ou à la stabilisation selon les choix faits 
    **dans la fenêtre 2025-2035**.
    """)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE : ANALYSE IA
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🤖 Analyse IA":

    st.markdown("## 🤖 Analyse IA — Powered by Claude")
    st.markdown(
        "Sélectionnez un scénario pour recevoir une analyse structurée par Claude (Anthropic)."
    )

    col_sel, col_info = st.columns([1, 2])

    with col_sel:
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

    with col_info:
        df_selected = results[selected_scenario]
        summary = extract_summary(df_selected, selected_scenario)

        st.markdown("**Données transmises à Claude :**")
        col_y1, col_y2, col_y3 = st.columns(3)
        with col_y1:
            st.markdown("**2025**")
            st.markdown(f"Pop : {summary['pop_2025']} Md")
            st.markdown(f"Res : {summary['res_2025']*100:.0f}%")
            st.markdown(f"Pol : {summary['pol_2025']:.3f}")
        with col_y2:
            st.markdown("**2050**")
            st.markdown(f"Pop : {summary['pop_2050']} Md")
            st.markdown(f"Res : {summary['res_2050']*100:.0f}%")
            st.markdown(f"Pol : {summary['pol_2050']:.3f}")
        with col_y3:
            st.markdown("**2100**")
            st.markdown(f"Pop : {summary['pop_2100']} Md")
            st.markdown(f"Res : {summary['res_2100']*100:.0f}%")
            st.markdown(f"HDI : {summary['hdi_2100']:.2f}")

    st.markdown("---")

    # Graphique mini du scénario sélectionné
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.plotly_chart(
            chart_trajectories({selected_scenario: results[selected_scenario]}, "resources"),
            use_container_width=True
        )
    with col_g2:
        st.plotly_chart(
            chart_trajectories({selected_scenario: results[selected_scenario]}, "population"),
            use_container_width=True
        )

    # Bouton analyse
    # Rate limiting : 1 appel / 10s par session
    now = time.time()
    last_call = st.session_state.get("last_api_call", 0)
    cooldown = 10  # secondes

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
            analysis = analyse_scenario(selected_scenario, summary)

        # La sortie est sanitisée dans claude_api.py (HTML-escaped + Markdown limité)
        st.markdown(
            f"<div class='ai-output'>{analysis}</div>",
            unsafe_allow_html=True
        )

    # Note API
    st.markdown("---")
    st.info(
        "💡 **Configuration requise** : Ajoutez votre clé `ANTHROPIC_API_KEY` dans le fichier `.env` "
        "pour activer les analyses IA. Sans clé, un message d'erreur s'affiche.",
        icon="ℹ️"
    )
