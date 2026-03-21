# WMv0.1→PRIMARY [2026-02-22]

## Status : Phase 5 en cours (déploiement)

---

### Complété

- Simulation World3 : 3 scénarios (BAU/BAU2/SW), calibrés, validés
- Interface Streamlit : 4 pages (overview, scénarios, limites planétaires, analyse IA)
- Intégration Claude API : analyse structurée par scénario
- 2 audits sécurité approfondis : 9 fixes (XSS, injection, whitelist, secrets, NaN, ReDoS...)
- Scripts : prompt contexte relance, script démo vidéo 3min, instructions déploiement

### En cours

- Phase 5 : guidage déploiement GitHub + Streamlit Cloud (user sans expérience GitHub)

### Métriques succès v0.1

```
Code fonctionnel       : ✅
Simulations correctes  : ✅  (BAU collapse, SW stabilisation)
UI 4 pages             : ✅
Claude API intégré     : ✅
Sécurité auditée       : ✅  (2 passes, 9 fixes)
URL publique           : ⏳  (Phase 5)
Vidéo démo             : ⏳  (après déploiement)
README                 : ✅
```

### Applications Anthropic — readiness

```
External Researcher Access : ✅ prêt (manque URL)
AI for Science             : ✅ prêt (manque URL)
Startup Program            : ✅ prêt (manque URL)
```

### Tokens

```
Utilisés  : ~15k/25k (60%)
Restants  : ~10k
Suffisant pour : guidage déploiement complet
```

### Prochaines étapes

1. Guidage GitHub (création compte + upload fichiers)
2. Déploiement Streamlit Cloud
3. Test URL publique
4. Enregistrement vidéo démo

---

*Pour relancer la conversation secondaire : fournir CONTEXT_WMv0.1_v2.md*
