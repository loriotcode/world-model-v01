"""
services/claude_api.py
Intégration Anthropic API — Feature "Analyse ce scénario"

Sécurité :
- Whitelist scénarios
- Sanitisation XSS de la sortie Claude
- Timeout sur appel API
- Erreurs typées, jamais exposées brutes
- Clé API jamais loguée
- load_dotenv() avec override=False (pas de substitution)
"""

import os
import re
import logging
import anthropic
from dotenv import load_dotenv

# override=False : .env ne peut pas écraser une variable déjà définie
# (protège contre substitution .env sur systèmes multi-tenant)
load_dotenv(override=False)

_logger = logging.getLogger(__name__)

# Whitelist stricte des scénarios autorisés
ALLOWED_SCENARIOS = {"BAU", "BAU2", "SW"}

# Timeout API en secondes
_API_TIMEOUT = 30.0


def get_client() -> "anthropic.Anthropic | None":
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return None
    # Validation format basique — on ne logue PAS la clé ni même ses premiers chars
    if not api_key.startswith("sk-ant-"):
        _logger.warning("ANTHROPIC_API_KEY: format inattendu (non sk-ant-*)")
        return None
    # Instanciation dans un try pour éviter toute fuite de clé en cas d'erreur
    try:
        return anthropic.Anthropic(api_key=api_key)
    except Exception:
        _logger.error("Impossible d'instancier le client Anthropic")
        return None


SYSTEM_PROMPT = (
    "Tu es un expert en modélisation des systèmes Terre et en durabilité planétaire. "
    "Tu analyses des résultats de simulation World3 (Limits to Growth, Meadows et al.) "
    "et fournis des insights pertinents, scientifiquement fondés, accessibles à un public "
    "éduqué non-spécialiste.\n\n"
    "Format de réponse STRUCTURÉ :\n"
    "1. **Lecture du scénario** (2-3 phrases) : Ce que montrent les trajectoires\n"
    "2. **Mécanismes clés** (bullet points) : Quels feedback loops sont à l'oeuvre\n"
    "3. **Point critique** (1 phrase en gras) : Le moment ou variable le plus décisif\n"
    "4. **Leviers d'action** (2-3 bullets) : Ce qui pourrait changer ce scénario\n\n"
    "Sois direct, évite le jargon inutile. Fenêtre temporelle : 2025-2035 (urgence réelle).\n"
    "Réponds UNIQUEMENT en texte brut et Markdown standard (gras, listes). "
    "N'émets JAMAIS de HTML, de balises, de scripts ou de liens."
)

# Regex pour restaurer uniquement le gras Markdown — ancré sur contenu alphanumérique
# Refuse le gras contenant des caractères spéciaux HTML (< > & " ')
_BOLD_RE = re.compile(r"\*\*([A-Za-zÀ-ÿ0-9 ,.:;!?()\-']{1,120})\*\*")


def _sanitize_for_html(text: str) -> str:
    """
    Sanitise la sortie Claude pour affichage HTML sécurisé.
    1. Escape tous les caractères HTML
    2. Restaure uniquement le Markdown gras (contenu alphanumérique strictement)
    3. Convertit les sauts de ligne
    """
    if not isinstance(text, str):
        return ""

    # Étape 1 : escape HTML complet
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&#x27;")

    # Étape 2 : restaurer le gras — regex stricte, contenu alphanumérique uniquement
    text = _BOLD_RE.sub(r"<strong>\1</strong>", text)

    # Étape 3 : sauts de ligne
    text = text.replace("\n", "<br>")

    return text


def _safe_error(context: str) -> str:
    """Message d'erreur générique — aucune info interne exposée."""
    _logger.error("Erreur non catégorisée dans : %s", context)
    return "⚠️ Une erreur est survenue lors de l'analyse. Réessayez ou vérifiez votre configuration."


