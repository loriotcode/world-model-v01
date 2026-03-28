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
)
from services.claude_api import analyse_scenario, extract_summary
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
    height  = 230,
    margin  = dict(l=30, r=10, t=20, b=30),
    font    = dict(size=9),
    legend  = dict(orientation="h", yanchor="bottom", y=1.02,
                   xanchor="right", x=1, font=dict(size=9)),
)
PLOTLY_CFG = dict(responsive=True, displayModeBar=False,
                  scrollZoom=False, doubleClick=False, displaylogo=False)

# Source unique des couleurs de statut
STATUS_COLORS = {"safe": "#4a7c59", "exceeded": "#d68910", "critical": "#a8323e"}

# Whitelist des variables (sécurité)
VARIABLES = ["population", "resources", "pollution", "capital",
             "life_expectancy", "food_per_capita", "hdi"]

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

def _get_year_row(scenario: str, year: int):
    df = results.get(scenario)
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

bau_2050 = _get_year_row("BAU", 2050)
sw_2050  = _get_year_row("SW",  2050)

# ─── CSS + JS ────────────────────────────────────────────────────────────────
st.markdown("""
<script>
(function(){
  if (screen.orientation && screen.orientation.lock) {
    screen.orientation.lock('landscape').catch(function(){});
  }
  function checkOrientation() {
    var el = document.getElementById('wm-overlay');
    if (el) el.style.display = (window.innerHeight > window.innerWidth) ? 'flex' : 'none';
  }
  ['resize', 'orientationchange'].forEach(function(ev){
    window.addEventListener(ev, function(){ setTimeout(checkOrientation, 300); });
  });
  setTimeout(checkOrientation, 600);
})();
</script>

<div id="wm-overlay" style="display:none;position:fixed;inset:0;z-index:99999;
  background:rgba(248,245,240,0.97);flex-direction:column;align-items:center;
  justify-content:center;font-family:sans-serif;text-align:center;padding:30px;">
  <div style="font-size:48px;margin-bottom:16px;animation:tilt 2s ease-in-out infinite;">📱</div>
  <div style="font-size:1.1em;font-weight:700;color:#2d3748;">Rotation requise</div>
  <div style="font-size:0.85em;color:#718096;margin-top:6px;">Mode paysage uniquement</div>
</div>

<style>
@keyframes tilt {
  0%,100% { transform:rotate(0deg); }
  30%,70%  { transform:rotate(-90deg); }
}

:root {
  --bg:     #f8f5f0;
  --panel:  #ffffff;
  --border: #d1c7b7;
  --text:   #2d3748;
  --muted:  #718096;
  --safe:   #4a7c59;
  --warn:   #d68910;
  --crit:   #a8323e;
  --accent: #4a7c59;
}

section[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display:none !important; }

.stApp { background:var(--bg) !important; color:var(--text); }

.block-container { padding:0.4rem 0.7rem 0.8rem !important; max-width:100% !important; }

.wm-header {
  display:flex; align-items:center; gap:8px;
  padding:5px 0; border-bottom:1px solid var(--border); margin-bottom:6px;
}
.wm-header h1 { font-size:0.95em; font-weight:700; margin:0; color:var(--text); }
.wm-header .sub { font-size:0.7em; color:var(--muted); margin-left:auto; }

.wm-metrics {
  display:grid; grid-template-columns:repeat(4,1fr); gap:5px; margin-bottom:7px;
}
.wm-metric {
  background:var(--panel); border:1px solid var(--border);
  border-radius:8px; padding:6px 7px; text-align:center;
}
.wm-metric .val   { font-size:1.1em; font-weight:700; color:var(--accent); }
.wm-metric .lbl   { font-size:0.63em; color:var(--muted); margin-top:1px; }
.wm-metric .delta { font-size:0.58em; color:var(--warn); margin-top:1px; }

.stTabs [data-baseweb="tab-list"] {
  gap:2px; background:#f0eae2; border-radius:8px; padding:3px; margin-bottom:7px;
}
.stTabs [data-baseweb="tab"] {
  border-radius:6px; padding:4px 10px; font-size:0.76em;
  font-weight:600; color:var(--muted); background:transparent; border:none;
}
.stTabs [aria-selected="true"] { background:var(--panel) !important; color:var(--accent) !important; }

.status-row   { display:flex; flex-wrap:wrap; gap:5px; margin:5px 0; }
.status-pill  { padding:3px 9px; border-radius:20px; font-size:0.7em; font-weight:600; }
.pill-safe     { background:rgba(74,124,89,.12);  color:var(--safe); border:1px solid var(--safe); }
.pill-exceeded { background:rgba(214,137,16,.12); color:var(--warn); border:1px solid var(--warn); }
.pill-critical { background:rgba(168,50,62,.12);  color:var(--crit); border:1px solid var(--crit); }

.bound-item {
  display:flex; align-items:center; gap:8px;
  padding:4px 0; border-bottom:1px solid var(--border); font-size:0.78em;
}
.bound-dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; }

.ia-result {
  background:var(--panel); border:1px solid var(--border); border-radius:10px;
  padding:11px 13px; font-size:0.81em; line-height:1.6; color:var(--text);
  max-height:255px; overflow-y:auto;
}
.ia-empty { font-size:0.8em; color:var(--muted); padding:10px 0; }

.sc-legend { display:flex; align-items:center; gap:5px; font-size:0.7em; }
.sc-dot    { width:8px; height:8px; border-radius:50%; flex-shrink:0; }

.stSelectbox label, .stMultiSelect label { font-size:0.76em !important; color:var(--muted) !important; }
div[data-baseweb="select"] { background:var(--panel) !important; border-color:var(--border) !important; }

.stButton button {
  background:var(--accent) !important; color:#fff !important;
  font-weight:700; border-radius:7px; border:none;
  font-size:0.83em; padding:6px 16px; width:100%;
}
.stButton button:disabled { opacity:0.45 !important; }

.wm-footer {
  margin-top:8px; font-size:0.66em; color:var(--muted);
  text-align:center; border-top:1px solid var(--border); padding-top:5px;
}

::-webkit-scrollbar { width:3px; height:3px; }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:2px; }
</style>
""", unsafe_allow_html=True)

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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Aperçu", "📈 Scénarios", "🌐 Limites", "🔄 Système", "🤖 IA"])

# ══ TAB 1 ════════════════════════════════════════════════════════════════════
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

# ══ TAB 2 ════════════════════════════════════════════════════════════════════
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

# ══ TAB 3 ════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f"""
    <div class="status-row">
      <span class="status-pill pill-safe">✓ {counts['safe']} Safe</span>
      <span class="status-pill pill-exceeded">⚠ {counts['exceeded']} Dépassée</span>
      <span class="status-pill pill-critical">✗ {counts['critical']} Critique</span>
    </div>""", unsafe_allow_html=True)

    if boundaries:
        fig = chart_planetary_boundaries_as_bars(boundaries)
        fig.update_layout(height=210, margin=dict(l=10, r=10, t=12, b=8), font=dict(size=8))
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

# ══ TAB 4 ════════════════════════════════════════════════════════════════════
with tab4:
    fig_sys = chart_system_diagram()
    fig_sys.update_layout(height=290)
    st.plotly_chart(fig_sys, use_container_width=True,
                    config=PLOTLY_CFG, key="chart_system")

# ══ TAB 5 ════════════════════════════════════════════════════════════════════
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

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='wm-footer'>World Model v0.1 · 2026 · SW bifurcation research</div>",
    unsafe_allow_html=True,
)
