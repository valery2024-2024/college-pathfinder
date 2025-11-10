# src/visualization.py
import math
import matplotlib.pyplot as plt
import networkx as nx


def _get_pos(G, pos=None):
    # 1) вже готові позиції
    if pos:
        return {n: (float(x), float(y)) for n, (x, y) in pos.items()}

    # 2) збираємо, що є в атрибутах вузлів
    fixed = {}
    for n, d in G.nodes(data=True):
        if "pos" in d and isinstance(d["pos"], (tuple, list)) and len(d["pos"]) == 2:
            x, y = d["pos"]
            fixed[n] = (float(x), float(y))
        elif "x" in d and "y" in d:
            fixed[n] = (float(d["x"]), float(d["y"]))

    # 2a) якщо позиції є для всіх — віддаємо як є
    if len(fixed) == G.number_of_nodes():
        return fixed

    # 3) інакше — дораховуємо відсутні, фіксуючи відомі
    if fixed:
        pos_full = nx.spring_layout(G, seed=42, pos=fixed, fixed=list(fixed.keys()))
    else:
        pos_full = nx.spring_layout(G, seed=42)

    return pos_full

def _draw_edge_labels_midpoints(
    ax, G, pos, edge_labels, fontsize=8, color="#6b7280", offset=0.06
):
    """Безпечне підписування ваг: текст у середині ребра з невеличким відступом
    перпендикулярно до ребра. Не використовує проблемний draw_networkx_edge_labels."""
    for (u, v), label in edge_labels.items():
        if u not in pos or v not in pos:
            continue
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        xm, ym = (x1 + x2) / 2.0, (y1 + y2) / 2.0

        dx, dy = (x2 - x1), (y2 - y1)
        L = math.hypot(dx, dy) or 1.0
        # невеликий зсув перпендикулярно до ребра, щоб текст не «злипався» з лінією
        ox, oy = (-dy / L * offset), (dx / L * offset)

        ax.text(
            xm + ox,
            ym + oy,
            str(label),
            fontsize=fontsize,
            color=color,
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.6),
        )


def draw_graph(
    G,
    pos=None,
    path=None,
    draw_weights=False,
    title=None,
    highlight_end=True,
):
    """Візуалізація графа корпусу."""
    pos = _get_pos(G, pos)

    fig, ax = plt.subplots(figsize=(12, 7))
    if title:
        ax.set_title(title, fontsize=14)

    # 1) База: вузли/ребра
    nx.draw_networkx_nodes(
        G, pos, node_size=1200, node_color="lightblue",
        edgecolors="black", linewidths=1.0, ax=ax
    )
    nx.draw_networkx_edges(G, pos, width=1.5, edge_color="lightgray", ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold", ax=ax)

    # 2) Підписи ваг ребер — БЕЗПЕЧНИМ способом
    if draw_weights:
        edge_labels = {(u, v): d.get("weight", "") for u, v, d in G.edges(data=True)}
        _draw_edge_labels_midpoints(ax, G, pos, edge_labels, fontsize=8, color="#6b7280")

    # 3) Маршрут + підсвітки
    if path and len(path) > 1:
        path_edges = list(zip(path[:-1], path[1:]))

        # 🔴 лінія маршруту
        nx.draw_networkx_edges(
            G, pos, edgelist=path_edges, width=3.0, edge_color="#e53935", ax=ax
        )

        # 🔵 старт
        start_node = path[0]
        nx.draw_networkx_nodes(
            G, pos, nodelist=[start_node], node_color="#29b6f6",
            node_size=1400, edgecolors="black", linewidths=1.5, ax=ax
        )

        # 🟢 фініш
        if highlight_end:
            end_node = path[-1]
            nx.draw_networkx_nodes(
                G, pos, nodelist=[end_node], node_color="#43a047",
                node_size=1400, edgecolors="black", linewidths=1.5, ax=ax
            )

            # акуратні межі та пропорції
            xs = [p[0] for p in pos.values()]
            ys = [p[1] for p in pos.values()]
            pad = 1.0
            ax.set_xlim(min(xs) - pad, max(xs) + pad)
            ax.set_ylim(min(ys) - pad, max(ys) + pad)
            ax.set_aspect("equal", adjustable="box")
            fig.tight_layout()

    ax.axis("off")
    fig.tight_layout()
    plt.show()
    return fig, ax
