
import json
import os
import customtkinter as ctk
import tkinter as tk
from interfaz.visualizacion import Visualizador2D, plot_3d

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
        json.dump(
            {"dimension": "2d", "E_global": None, "A_global": 0.1},
            f, indent=4
        )

    # Siempre reiniciar elementos.json con nodos y elementos vacíos
    with open(RUTA_ELEMENTOS, "w") as f:
        json.dump(
            {"nodos": [], "elementos": []},
            f, indent=4
        )

    def _configurar_ventana(self):
        self.update_idletasks()
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

        # --- Derecha: Canvas y scrollbars ---
        # Usa CTkFrame para que el Canvas no se recorte
        der = ctk.CTkFrame(self)
        der.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        # El frame der expande su único hijo
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

        # Scrollbars
        h_scroll = tk.Scrollbar(cont, orient="horizontal", command=self.canvas.xview)
        v_scroll = tk.Scrollbar(cont, orient="vertical",   command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        h_scroll.grid(row=1, column=0, sticky="ew")
        v_scroll.grid(row=0, column=1, sticky="ns")

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
        self._escribir_consola("📦 Interfaz inicializada.")

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
        # 1. Leer valores
        try:
            coords = [float(e.get()) for e in self.nodo_entries]
            E = float(self.entrada_E.get())
            A = float(self.entrada_A.get())
        except ValueError:
            return self._escribir_consola("❌ Error: datos inválidos")

        # 2. Guardar globals y nodo en JSON (omito por brevedad)

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
        # clic fuera de nodo limpia
        self.seleccion.clear()

    def _on_node_click(self, nid):
        # Selección de nodos para conectar
        self.seleccion.append(nid)
        if len(self.seleccion) == 2:
            i, j = self.seleccion
            # Dibujar línea entre ellos
            self.visual2d.conectar(i, j)
            # Ajustar scrollregion tras la línea
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self._escribir_consola(f"✏️ Conectados nodos {i} ↔ {j}")
            self.seleccion.clear()

    def _escribir_consola(self, txt):
        self.consola.config(state="normal");
        self.consola.insert(tk.END, txt+"\n");
        self.consola.see(tk.END); self.consola.config(state="disabled")
