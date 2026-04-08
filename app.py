"""
app.py — World Model v0.1
Landscape-first smartphone · thème warm original
Sécurité / robustesse / économie v2
"""

import re
import sys
import time
import html as _html
import logging
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="World Model v0.1",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── PATH ────────────────────────────────────────────────────────────────────
_ROOT = str(Path(__file__).resolve().parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from models.world3 import run_all_scenarios, SCENARIOS
from models.planetary import load_boundaries, get_status_counts, STATUS_LABELS
from utils.charts import (
    chart_trajectories,
    chart_planetary_boundaries_as_bars,
    chart_boundary_feedback_network,
    chart_earth4all_architecture,
    chart_levers_diagram,
    chart_system_diagram,
    STATUS_COLORS,
)
from utils.styles import STYLES
from services.claude_api import analyse_scenario, extract_summary
try:
    from services.iso_component import build_iso_html
    _ISO_OK = True
except Exception as _iso_err:
    _ISO_OK = False
    build_iso_html = None
from utils.logging_config import configure_logging

configure_logging()
log = logging.getLogger(__name__)

# ─── SESSION STATE ────────────────────────────────────────────────────────────
_SS_DEFAULTS = {"last_api_call": 0.0, "last_analysis": "", "last_scenario": "", "active_tab": 0}
for k, v in _SS_DEFAULTS.items():
    st.session_state.setdefault(k, v)

# ─── CONSTANTES ──────────────────────────────────────────────────────────────
COOLDOWN_S   = 10
CHART_LAYOUT = dict(
    height  = 520,
    margin  = dict(l=30, r=10, t=30, b=30),
    font    = dict(size=11),
    legend  = dict(orientation="h", yanchor="bottom", y=1.02,
                   xanchor="right", x=1, font=dict(size=11)),
)
PLOTLY_CFG = dict(responsive=True, displayModeBar=False,
                  scrollZoom=False, doubleClick=False, displaylogo=False)

# Whitelist des variables (sécurité)
VARIABLES = ["population", "resources", "pollution", "capital",
             "life_expectancy", "food_per_capita", "hdi"]

PAGES = ["📈 Modèle", "🌐 Limites", "🔄 Système", "🤖 IA"]

# ─── HELPERS ─────────────────────────────────────────────────────────────────
_COLOR_RE  = re.compile(r'^#[0-9a-fA-F]{3,6}$')
_HTML_TAGS = re.compile(r'<[^>]+>')

def _safe_html(value) -> str:
    return _html.escape(str(value))

def _safe_color(color: str, fallback: str = "#888888") -> str:
    """Valide un code couleur hex avant injection dans un attribut style."""
    c = str(color).strip()
    return c if _COLOR_RE.match(c) else fallback

def _strip_html(text: str) -> str:
    """Supprime les balises HTML d'un texte (output LLM) avant affichage unsafe."""
    return _HTML_TAGS.sub("", str(text))

def _render_chart(fig, key: str):
    fig.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CFG, key=key)

def _get_year_row(data: dict, scenario: str, year: int):
    df = data.get(scenario)
    if df is None or df.empty:
        return None
    rows = df[df["year"] == year]
    return rows.iloc[0] if not rows.empty else None

# ─── CHARGEMENT DONNÉES ───────────────────────────────────────────────────────
@st.cache_resource
def _load_simulations():
    try:
        return run_all_scenarios()
    except Exception:
        log.exception("Erreur chargement simulations")
        return {}

@st.cache_resource
def _load_boundaries():
    try:
        return load_boundaries()
    except Exception:
        log.exception("Erreur chargement limites planétaires")
        return []

results    = _load_simulations()
boundaries = _load_boundaries()
counts     = get_status_counts(boundaries) if boundaries else {"safe": 0, "exceeded": 0, "critical": 0}

if not results:
    st.error("Impossible de charger les simulations. Vérifiez les logs.")
    st.stop()

bau_2050 = _get_year_row(results, "BAU", 2050)
sw_2050  = _get_year_row(results, "SW",  2050)

# ─── CSS + JS ────────────────────────────────────────────────────────────────
st.markdown(STYLES, unsafe_allow_html=True)

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='wm-header'><h1>Our World Model.v01</h1></div>",
    unsafe_allow_html=True,
)

