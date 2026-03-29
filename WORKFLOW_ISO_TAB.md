# WORKFLOW — Onglet Simulation Isométrique WMv0.1
**Moteur : Canvas 2D pur** · **Données : world3.py** · **Stack : Python + JS vanilla**

---

## CORRECTIONS INTÉGRÉES

| Problème | Fix |
|----------|-----|
| `skewY(-30deg)` ≠ iso | `screenX=(col-row)*TW/2`, `screenY=(col+row)*TH/2` |
| `innerHTML=''` par frame | Dirty-flag : `prev_grid` comparé tile par tile |
| RAF sans throttle | `setTimeout(step, 1000/YEARS_PER_SEC)` |
| Drag/pan | Désactivé |
| Menu droite | Drawer gauche slide-in CSS |
| Timeline 2020-2090 | 1940-2100, interpolation annuelle |
| Cache 150k entrées | Calcul à la demande par année |
| XSS json inject | `json.dumps(data, ensure_ascii=True)` |

---

## PHASE 0 — Fondation ✅ décidé, pas encore codé

- [x] A1. Moteur Canvas 2D pur (validé screenshot)
- [x] A2. Grille TW=32, TH=16, ~20×16 tuiles
- [ ] A3. Bridge `world3.py` → grille (Phase 1)
- [ ] A4. Intégration `st.components.v1.html` (Phase 5)

---

## PHASE 1 — Pipeline données
**Skills : `/python-pro` `/python-patterns`**

### Prompt B1
```
En utilisant /python-pro, crée utils/iso_data.py.
Définis TILE_STATES : dict de 12 types → {color_top, color_left, color_right, height}.
Types : deep_water, water, sand, grass, forest, farmland,
        suburb, urban, dense_urban, industrial, wasteland, park.
```

### Prompt B2
```
En utilisant /python-patterns, dans utils/iso_data.py ajoute :
world3_to_grid(df_row, cols=20, rows=16) → List[List[str]]
- Normalise les 6 variables [0-1] depuis df_row
- Mapping : resources→nature (forêt/prairie/désert), population→urban density,
  capital→industrial, food_per_capita→farmland, hdi→suburb/urban quality
- Zones fixes : centre=urbain, périphérie=campagne, bords=nature
```

### Prompt B3
```
Dans utils/iso_data.py ajoute interpolate_year(df, year) → Series.
df a des rows annuelles de 1900 à 2100. Retourne la row pour l'année exacte.
Teste avec year=1972, year=2026, year=2100.
```

### Prompt B4
```
Dans utils/iso_data.py ajoute get_scenario_grid(results, scenario, year) → List[List[str]].
Règles : BAU forcé si year <= 2026 quel que soit scenario.
Retourne world3_to_grid(interpolate_year(results[sc], year)).
```

---

## PHASE 2 — Moteur Canvas
**Skills : `/2d-games` `/fixing-motion-performance` `/focused-fix` `/autoresearch-agent`**

### Prompt C1
```
En utilisant /2d-games, crée services/iso_engine.js (JS vanilla).
Fonction drawTile(ctx, col, row, tileState):
- Projection iso : sx=(col-row)*TW/2+offsetX, sy=(col+row)*TH/2+offsetY
- Dessine losange top + face gauche (shadow) + face droite (light) avec les couleurs de tileState
- Si tileState.height > 0 : extrude les faces latérales vers le bas
TW=32, TH=16. Exporte drawTile.
```

### Prompt C2
```
En utilisant /2d-games, dans iso_engine.js ajoute renderGrid(ctx, grid, prevGrid).
- Ordre painter : row 0→N, col 0→N
- Dirty-flag : ne redessiner la tuile [r][c] que si grid[r][c] !== prevGrid[r][c]
- Overlay pollution : calque semi-transparent violet sur toute la grille (alpha depuis WM_STATE.pollution)
Retourne la grille rendue comme nouvelle prevGrid.
```

### Prompt C3 (assets V1)
```
Dans iso_engine.js, génère drawTile procéduralement pour les 12 types avec Canvas :
- Dégradés lineaires pour donner du relief (forêt=vert foncé/clair, eau=bleu, désert=ocre...)
- Aucun PNG externe — tout en Canvas API
Fournis les couleurs HSL pour chaque type (top/left/right).
```

