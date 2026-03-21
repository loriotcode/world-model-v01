# CONTEXT_WMv0.1_v2.md — Relance conversation WMv0.1

**Type :** Contexte persistant conversation secondaire  
**Statut :** Phase 5 en cours (déploiement + démo)  
**Tokens consommés :** ~15k/25k

---

## ÉTAT DU PROTOTYPE

```yaml
Status: Code complet, audité, prêt à déployer
Phases_complétées: 1, 2, 3, 4, Sécurité (×2)
Phase_en_cours: 5 (déploiement + script démo vidéo)
```

### Fichiers livrés (10 fichiers, ~49ko)

```
world-model-v01/
├── app.py                  # Streamlit 4 pages
├── requirements.txt
├── .env.example
├── .gitignore
├── models/world3.py        # Simulation World3 3 scénarios
├── models/planetary.py     # 9 limites planétaires
├── services/claude_api.py  # Intégration Anthropic API
├── utils/charts.py         # Plotly (dashboard, trajectoires, radar)
└── data/boundaries.json    # Données SRC 2023
```

### Simulations calibrées (validées)

```
BAU  2100 : pop=5.1Md, res=16%, hdi=0.21  (collapse)
BAU2 2100 : pop=8.2Md, res=12%, hdi=0.44  (collapse tardif)
SW   2100 : pop=5.1Md, res=70%, hdi=0.86  (stabilisation)
```

---

## SÉCURITÉ — AUDITS COMPLÉTÉS

9 fixes appliqués sur 2 passes :
- XSS : html.escape systématique (11 points), sanitisation sortie Claude
- Prompt injection : whitelist ALLOWED_SCENARIOS stricte
- Erreurs API : typées, jamais exposées brutes
- Validation : hex colors, plage temporelle, types numériques NaN/Inf
- Secrets : aucun sk-ant- dans les fichiers trackés
- Rate limiting : cooldown 10s via session_state
- Supply chain : toutes dépendances épinglées (==)

---

## CONTEXTE HÉRITÉ

```yaml
Position_ontologique: Nœud computationnel processus 3.8Ga
Objectif: Bifurcation SW vs BAU2 collapse 2030-2050
Fenêtre: 2025-2035 (9 ans)
Limites_planétaires: 7/9 dépassées

Scénario_3: Partenariat Anthropic
  - External Researcher Access (P=65%)
  - AI for Science P=45%, 20k$ crédits)
  - Startup Program (P=55%, 25k$ crédits)

Budget_utilisé: ~0€ (déploiement restant: 0€ si Streamlit Cloud)
Stack: Python + Streamlit + Anthropic API claude-opus-4-6
```

---

## PROCHAINE ACTION (Phase 5)

```
Utilisateur n'a pas de compte GitHub — guidage pas à pas requis :
1. Créer compte GitHub (github.com)
2. Créer repo public "world-model-v01"
3. Upload 10 fichiers via interface web (pas de CLI)
4. Créer compte Streamlit Cloud (share.streamlit.io)
5. Connecter repo → Deploy → ajouter ANTHROPIC_API_KEY dans secrets
6. Tester URL publique
7. Produire script vidéo démo 3 min
```

---

## RÈGLES OPÉRATIONNELLES

```
- Mode compact actif (tokens >50%)
- Priorité : démo-ready > feature-complete
- Décisions bloquantes : présenter A/B + recommandation
- Barre tokens : afficher à chaque réponse avec slash prévisionnel
- User commandes : "tokens", "status", "résumé primaire", "phase N"
```

**FIN CONTEXT_WMv0.1_v2.md**
