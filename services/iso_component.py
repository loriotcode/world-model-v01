"""
iso_component.py — Composant HTML Streamlit pour l'onglet isométrique WMv0.1
"""
from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _read_js(name: str) -> str:
    return (_HERE / name).read_text(encoding="utf-8")


def build_iso_html(results: dict, default_scenario: str = "BAU") -> str:
    """
    Génère le HTML complet pour st.components.v1.html.
    - Inline des 3 fichiers JS
    - Sérialise uniquement le scénario actif (évite surcharge mémoire)
    - json.dumps ensure_ascii=True pour éviter injection </script>
    """
    # Sérialise tous les scénarios (clé → liste de dicts annuels)
    wm_data: dict[str, list[dict]] = {}
    for sc, df in results.items():
        df_reset = df.reset_index()
        if "year" not in df_reset.columns and df_reset.index.name == "year":
            df_reset = df.reset_index()
        wm_data[sc] = df_reset.to_dict(orient="records")

    wm_data_json = json.dumps(wm_data, ensure_ascii=True, allow_nan=False)

    engine_js   = _read_js("iso_engine.js")
    controls_js = _read_js("iso_controls.js")
    drawer_js   = _read_js("iso_drawer.js")

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #1a1a2e; font-family: monospace; overflow: hidden; }}

  /* Toolbar */
  #wm-iso-toolbar {{
    display: flex; align-items: center; gap: 8px;
    background: #0f0f1e; padding: 4px 10px;
    height: 38px; width: 100%;
  }}
  #wm-iso-play {{
    background: #263238; color: #eee; border: 1px solid #4fc3f7;
    padding: 2px 10px; border-radius: 4px; cursor: pointer; font-size: 14px;
  }}
  #wm-iso-year {{ font-size: 16px; font-weight: bold; color: #4fc3f7; min-width: 42px; }}
  #wm-iso-slider {{ flex: 1; accent-color: #4fc3f7; }}
  /* Scenario inline buttons */
  #wm-iso-scenario-btns {{ display: flex; gap: 4px; margin-left: 6px; }}
  .sc-tb-btn {{
    background: #1e2a38; color: #90a4ae; border: 1px solid #37474f;
    padding: 2px 10px; border-radius: 12px; cursor: pointer;
    font-size: 11px; font-family: monospace; white-space: nowrap;
  }}
  .sc-tb-btn.active {{ border-color: #4fc3f7; color: #4fc3f7; background: #263238; }}
  .sc-tb-btn.wm-disabled {{ opacity: 0.4; pointer-events: none; }}

  /* Canvas */
  canvas {{ display: block; }}

  /* Banner checkpoint */
  #wm-iso-banner {{
    display: none; position: fixed; top: 50px; left: 50%;
    transform: translateX(-50%);
    background: #1b5e20; color: #a5d6a7; padding: 8px 20px;
    border-radius: 8px; font-size: 13px; z-index: 100;
    border: 1px solid #43a047;
  }}

  /* Overlay portrait */
  #wm-iso-portrait-overlay {{
    display: none; position: fixed; inset: 0;
    background: rgba(0,0,0,0.85); color: #eee;
    flex-direction: column; align-items: center; justify-content: center;
    font-size: 18px; z-index: 200; gap: 12px;
  }}
</style>
</head>
<body>

<div id="wm-iso-toolbar">
  <button id="wm-iso-play">▶</button>
  <span id="wm-iso-year">1960</span>
  <input type="range" id="wm-iso-slider" min="1960" max="2100" value="1960" step="1">
  <div id="wm-iso-scenario-btns"></div>
</div>

<canvas id="wm-iso-canvas"></canvas>

<div id="wm-iso-banner">⏸ 2026 — choisissez un scénario</div>

<div id="wm-iso-portrait-overlay">
  <span>↻</span>
  <span>Tournez votre écran</span>
</div>

<script>
// ── Données World3 injectées
const WM_DATA = {wm_data_json};

// ── Paramètres canvas
const COLS = 60, ROWS = 50;

// ── State
let currentScenario = {json.dumps(default_scenario, ensure_ascii=True)};
let prevGrid = null;

// ── Resize canvas
const canvas = document.getElementById('wm-iso-canvas');
function resizeCanvas() {{
  canvas.width  = window.innerWidth;
  canvas.height = window.innerHeight - 38;
  TW = 28;
  TH = 14;
}}
resizeCanvas();
window.addEventListener('resize', () => {{ resizeCanvas(); prevGrid = null; redraw(); }});

// ── Offset centrage
function getOffset() {{
  // Centre la grille isométrique et la force à déborder du viewport
  // sx_center = (COLS/2 - ROWS/2)*TW/2 + offsetX → offsetX = W/2 - (COLS/2-ROWS/2)*TW/2
  // sy_center = (COLS/2 + ROWS/2)*TH/2 + offsetY → offsetY = H/2 - (COLS/2+ROWS/2)*TH/2
  return {{
    x: canvas.width  / 2 - (COLS / 2 - ROWS / 2) * TW / 2,
    y: canvas.height / 2 - (COLS / 2 + ROWS / 2) * TH / 2,
  }};
}}

// ── Damier calibrage 1960-1969
function _checkerboard(cols, rows) {{
  const grid = [];
  for (let r = 0; r < rows; r++) {{
    const line = [];
    for (let c = 0; c < cols; c++) {{
      line.push((c + r) % 2 === 0 ? 'checker_black' : 'checker_white');
    }}
    grid.push(line);
  }}
  return grid;
}}

