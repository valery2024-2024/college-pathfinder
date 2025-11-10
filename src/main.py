# src/main.py
import sys
from pathlib import Path
import networkx as nx

from config import DATA_PATH, DRAW_WEIGHTS, DEFAULT_ALGO
from data_loader import load_graph_from_json, load_positions
from graph_model import build_graph, node_exists
from pathfinding import dijkstra_path, astar_path
from visualization import draw_graph


def choose_algo(name: str) -> str:
    name = (name or "").strip().lower()
    if name in ("d", "dijkstra"):
        return "dijkstra"
    if name in ("a", "astar", "a*"):
        return "astar"
    return DEFAULT_ALGO


def main() -> None:
    print(" Система пошуку найкоротшого маршруту по корпусу коледжу (Python) ")

    if not Path(DATA_PATH).exists():
        print(f" Дані не знайдено: {DATA_PATH}")
        print("   Спочатку згенеруйте файл даних командою:\n"
              "   python -m src.generate_data")
        sys.exit(1)

    # 1) читаємо JSON
    data = load_graph_from_json(DATA_PATH)
    # 2) будуємо граф (функція з твого graph_model.py)
    G: nx.Graph = build_graph(data)

    while True:
        start = input("Введіть початкову точку (наприклад, 12 або SPORT): ").strip()
        end   = input("Введіть кінцеву точку (наприклад, LIB): ").strip()

        if not node_exists(G, start) or not node_exists(G, end):
            print(" Вузол(и) не знайдено в графі. Перевірте назви і спробуйте знову.")
            again = input("Спробувати ще? (yes/no): ").strip().lower()
            if again != "yes":
                break
            continue

        algo = choose_algo(input("Алгоритм [dijkstra/astar] (Enter = dijkstra): "))

        try:
            if algo == "astar":
                path, dist = astar_path(G, start, end)
            else:
                path, dist = dijkstra_path(G, start, end)
        except Exception as ex:
            print(f" Помилка пошуку: {ex}")
            again = input("Спробувати ще? (yes/no): ").strip().lower()
            if again != "yes":
                break
            continue

        print("\n Найкоротший маршрут:", " далі ".join(path))
        print(f"   Загальна довжина: {dist:.2f} (умовн. од.)\n")

        vis = input("Показати візуалізацію? (yes/no): ").strip().lower()
        if vis == "yes":
            pos_json = load_positions(DATA_PATH)   # ключі — str(node_id)
            # беремо тільки наявні у JSON
            pos = {n: pos_json[str(n)] for n in G.nodes if str(n) in pos_json}

            draw_graph(
                G,
                #pos=pos,
                path=path,
                draw_weights=DRAW_WEIGHTS,
                title=f"Маршрут {start} → {end} ({algo})",
            )   

            print(f"[diag] pos: {len(pos)} із {G.number_of_nodes()} вузлів мають координати")     

        again = input("Виконати новий пошук? (yes/no): ").strip().lower()
        if again != "yes":
            print(" Програму завершено.")
            break


if __name__ == "__main__":
    main()