# ─── KPI values ──────────────────────────────────────────────────────────────
pop_val = f"{bau_2050['population']:.1f}" if bau_2050 is not None else "—"
res_val = f"{bau_2050['resources']*100:.0f}%" if bau_2050 is not None else "—"
lim_val = f"{counts['exceeded'] + counts['critical']}/9"

# ─── NAVIGATION (radio horizontal, styled as cubes) ──────────────────────────
_NAV_OPTS = [
    f"📈 Modèle\n{pop_val} Md",
    f"🌐 Limites\n{lim_val}",
    f"🔄 Système\n{res_val}",
    "🤖 IA",
    "🏙 Simulation",
    "🛠 Code",
]
_nav_sel = st.radio("nav", _NAV_OPTS, horizontal=True,
                    label_visibility="collapsed", key="nav_radio")
active = _NAV_OPTS.index(_nav_sel)

# ══ Contenu conditionnel selon onglet actif ══════════════════════════════════

if active == 0:   # ── Modèle
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        model_src = st.selectbox(
            "Modèle", ["WorldDynamics.jl (World3)", "Earth4All.jl"],
            key="model_src", label_visibility="collapsed",
        )
    with c2:
        variable = st.selectbox("Variable", VARIABLES, key="v_sc",
                                label_visibility="collapsed")
    with c3:
        sc_keys     = list(SCENARIOS.keys())
        selected_sc = st.multiselect("Scénarios", sc_keys, default=sc_keys,
                                     key="sc_sel", label_visibility="collapsed")
        selected_sc = [k for k in selected_sc if k in SCENARIOS]

    if model_src == "Earth4All.jl":
        st.info("Earth4All.jl — intégration en cours. Données placeholder.")
        fig_e4a = chart_earth4all_architecture()
        fig_e4a.update_layout(height=520)
        st.plotly_chart(fig_e4a, use_container_width=True, config=PLOTLY_CFG,
                        key="chart_e4a_model")
    else:
        if selected_sc:
            _render_chart(chart_trajectories(
                {k: results[k] for k in selected_sc}, variable,
            ), key="chart_scenarios")
        else:
            st.info("Sélectionne au moins un scénario.")

