# visualizacion.py
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D  # para proyección 3D


class Visualizador2D:
    def __init__(self, canvas, scale=50, offset=(50, 50)):
        self.canvas = canvas
        self.scale = scale
        self.offset = offset
        self.nodos = {}  # { id: (x_m,y_m) }

    def _met2px(self, x_m, y_m):
        px = self.offset[0] + x_m * self.scale
        py = self.offset[1] + (-y_m) * self.scale + self.canvas.winfo_height() / 2
        return px, py

    def agregar_nodo(self, nid, coord):
        """Dibuja un nodo (círculo + etiqueta) y lo registra."""
        x_m, y_m = coord
        px, py = self._met2px(x_m, y_m)
        r = 6
        oval = self.canvas.create_oval(px - r, py - r, px + r, py + r, fill="blue", tags=(f"n{nid}",))
        text = self.canvas.create_text(px, py - 12, text=str(nid), tags=(f"n{nid}",))
        self.nodos[nid] = coord

    def conectar(self, id1, id2, color="red", width=2):
        """Dibuja línea entre nodos ya registrados."""
        c1 = self.nodos[id1];
        c2 = self.nodos[id2]
        x1, y1 = self._met2px(*c1);
        x2, y2 = self._met2px(*c2)
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)


def plot_3d(nodes, elementos):
    """
    Abre una ventana Matplotlib 3D con los nodos y líneas de los elementos.
    - nodes: lista de dicts {'id','coord':[x,y,z],...}
    - elementos: lista de tuplas (id1,id2)
    """
    ventana = tk.Toplevel()
    ventana.title("Visualización 3D")
    fig = Figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection='3d')

    # Extraer coords
    xs = [n['coord'][0] for n in nodes]
    ys = [n['coord'][1] for n in nodes]
    zs = [n['coord'][2] for n in nodes]
    ax.scatter(xs, ys, zs, c='b')

    # Etiquetas
    for n in nodes:
        x, y, z = n['coord']
        ax.text(x, y, z, str(n['id']))

    # Dibujar elementos
    for (i, j) in elementos:
        c1 = next(n['coord'] for n in nodes if n['id'] == i)
        c2 = next(n['coord'] for n in nodes if n['id'] == j)
        ax.plot([c1[0], c2[0]], [c1[1], c2[1]], [c1[2], c2[2]], c='r')

    canvas = FigureCanvasTkAgg(fig, master=ventana)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
