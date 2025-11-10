# src/generate_data.py
import json
from pathlib import Path

# Крок сітки (умовні одиниці)
DX, DY = 2, 2

# Короткі мітки
LBL = {
    "SPORT": "СПРТ",
    "HALL":  "АКТ",
    "LOBBY": "ХОЛ",
    "LIB":   "БІБЛ",
}

def add_node(nodes, _id, x, y, floor, ntype="room", label=None, wing=None):
    nodes.append({
        "id": _id,
        "label": label if label else _id,
        "type": ntype,
        "floor": floor,
        "wing": wing,
        "pos": (x, y)
    })

def add_edge(edges, u, v, w=2):
    edges.append({"u": u, "v": v, "weight": float(w)})

def corridor(nodes, edges, ids, x0, y0, floor, horizontal=True, wing=None):
    """Створює ланцюжок аудиторій по сітці."""
    prev = None
    for i, rid in enumerate(ids):
        x = x0 + (i * DX if horizontal else 0)
        y = y0 + (0 if horizontal else i * DY)
        add_node(nodes, str(rid), x, y, floor, "room", str(rid), wing=wing)
        if prev:
            add_edge(edges, prev, str(rid), 2)
        prev = str(rid)

def build_data():
    nodes, edges = [], []

    # ---------------------------
    # 1 ПОВЕРХ (y ~ 10)
    # ---------------------------
    f1y = 10
    # Ліве крило: СПРТ (x=-8), АКТ (x=-6)
    add_node(nodes, "SPORT", -8, f1y, 1, "sport", LBL["SPORT"], wing="left")
    add_node(nodes, "HALL",  -6, f1y, 1, "hall",  LBL["HALL"],  wing="left")
    add_edge(edges, "SPORT", "HALL", 2)

    # Центральний ХОЛ (x=-2)
    add_node(nodes, "LOBBY", -2, f1y, 1, "lobby", LBL["LOBBY"])

    # Сходи ліві/праві
    add_node(nodes, "STAIR_L_F1", -4, f1y, 1, "stair", "SL1", wing="left")
    add_node(nodes, "STAIR_R_F1",  6, f1y, 1, "stair", "SR1", wing="right")

    # Коридор аудиторій праворуч (1..13) від x=0 до x=24
    corridor(nodes, edges, list(range(1, 14)), x0=0, y0=f1y, floor=1, horizontal=True, wing="right")

    # Зв’язки по 1-му
    add_edge(edges, "HALL", "LOBBY", 2)
    add_edge(edges, "LOBBY", "1", 2)         # ХОЛ до початку коридору
    add_edge(edges, "1", "STAIR_R_F1", 4)    # праві сходи ближче до 6-ї
    add_edge(edges, "6", "STAIR_R_F1", 3)
    add_edge(edges, "LOBBY", "STAIR_L_F1", 2)

    # ---------------------------
    # 2 ПОВЕРХ (y ~ 20)
    # ---------------------------
    f2y = 20
    # Ліві сходи/праві сходи
    add_node(nodes, "STAIR_L_F2", -4, f2y, 2, "stair", "SL2", wing="left")
    add_node(nodes, "STAIR_R_F2",  6, f2y, 2, "stair", "SR2", wing="right")

    # Ліве крило: аудиторії 14..18 уздовж лівої частини (горизонт зліва направо до ХОЛ-2)
    corridor(nodes, edges, [14, 15, 16, 17, 18], x0=-8, y0=f2y, floor=2, horizontal=True, wing="left")

    # БІБЛ поруч з 18-ю (ближче до центру)
    add_node(nodes, "LIB", -2, f2y, 2, "lib", LBL["LIB"], wing="left")
    add_edge(edges, "18", "LIB", 3)
    add_edge(edges, "LIB", "STAIR_L_F2", 2)

    # Правий коридор 19..25
    corridor(nodes, edges, [19, 20, 21, 22, 23, 24, 25], x0=4, y0=f2y, floor=2, horizontal=True, wing="right")
    add_edge(edges, "19", "STAIR_R_F2", 2)

    # Перемичка центр (між лівою та правою частиною)
    add_edge(edges, "LIB", "19", 6)

    # ---------------------------
    # 3 ПОВЕРХ (y ~ 30)
    # ---------------------------
    f3y = 30
    # Сходи
    add_node(nodes, "STAIR_L_F3", -4, f3y, 3, "stair", "SL3", wing="left")
    add_node(nodes, "STAIR_R_F3",  6, f3y, 3, "stair", "SR3", wing="right")

    # Довгий коридор 26..47 (праве крило та навколо)
    corridor(nodes, edges, list(range(26, 48)), x0=-2, y0=f3y, floor=3, horizontal=True, wing="right")

    # Зв’язки зі сходами
    add_edge(edges, "26", "STAIR_L_F3", 2)
    add_edge(edges, "33", "STAIR_R_F3", 3)

    # ---------------------------
    # Вертикальні зв’язки сходів між поверхами
    # ---------------------------
    add_edge(edges, "STAIR_L_F1", "STAIR_L_F2", 4)
    add_edge(edges, "STAIR_L_F2", "STAIR_L_F3", 4)
    add_edge(edges, "STAIR_R_F1", "STAIR_R_F2", 4)
    add_edge(edges, "STAIR_R_F2", "STAIR_R_F3", 4)

    return {"nodes": nodes, "edges": edges}

def main():
    data = build_data()
    out = Path(__file__).resolve().parents[1] / "data" / "data.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f" Згенеровано {out}")

if __name__ == "__main__":
    main()
