# src/graph_model.py
import json
import networkx as nx

def build_graph(data: dict) -> nx.Graph:
    """
    Побудувати граф NetworkX із JSON-даних.
    Підтримує атрибути вузлів: pos=(x,y), type, floor, wing.
    Кожне ребро: u, v, weight.
    """
    G = nx.Graph()
    # додавання вузлів
    for n in data["nodes"]:
        node_id = n["id"]
        pos = tuple(n.get("pos", (0, 0)))
        G.add_node(
            node_id,
            label=n.get("label", node_id),
            type=n.get("type", "room"),
            floor=n.get("floor"),
            wing=n.get("wing"),
            pos=pos
        )
    # додавання ребер
    for e in data["edges"]:
        u, v, w = e["u"], e["v"], float(e.get("weight", 1.0))
        G.add_edge(u, v, weight=w)
    return G

def node_exists(G: nx.Graph, node: str) -> bool:
    return node in G.nodes