elif active == 1:   # ── Limites
    st.markdown(f"""
    <div class="status-row">
      <span class="status-pill pill-safe">✓ {counts['safe']} Safe</span>
      <span class="status-pill pill-exceeded">⚠ {counts['exceeded']} Dépassée</span>
      <span class="status-pill pill-critical">✗ {counts['critical']} Critique</span>
    </div>""", unsafe_allow_html=True)

    if boundaries:
        fig_bars = chart_planetary_boundaries_as_bars(boundaries)
        fig_bars.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=8),
                               font=dict(size=9))
        st.plotly_chart(fig_bars, use_container_width=True, config=PLOTLY_CFG,
                        key="chart_boundaries")

        st.markdown("**Réseau de rétroaction**", help="Flèches rouges = amplifying · Bleues = dampening · Bordure rouge = irréversible")
        fig_net = chart_boundary_feedback_network(boundaries)
        fig_net.update_layout(height=460)
        st.plotly_chart(fig_net, use_container_width=True, config=PLOTLY_CFG,
                        key="chart_feedback_net")

        for b in boundaries:
            label, _ = STATUS_LABELS[b["status"]]
            color = _safe_color(STATUS_COLORS.get(b["status"], "#888888"))
            irr_badge = "<span class='irrev-badge'>IRRÉVERSIBLE</span>" if b.get("irreversible") else ""
            st.markdown(
                f"<div class='bound-item'>"
                f"<div class='bound-dot' style='background:{color}'></div>"
                f"<span>{_safe_html(b['name'])}{irr_badge}</span>"
                f"<span style='margin-left:auto;color:{color}'>{_safe_html(label)}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.warning("Données limites planétaires indisponibles.")

elif active == 2:   # ── Système
    _model = st.session_state.get("model_src", "WorldDynamics.jl (World3)")
    if _model == "Earth4All.jl":
        st.markdown("**Architecture Earth4All**")
        fig_e4a = chart_earth4all_architecture()
        fig_e4a.update_layout(height=460)
        st.plotly_chart(fig_e4a, use_container_width=True, config=PLOTLY_CFG,
                        key="chart_e4a_sys")
        st.markdown("**Leviers & Tipping Points**")
        fig_lev = chart_levers_diagram()
        fig_lev.update_layout(height=460)
        st.plotly_chart(fig_lev, use_container_width=True, config=PLOTLY_CFG,
                        key="chart_levers")
    else:
        fig_sys = chart_system_diagram()
        fig_sys.update_layout(height=520)
        st.plotly_chart(fig_sys, use_container_width=True,
                        config=PLOTLY_CFG, key="chart_system")

elif active == 3:   # ── IA
    main_col, panel_col = st.columns([3, 1])
    with main_col:
        c1, c2 = st.columns([2, 1])
        with c1:
            ia_sc = st.selectbox("Scénario", list(SCENARIOS.keys()), key="ia_sc",
                                 label_visibility="collapsed")
        with c2:
            now = time.time()
            try:
                _last_call = float(st.session_state.get("last_api_call", 0.0))
            except (TypeError, ValueError):
                _last_call = 0.0
                st.session_state["last_api_call"] = 0.0
            cooldown = now - _last_call < COOLDOWN_S
            btn = st.button("Analyser", disabled=cooldown)

        if cooldown:
            remaining = int(COOLDOWN_S - (now - _last_call))
            st.warning(f"Patientez {remaining}s")

        if btn and ia_sc in results:
            st.session_state.last_api_call = time.time()
            st.session_state.last_scenario = ia_sc
            try:
                summary = extract_summary(results[ia_sc], ia_sc)
                with st.spinner("Analyse en cours…"):
                    st.session_state.last_analysis = _strip_html(analyse_scenario(ia_sc, summary))
            except Exception:
                log.exception("Erreur analyse IA")
                st.error("Erreur lors de l'analyse. Vérifiez la clé API et réessayez.")

        if st.session_state.get("last_analysis"):
            st.markdown(
                f"<div class='ia-result'>{st.session_state.get('last_analysis', '')}</div>",
                unsafe_allow_html=True,
            )
        elif not btn:
            st.markdown(
                "<div class='ia-empty'>Sélectionne un scénario et lance l'analyse.</div>",
                unsafe_allow_html=True,
            )
        st.markdown("---")
        st.markdown("**Pixel Agents — Bureau IA**")
        st.image(
            "https://raw.githubusercontent.com/pablodelucca/pixel-agents/main/webview-ui/public/Screenshot.jpg",
            use_container_width=True,
        )

    with panel_col:
        st.markdown("#### Orchestration")
        st.selectbox("Type", ["Séquentiel", "Parallèle", "Hiérarchique"],
                     key="orch_type", label_visibility="collapsed")
        st.markdown("---")
        st.markdown("#### Outils")
        postal = st.text_input("Code postal", key="postal_code",
                               label_visibility="collapsed", placeholder="Code postal…")
        if postal:
            st.info(f"Recherche ONH région {postal}…")

elif active == 4:   # ── Simulation isométrique
    if not _ISO_OK:
        st.error(f"Erreur chargement composant iso : {_iso_err}")
    else:
        import streamlit.components.v1 as components
        components.html(build_iso_html(results), height=900, scrolling=False)

elif active == 5:   # ── Code & GitHub
    st.markdown("### Code & Contributions")
    st.markdown(
        "**Repository:** "
        "[world-model-v01](https://github.com/loriotcode/world-model-v01)"
    )
    st.markdown("**Stack:** Streamlit 1.43.2 · Plotly 5.20 · World3 (Python) · Canvas ISO")
    st.markdown("**Deploy:** Railway (branche main)")
    st.markdown("---")
    st.markdown(
        "**Modèles:** WorldDynamics.jl (World3 simplifié) · Earth4All.jl (placeholder)\n\n"
        "**Données:** 9 limites planétaires (Stockholm Resilience Centre 2023) · "
        "3 scénarios (BAU, BAU2, SW) · Simulation 1970–2100"
    )

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='wm-footer'>"
    "<a href='https://github.com/loriotcode/world-model-v01' target='_blank'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True,
)
