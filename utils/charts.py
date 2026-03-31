"""
utils/charts.py — Landscape smartphone
"""

import math
import plotly.graph_objects as go
import pandas as pd
import html as _html

from models.world3 import SCENARIOS

# --- THEME ---
BACKGROUND_COLOR = "#f8f5f0"
PLOT_BACKGROUND  = "#ffffff"
GRID_COLOR       = "#e8e0d5"
TEXT_COLOR       = "#2d3748"
AXIS_COLOR       = "#4a5568"

# Couleurs de statut (source unique)
STATUS_COLORS = {
    "safe":     "#4a7c59",
    "exceeded": "#d68910",
    "critical": "#a8323e",
}

# --- META variables ---
VARIABLE_META = {
    "population":      {"label": "Population",        "yaxis": "Milliards hab."},
    "resources":       {"label": "Ressources",         "yaxis": "Fraction (0-1)"},
    "pollution":       {"label": "Pollution",          "yaxis": "Index"},
    "capital":         {"label": "Capital industriel", "yaxis": "Index"},
    "life_expectancy": {"label": "Espérance de vie",   "yaxis": "Années"},
    "food_per_capita": {"label": "Nourriture/hab.",    "yaxis": "Index"},
    "hdi":             {"label": "HDI",                "yaxis": "Score (0-1)"},
}

# Config axes : zoom désactivé
_AXIS_BASE = dict(
    fixedrange=True,
    showgrid=True,
    gridcolor=GRID_COLOR,
    gridwidth=1,
    title_font=dict(size=8, color=AXIS_COLOR),
    tickfont=dict(size=7, color=AXIS_COLOR),
    linecolor=GRID_COLOR,
)


# =========================================================
# TRAJECTOIRES
# =========================================================
def chart_trajectories(results, variable):
    meta = VARIABLE_META.get(variable, {"label": variable, "yaxis": ""})
    fig  = go.Figure()

    for key in results:
        df = results[key]
        sc = SCENARIOS[key]

        fig.add_trace(go.Scatter(
            x=df["year"],
            y=df[variable],
            name=_html.escape(sc["label"]),
            line=dict(color=sc["color"], width=2),
            hovertemplate=(
                "<b>" + _html.escape(sc["label"]) + "</b><br>"
                "Année : %{x}<br>"
                + _html.escape(meta["yaxis"]) + " : %{y:.2f}<extra></extra>"
            ),
        ))

    fig.add_vline(x=2026, line_dash="dot", line_color=AXIS_COLOR, line_width=1)

    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font=dict(color=TEXT_COLOR),
        legend=dict(
            orientation="h", y=1.02, xanchor="right", x=1,
            font=dict(size=11),
        ),
        xaxis=dict(title=dict(text="Année"), **_AXIS_BASE),
        yaxis=dict(title=dict(text=meta["yaxis"]), **_AXIS_BASE),
        dragmode=False,
    )

    return fig


