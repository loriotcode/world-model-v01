"""
iso_data.py — Données isométriques WMv0.1
Mapping World3 → tuiles, interpolation annuelle, grille scénario.
"""
from __future__ import annotations

from typing import TypedDict

import pandas as pd


# ---------------------------------------------------------------------------
# Types de tuiles
# ---------------------------------------------------------------------------

class TileState(TypedDict):
    color_top:   str   # face supérieure (losange)
    color_left:  str   # face gauche (ombre)
    color_right: str   # face droite (lumière)
    height:      int   # hauteur extrusion en pixels (0 = plat)


TILE_STATES: dict[str, TileState] = {
    "deep_water": {
        "color_top":   "#1565C0",
        "color_left":  "#0D47A1",
        "color_right": "#1976D2",
        "height": 0,
    },
    "water": {
        "color_top":   "#1976D2",
        "color_left":  "#1565C0",
        "color_right": "#42A5F5",
        "height": 0,
    },
    "sand": {
        "color_top":   "#F9A825",
        "color_left":  "#F57F17",
        "color_right": "#FBC02D",
        "height": 0,
    },
    "grass": {
        "color_top":   "#388E3C",
        "color_left":  "#2E7D32",
        "color_right": "#43A047",
        "height": 0,
    },
    "forest": {
        "color_top":   "#2E7D32",
        "color_left":  "#1B5E20",
        "color_right": "#388E3C",
        "height": 4,
    },
    "farmland": {
        "color_top":   "#A1887F",
        "color_left":  "#795548",
        "color_right": "#BCAAA4",
        "height": 0,
    },
    "suburb": {
        "color_top":   "#90A4AE",
        "color_left":  "#607D8B",
        "color_right": "#B0BEC5",
        "height": 6,
    },
    "urban": {
        "color_top":   "#546E7A",
        "color_left":  "#37474F",
        "color_right": "#78909C",
        "height": 10,
    },
    "dense_urban": {
        "color_top":   "#455A64",
        "color_left":  "#263238",
        "color_right": "#546E7A",
        "height": 16,
    },
    "industrial": {
        "color_top":   "#E64A19",
        "color_left":  "#BF360C",
        "color_right": "#FF7043",
        "height": 14,
    },
    "wasteland": {
        "color_top":   "#795548",
        "color_left":  "#4E342E",
        "color_right": "#8D6E63",
        "height": 0,
    },
    "park": {
        "color_top":   "#43A047",
        "color_left":  "#2E7D32",
        "color_right": "#66BB6A",
        "height": 2,
    },
}


# ---------------------------------------------------------------------------
# B2 — Mapping World3 → grille
# ---------------------------------------------------------------------------

COLS = 20
ROWS = 16

# Zones fixes (tuile centrale = urban, périphérie = campagne, bords = nature)
_CENTER_COL = COLS // 2
_CENTER_ROW = ROWS // 2


def _distance_to_center(col: int, row: int) -> float:
    return ((col - _CENTER_COL) ** 2 + (row - _CENTER_ROW) ** 2) ** 0.5


_MAX_DIST = _distance_to_center(0, 0)


def world3_to_grid(df_row: pd.Series, cols: int = COLS, rows: int = ROWS) -> list[list[str]]:
    """
    Convertit une ligne de données World3 normalisées en grille de tuiles.

    Variables attendues dans df_row (valeurs brutes, normalisées ici) :
        resources, population, pollution, food_per_capita, capital, hdi
    """
    def _norm(key: str, lo: float, hi: float) -> float:
        raw = float(df_row.get(key, (lo + hi) / 2))
        return max(0.0, min(1.0, (raw - lo) / (hi - lo)))

    # Plages réelles du modèle world3.py (après clamp + unités DataFrame)
    res  = _norm("resources",        0.0, 1.0)   # [0-1] clamped
    pop  = _norm("population",       0.0, 15.0)  # milliards (3.9→~12)
    pol  = _norm("pollution",        0.0, 2.0)   # [0-2] clamped
    food = _norm("food_per_capita",  0.0, 1.0)   # [0-1] normalisé
    cap  = _norm("capital",          0.0, 1.5)   # [0-1.5] clamped
    hdi  = _norm("hdi",              0.0, 1.0)   # [0-1] normalisé

    grid: list[list[str]] = []

    for row in range(rows):
        line: list[str] = []
        for col in range(cols):
            dist = _distance_to_center(col, row) / _MAX_DIST  # [0-1]

            # --- bords : nature ---
            if dist > 0.85:
                if col < 2 or row < 2:
                    tile = "deep_water"
                elif pol > 0.10:
                    tile = "wasteland"
                elif res > 0.7:
                    tile = "forest"
                elif res > 0.4:
                    tile = "grass"
                elif food > 0.5:
                    tile = "farmland"
                else:
                    tile = "sand"

            # --- périphérie : campagne/nature ---
            elif dist > 0.60:
                if pol > 0.10:
                    tile = "wasteland"
                elif res > 0.7:
                    tile = "forest"
                elif res > 0.4:
                    tile = "grass"
                elif food > 0.5:
                    tile = "farmland"
                else:
                    tile = "sand"

            # --- zone intermédiaire : suburb/rural ---
            elif dist > 0.35:
                if pol > 0.12:
                    tile = "wasteland"
                elif cap > 0.25:
                    tile = "industrial"
                elif hdi > 0.55:
                    tile = "suburb"
                elif res > 0.5:
                    tile = "grass"
                else:
                    tile = "farmland"

            # --- centre : urbain ---
            else:
                if pol > 0.13:
                    tile = "wasteland"
                elif cap > 0.30:
                    tile = "industrial"
                elif pop > 0.40 and hdi > 0.5:
                    tile = "dense_urban"
                elif pop > 0.25:
                    tile = "urban"
                else:
                    tile = "suburb"

            # parcs ponctuels (basse pollution + bonne hdi en zone intermédiaire)
            if dist < 0.45 and pol < 0.3 and hdi > 0.7 and (col + row) % 7 == 0:
                tile = "park"

            line.append(tile)
        grid.append(line)

    return grid


# ---------------------------------------------------------------------------
# B3 — Interpolation annuelle
# ---------------------------------------------------------------------------

def interpolate_year(df: pd.DataFrame, year: int | float) -> pd.Series:
    """
    Retourne la ligne interpolée pour une année donnée.
    df doit avoir une colonne 'year' ou un index entier représentant l'année.
    """
    if "year" in df.columns:
        df = df.set_index("year")

    years = df.index.astype(float)
    year_f = float(year)

    if year_f in years:
        return df.loc[year_f]

    lo = years[years <= year_f].max() if (years <= year_f).any() else years.min()
    hi = years[years >= year_f].min() if (years >= year_f).any() else years.max()

    if lo == hi:
        return df.loc[lo]

    t = (year_f - lo) / (hi - lo)
    return df.loc[lo] + t * (df.loc[hi] - df.loc[lo])


# ---------------------------------------------------------------------------
# B4 — get_scenario_grid
# ---------------------------------------------------------------------------

def get_scenario_grid(
    results: dict[str, pd.DataFrame],
    scenario: str,
    year: int,
) -> list[list[str]]:
    """
    Retourne la grille pour un scénario et une année.
    BAU forcé si year <= 2026.
    """
    sc = "BAU" if year <= 2026 else scenario
    df = results[sc]
    row = interpolate_year(df, year)
    return world3_to_grid(row)