### Prompt C4
```
Dans iso_engine.js ajoute lockLandscape():
screen.orientation.lock('landscape').catch(()=>{})
+ overlay portrait (#wm-iso-overlay) identique à celui de utils/styles.py.
```

---

## PHASE 3 — Contrôles timeline
**Skills : `/animejs-animation` `/fixing-motion-performance`**

### Prompt D1-D4
```
En utilisant /animejs-animation pour les transitions UI (pas le canvas),
crée services/iso_controls.js :
- Timeline input[range] min=1940 max=2100 step=1
- Play/Pause : setTimeout(step, 1000/YEARS_PER_SEC), YEARS_PER_SEC=2
- Pause auto à year===2026 si !hasPassedCheckpoint, showBanner()
- Grisage : .disabled { pointer-events:none; opacity:0.4 }
  appliqué à .scenario-btn quand isPlaying===true
- Exporte { init, play, pause, seek }
```

---

## PHASE 4 — Drawer scénarios
**Skills : `/animejs-animation`**

### Prompt E1-E3
```
En utilisant /animejs-animation pour la transition slide,
crée services/iso_drawer.js :
- Drawer gauche : transform translateX(-100%) → 0 en 300ms ease
- 6 boutons scénarios : BAU, BAU2, SW, CT, FW, Personnalisé
- Verrouillage : disabled si year < 2026 OU isPlaying
- Bouton ☰ dans la toolbar pour toggle
- Exporte { init, open, close }
```

---

## PHASE 5 — Intégration Streamlit
**Skills : `/python-pro` `/focused-fix` `/playwright-pro`**

### Prompt F1
```
Dans app.py, ajoute l'onglet 🏙 à la barre st.tabs existante.
tab6 = nouveau dernier onglet. Contenu : st.components.v1.html(iso_html, height=600).
```

### Prompt F2-F3
```
En utilisant /python-pro, crée services/iso_component.py :
- build_iso_html(results, default_scenario="BAU") → str HTML
- Charge iso_engine.js, iso_controls.js, iso_drawer.js comme inline <script>
- Sérialise uniquement le scénario actif : json.dumps(data, ensure_ascii=True)
  (évite injection </script>)
- Passe WM_DATA au JS via const injection sécurisée
```

### Prompt F4
```
En utilisant /focused-fix, vérifie la hauteur responsive du composant :
- Desktop : height=600
- JS détecte window.innerHeight, postMessage vers Streamlit si < 500px (mobile)
Teste sur desktop et mobile landscape.
```

### Prompt F5 (review)
```
Lance /pr-review-expert sur le diff complet de l'onglet iso.
Puis /tech-debt-tracker sur les nouveaux fichiers utils/iso_data.py et services/iso_*.
```

---

## SÉQUENCE D'EXÉCUTION

```
B1 → B2 → B3 → B4          pipeline Python
              ↓
         C1 → C2 → C3 → C4  moteur Canvas JS
                   ↓
              D1-D4          timeline JS
              E1-E3          drawer JS
                        ↓
                   F1 → F2 → F3 → F4   Streamlit
                                   ↓
                              F5 review
```

---

## SKILLS PAR PHASE (corrigé)

| Phase | Skills | Raison |
|-------|--------|--------|
| B — Pipeline Python | `/python-pro` `/python-patterns` | Mapping données + interpolation |
| C — Canvas moteur | `/2d-games` `/fixing-motion-performance` `/focused-fix` | Rendu iso + perf |
| C — Optimisation perf | `/autoresearch-agent` | FPS mesurable = boucle auto |
| D/E — UI animations | `/animejs-animation` | Drawer + transitions DOM (pas canvas) |
| F — Intégration | `/python-pro` `/focused-fix` | Streamlit pur, pas Next.js |
| F — Tests | `/playwright-pro` | E2E : play, pause, changement scénario |
| Review | `/pr-review-expert` `/tech-debt-tracker` | Qualité finale |

---

## ASSETS

| V1 (maintenant) | V2 (optionnel, toi) |
|-----------------|---------------------|
| Canvas procédural — dégradés HSL, zéro PNG | Piskel 32×16px losanges, toi tu dessines |
| Je fournis les specs couleurs exactes | LDtk : desktop uniquement, non accessible |
| `/computer-use-agents` : trop coûteux pour Piskel web | GIMP installé pour composition sprite sheet |

---

**Prêt à coder : Prompt B1 en premier.**
