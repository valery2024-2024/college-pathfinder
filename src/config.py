from pathlib import Path

# шлях до JSON із графом корпусу
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "data.json"

# Візуалізація: чи підписувати ваги ребер
DRAW_WEIGHTS = True

# Алгоритм за замовчуванням: "dijkstra" або "astar"
DEFAULT_ALGO = "dijkstra"