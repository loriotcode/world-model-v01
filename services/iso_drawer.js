/**
 * iso_drawer.js — Drawer scénarios (slide gauche) — WMv0.1
 * Anime.js pour la transition CSS transform.
 */

const SCENARIOS = ['BAU', 'BAU2', 'SW'];  // scénarios réels du modèle world3.py
let _currentScenario = 'BAU';
let _isOpen = false;
let _onScenarioChange = null;  // callback(scenario)

// ---------------------------------------------------------------------------
// Rendu des boutons
// ---------------------------------------------------------------------------
function _renderBtns(year, isPlaying) {
  const list = document.getElementById('wm-iso-scenario-list');
  if (!list) return;
  list.innerHTML = '';

  SCENARIOS.forEach(sc => {
    const btn = document.createElement('button');
    btn.className = 'scenario-btn' + (sc === _currentScenario ? ' active' : '');
    btn.textContent = sc;

    // Verrouillage : disabled si year < 2026 OU isPlaying
    const locked = year < 2026 || isPlaying;
    if (locked) btn.classList.add('wm-disabled');

    btn.addEventListener('click', () => {
      if (locked) return;
      _currentScenario = sc;
      _renderBtns(year, isPlaying);
      if (_onScenarioChange) _onScenarioChange(sc);
      close();
    });

    list.appendChild(btn);
  });
}

// ---------------------------------------------------------------------------
// Slide transition
// ---------------------------------------------------------------------------
function open() {
  const drawer = document.getElementById('wm-iso-drawer');
  if (!drawer || _isOpen) return;
  _isOpen = true;
  if (typeof anime !== 'undefined') {
    anime({ targets: drawer, translateX: ['−100%', '0%'], duration: 300, easing: 'easeOutCubic' });
  } else {
    drawer.style.transform = 'translateX(0%)';
  }
}

function close() {
  const drawer = document.getElementById('wm-iso-drawer');
  if (!drawer || !_isOpen) return;
  _isOpen = false;
  if (typeof anime !== 'undefined') {
    anime({ targets: drawer, translateX: ['0%', '-100%'], duration: 300, easing: 'easeInCubic',
            complete: () => { drawer.style.transform = 'translateX(-100%)'; } });
  } else {
    drawer.style.transform = 'translateX(-100%)';
  }
}

// ---------------------------------------------------------------------------
// API publique
// ---------------------------------------------------------------------------
function initDrawer(onScenarioChange, getYear, getIsPlaying) {
  _onScenarioChange = onScenarioChange;

  const toggleBtn = document.getElementById('wm-iso-menu-btn');
  if (toggleBtn) toggleBtn.addEventListener('click', () => _isOpen ? close() : open());

  // Mise à jour état au changement de lecture/année
  document.addEventListener('wm-state-change', () => {
    _renderBtns(getYear(), getIsPlaying());
  });

  _renderBtns(1940, false);
}
