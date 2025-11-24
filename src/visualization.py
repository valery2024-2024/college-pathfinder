import math
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patheffects import withStroke


def _draw_node_labels(ax, pos, labels, dy=0.06, fs=9):
    # акуратні підписи вузлів зі зсувом вгору і білою підкладкою.
    for n, (x, y) in pos.items():
        ax.text(
            x, y + dy, str(labels.get(n, n)),
            fontsize=fs, fontweight="bold", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75),
            zorder=6, clip_on=False,
            path_effects=[withStroke(linewidth=1.5, foreground="white")]  
        )

def _get_pos(G, pos=None):
    # вже готові позиції
    if pos:
        return {n: (float(x), float(y)) for n, (x, y) in pos.items()}

    # збирає те що є в атрибутах вузлів
    fixed = {}
    for n, d in G.nodes(data=True):
        if "pos" in d and isinstance(d["pos"], (tuple, list)) and len(d["pos"]) == 2:
            x, y = d["pos"]
            fixed[n] = (float(x), float(y))
        elif "x" in d and "y" in d:
            fixed[n] = (float(d["x"]), float(d["y"]))

    # якщо позиції є для всіх - віддає як є
    if len(fixed) == G.number_of_nodes():
        return fixed

    # інакше - дораховує відсутні, фіксуючи відомі 
    if fixed:
        pos_full = nx.spring_layout(G, seed=42, pos=fixed, fixed=list(fixed.keys()))
    else:
        pos_full = nx.spring_layout(G, seed=42)

    return pos_full

def _draw_edge_labels_midpoints(
    ax, G, pos, edge_labels, fontsize=8, color="#6b7280", offset=0.06):
    # безпечне підписування ваг: текст у середині ребра з невеличким відступом
    for (u, v), label in edge_labels.items():
        if u not in pos or v not in pos:
            continue
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        xm, ym = (x1 + x2) / 2.0, (y1 + y2) / 2.0

        dx, dy = (x2 - x1), (y2 - y1)
        L = math.hypot(dx, dy) or 1.0
        # невеликий зсув щоб текст не злипався
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
    # візуалізація графа корпусу.
    pos = _get_pos(G, pos)

    fig, ax = plt.subplots(figsize=(12, 7))
    if title:
        ax.set_title(title, fontsize=14)

    # база: вузли/ребра
    nx.draw_networkx_nodes(
        G, pos, node_size=1200, node_color="lightblue",
        edgecolors="black", linewidths=1.0, ax=ax
    )
    nx.draw_networkx_edges(G, pos, width=1.5, edge_color="lightgray", ax=ax)
    labels = {n: G.nodes[n].get("label", n) for n in G.nodes()}
    _draw_node_labels(ax, pos, labels, dy=0.07, fs=9)

    if draw_weights:
        edge_labels = {(u, v): d.get("weight", "") for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels=edge_labels,
            font_size=8,
            rotate=False,            
            label_pos=0.55,          
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.65),
            clip_on=False
        )    

    # Маршрут + підсвічування кольором
    if path and len(path) > 1:
        path_edges = list(zip(path[:-1], path[1:]))

        # лінія маршруту відображається червоним кольором
        nx.draw_networkx_edges(
            G, pos, edgelist=path_edges, width=3.0, edge_color="#e53935", ax=ax
        )

        # старт відображається синім кольором
        start_node = path[0]
        nx.draw_networkx_nodes(
            G, pos, nodelist=[start_node], node_color="#29b6f6",
            node_size=1400, edgecolors="black", linewidths=1.5, ax=ax
        )

        # фініш відображається синім кольором
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
