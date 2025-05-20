
import json
import os
import customtkinter as ctk
import tkinter as tk
from interfaz.visualizacion import Visualizador2D
from tkinter import filedialog

RUTA_DATOS      = "datos/datos.json"
RUTA_ELEMENTOS  = "datos/elementos.json"

class InterfazCerchas(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Resolución de Cerchas")
        self.crear_archivos_si_no_existen()
        self._configurar_ventana()
        self._crear_componentes()

    def crear_archivos_si_no_existen(self):
        os.makedirs("datos", exist_ok=True)

    # Siempre reiniciar datos.json con estructura vacía
    with open(RUTA_DATOS, "w") as f:
        json.dump({
            "dimension": "2d",
            "E_global": None,
            "A_global": 0.1,
            "nodos": []
        }, f, indent=4)

    # Siempre reiniciar elementos.json con nodos y elementos vacíos
    with open(RUTA_ELEMENTOS, "w") as f:
        json.dump(  {"nodos": [], "elementos": []},  f, indent=4)

    def _configurar_ventana(self):
        self._state_before_windows_set_titlebar_color ='zoomed'
        self.minsize(1200, 700)

        # Forzar maximizado tras inicializar
        self.after_idle(lambda: self.wm_state("zoomed"))

        # Layout de filas/columnas
        self.grid_rowconfigure(0, weight=9)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

    def _crear_componentes(self):
        # Izquierda: ingreso de datos
        izq = ctk.CTkScrollableFrame(self, label_text="Ingreso de Datos")
        izq.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Dimensión
        self.dimension = tk.StringVar(value="2d")
        dim_f = ctk.CTkFrame(izq, fg_color="transparent")
        dim_f.pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(dim_f, text="Dimensión:").pack(side="left")
        for txt, val in [("1D","1d"),("2D","2d"),("3D","3d")]:
            ctk.CTkRadioButton(dim_f, text=txt, variable=self.dimension,
                               value=val, command=self._actualizar_campos).pack(side="left", padx=5)

        # Formulario nodos
        self.campos_frame = ctk.CTkFrame(izq)
        self.campos_frame.pack(fill="x", padx=10, pady=10)
        self.nodo_entries = []
        self.valor_E_global = tk.BooleanVar(value=False)
        self.valor_A_global = tk.BooleanVar(value=False)
        self._actualizar_campos()

        ctk.CTkButton(izq, text="Agregar Nodo", command=self._agregar_nodo).pack(pady=(0,5))
        #Botones de guardar y cargar
        ctk.CTkButton(izq, text="Guardar...", command=self._guardar_archivo).pack(pady=(5,0))
        ctk.CTkButton(izq, text="Cargar...",  command=self._cargar_archivo).pack(pady=(2,10))

# --- Derecha: Canvas y scrollbars ---
        der = ctk.CTkFrame(self)
        der.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        der.grid_rowconfigure(0, weight=1)
        der.grid_columnconfigure(0, weight=1)

        # Contenedor interno para canvas + barras
        cont = ctk.CTkFrame(der)
        cont.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        cont.grid_rowconfigure(0, weight=1)
        cont.grid_columnconfigure(0, weight=1)

        # Canvas principal
        self.canvas = tk.Canvas(cont, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Inicializar visualizador 2D y selección
        self.visual2d = Visualizador2D(self.canvas)
        self.seleccion = []
        # No bind general a canvas, cada nodo se bindea al crearlo

        # Inferior: consola
        inf = ctk.CTkFrame(self)
        inf.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.consola = tk.Text(inf, height=8, wrap="word", state="disabled",
                               bg="#1e1e1e", fg="#d4d4d4")
        self.consola.pack(expand=True, fill="both", padx=5, pady=5)
        self._escribir_consola("Interfaz inicializada.")

    def _actualizar_campos(self):
        for w in self.campos_frame.winfo_children(): w.destroy()
        dim = self.dimension.get()
        coords = ["X","Y","Z"][:{"1d":1,"2d":2,"3d":3}[dim]]

        # Coordenadas
        cf = ctk.CTkFrame(self.campos_frame)
        cf.pack(fill="x", pady=5)
        entradas = []
        for c in coords:
            sub = ctk.CTkFrame(cf, fg_color="transparent")
            sub.pack(side="left", padx=5)
            ctk.CTkLabel(sub, text=c).pack()
            e = ctk.CTkEntry(sub, width=70)
            e.pack()
            ctk.CTkLabel(sub, text="[m]").pack()
            entradas.append(e)
        # Fuerzas (Fx, Fy, Fz según dimensión)
        ff = ctk.CTkFrame(self.campos_frame)
        ff.pack(fill="x", pady=5)
        f_labels = ["Fx","Fy","Fz"][:len(coords)]
        self.force_entries = []
        for f in f_labels:
            subf = ctk.CTkFrame(ff, fg_color="transparent")
            subf.pack(side="left", padx=5)
            ctk.CTkLabel(subf, text=f).pack()
            ef = ctk.CTkEntry(subf, width=70)
            ef.insert(0, "0")             # valor inicial 0
            ef.pack()
            ctk.CTkLabel(subf, text="[Tonf]").pack()
            self.force_entries.append(ef)

        # E y A
        pf = ctk.CTkFrame(self.campos_frame)
        pf.pack(fill="x", pady=10)
        e_sub = ctk.CTkFrame(pf, fg_color="transparent")
        e_sub.pack(side="left", padx=10)
        ctk.CTkLabel(e_sub, text="E").pack()
        self.entrada_E = ctk.CTkEntry(e_sub, width=120); self.entrada_E.pack()

        valores_E = {
            "Acero (2.1e7)": 2.1e7,
            "Hormigón (2.5e6)": 2.5e6
        }
        combo_E = ctk.CTkOptionMenu(
            e_sub,
            values=list(valores_E.keys()),
            command=lambda v: self.entrada_E.delete(0,"end") or self.entrada_E.insert(0,str(valores_E[v]))
        )
        combo_E.set("Acero (2.1e7)")  # valor inicial
        combo_E.pack(pady=(5,0))
        self.entrada_E.insert(0, "21000000")

        ctk.CTkLabel(e_sub, text="[Ton/m²]").pack()
        ctk.CTkCheckBox(e_sub, text="Global", variable=self.valor_E_global).pack()
        a_sub = ctk.CTkFrame(pf, fg_color="transparent")
        a_sub.pack(side="left", padx=10)
        ctk.CTkLabel(a_sub, text="A").pack()
        self.entrada_A = ctk.CTkEntry(a_sub, width=120)
        self.entrada_A.insert(0, "0.1")
        self.entrada_A.pack()
        ctk.CTkLabel(a_sub, text="[cm²]").pack()
        ctk.CTkCheckBox(a_sub, text="Global", variable=self.valor_A_global).pack()
        ctk.CTkLabel(self.campos_frame, text="Sistema de Unidades: Tonf, m").pack(pady=5)
        self.nodo_entries = entradas

    def _agregar_nodo(self):
        #1. Leer valores…
        try:
            coords = [float(e.get()) for e in self.nodo_entries]
            E = float(self.entrada_E.get())
            A = float(self.entrada_A.get())
            forces = [float(f.get()) for f in self.force_entries]
        except ValueError:
            return self._escribir_consola("❌ Error: datos inválidos")

        # 2. Guardar globals en datos.json (si se marcan como globales)
        with open(RUTA_DATOS, "r+") as f:
            cfg = json.load(f)
            if self.valor_E_global.get(): cfg["E_global"] = E
            if self.valor_A_global.get(): cfg["A_global"] = A
            f.seek(0); f.truncate()
            json.dump(cfg, f, indent=4)

        # 2b. Guardar el nodo directamente en datos.json
        with open(RUTA_DATOS, "r+") as f:
            cfg = json.load(f)
            nodos = cfg.setdefault("nodos", [])
            nid = len(nodos) + 1

            # mapea force_entries a fx, fy, fz según dimensión
            labels = ["fx", "fy", "fz"][:len(coords)]
            fuerza = { lbl: float(ent.get()) for lbl, ent in zip(labels, self.force_entries) }

            nodo = {
                "id":     nid,
                "coords": coords,
                "E":      E if not self.valor_E_global.get() else None,
                "A":      A if not self.valor_A_global.get() else None,
                **fuerza
            }
            nodos.append(nodo)

            # vuelca de nuevo todo el JSON
            f.seek(0); f.truncate()
            json.dump(cfg, f, indent=4)


        # 3. Dibujar en 2D
        nid = len(self.visual2d.nodos) + 1
        self.visual2d.agregar_nodo(nid, coords)

        # 4. Bindear clic para este nodo
        tag = f"n{nid}"
        self.canvas.tag_bind(tag, "<Button-1>", lambda e, id=nid: self._on_node_click(id))

        # 5. Actualizar scrollregion
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # 6. Consola y limpieza de campos
        self._escribir_consola(f"✅ Nodo {nid} agregado.")
        for e in self.nodo_entries:
            e.delete(0, tk.END)

    def _on_canvas_click(self, event):
        # clic fuera de nodo: detengo parpadeo y limpio selección
        self.visual2d.stop_parpadeo()
        self.seleccion.clear()

    def _on_node_click(self, nid):
        # Empiezo parpadeo en este nodo (hasta que elijan otro)
        self.visual2d.parpadear_nodo(nid)

        # Agrego a lista de selección
        self.seleccion.append(nid)
        if len(self.seleccion) == 2:
            i, j = self.seleccion
            # conectar; si i == j, no hará nada porque conectar() lo chequea
            self.visual2d.conectar(i, j)
            # Tras el enlace, reajusto scrollregion
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            # Opcional: luego de conectar, detengo el parpadeo del segundo
            self.visual2d.stop_parpadeo()

            self._escribir_consola(f" Conectados nodos {i} ↔ {j}")
            self.seleccion.clear()


    def _escribir_consola(self, txt):
        self.consola.config(state="normal");
        self.consola.insert(tk.END, txt+"\n");
        self.consola.see(tk.END); self.consola.config(state="disabled")

    def _guardar_archivo(self):
        """Solicita ruta y copia datos.json + elementos.json allí."""
        dest = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Guardar proyecto como..."
        )
        if not dest:
            return
        # Por convención, guardamos dos archivos:
        base, _ = os.path.splitext(dest)
        for nombre in [RUTA_DATOS, RUTA_ELEMENTOS]:
            destino = f"{base}_{os.path.basename(nombre)}"
            with open(nombre, "r") as src, open(destino, "w") as dst:
                dst.write(src.read())
        self._escribir_consola(f"✅ Proyecto guardado en «{base}_*.json»")

    def _cargar_archivo(self):
        """Solicita un JSON principal, carga ambos y repuebla canvas."""
        origen = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Cargar datos de proyecto..."
        )
        if not origen:
            return
        # Inferir base para ambos
        base, _ = os.path.splitext(origen)
        # Leer configuraciones
        # Leer el archivo datos.json guardado
        with open(origen, "r") as f:
            cfg = json.load(f)
        self.dimension.set(cfg["dimension"])
        # (actualiza E_global y A_global si quieres)

        # Vacía el canvas
        self.canvas.delete("all")
        self.visual2d.clear()

        # Recrea cada nodo según cfg["nodos"]
        for nodo in cfg.get("nodos", []):
            self.visual2d.agregar_nodo(nodo["id"], nodo["coords"])
            tag = f"n{nodo['id']}"
            self.canvas.tag_bind(tag, "<Button-1>",
                                 lambda e, id=nodo["id"]: self._on_node_click(id))

            # Si tienes elementos/conexiones en cfg, repítelas aquí…

        # Rehacer conexiones
        for elm in data["elementos"]:
            self.visual2d.conectar(elm["i"], elm["j"])
        # Ajustar scroll
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._escribir_consola("✅ Proyecto cargado y canvas actualizado.")