# =========================================================
# BARRES LIMITES PLANÉTAIRES — ratio current/safe_limit
# =========================================================
def chart_planetary_boundaries_as_bars(boundaries):
    """
    Affiche chaque limite comme % de sa valeur sûre (100% = seuil).
    Les limites sans données numériques (novel_entities) sont affichées
    à 160% avec un marqueur spécial.
    Badges "IRRÉVERSIBLE" sur les barres concernées.
    """
    names    = []
    ratios   = []
    colors   = []
    hovers   = []
    has_data = []
    irrevs   = []

    for b in boundaries:
        cur  = b.get("current")
        lim  = b.get("safe_limit")
        stat = b["status"]
        irr  = b.get("irreversible", False)

        if cur is not None and lim is not None and lim > 0:
            ratio = (cur / lim) * 100
            hover = (
                f"<b>{_html.escape(b['name'])}</b><br>"
                f"Actuel : {cur}<br>"
                f"Limite sûre : {lim}<br>"
                f"Ratio : {ratio:.0f}%"
            )
            if irr:
                hover += "<br>⚠️ Irréversible"
            has_data.append(True)
        else:
            ratio = 160          # valeur symbolique pour "indéterminé"
            hover = (
                f"<b>{_html.escape(b['name'])}</b><br>"
                "Pas de mesure quantitative<br>"
                "Limite franchie (évaluation qualitative)"
            )
            if irr:
                hover += "<br>⚠️ Irréversible"
            has_data.append(False)

        names.append(b["name"])
        ratios.append(ratio)
        colors.append(STATUS_COLORS.get(stat, "#888888"))
        hovers.append(hover)
        irrevs.append(irr)

    fig = go.Figure()

    # Barres principales avec % au-dessus
    max_ratio = max((r for r in ratios), default=100)
    text_labels = [f"{r:.0f}%" if hd else "N/A" for r, hd in zip(ratios, has_data)]

    fig.add_trace(go.Bar(
        x=names,
        y=ratios,
        marker_color=colors,
        text=text_labels,
        textposition="outside",
        textfont=dict(size=8, color=TEXT_COLOR),
        cliponaxis=False,
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hovers,
        showlegend=False,
    ))

    # Ligne de référence à 100% (= seuil sûr)
    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color=AXIS_COLOR,
        line_width=1.5,
        annotation_text="Seuil sûr",
        annotation_font_size=8,
        annotation_font_color=AXIS_COLOR,
        annotation_position="top right",
    )

    # Badge "⚠ IRRÉVERSIBLE" au-dessus des barres concernées
    for name, ratio, irr in zip(names, ratios, irrevs):
        if irr:
            fig.add_annotation(
                x=name,
                y=ratio + max_ratio * 0.06,
                text="<b>⚠ IRRÉVERSIBLE</b>",
                showarrow=False,
                font=dict(size=7, color="#a8323e"),
                bgcolor="rgba(168,50,62,0.10)",
                borderpad=2,
            )

    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font=dict(color=TEXT_COLOR),
        showlegend=False,
        xaxis=dict(
            title=dict(text="Limite planétaire"),
            tickangle=-35,
            **_AXIS_BASE,
        ),
        yaxis=dict(
            title=dict(text="% du seuil sûr"),
            range=[0, max_ratio * 1.38],
            **_AXIS_BASE,
        ),
        dragmode=False,
    )

    return fig


# =========================================================
# RÉSEAU FEEDBACK LIMITES PLANÉTAIRES
# =========================================================
def chart_boundary_feedback_network(boundaries):
    """
    Réseau d'adjacence des boucles de rétroaction entre limites planétaires.
    9 nœuds en cercle, colorés par statut.
    Bordure rouge épaisse pour irréversible=True.
    Flèches rouges=amplifying, bleues=dampening.
    """
    n = len(boundaries)
    cx, cy, radius = 0.5, 0.5, 0.40
    angle_offset = -math.pi / 2   # premier nœud en haut

    positions = {}
    for i, b in enumerate(boundaries):
        angle = angle_offset + i * 2 * math.pi / n
        positions[b["id"]] = (
            cx + radius * math.cos(angle),
            cy + radius * math.sin(angle),
        )

    AMP_COLOR  = "#a8323e"
    DAMP_COLOR = "#3498db"

    fig = go.Figure()

    # Flèches (feedback loops)
    for b in boundaries:
        sx, sy = positions[b["id"]]
        for loop in b.get("feedback_loops", []):
            tid = loop.get("target_id", "")
            if tid not in positions:
                continue
            dx, dy = positions[tid]
            color = AMP_COLOR if loop.get("type") == "amplifying" else DAMP_COLOR
            desc  = loop.get("description", "")[:80]
            fig.add_annotation(
                x=dx, y=dy,
                ax=sx, ay=sy,
                xref="x", yref="y",
                axref="x", ayref="y",
                showarrow=True,
                arrowhead=2, arrowsize=0.85, arrowwidth=1.5,
                arrowcolor=color,
                standoff=20, startstandoff=14,
                opacity=0.65,
                text="",
                hovertext=desc,
            )

    # Nœuds
    short_names = {
        "climate": "Climat", "biodiversity": "Biodiv.",
        "land": "Terres", "freshwater": "Eau douce",
        "biogeochemical": "N/P", "ocean": "Océans",
        "aerosols": "Aérosols", "ozone": "Ozone",
        "novel_entities": "Polluants",
    }

    node_x, node_y, node_text = [], [], []
    node_color, node_lc, node_lw, hover_texts = [], [], [], []

    for b in boundaries:
        x, y = positions[b["id"]]
        node_x.append(x)
        node_y.append(y)
        node_text.append(short_names.get(b["id"], b["name"][:8]))
        node_color.append(STATUS_COLORS.get(b["status"], "#888888"))
        irr = b.get("irreversible", False)
        node_lc.append("#a8323e" if irr else "white")
        node_lw.append(3.5 if irr else 1.5)
        fb_count = len(b.get("feedback_loops", []))
        hover_texts.append(
            f"<b>{b['name']}</b><br>"
            f"Statut : {b['status']}<br>"
            f"{'⚠️ Irréversible<br>' if irr else ''}"
            f"Boucles : {fb_count}"
        )

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        marker=dict(
            size=44, color=node_color, opacity=0.92,
            line=dict(color=node_lc, width=node_lw),
        ),
        text=node_text,
        textposition="middle center",
        textfont=dict(size=7, color="white", family="sans-serif"),
        hovertext=hover_texts,
        hoverinfo="text",
        showlegend=False,
    ))

    # Légende fictive
    for label, color, dash in [
        ("Amplifying", AMP_COLOR, "solid"),
        ("Dampening",  DAMP_COLOR, "solid"),
    ]:
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="lines",
            line=dict(color=color, width=2, dash=dash),
            name=label, showlegend=True,
        ))
    for label, color in STATUS_COLORS.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(color=color, size=8),
            name=label.capitalize(), showlegend=True,
        ))

    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        xaxis=dict(range=[0.0, 1.0], visible=False, fixedrange=True),
        yaxis=dict(range=[0.0, 1.0], visible=False, fixedrange=True),
        legend=dict(
            orientation="h", y=-0.06, x=0.5, xanchor="center",
            font=dict(size=8), bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=8, r=8, t=8, b=8),
        dragmode=False,
    )

    return fig


