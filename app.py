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
_SS_DEFAULTS = {"last_api_call": 0.0, "last_analysis": "", "last_scenario": ""}
for k, v in _SS_DEFAULTS.items():
    st.session_state.setdefault(k, v)

# ─── CONSTANTES ──────────────────────────────────────────────────────────────
COOLDOWN_S   = 10
CHART_LAYOUT = dict(
    height  = 400,
    margin  = dict(l=30, r=10, t=20, b=30),
    font    = dict(size=9),
    legend  = dict(orientation="h", yanchor="bottom", y=1.02,
                   xanchor="right", x=1, font=dict(size=9)),
)
PLOTLY_CFG = dict(responsive=True, displayModeBar=False,
                  scrollZoom=False, doubleClick=False, displaylogo=False)

# Whitelist des variables (sécurité)
VARIABLES = ["population", "resources", "pollution", "capital",
             "life_expectancy", "food_per_capita", "hdi"]

PAGES = ["🏠 Aperçu", "📈 Scénarios", "🌐 Limites", "🔄 Système", "🤖 IA"]

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
    "<div class='wm-header'><span>🌍</span><h1>World Model v0.1</h1>"
    "<span class='sub'>2026 · Simondon SW</span></div>",
    unsafe_allow_html=True,
)

# ─── MÉTRIQUES ───────────────────────────────────────────────────────────────
pop_val = f"{bau_2050['population']:.1f}" if bau_2050 is not None else "—"
res_val = f"{bau_2050['resources']*100:.0f}%" if bau_2050 is not None else "—"
hdi_sw  = f"{sw_2050['hdi']:.2f}"  if sw_2050  is not None else "—"
hdi_bau = f"{bau_2050['hdi']:.2f}" if bau_2050 is not None else "—"

st.markdown(f"""
<div class="wm-metrics">
  <div class="wm-metric">
    <div class="val">{counts['exceeded'] + counts['critical']}/9</div>
    <div class="lbl">Limites</div>
    <div class="delta">{counts['critical']} crit.</div>
  </div>
  <div class="wm-metric">
    <div class="val">{_safe_html(pop_val)}</div>
    <div class="lbl">Pop. 2050 Md</div>
    <div class="delta">BAU</div>
  </div>
  <div class="wm-metric">
    <div class="val">{_safe_html(res_val)}</div>
    <div class="lbl">Ressources</div>
    <div class="delta">BAU 2050</div>
  </div>
  <div class="wm-metric">
    <div class="val">{_safe_html(hdi_sw)}</div>
    <div class="lbl">HDI SW</div>
    <div class="delta">vs {_safe_html(hdi_bau)}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── NAVIGATION ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠", "📈", "🌐", "🔄", "🤖", "🏙"])

# ══ TAB 1 : Aperçu ═══════════════════════════════════════════════════════════
with tab1:
    var_home = st.selectbox("Variable", VARIABLES[:5], key="v_home",
                            label_visibility="collapsed")
    _render_chart(chart_trajectories(results, var_home), key="chart_home")

    cols = st.columns(len(SCENARIOS))
    for col, (_, sc) in zip(cols, SCENARIOS.items()):
        col.markdown(
            f"<div class='sc-legend'>"
            f"<div class='sc-dot' style='background:{_safe_color(sc['color'])}'></div>"
            f"{_safe_html(sc['label'])}</div>",
            unsafe_allow_html=True,
        )

# ══ TAB 2 : Scénarios ════════════════════════════════════════════════════════
with tab2:
    c1, c2 = st.columns(2)
    with c1:
        variable = st.selectbox("Variable", VARIABLES, key="v_sc",
                                label_visibility="collapsed")
    with c2:
        sc_keys     = list(SCENARIOS.keys())
        selected_sc = st.multiselect("Scénarios", sc_keys, default=sc_keys,
                                     key="sc_sel", label_visibility="collapsed")
        selected_sc = [k for k in selected_sc if k in SCENARIOS]  # whitelist

    if selected_sc:
        _render_chart(chart_trajectories(
            {k: results[k] for k in selected_sc}, variable,
        ), key="chart_scenarios")
    else:
        st.info("Sélectionne au moins un scénario.")

# ══ TAB 3 : Limites ══════════════════════════════════════════════════════════
with tab3:
    st.markdown(f"""
    <div class="status-row">
      <span class="status-pill pill-safe">✓ {counts['safe']} Safe</span>
      <span class="status-pill pill-exceeded">⚠ {counts['exceeded']} Dépassée</span>
      <span class="status-pill pill-critical">✗ {counts['critical']} Critique</span>
    </div>""", unsafe_allow_html=True)

    if boundaries:
        fig = chart_planetary_boundaries_as_bars(boundaries)
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=12, b=8), font=dict(size=8))
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CFG, key="chart_boundaries")

        for b in boundaries:
            label, _ = STATUS_LABELS[b["status"]]
            color = _safe_color(STATUS_COLORS.get(b["status"], "#888888"))
            st.markdown(
                f"<div class='bound-item'>"
                f"<div class='bound-dot' style='background:{color}'></div>"
                f"<span>{_safe_html(b['name'])}</span>"
                f"<span style='margin-left:auto;color:{color}'>{_safe_html(label)}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.warning("Données limites planétaires indisponibles.")

# ══ TAB 4 : Système ══════════════════════════════════════════════════════════
with tab4:
    fig_sys = chart_system_diagram()
    fig_sys.update_layout(height=480)
    st.plotly_chart(fig_sys, use_container_width=True,
                    config=PLOTLY_CFG, key="chart_system")

# ══ TAB 5 : IA ═══════════════════════════════════════════════════════════════
with tab5:
    c1, c2 = st.columns([2, 1])
    with c1:
        ia_sc = st.selectbox("Scénario", list(SCENARIOS.keys()), key="ia_sc",
                             label_visibility="collapsed")
    with c2:
        now      = time.time()
        try:
            _last_call = float(st.session_state.get("last_api_call", 0.0))
        except (TypeError, ValueError):
            _last_call = 0.0
            st.session_state["last_api_call"] = 0.0
        cooldown = now - _last_call < COOLDOWN_S
        btn      = st.button("Analyser", disabled=cooldown)

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

# ══ TAB 6 : Simulation isométrique ══════════════════════════════════════════
with tab6:
    if not _ISO_OK:
        st.error(f"Erreur chargement composant iso : {_iso_err}")
    else:
        import streamlit.components.v1 as components
        components.html(build_iso_html(results), height=900, scrolling=False)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='wm-footer'>World Model v0.1 · 2026 · SW bifurcation research</div>",
    unsafe_allow_html=True,
)
