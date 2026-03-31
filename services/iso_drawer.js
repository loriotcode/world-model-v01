/**
 * iso_drawer.js — Boutons scénarios inline (toolbar droite) — WMv0.1
 */

const SCENARIOS = ['BAU', 'BAU2', 'SW'];
let _currentScenario = 'BAU';
let _onScenarioChange = null;

function _renderScenarioBtns(year, isPlaying) {
  const container = document.getElementById('wm-iso-scenario-btns');
  if (!container) return;
  container.innerHTML = '';
  const locked = year < 2026 || isPlaying;

  SCENARIOS.forEach(sc => {
    const btn = document.createElement('button');
    btn.className = 'sc-tb-btn' + (sc === _currentScenario ? ' active' : '');
    btn.textContent = sc;
    if (locked) btn.classList.add('wm-disabled');

    btn.addEventListener('click', () => {
      const nowYear    = parseInt(document.getElementById('wm-iso-slider').value) || 1970;
      const nowPlaying = document.getElementById('wm-iso-play')?.textContent === '⏸';
      if (nowYear < 2026 || nowPlaying) return;
      _currentScenario = sc;
      _renderScenarioBtns(nowYear, false);
      if (_onScenarioChange) _onScenarioChange(sc);
    });

    container.appendChild(btn);
  });
}

function initDrawer(onScenarioChange, getYear, getIsPlaying) {
  _onScenarioChange = onScenarioChange;
  document.addEventListener('wm-state-change', () => {
    _renderScenarioBtns(getYear(), getIsPlaying());
  });
  _renderScenarioBtns(1960, false);
}