// ── Récupère la grille pour (scenario, year) depuis WM_DATA
function getGridForYear(scenario, year) {{
  if (year < 1970) return _checkerboard(COLS, ROWS);
  const sc = year <= 2026 ? 'BAU' : scenario;
  const rows = WM_DATA[sc];
  if (!rows || rows.length === 0) return null;

  // Interpolation simple
  const years = rows.map(r => r.year || r.Year || 0);
  let lo = rows[0], hi = rows[rows.length - 1];
  for (let i = 0; i < rows.length - 1; i++) {{
    if (years[i] <= year && years[i+1] >= year) {{ lo = rows[i]; hi = rows[i+1]; break; }}
  }}
  const t = (hi.year - lo.year) > 0 ? (year - lo.year) / (hi.year - lo.year) : 0;
  const interp = {{}};
  for (const k of Object.keys(lo)) interp[k] = lo[k] + t * ((hi[k] || 0) - (lo[k] || 0));

  return worldDataToGrid(interp, COLS, ROWS);
}}

// ── Mapping données → grille (miroir de iso_data.py)
function worldDataToGrid(row, cols, rows) {{
  const norm = (k, lo, hi) => Math.max(0, Math.min(1, ((row[k] || 0) - lo) / (hi - lo)));
  // Mêmes plages que iso_data.py (unités réelles du modèle world3.py)
  const res  = norm('resources',        0.0, 1.0);   // [0-1] clamped
  const pop  = norm('population',       0.0, 15.0);  // milliards
  const pol  = norm('pollution',        0.0, 2.0);   // [0-2] clamped
  const food = norm('food_per_capita',  0.0, 1.0);   // [0-1] normalisé
  const cap  = norm('capital',          0.0, 1.5);   // [0-1.5] clamped
  const hdi  = norm('hdi',              0.0, 1.0);   // [0-1] normalisé
  const cx = cols / 2, cy = rows / 2;
  const maxD = Math.sqrt(cx*cx + cy*cy);
  const grid = [];
  for (let r = 0; r < rows; r++) {{
    const line = [];
    for (let c = 0; c < cols; c++) {{
      const dist = Math.sqrt((c-cx)**2 + (r-cy)**2) / maxD;
      let tile;
      if (dist > 0.85) {{
        if (c < 2 || r < 2)  tile = 'deep_water';
        else if (pol > 0.10) tile = 'wasteland';
        else if (res > 0.7)  tile = 'forest';
        else if (res > 0.4)  tile = 'grass';
        else if (food > 0.5) tile = 'farmland';
        else                 tile = 'sand';
      }} else if (dist > 0.60) {{
        if (pol > 0.10)      tile = 'wasteland';
        else if (res > 0.7)  tile = 'forest';
        else if (res > 0.4)  tile = 'grass';
        else if (food > 0.5) tile = 'farmland';
        else                 tile = 'sand';
      }} else if (dist > 0.35) {{
        if (pol > 0.12)      tile = 'wasteland';
        else if (cap > 0.25) tile = 'industrial';
        else if (hdi > 0.55) tile = 'suburb';
        else if (res > 0.5)  tile = 'grass';
        else                 tile = 'farmland';
      }} else {{
        if (pol > 0.13)                    tile = 'wasteland';
        else if (cap > 0.30)               tile = 'industrial';
        else if (pop > 0.40 && hdi > 0.5) tile = 'dense_urban';
        else if (pop > 0.25)               tile = 'urban';
        else                               tile = 'suburb';
      }}
      if (dist < 0.45 && pol < 0.3 && hdi > 0.7 && (c+r) % 7 === 0) tile = 'park';
      line.push(tile);
    }}
    grid.push(line);
  }}
  return grid;
}}

// ── Redraw
function redraw() {{
  const ctx = canvas.getContext('2d');
  const off = getOffset();
  // Fond neutre (contraste avec toutes les tuiles)
  ctx.fillStyle = '#f8f5f0';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const year     = parseInt(document.getElementById('wm-iso-slider').value);
  const grid     = getGridForYear(currentScenario, year) || prevGrid;
  if (!grid) return;

  // pollution normalisée [0-2] → overlay [0-1]
  const _scPol = year <= 2026 ? 'BAU' : currentScenario;
  const _polRows = WM_DATA[_scPol] || [];
  const _polRow = _polRows.find(r => r.year === year) || _polRows[_polRows.length - 1] || {{}};
  const polVal = Math.min(1, (_polRow.pollution || 0) / 2.0);

  prevGrid = renderGrid(ctx, grid, null, off.x, off.y, Math.min(polVal, 1));
}}

// ── Moteur JS chargé inline ci-dessous
</script>

<!-- iso_engine.js inline -->
<script>
{engine_js}
</script>

<!-- iso_controls.js inline -->
<script>
{controls_js}
</script>

<!-- iso_drawer.js inline -->
<script>
{drawer_js}
</script>

<script>
// ── Init controls (iso_controls.js)
init(function(year) {{
  document.dispatchEvent(new Event('wm-state-change'));
  redraw();
}});

// ── Init scenario buttons (iso_drawer.js)
initDrawer(
  function(sc) {{
    currentScenario = sc;
    document.dispatchEvent(new Event('wm-state-change'));
    redraw();
  }},
  function() {{ return parseInt(document.getElementById('wm-iso-slider').value); }},
  function() {{ return _isPlaying || false; }}
);

// ── Redraw initial
redraw();
lockLandscape();
</script>

</body>
</html>"""