# =========================================================
# DIAGRAMME EARTH4ALL — ARCHITECTURE 5 SECTEURS
# =========================================================
def chart_earth4all_architecture():
    """
    5 secteurs Earth4All interconnectés sur fond sombre.
    PLACEHOLDER — à compléter avec données Earth4All.jl réelles.
    """
    DARK = "#1a1a2e"

    SECTORS = [
        {"id": "energy",     "label": "⚡ Énergie",      "x": 0.50, "y": 0.85, "color": "#f39c12"},
        {"id": "food",       "label": "🌾 Alimentation",  "x": 0.84, "y": 0.55, "color": "#27ae60"},
        {"id": "inequality", "label": "⚖ Inégalités",    "x": 0.70, "y": 0.18, "color": "#8e44ad"},
        {"id": "population", "label": "👥 Population",    "x": 0.30, "y": 0.18, "color": "#3498db"},
        {"id": "finance",    "label": "💰 Finance",       "x": 0.16, "y": 0.55, "color": "#e74c3c"},
    ]
    CONNECTIONS = [
        ("energy", "food"),   ("food", "inequality"),
        ("inequality", "population"), ("population", "finance"),
        ("finance", "energy"), ("energy", "inequality"),
        ("food", "finance"),
    ]
    ARROW_COLORS = ["#f39c12","#27ae60","#8e44ad","#3498db","#e74c3c","#a8323e","#16a085"]

    fig = go.Figure()

    sec_map = {s["id"]: s for s in SECTORS}
    for i, (sid, did) in enumerate(CONNECTIONS):
        src, dst = sec_map[sid], sec_map[did]
        fig.add_annotation(
            x=dst["x"], y=dst["y"],
            ax=src["x"], ay=src["y"],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3,
            arrowsize=1.1, arrowwidth=2.5,
            arrowcolor=ARROW_COLORS[i % len(ARROW_COLORS)],
            standoff=28, startstandoff=22,
            opacity=0.80, text="",
        )

    for sec in SECTORS:
        fig.add_trace(go.Scatter(
            x=[sec["x"]], y=[sec["y"]],
            mode="markers+text",
            marker=dict(size=62, color=sec["color"], opacity=0.90,
                        line=dict(width=2, color="rgba(255,255,255,0.25)")),
            text=[sec["label"]],
            textposition="middle center",
            textfont=dict(size=9, color="white", family="sans-serif"),
            hoverinfo="skip", showlegend=False,
        ))

    fig.add_annotation(
        x=0.5, y=0.5,
        text="<b>PLACEHOLDER — Earth4All.jl</b><br>à compléter avec données réelles",
        showarrow=False,
        font=dict(size=10, color="rgba(255,255,255,0.18)"),
        align="center",
    )

    fig.update_layout(
        paper_bgcolor=DARK, plot_bgcolor=DARK,
        xaxis=dict(range=[-0.05, 1.05], visible=False, fixedrange=True),
        yaxis=dict(range=[-0.05, 1.05], visible=False, fixedrange=True),
        margin=dict(l=4, r=4, t=4, b=4),
        dragmode=False,
    )

    return fig


