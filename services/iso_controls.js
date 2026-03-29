/**
 * iso_controls.js — Timeline + Play/Pause — WMv0.1
 * Anime.js pour transitions UI uniquement (pas canvas).
 */

const YEARS_PER_SEC = 2;
let _year        = 1940;
let _isPlaying   = false;
let _timer       = null;
let _hasPassedCheckpoint = false;
let _onYearChange = null;  // callback(year)

// ---------------------------------------------------------------------------
// Banner checkpoint 2026
// ---------------------------------------------------------------------------
function _showBanner() {
  const banner = document.getElementById('wm-iso-banner');
  if (!banner) return;
  banner.style.display = 'flex';
  // Disparaît après 4s via anime.js
  if (typeof anime !== 'undefined') {
    anime({ targets: banner, opacity: [1, 0], delay: 3000, duration: 800,
            easing: 'easeInQuad', complete: () => { banner.style.display = 'none'; banner.style.opacity = 1; } });
  }
}

// ---------------------------------------------------------------------------
// Grisage des boutons scénario pendant lecture
// ---------------------------------------------------------------------------
function _setScenarioBtnsDisabled(disabled) {
  document.querySelectorAll('.scenario-btn').forEach(btn => {
    btn.classList.toggle('wm-disabled', disabled);
  });
}

// ---------------------------------------------------------------------------
// Step
// ---------------------------------------------------------------------------
function _step() {
  if (!_isPlaying) return;

  _year++;
  if (_year > 2100) { _year = 2100; pause(); return; }

  // Pause automatique à 2026
  if (_year === 2026 && !_hasPassedCheckpoint) {
    _hasPassedCheckpoint = true;
    pause();
    _showBanner();
    return;
  }

  _syncUI();
  if (_onYearChange) _onYearChange(_year);
  _timer = setTimeout(_step, 1000 / YEARS_PER_SEC);
}

function _syncUI() {
  const yearEl   = document.getElementById('wm-iso-year');
  const sliderEl = document.getElementById('wm-iso-slider');
  if (yearEl)   yearEl.textContent = _year;
  if (sliderEl) sliderEl.value     = _year;
}

// ---------------------------------------------------------------------------
// API publique
// ---------------------------------------------------------------------------
function play() {
  if (_isPlaying) return;
  _isPlaying = true;
  _setScenarioBtnsDisabled(true);
  const playBtn = document.getElementById('wm-iso-play');
  if (playBtn) playBtn.textContent = '⏸';
  _timer = setTimeout(_step, 1000 / YEARS_PER_SEC);
}

function pause() {
  _isPlaying = false;
  clearTimeout(_timer);
  _setScenarioBtnsDisabled(false);
  const playBtn = document.getElementById('wm-iso-play');
  if (playBtn) playBtn.textContent = '▶';
}

function seek(year) {
  _year = Math.max(1940, Math.min(2100, year));
  _syncUI();
  if (_onYearChange) _onYearChange(_year);
}

function init(onYearChange) {
  _onYearChange = onYearChange;

  const playBtn  = document.getElementById('wm-iso-play');
  const sliderEl = document.getElementById('wm-iso-slider');

  if (playBtn)  playBtn.addEventListener('click', () => _isPlaying ? pause() : play());
  if (sliderEl) sliderEl.addEventListener('input', e => seek(parseInt(e.target.value)));

  _syncUI();
}
