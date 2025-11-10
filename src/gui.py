# src/gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import networkx as nx

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.config import DATA_PATH, DRAW_WEIGHTS, DEFAULT_ALGO
from src.data_loader import load_graph_from_json
from src.graph_model import build_graph
from src.pathfinding import dijkstra_path, astar_path

FLOOR_TABS = [1, 2, 3, "all"]  # 4-та вкладка = усі поверхи

class FloorPlot(ttk.Frame):
    def __init__(self, master, title=""):
        super().__init__(master)
        self.fig = Figure(figsize=(7, 4.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.axis("off")
        self.ax.set_title(title)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def draw_subgraph(self, G: nx.Graph, floor: int | None, path=None, draw_weights=True):
        self.ax.clear()
        self.ax.axis("off")

        if floor == "all" or floor is None:
            nodes = list(G.nodes)
        else:
            nodes = [n for n, d in G.nodes(data=True) if d.get("floor") == floor]

        subG = G.subgraph(nodes).copy()
        if not nodes:
            self.ax.set_title("Немає вузлів для відображення")
            self.canvas.draw_idle()
            return

        if all("pos" in G.nodes[n] for n in nodes):
            pos = {n: G.nodes[n]["pos"] for n in nodes}
        else:
            pos = nx.spring_layout(subG, seed=7)

        labels = {n: G.nodes[n].get("label", n) for n in nodes}
        nx.draw(subG, pos, with_labels=True, labels=labels,
                node_size=650, node_color="#cde6ff", font_size=9, ax=self.ax)

        if draw_weights:
            el = nx.get_edge_attributes(subG, "weight")
            nx.draw_networkx_edge_labels(subG, pos, edge_labels=el, font_size=8, ax=self.ax)

        if path:
            p = [n for n in path if n in subG.nodes]
            if len(p) > 1:
                # 🔴 1) Маршрут — червоний
                nx.draw_networkx_edges(
                    subG, pos,
                    edgelist=list(zip(p, p[1:])),
                    width=3.5,
                    edge_color="#e53935",  # насичений червоний
                    ax=self.ax
                )

                # 🔵 2) Стартова точка — блакитна
                start_node = p[0]
                nx.draw_networkx_nodes(
                    subG, pos,
                    nodelist=[start_node],
                    node_color="#29b6f6",  # блакитний
                    node_size=700,
                    edgecolors="black",
                    linewidths=1.5,
                    ax=self.ax
                )

                # 🟢 3) Кінцева точка — зелена
                end_node = p[-1]
                nx.draw_networkx_nodes(
                    subG, pos,
                    nodelist=[end_node],
                    node_color="#43a047",  # зелений
                    node_size=700,
                    edgecolors="black",
                    linewidths=1.5,
                    ax=self.ax
                )    


        #if path:
           # p = [n for n in path if n in subG.nodes]
            #if len(p) > 1:
                #nx.draw_networkx_edges(subG, pos, edgelist=list(zip(p, p[1:])), width=3, edge_color="#e53935", ax=self.ax)

        t = "Усі поверхи" if floor == "all" else f"Поверх {floor}"
        self.ax.set_title(t)
        self.fig.tight_layout()
        self.canvas.draw_idle()

class PathfinderGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Навігація корпусом — сітка + вкладки поверхів")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        if not Path(DATA_PATH).exists():
            messagebox.showerror("Дані", f"Не знайдено {DATA_PATH}\nСпочатку: python -m src.generate_data")
            self.destroy()
            return

        data = load_graph_from_json(DATA_PATH)
        self.G = build_graph(data)
        self.nodes_sorted = self._sorted_nodes()

        self._build_controls()
        self._build_tabs()
        self._redraw_all(path=None)

    def _sorted_nodes(self):
        def keyf(n):
            d = self.G.nodes[n]
            floor = d.get("floor", 0) or 0               # None -> 0
            wing  = d.get("wing") or ""                  # None -> ""
            typ   = d.get("type") or "room"              # None -> "room"
            label = str(d.get("label", n))
            return (int(floor), wing, typ, label)

        result = []
        for n in sorted(self.G.nodes, key=keyf):
            lab = str(self.G.nodes[n].get("label", n))
            display = f"{n} — {lab}" if lab != n else n
            result.append((display, n))
        return result    

   # def _sorted_nodes(self):
   #     def keyf(n):
    #        d = self.G.nodes[n]
     #       return (d.get("floor", 0) or 0, d.get("wing",""), d.get("type","room"), str(d.get("label", n)))
      #  res = []
       # for n in sorted(self.G.nodes, key=keyf):
        #    lab = str(self.G.nodes[n].get("label", n))
         #   display = f"{n} — {lab}" if lab != n else n
          #  res.append((display, n))
        #return res

    def _build_controls(self):
        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Початок:").grid(row=0, column=0, sticky="w")
        self.start_var = tk.StringVar()
        self.start_cb = ttk.Combobox(top, textvariable=self.start_var, state="readonly", width=28,
                                     values=[d for d,_ in self.nodes_sorted])
        self.start_cb.grid(row=0, column=1, padx=5)
        if self.nodes_sorted: self.start_cb.current(0)

        ttk.Label(top, text="Кінець:").grid(row=0, column=2, sticky="w")
        self.end_var = tk.StringVar()
        self.end_cb = ttk.Combobox(top, textvariable=self.end_var, state="readonly", width=28,
                                   values=[d for d,_ in self.nodes_sorted])
        self.end_cb.grid(row=0, column=3, padx=5)
        if len(self.nodes_sorted)>1: self.end_cb.current(1)

        algo = ttk.LabelFrame(top, text="Алгоритм")
        algo.grid(row=0, column=4, padx=10)
        self.algo_var = tk.StringVar(value=DEFAULT_ALGO)
        ttk.Radiobutton(algo, text="Dijkstra", value="dijkstra", variable=self.algo_var).pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(algo, text="A*",       value="astar",    variable=self.algo_var).pack(side=tk.LEFT, padx=6)

        btns = ttk.Frame(top)
        btns.grid(row=0, column=5, padx=10)
        ttk.Button(btns, text="Побудувати маршрут", command=self._on_build).pack(fill=tk.X, pady=1)
        ttk.Button(btns, text="Очистити", command=self._on_clear).pack(fill=tk.X, pady=1)

        # Результат
        res = ttk.Frame(self, padding=(8,4))
        res.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(res, text="Результат:").pack(anchor="w")
        self.result_txt = tk.Text(res, height=4, wrap="word")
        self.result_txt.pack(fill=tk.X)
        self.result_txt.configure(state="disabled")

    def _build_tabs(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.plots = {}
        for f in FLOOR_TABS:
            title = "Усі поверхи" if f == "all" else f"Поверх {f}"
            frame = FloorPlot(self.nb, title=title)
            self.nb.add(frame, text=title)
            self.plots[f] = frame

    # utils
    def _to_id(self, display):
        return display.split("—",1)[0].strip() if "—" in display else display

    def _set_result(self, text):
        self.result_txt.configure(state="normal")
        self.result_txt.delete("1.0", tk.END)
        self.result_txt.insert(tk.END, text)
        self.result_txt.configure(state="disabled")

    def _redraw_all(self, path):
        for f, plot in self.plots.items():
            plot.draw_subgraph(self.G, f, path=path, draw_weights=True)

    # actions
    def _on_build(self):
        s = self._to_id(self.start_var.get().strip())
        e = self._to_id(self.end_var.get().strip())
        if not s or not e:
            messagebox.showwarning("Введення", "Оберіть початок і кінець.")
            return
        if s not in self.G.nodes or e not in self.G.nodes:
            messagebox.showerror("Помилка", "Точка відсутня в графі.")
            return
        algo = self.algo_var.get().lower()
        try:
            if algo == "astar":
                from src.pathfinding import astar_path
                path, dist = astar_path(self.G, s, e)
                name = "A*"
            else:
                from src.pathfinding import dijkstra_path
                path, dist = dijkstra_path(self.G, s, e)
                name = "Dijkstra"
        except Exception as ex:
            messagebox.showerror("Помилка пошуку", str(ex))
            return

        labels = {n: self.G.nodes[n].get("label", n) for n in path}
        chain = " → ".join(labels[n] for n in path)
        self._set_result(f"Найкоротший маршрут: {chain}\nДовжина: {dist:.2f}\nАлгоритм: {name}")
        self._redraw_all(path)

    def _on_clear(self):
        self._set_result("")
        self._redraw_all(path=None)

def main():
    app = PathfinderGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
