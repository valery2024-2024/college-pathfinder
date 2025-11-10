# src/pathfinding.py
import math
import networkx as nx
from typing import Tuple, List

def _euclid(a: tuple[float, float], b: tuple[float, float]) -> float:
    ax, ay = a
    bx, by = b
    return math.hypot(ax - bx, ay - by)

def dijkstra_path(G: nx.Graph, start: str, end: str) -> Tuple[List[str], float]:
    """Найкоротший шлях Дейкстрою (ваги ребер 'weight')."""
    path = nx.dijkstra_path(G, start, end, weight="weight")
    dist = nx.dijkstra_path_length(G, start, end, weight="weight")
    return path, float(dist)

def astar_path(G: nx.Graph, start: str, end: str) -> Tuple[List[str], float]:
    """
    A* із евклідовою евристикою за координатами вузлів ('pos').
    Працює коректно, якщо старт/фініш і проміжні вузли мають pos.
    """
    def h(u, v):
        pu = G.nodes[u].get("pos", (0.0, 0.0))
        pv = G.nodes[v].get("pos", (0.0, 0.0))
        return _euclid(pu, pv)

    path = nx.astar_path(G, start, end, heuristic=h, weight="weight")
    # підрахуємо довжину фактичну за вагами
    dist = 0.0
    for a, b in zip(path, path[1:]):
        dist += G.edges[a, b].get("weight", 1.0)
    return path, float(dist)