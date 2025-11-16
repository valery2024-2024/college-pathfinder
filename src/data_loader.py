from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Tuple


def load_graph_from_json(path: str | Path) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Файл не знайдено: {p}")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def load_positions(json_path: str | Path) -> Dict[str, Tuple[float, float]]:
    json_path = Path(json_path)
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    pos: Dict[str, Tuple[float, float]] = {}
    for node in data.get("nodes", []):
        nid = str(node["id"])
        x = float(node.get("x", 0.0))
        y = float(node.get("y", 0.0))
        pos[nid] = (x, y)
    return pos