# =========================================================
# DIAGRAMME LEVIERS / TIPPING POINTS (Earth4All)
# =========================================================
def chart_levers_diagram():
    """
    5 leviers Earth4All → tipping points sociaux-écologiques.
    PLACEHOLDER — à compléter avec données Earth4All.jl réelles.
    """
    DARK = "#1a1a2e"

    LEVERS = [
        {"num": 1, "label": "Énergie\nRenouvelable",  "x": 0.15, "y": 0.78, "color": "#f39c12"},
        {"num": 2, "label": "Alimentation\nDurable",  "x": 0.15, "y": 0.55, "color": "#27ae60"},
        {"num": 3, "label": "Nouveau\nDéveloppement", "x": 0.15, "y": 0.32, "color": "#3498db"},
        {"num": 4, "label": "Réduction\nInégalités",  "x": 0.15, "y": 0.09, "color": "#8e44ad"},
        {"num": 5, "label": "Éducation\n& Égalité",   "x": 0.15, "y":-0.14, "color": "#e74c3c"},
    ]
    TIPPING = [
        {"label": "Santé\nPlanétaire",   "x": 0.75, "y": 0.70, "color": "#4a7c59"},
        {"label": "Cohésion\nSociale",   "x": 0.75, "y": 0.32, "color": "#2980b9"},
        {"label": "Prospérité\nDurable", "x": 0.75, "y":-0.06, "color": "#d68910"},
    ]
    CONNECTIONS = [(0,0),(0,2),(1,0),(1,2),(2,1),(2,2),(3,1),(4,1),(4,2)]

    fig = go.Figure()

    for li, ti in CONNECTIONS:
        lv, tp = LEVERS[li], TIPPING[ti]
        fig.add_annotation(
            x=tp["x"], y=tp["y"],
            ax=lv["x"] + 0.06, ay=lv["y"],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2,
            arrowsize=0.80, arrowwidth=1.3,
            arrowcolor="rgba(255,255,255,0.28)",
            standoff=24, startstandoff=14,
            opacity=0.6, text="",
        )

    for lv in LEVERS:
        fig.add_trace(go.Scatter(
            x=[lv["x"]], y=[lv["y"]],
            mode="markers+text",
            marker=dict(size=50, color=lv["color"], symbol="square",
                        opacity=0.90, line=dict(width=1.5, color="rgba(255,255,255,0.25)")),
            text=[f"<b>{lv['num']}</b>"],
            textposition="middle center",
            textfont=dict(size=13, color="white", family="sans-serif"),
            hovertext=[lv["label"].replace("\n", " ")],
            hoverinfo="text", showlegend=False,
        ))
        fig.add_annotation(
            x=lv["x"] + 0.12, y=lv["y"],
            text=lv["label"].replace("\n", "<br>"),
            showarrow=False,
            font=dict(size=9, color="rgba(255,255,255,0.88)"),
            align="left", xanchor="left",
        )

    for tp in TIPPING:
        fig.add_trace(go.Scatter(
            x=[tp["x"]], y=[tp["y"]],
            mode="markers+text",
            marker=dict(size=60, color=tp["color"], symbol="diamond",
                        opacity=0.88, line=dict(width=2, color="rgba(255,255,255,0.25)")),
            text=[tp["label"].replace("\n", "<br>")],
            textposition="middle center",
            textfont=dict(size=8, color="white", family="sans-serif"),
            hoverinfo="skip", showlegend=False,
        ))

    for label, x in [("LEVIERS", 0.15), ("TIPPING POINTS", 0.75)]:
        fig.add_annotation(
            x=x, y=0.92,
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(size=10, color="rgba(255,255,255,0.65)"),
            xanchor="center",
        )

    fig.add_annotation(
        x=0.5, y=0.42,
        text="<b>PLACEHOLDER — Earth4All.jl</b><br>à compléter avec données réelles",
        showarrow=False,
        font=dict(size=9, color="rgba(255,255,255,0.14)"),
        align="center",
    )

    fig.update_layout(
        paper_bgcolor=DARK, plot_bgcolor=DARK,
        xaxis=dict(range=[-0.05, 1.05], visible=False, fixedrange=True),
        yaxis=dict(range=[-0.22, 1.00], visible=False, fixedrange=True),
        margin=dict(l=4, r=4, t=4, b=4),
        dragmode=False,
    )

    return fig


