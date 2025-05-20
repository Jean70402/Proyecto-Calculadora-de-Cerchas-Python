class Visualizador2D:
    def __init__(self, canvas, scale=50, offset=(50, 50)):
        self.canvas = canvas
        self.scale = scale
        self.offset = offset
        self.nodos = {}         # { id: (x_m, y_m) }
        self._ovales = {}       # { id: oval_id }
        self.blinking_nodo = None  # id del nodo que está parpadeando (o None)

    def config_canvas(self, x_m, y_m):
        px = self.offset[0] + x_m * self.scale
        py = self.offset[1] + (-y_m) * self.scale + self.canvas.winfo_height() / 2
        return px, py

    def agregar_nodo(self, nid, coord):
        """Dibuja un nodo (círculo + etiqueta) y lo registra."""
        x_m, y_m = coord
        px, py = self.config_canvas(x_m, y_m)
        r = 6
        oval = self.canvas.create_oval(px - r, py - r, px + r, py + r,
                                       fill="blue", tags=(f"n{nid}",))
        self.canvas.create_text(px, py - 12, text=str(nid), tags=(f"n{nid}",))
        self.nodos[nid] = coord
        self._ovales[nid] = oval

    def conectar(self, id1, id2, color="red", width=2):
        """Dibuja línea entre nodos ya registrados, pero no permite id1 == id2."""
        if id1 == id2:
            return
        c1 = self.nodos[id1]
        c2 = self.nodos[id2]
        x1, y1 = self.config_canvas(*c1)
        x2, y2 = self.config_canvas(*c2)
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

    def _blink_loop(self, nid):
        """Bucle que alterna color mientras self.blinking_nodo == nid."""
        oval_id = self._ovales.get(nid)
        if oval_id is None or self.blinking_nodo != nid:
            # Si ya no debe parpadear, aseguro que quede azul
            if oval_id is not None:
                self.canvas.itemconfig(oval_id, fill="blue")
            return

        # alterno color
        color_actual = self.canvas.itemcget(oval_id, "fill")
        nuevo = "yellow" if color_actual == "blue" else "blue"
        self.canvas.itemconfig(oval_id, fill=nuevo)
        # vuelvo a llamar en 300 ms mientras siga siendo el nodo activo
        self.canvas.after(300, lambda: self._blink_loop(nid))

    def parpadear_nodo(self, nid):
        """Inicia el parpadeo indefinido de `nid`. Detiene el anterior si lo hay."""
        # 1) Si hay otro parpadeando, lo detengo y lo pongo azul
        if self.blinking_nodo is not None and self.blinking_nodo != nid:
            prev_oval = self._ovales.get(self.blinking_nodo)
            if prev_oval:
                self.canvas.itemconfig(prev_oval, fill="blue")

        # 2) Marco este nodo como el que parpadea
        self.blinking_nodo = nid
        # 3) Arranco el bucle de parpadeo
        self._blink_loop(nid)

    def stop_parpadeo(self):
        """Detiene cualquier parpadeo en curso (se invoca al hacer clic fuera o al reiniciar selección)."""
        if self.blinking_nodo is not None:
            oval_id = self._ovales.get(self.blinking_nodo)
            if oval_id:
                self.canvas.itemconfig(oval_id, fill="blue")
        self.blinking_nodo = None
