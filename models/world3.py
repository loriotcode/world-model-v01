"""
models/world3.py
Simulation World3 simplifiée — 4 variables core + feedback loops
Basé sur Meadows et al. "Limits to Growth" (1972, 2004)
"""

import re
import numpy as np
import pandas as pd

# Regex validation couleur hex CSS
_HEX_COLOR_RE = re.compile(r'^#[0-9a-fA-F]{6}$')

def _validate_hex_color(color: str, field: str) -> str:
    """Valide qu'une couleur est un hex CSS strict (#rrggbb)."""
    if not isinstance(color, str) or not _HEX_COLOR_RE.match(color):
        raise ValueError(f"{field}: couleur hex invalide {color!r} (attendu #rrggbb)")
    return color


# ── Paramètres scénarios ─────────────────────────────────────────────────────

SCENARIOS = {
    "BAU": {
        "label": "Business as Usual (BAU)",
        "color": "#e74c3c",
        "description": "Tendances actuelles non modifiées. Déclin progressif, ressources épuisées.",
        "params": {
            "tech_progress": 0.003,
            "pollution_control": 0.003,
            "resource_efficiency": 1.0,
            "birth_rate_mod": 1.0,
            "investment_rate": 0.20,
            "pollution_emission_factor": 1.0,
            "resource_depletion_factor": 1.0,
        }
    },
    "BAU2": {
        "label": "BAU + Tech Optimiste (BAU2)",
        "color": "#e67e22",
        "description": "Progrès tech accéléré mais sans changement systémique. Collapse retardé.",
        "params": {
            "tech_progress": 0.012,
            "pollution_control": 0.012,
            "resource_efficiency": 1.6,
            "birth_rate_mod": 0.92,
            "investment_rate": 0.22,
            "pollution_emission_factor": 0.85,
            "resource_depletion_factor": 0.70,
        }
    },
    "SW": {
        "label": "Sustainable World (SW)",
        "color": "#27ae60",
        "description": "Transition systémique : sobriété + tech propre + gouvernance mondiale. Stabilisation.",
        "params": {
            "tech_progress": 0.020,
            "pollution_control": 0.030,
            "resource_efficiency": 2.8,
            "birth_rate_mod": 0.75,
            "investment_rate": 0.16,
            "pollution_emission_factor": 0.40,
            "resource_depletion_factor": 0.30,
        }
    }
}

# Validation couleurs au chargement — fail-fast si SCENARIOS mal configuré
for _k, _sc in SCENARIOS.items():
    _validate_hex_color(_sc["color"], f"SCENARIOS[{_k!r}]['color']")

# Whitelist pour validation externe
VALID_SCENARIO_KEYS = set(SCENARIOS.keys())

# Année à partir de laquelle les scénarios divergent de BAU
BIFURCATION_YEAR = 2026

# ── Constantes calibrées ─────────────────────────────────────────────────────

INITIAL_CONDITIONS = {
    "population": 3.9e9,
    "capital":    0.35,
    "pollution":  0.12,
    "resources":  1.0,
}

LIFE_EXPECTANCY_BASE = 32
LIFE_EXPECTANCY_MAX  = 85
POLLUTION_DECAY      = 0.02