# =========================================================
# DIAGRAMME SYSTÉMIQUE — bulles + flèches + boucles
# =========================================================
def chart_system_diagram():
    """
    Diagramme causal World3 :
      - 6 nœuds (bulles) pour les variables principales
      - Flèches étiquetées +/- pour chaque interaction
      - Boucles R1 (croissance), B1 (effondrement), B2 (contrainte ressources)
    """

    # ── Nœuds ────────────────────────────────────────────────────────────────
    NODES = {
        "pop":  {"x": 0.50, "y": 0.50, "label": "Population",  "color": "#3498db", "size": 54},
        "cap":  {"x": 0.82, "y": 0.68, "label": "Capital",     "color": "#d68910", "size": 44},
        "nour": {"x": 0.50, "y": 0.90, "label": "Nourriture",  "color": "#4a7c59", "size": 40},
        "res":  {"x": 0.82, "y": 0.20, "label": "Ressources",  "color": "#27ae60", "size": 40},
        "pol":  {"x": 0.18, "y": 0.20, "label": "Pollution",   "color": "#a8323e", "size": 40},
        "esp":  {"x": 0.18, "y": 0.68, "label": "Esp. vie",    "color": "#8e44ad", "size": 40},
    }

    # ── Arêtes ───────────────────────────────────────────────────────────────
    # (src, dst, signe, couleur, tiret, offset_x src, offset_x dst)
    EDGES = [
        # R1 — Boucle de croissance (vert)
        ("pop",  "cap",  "+", "#27ae60", "solid",  0.0,  0.0),
        ("cap",  "nour", "+", "#27ae60", "solid",  0.0,  0.0),
        ("nour", "pop",  "+", "#27ae60", "solid", -0.04, -0.04),
        # B1 — Rétroaction pollution/effondrement (rouge tirets)
        ("pop",  "pol",  "+", "#a8323e", "dash",   0.0,  0.0),
        ("pol",  "esp",  "−", "#a8323e", "dash",   0.0,  0.0),
        ("esp",  "pop",  "+", "#a8323e", "dash",   0.04,  0.04),
        # B2 — Contrainte ressources (orange pointillé)
        ("cap",  "res",  "−", "#d68910", "dot",   -0.025, -0.025),
        ("res",  "cap",  "+", "#d68910", "dot",    0.025,  0.025),
        # Pression démographique sur ressources (gris)
        ("pop",  "res",  "−", "#718096", "solid",  0.0,  0.0),
    ]

    # ── Boucles de fond (polygones semi-transparents) ─────────────────────────
    LOOPS = [
        {   # R1 — triangle Pop / Cap / Nour
            "path": "M 0.50,0.50 L 0.82,0.68 L 0.50,0.90 Z",
            "fill": "rgba(39,174,96,0.07)",
            "line": "rgba(39,174,96,0.25)",
            "label": "🔄 R1 Croissance",
            "lx": 0.66, "ly": 0.74,
            "lcolor": "#27ae60",
        },
        {   # B1 — triangle Pop / Pol / Esp
            "path": "M 0.50,0.50 L 0.18,0.20 L 0.18,0.68 Z",
            "fill": "rgba(168,50,62,0.07)",
            "line": "rgba(168,50,62,0.25)",
            "label": "⚖ B1 Effondrement",
            "lx": 0.27, "ly": 0.50,
            "lcolor": "#a8323e",
        },
        {   # B2 — bande droite Cap / Res
            "path": "M 0.75,0.20 L 0.92,0.20 L 0.92,0.68 L 0.75,0.68 Z",
            "fill": "rgba(214,137,16,0.07)",
            "line": "rgba(214,137,16,0.25)",
            "label": "⚖ B2 Contrainte",
            "lx": 0.91, "ly": 0.44,
            "lcolor": "#d68910",
        },
    ]

    fig = go.Figure()

    # ── Dessiner les polygones de boucle ──────────────────────────────────────
    for loop in LOOPS:
        fig.add_shape(
            type="path", path=loop["path"],
            xref="x", yref="y",
            fillcolor=loop["fill"],
            line=dict(color=loop["line"], width=1),
        )

    # ── Dessiner les flèches ──────────────────────────────────────────────────
    for (src_id, dst_id, sign, color, dash, ox_src, ox_dst) in EDGES:
        src = NODES[src_id]
        dst = NODES[dst_id]

        sx = src["x"] + ox_src
        sy = src["y"]
        dx = dst["x"] + ox_dst
        dy = dst["y"]

        # Standoff proportionnel à la taille du nœud destination (px → data)
        standoff = int(dst["size"] * 0.45)

        fig.add_annotation(
            x=dx, y=dy, ax=sx, ay=sy,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True,
            arrowhead=2, arrowsize=1.1, arrowwidth=1.4,
            arrowcolor=color,
            standoff=standoff,
            startstandoff=int(src["size"] * 0.30),
            text="",
        )

        # Étiquette +/− au milieu de la flèche
        mx = (sx + dx) / 2
        my = (sy + dy) / 2
        fig.add_annotation(
            x=mx, y=my,
            text=f"<b>{sign}</b>",
            showarrow=False,
            font=dict(size=9, color=color),
            bgcolor="rgba(248,245,240,0.85)",
            borderpad=1,
        )

    # ── Nœuds (bulles) ───────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=[n["x"] for n in NODES.values()],
        y=[n["y"] for n in NODES.values()],
        mode="markers+text",
        marker=dict(
            size=[n["size"] for n in NODES.values()],
            color=[n["color"] for n in NODES.values()],
            opacity=0.92,
            line=dict(width=2, color="white"),
        ),
        text=[n["label"] for n in NODES.values()],
        textposition="middle center",
        textfont=dict(size=7, color="white", family="sans-serif"),
        hoverinfo="skip",
        showlegend=False,
    ))

    # ── Labels des boucles ───────────────────────────────────────────────────
    for loop in LOOPS:
        fig.add_annotation(
            x=loop["lx"], y=loop["ly"],
            text=f"<b>{loop['label']}</b>",
            showarrow=False,
            font=dict(size=7, color=loop["lcolor"]),
            bgcolor="rgba(248,245,240,0.0)",
        )

    # ── Légende (traces fantômes) ─────────────────────────────────────────────
    for label, color in [
        ("R1 Croissance (+)", "#27ae60"),
        ("B1 Effondrement",   "#a8323e"),
        ("B2 Contrainte",     "#d68910"),
        ("Pression pop.",     "#718096"),
    ]:
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="lines",
            line=dict(color=color, width=2),
            name=label, showlegend=True,
        ))

    # ── Layout ───────────────────────────────────────────────────────────────
    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        xaxis=dict(range=[-0.05, 1.05], visible=False, fixedrange=True),
        yaxis=dict(range=[-0.02, 1.02], visible=False, fixedrange=True),
        legend=dict(
            orientation="h", y=-0.04, x=0.5, xanchor="center",
            font=dict(size=7), bgcolor="rgba(0,0,0,0)",
            itemwidth=40,
        ),
        margin=dict(l=4, r=4, t=4, b=4),
        dragmode=False,
    )

    return fig
