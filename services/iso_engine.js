/**
 * iso_engine.js — Moteur isométrique Canvas 2D pur — WMv0.1
 * Projection : sx=(col-row)*TW/2+offsetX, sy=(col+row)*TH/2+offsetY
 * Ordre painter : row 0→N, col 0→N
 */

const TW = 80;  // tile width
const TH = 40;  // tile height

// ---------------------------------------------------------------------------
// C3 — Palette procédurale (12 types, zéro PNG)
// ---------------------------------------------------------------------------
const TILE_DEFS = {
  deep_water:  { top: '#1565C0', left: '#0D47A1', right: '#1976D2', h: 0 },
  water:       { top: '#1976D2', left: '#1565C0', right: '#42A5F5', h: 0 },
  sand:        { top: '#F9A825', left: '#F57F17', right: '#FBC02D', h: 0 },
  grass:       { top: '#388E3C', left: '#2E7D32', right: '#43A047', h: 0 },
  forest:      { top: '#2E7D32', left: '#1B5E20', right: '#388E3C', h: 4 },
  farmland:    { top: '#A1887F', left: '#795548', right: '#BCAAA4', h: 0 },
  suburb:      { top: '#90A4AE', left: '#607D8B', right: '#B0BEC5', h: 6 },
  urban:       { top: '#4DD0E1', left: '#00ACC1', right: '#80DEEA', h: 10 },
  dense_urban: { top: '#FFA726', left: '#F57C00', right: '#FFD54F', h: 16 },
  industrial:  { top: '#E64A19', left: '#BF360C', right: '#FF7043', h: 14 },
  wasteland:   { top: '#795548', left: '#4E342E', right: '#8D6E63', h: 0 },
  park:        { top: '#43A047', left: '#2E7D32', right: '#66BB6A', h: 2 },
};

// ---------------------------------------------------------------------------
// C1 — drawTile
// ---------------------------------------------------------------------------
/**
 * @param {CanvasRenderingContext2D} ctx
 * @param {number} col
 * @param {number} row
 * @param {string} tileType  — clé de TILE_DEFS
 * @param {number} offsetX
 * @param {number} offsetY
 */
function drawTile(ctx, col, row, tileType, offsetX, offsetY) {
  const def = TILE_DEFS[tileType] || TILE_DEFS.grass;
  const sx = (col - row) * TW / 2 + offsetX;
  const sy = (col + row) * TH / 2 + offsetY;
  const h  = def.h;

  // --- Face supérieure (losange) ---
  ctx.beginPath();
  ctx.moveTo(sx,          sy);
  ctx.lineTo(sx + TW / 2, sy + TH / 2);
  ctx.lineTo(sx,          sy + TH);
  ctx.lineTo(sx - TW / 2, sy + TH / 2);
  ctx.closePath();
  ctx.fillStyle = def.top;
  ctx.fill();
  ctx.strokeStyle = 'rgba(0,0,0,0.12)';
  ctx.lineWidth = 0.5;
  ctx.stroke();

  if (h > 0) {
    // --- Face gauche (ombre) ---
    ctx.beginPath();
    ctx.moveTo(sx - TW / 2, sy + TH / 2);
    ctx.lineTo(sx,          sy + TH);
    ctx.lineTo(sx,          sy + TH + h);
    ctx.lineTo(sx - TW / 2, sy + TH / 2 + h);
    ctx.closePath();
    ctx.fillStyle = def.left;
    ctx.fill();
    ctx.strokeStyle = 'rgba(0,0,0,0.12)';
    ctx.stroke();

    // --- Face droite (lumière) ---
    ctx.beginPath();
    ctx.moveTo(sx + TW / 2, sy + TH / 2);
    ctx.lineTo(sx,          sy + TH);
    ctx.lineTo(sx,          sy + TH + h);
    ctx.lineTo(sx + TW / 2, sy + TH / 2 + h);
    ctx.closePath();
    ctx.fillStyle = def.right;
    ctx.fill();
    ctx.strokeStyle = 'rgba(0,0,0,0.12)';
    ctx.stroke();

  }
}

// ---------------------------------------------------------------------------
// C2 — renderGrid  (dirty-flag + pollution overlay)
// ---------------------------------------------------------------------------
/**
 * @param {CanvasRenderingContext2D} ctx
 * @param {string[][]} grid       — grille actuelle [rows][cols]
 * @param {string[][]} prevGrid   — grille précédente (null = premier rendu)
 * @param {number}     offsetX
 * @param {number}     offsetY
 * @param {number}     pollution  — [0-1] intensité de l'overlay pollution
 * @returns {string[][]} nouvelle prevGrid
 */
function renderGrid(ctx, grid, prevGrid, offsetX, offsetY, pollution) {
  const rows = grid.length;
  const cols = grid[0].length;

  // Ordre painter : row 0→N, col 0→N
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const tile = grid[row][col];
      if (prevGrid && prevGrid[row] && prevGrid[row][col] === tile) continue;
      drawTile(ctx, col, row, tile, offsetX, offsetY);
    }
  }

  // Overlay pollution semi-transparent violet
  if (pollution > 0) {
    ctx.save();
    ctx.globalAlpha = pollution * 0.45;
    ctx.fillStyle = '#6A0DAD';
    ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    ctx.restore();
  }

  return grid.map(r => [...r]);
}

// ---------------------------------------------------------------------------
// C4 — lockLandscape + overlay portrait
// ---------------------------------------------------------------------------
function lockLandscape() {
  if (screen.orientation && screen.orientation.lock) {
    screen.orientation.lock('landscape').catch(() => {});
  }

  const overlay = document.getElementById('wm-iso-portrait-overlay');
  if (!overlay) return;

  const check = () => {
    const isPortrait = window.innerHeight > window.innerWidth;
    overlay.style.display = isPortrait ? 'flex' : 'none';
  };

  window.addEventListener('resize', check);
  window.addEventListener('orientationchange', check);
  check();
}