class World3Simulation:
    """
    Simulation World3 simplifiée.
    4 stocks : Population, Capital, Pollution, Ressources
    Intégrateur Euler, pas dt=1 an, 1970-2100
    """

    def __init__(self, scenario_key: str = "BAU"):
        # Validation entrée
        if scenario_key not in VALID_SCENARIO_KEYS:
            raise ValueError(
                f"Scénario inconnu : {scenario_key!r}. "
                f"Valeurs autorisées : {sorted(VALID_SCENARIO_KEYS)}"
            )
        self.scenario_key = scenario_key
        self.scenario = SCENARIOS[scenario_key]
        self.p = self.scenario["params"]

    def _life_expectancy(self, capital_idx: float, pollution_idx: float) -> float:
        base = LIFE_EXPECTANCY_BASE + (LIFE_EXPECTANCY_MAX - LIFE_EXPECTANCY_BASE) * capital_idx
        pollution_penalty = pollution_idx * 25
        return max(20.0, base - pollution_penalty)

    def _birth_rate(self, capital_idx: float, year: int) -> float:
        base_rate = 0.040 - 0.022 * capital_idx
        if year > 2000:
            base_rate *= (1 - 0.003 * (year - 2000))
        return max(0.010, base_rate * self.p["birth_rate_mod"])

    def _death_rate(self, life_expectancy: float) -> float:
        return 1.0 / max(15.0, life_expectancy)

    def _capital_growth(self, capital_idx: float, resources_idx: float, year: int) -> float:
        tech_factor = 1.0 + self.p["tech_progress"] * (year - 1970)
        resource_constraint = resources_idx ** 0.5
        efficiency = self.p["resource_efficiency"]
        growth = self.p["investment_rate"] * resource_constraint * tech_factor * efficiency
        depreciation = 0.05 * capital_idx
        return growth * 0.03 - depreciation

    def _pollution_delta(self, capital_idx: float, population: float, year: int) -> float:
        emissions = capital_idx * (population / 4e9) * 0.015 * self.p["pollution_emission_factor"]
        tech_mult = 1.0 + self.p["tech_progress"] * (year - 1970) * 5
        control = self.p["pollution_control"] * tech_mult * capital_idx * 0.5
        natural_decay = POLLUTION_DECAY * capital_idx * 0.3
        return emissions - control - natural_decay

    def _resource_depletion(self, capital_idx: float, population: float) -> float:
        base_rate = 0.012
        pop_factor = population / 4e9
        cap_factor = capital_idx / 0.35
        efficiency = self.p["resource_efficiency"]
        depletion_mod = self.p["resource_depletion_factor"]
        return -(base_rate * pop_factor * cap_factor / efficiency * depletion_mod)

    def run(self, start: int = 1970, end: int = 2100) -> pd.DataFrame:
        """Lance la simulation, retourne DataFrame annuel.

        Avant BIFURCATION_YEAR, tous les scénarios suivent les paramètres BAU.
        La divergence commence à partir de BIFURCATION_YEAR.
        """
        # Validation plage temporelle
        if not (1900 <= start < end <= 2200):
            raise ValueError(f"Plage temporelle invalide : {start}-{end}")

        years = list(range(start, end + 1))

        pop = INITIAL_CONDITIONS["population"]
        cap = INITIAL_CONDITIONS["capital"]
        pol = INITIAL_CONDITIONS["pollution"]
        res = INITIAL_CONDITIONS["resources"]

        _bau_params = SCENARIOS["BAU"]["params"]
        _sc_params  = self.scenario["params"]

        records = []

        for year in years:
            # Avant la bifurcation, tous les scénarios suivent BAU
            self.p = _sc_params if year >= BIFURCATION_YEAR else _bau_params

            # Clamp valeurs
            cap = max(0.01, min(1.5, cap))
            pol = max(0.0,  min(2.0, pol))
            res = max(0.0,  min(1.0, res))
            pop = max(1e6, pop)

            # Facteur collapse
            collapse_factor = 1.0
            if res < 0.1:
                collapse_factor *= (res / 0.1) ** 2
            if pol > 1.0:
                collapse_factor *= max(0.1, 1.0 - (pol - 1.0) * 0.5)

            # Variables intermédiaires
            le = self._life_expectancy(cap, pol) * collapse_factor
            br = self._birth_rate(cap, year)
            dr = self._death_rate(le)

            # Déltas annuels
            dpop = pop * (br - dr) * collapse_factor
            dcap = self._capital_growth(cap, res, year) * collapse_factor
            dpol = self._pollution_delta(cap, pop, year)
            dres = self._resource_depletion(cap, pop) if res > 0 else 0.0

            # Indicateurs dérivés
            food_per_capita = min(1.0, (cap * 0.8 + res * 0.2) / 0.4) * collapse_factor
            hdi_approx = min(1.0, (le / 85 * 0.33 + cap * 0.33 + food_per_capita * 0.33))

            records.append({
                "year":            year,
                "population":      pop / 1e9,
                "capital":         cap,
                "pollution":       pol,
                "resources":       res,
                "life_expectancy": le,
                "birth_rate":      br * 1000,
                "death_rate":      dr * 1000,
                "food_per_capita": food_per_capita,
                "hdi":             hdi_approx,
            })

            pop += dpop
            cap += dcap
            pol += dpol
            res += dres

        return pd.DataFrame(records)


def run_all_scenarios(start: int = 1970, end: int = 2100) -> dict:
    """Lance les 3 scénarios et retourne un dict {key: DataFrame}."""
    return {
        key: World3Simulation(key).run(start, end)
        for key in SCENARIOS
    }


# ── Test rapide ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    results = run_all_scenarios()
    for name, df in results.items():
        row_2050 = df[df["year"] == 2050].iloc[0]
        print(f"\n{'='*40}")
        print(f"Scénario : {name}")
        print(f"  Population 2050 : {row_2050['population']:.2f} Md")
        print(f"  Capital 2050    : {row_2050['capital']:.3f}")
        print(f"  Pollution 2050  : {row_2050['pollution']:.3f}")
        print(f"  Ressources 2050 : {row_2050['resources']:.3f}")
        print(f"  HDI 2050        : {row_2050['hdi']:.3f}")
