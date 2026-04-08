"""
utils/styles.py — CSS + JS pour World Model v0.1
"""

STYLES = """
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

/* Masque le bandeau Streamlit natif (⋮ menu) */
header[data-testid="stHeader"] { display:none !important; }
section[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display:none !important; }

.stApp { background:var(--bg) !important; color:var(--text); }

.block-container { padding:0.4rem 0.7rem 0.8rem !important; max-width:100% !important; }

.wm-header {
  padding:10px 0 6px; margin:0;
}
.wm-header h1 { font-size:0.82em; font-weight:700; margin:0; color:var(--text); letter-spacing:0.01em; }

/* ── Navigation radio → cubes (6 blocs) ── */
div[data-testid="stRadio"] { margin-bottom:7px; }
div[data-testid="stRadio"] > div[role="radiogroup"] {
  display:grid !important;
  grid-template-columns:repeat(6,1fr) !important;
  gap:5px !important;
}
div[data-testid="stRadio"] label {
  background:var(--panel) !important;
  border:1px solid var(--border) !important;
  border-radius:8px !important;
  padding:7px 5px !important;
  text-align:center !important;
  cursor:pointer !important;
  min-height:50px !important;
  display:flex !important;
  flex-direction:column !important;
  align-items:center !important;
  justify-content:center !important;
  font-size:0.72em !important;
  line-height:1.35 !important;
  white-space:pre-line !important;
  transition:border-color 0.15s !important;
}
div[data-testid="stRadio"] label:hover {
  border-color:var(--accent) !important;
}
div[data-testid="stRadio"] label:has(input:checked) {
  border-color:var(--accent) !important;
  font-weight:700 !important;
  box-shadow:0 1px 4px rgba(74,124,89,0.18) !important;
}
/* Masquer le cercle radio natif */
div[data-testid="stRadio"] input[type="radio"] { display:none !important; }

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
  position:fixed; bottom:6px; right:10px;
  font-size:0.60em; color:var(--muted); opacity:0.55;
  background:transparent; text-align:right;
}
.wm-footer a { color:var(--muted); text-decoration:none; }
.wm-footer a:hover { opacity:1; color:var(--accent); }

/* Selecteurs compacts */
.compact-select .stSelectbox > div > div { min-height:28px !important; font-size:0.75em !important; }
.compact-select label { font-size:0.68em !important; margin-bottom:1px !important; }

/* Badges irreversibilite */
.irrev-badge {
  display:inline-block; font-size:0.58em; font-weight:700;
  color:#fff; background:var(--crit); border-radius:3px;
  padding:1px 4px; margin-left:5px; vertical-align:middle;
  letter-spacing:0.04em;
}

/* Diagrammes Earth4All — fond sombre */
.dark-diagram { background:#1a1a2e; border-radius:10px; overflow:hidden; }

::-webkit-scrollbar { width:3px; height:3px; }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:2px; }

/* ── Responsive smartphone ── */
@media (max-width:768px) {
  div[data-testid="stRadio"] > div[role="radiogroup"] {
    grid-template-columns:repeat(3,1fr) !important;
  }
  div[data-testid="stRadio"] label { min-height:40px !important; font-size:0.65em !important; }
  .block-container { padding:0.2rem 0.3rem 0.5rem !important; }
  .wm-footer { position:static; text-align:center; margin-top:4px; }
}
</style>
"""