def analyse_scenario(scenario_name: str, data_summary: dict) -> str:
    """
    Analyse un scénario World3 via Claude.
    Retourne du HTML sanitisé prêt pour unsafe_allow_html=True.
    """
    # Validation entrée — whitelist strict
    if not isinstance(scenario_name, str) or scenario_name not in ALLOWED_SCENARIOS:
        _logger.warning("Scénario non autorisé : %r", scenario_name)
        return "⚠️ Scénario invalide."

    if not isinstance(data_summary, dict):
        return "⚠️ Données de simulation invalides."

    client = get_client()
    if not client:
        return "⚠️ Clé API Anthropic non configurée. Ajoutez ANTHROPIC_API_KEY dans .env"

    # Formatage sécurisé — valeurs numériques uniquement, jamais de strings user
    def _pct(key: str) -> str:
        v = data_summary.get(key)
        return f"{v * 100:.0f}%" if isinstance(v, (int, float)) and not (v != v) else "N/A"  # not NaN

    def _f2(key: str) -> str:
        v = data_summary.get(key)
        return f"{v:.2f}" if isinstance(v, (int, float)) and not (v != v) else "N/A"

    def _f3(key: str) -> str:
        v = data_summary.get(key)
        return f"{v:.3f}" if isinstance(v, (int, float)) and not (v != v) else "N/A"

    # scenario_name est validé contre whitelist — safe à insérer
    prompt = (
        f"Analyse le scénario {scenario_name} de la simulation World3 simplifiée.\n\n"
        f"Trajectoires clés :\n\n"
        f"2025 (aujourd'hui) :\n"
        f"- Population : {_f2('pop_2025')} milliards\n"
        f"- Ressources restantes : {_pct('res_2025')}\n"
        f"- Pollution : {_f3('pol_2025')} (index)\n"
        f"- Capital : {_f3('cap_2025')} (index)\n\n"
        f"2050 :\n"
        f"- Population : {_f2('pop_2050')} milliards\n"
        f"- Ressources restantes : {_pct('res_2050')}\n"
        f"- Pollution : {_f3('pol_2050')}\n"
        f"- Capital : {_f3('cap_2050')}\n\n"
        f"2100 :\n"
        f"- Population : {_f2('pop_2100')} milliards\n"
        f"- Ressources restantes : {_pct('res_2100')}\n"
        f"- HDI approx. : {_f2('hdi_2100')}\n\n"
        f"Fournis ton analyse structurée."
    )

    try:
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=800,
            timeout=_API_TIMEOUT,       # ← timeout ajouté
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text
        return _sanitize_for_html(raw)

    except anthropic.AuthenticationError:
        # Ne pas logger le message d'erreur anthropic (peut contenir la clé tronquée)
        _logger.error("Authentification API échouée")
        return "⚠️ Clé API invalide ou expirée. Vérifiez ANTHROPIC_API_KEY dans .env"
    except anthropic.RateLimitError:
        _logger.warning("Rate limit API Anthropic atteint")
        return "⚠️ Limite de requêtes API atteinte. Réessayez dans quelques instants."
    except anthropic.APIConnectionError:
        _logger.error("Connexion API Anthropic échouée")
        return "⚠️ Connexion à l'API impossible. Vérifiez votre connexion réseau."
    except anthropic.APITimeoutError:
        _logger.warning("Timeout API Anthropic (%ss)", _API_TIMEOUT)
        return "⚠️ L'analyse a pris trop de temps. Réessayez dans un instant."
    except Exception:
        return _safe_error("analyse_scenario")


def extract_summary(df, scenario_name: str) -> dict:
    """Extrait les données clés d'un DataFrame pour l'analyse Claude."""
    if not isinstance(scenario_name, str) or scenario_name not in ALLOWED_SCENARIOS:
        raise ValueError(f"Scénario non autorisé : {scenario_name!r}")

    def get_row(year: int):
        rows = df[df["year"] == year]
        return rows.iloc[0] if len(rows) > 0 else None

    r25, r50, r100 = get_row(2025), get_row(2050), get_row(2100)

    def safe_round(row, col: str, decimals: int):
        try:
            v = float(row[col]) if row is not None else None
            if v is None or v != v:  # NaN check
                return None
            return round(v, decimals)
        except (TypeError, ValueError, KeyError):
            return None

    return {
        "scenario": scenario_name,
        "pop_2025": safe_round(r25,  "population", 2),
        "res_2025": safe_round(r25,  "resources",  3),
        "pol_2025": safe_round(r25,  "pollution",  3),
        "cap_2025": safe_round(r25,  "capital",    3),
        "pop_2050": safe_round(r50,  "population", 2),
        "res_2050": safe_round(r50,  "resources",  3),
        "pol_2050": safe_round(r50,  "pollution",  3),
        "cap_2050": safe_round(r50,  "capital",    3),
        "pop_2100": safe_round(r100, "population", 2),
        "res_2100": safe_round(r100, "resources",  3),
        "hdi_2100": safe_round(r100, "hdi",        3),
    }
