"""
models/planetary.py
Chargement et helpers pour les 9 limites planétaires.
Inclut validation stricte du schéma JSON au chargement.
"""

import json
import logging
from pathlib import Path

_logger = logging.getLogger(__name__)

DATA_PATH = Path(__file__).parent.parent / "data" / "boundaries.json"

# Whitelist des statuts autorisés
VALID_STATUSES = {"safe", "exceeded", "critical"}

STATUS_LABELS = {
    "safe":     ("✅ Zone sûre",  "#27ae60"),
    "exceeded": ("⚠️ Dépassée",  "#e67e22"),
    "critical": ("🔴 Critique",   "#e74c3c"),
}

# Schéma minimal attendu par entrée
_REQUIRED_FIELDS = {"id", "name", "indicator", "status", "description"}


def _validate_boundary(b: dict, index: int) -> dict:
    """
    Valide et normalise une limite planétaire.
    - Vérifie les champs requis
    - Valide le status contre la whitelist
    - Nettoie les valeurs numériques
    Lève ValueError si la structure est invalide.
    """
    missing = _REQUIRED_FIELDS - set(b.keys())
    if missing:
        raise ValueError(f"Limite #{index} : champs manquants {missing}")

    status = b["status"]
    if status not in VALID_STATUSES:
        raise ValueError(
            f"Limite '{b.get('id', index)}' : status invalide {status!r}. "
            f"Autorisés : {VALID_STATUSES}"
        )

    # Valeurs numériques optionnelles — forcer float ou None
    safe_limit = b.get("safe_limit")
    current    = b.get("current")

    if safe_limit is not None and not isinstance(safe_limit, (int, float)):
        raise ValueError(f"Limite '{b['id']}' : safe_limit doit être numérique")
    if current is not None and not isinstance(current, (int, float)):
        raise ValueError(f"Limite '{b['id']}' : current doit être numérique")

    # Champs optionnels étendus
    irreversible = b.get("irreversible", False)
    if not isinstance(irreversible, bool):
        raise ValueError(f"Limite '{b['id']}' : irreversible doit être un booléen")

    raw_loops = b.get("feedback_loops", [])
    if not isinstance(raw_loops, list):
        raise ValueError(f"Limite '{b['id']}' : feedback_loops doit être une liste")

    feedback_loops = []
    valid_types = {"amplifying", "dampening"}
    for loop in raw_loops:
        if not isinstance(loop, dict):
            continue
        loop_type = loop.get("type", "")
        if loop_type not in valid_types:
            _logger.warning("Type de feedback invalide ignoré : %r", loop_type)
            continue
        feedback_loops.append({
            "target_id":   str(loop.get("target_id", ""))[:64],
            "type":        loop_type,
            "description": str(loop.get("description", ""))[:512],
            "source":      str(loop.get("source", "placeholder"))[:256],
        })

    # Retourner un dict propre avec seulement les champs connus
    return {
        "id":             str(b["id"])[:64],
        "name":           str(b["name"])[:128],
        "indicator":      str(b["indicator"])[:256],
        "status":         status,                        # validé contre whitelist
        "description":    str(b["description"])[:512],
        "safe_limit":     float(safe_limit) if safe_limit is not None else None,
        "current":        float(current) if current is not None else None,
        "irreversible":   irreversible,
        "feedback_loops": feedback_loops,
    }


def load_boundaries() -> list[dict]:
    """
    Charge et valide boundaries.json.
    Lève RuntimeError si le fichier est absent, invalide ou corrompu.
    """
    if not DATA_PATH.exists():
        raise RuntimeError(f"Fichier de données introuvable : {DATA_PATH}")

    try:
        with open(DATA_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"boundaries.json invalide (JSON corrompu) : {e}") from e

    if not isinstance(data, dict) or "boundaries" not in data:
        raise RuntimeError("boundaries.json : clé 'boundaries' manquante")

    raw = data["boundaries"]
    if not isinstance(raw, list) or len(raw) == 0:
        raise RuntimeError("boundaries.json : 'boundaries' doit être une liste non vide")

    validated = []
    for i, b in enumerate(raw):
        if not isinstance(b, dict):
            raise RuntimeError(f"Limite #{i} : doit être un objet JSON")
        validated.append(_validate_boundary(b, i))

    _logger.info("Loaded %d planetary boundaries", len(validated))
    return validated


def get_status_counts(boundaries: list[dict]) -> dict:
    """Compte les limites par statut. Statuts inconnus ignorés avec warning."""
    counts = {"safe": 0, "exceeded": 0, "critical": 0}
    for b in boundaries:
        status = b.get("status")
        if status in counts:
            counts[status] += 1
        else:
            _logger.warning("Statut inattendu ignoré : %r", status)
    return counts


def get_feedback_graph(boundaries: list[dict]) -> dict:
    """
    Retourne un graphe d'adjacence des boucles de rétroaction.
    Structure: {source_id: [{"target_id": ..., "type": ..., "description": ..., "source": ...}]}
    """
    graph = {}
    for b in boundaries:
        bid = b["id"]
        graph[bid] = b.get("feedback_loops", [])
    return graph


def boundary_radar_data(boundaries: list[dict]) -> dict:
    """Données pour graphique radar Plotly."""
    score_map = {"safe": 0.2, "exceeded": 0.6, "critical": 1.0}
    names  = [b["name"]   for b in boundaries]
    scores = [score_map.get(b["status"], 0.5) for b in boundaries]
    return {"names": names, "scores": scores}
