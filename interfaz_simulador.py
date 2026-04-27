import tkinter as tk
from tkinter import ttk, filedialog
import copy
from logica_planificador import leer_archivo, obtener_siguiente_proceso

class AppSimulador:
    def __init__(self, root):
        self.root = root
        self.root.title("TRABAJO: Franklin Alfred Chura Yupa - Planificador CPU")
        self.root.geometry("1200x800")
        
        self.procesos_originales = []
        self.procesos_entrada = []
        self.cola_listos = []
        self.proceso_en_cpu = None
        self.tiempo_actual = 0
        self.simulando = False
        self.politica = tk.StringVar(value="FCFS")
        self.colores = {}
        self.nombres_ordenados = []

        self.setup_ui()

    def setup_ui(self):
        frame_header = tk.Frame(self.root, bg="#2c3e50", pady=5)
        frame_header.pack(fill=tk.X)
        tk.Label(frame_header, text="TRABAJO: Franklin Alfred Chura Yupa", fg="white", bg="#2c3e50", font=("Arial", 12, "bold")).pack()

        frame_top = tk.Frame(self.root, pady=10)
        frame_top.pack(fill=tk.X)
        tk.Button(frame_top, text="Cargar Archivo", command=self.cargar).pack(side=tk.LEFT, padx=10)
        tk.Label(frame_top, text="Algoritmo:").pack(side=tk.LEFT, padx=5)
        ttk.Combobox(frame_top, textvariable=self.politica, values=["FCFS", "SPN"], state="readonly", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_top, text="EJECUTAR", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), command=self.iniciar).pack(side=tk.LEFT, padx=10)
        self.lbl_reloj = tk.Label(frame_top, text="Tiempo: 0", font=("Arial", 12, "bold"))
        self.lbl_reloj.pack(side=tk.RIGHT, padx=20)

        self.canvas = tk.Canvas(self.root, bg="white", height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10)

        self.frame_tabla = tk.Frame(self.root, pady=10)
        self.frame_tabla.pack(fill=tk.X, padx=20)

        columnas = ("P", "TLL", "TEJ", "TR", "TW", "TI", "TF")
        self.tabla = ttk.Treeview(self.frame_tabla, columns=columnas, show="headings", height=6)
        headers = ["Proceso", "TLL", "T. ejecucion", "T. Respuesta", "T. Espera", "T Inicio", "T. Final"]
        for col, txt in zip(columnas, headers):
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=110, anchor="center")
        self.tabla.pack(fill=tk.X)

        self.frame_prom = tk.Frame(self.frame_tabla)
        self.frame_prom.pack(fill=tk.X)
        tk.Label(self.frame_prom, text="Promedios", font=("Arial", 10, "bold"), width=42, anchor="e").pack(side=tk.LEFT)
        self.lbl_prom_tr = tk.Label(self.frame_prom, text="0.0", font=("Arial", 10, "bold"), bg="#ffff00", width=15)
        self.lbl_prom_tr.pack(side=tk.LEFT, padx=5)
        self.lbl_prom_tw = tk.Label(self.frame_prom, text="0.0", font=("Arial", 10, "bold"), bg="#ffff00", width=15)
        self.lbl_prom_tw.pack(side=tk.LEFT)

    def cargar(self):
        ruta = filedialog.askopenfilename()
        if ruta:
            self.procesos_originales = leer_archivo(ruta)
            if self.procesos_originales:
                self.nombres_ordenados = sorted([p.nombre for p in self.procesos_originales])
                cols = ["#e67e22", "#3498db", "#2ecc71", "#9b59b6", "#f1c40f"]
                self.colores = {n: cols[i % len(cols)] for i, n in enumerate(self.nombres_ordenados)}
                self.root.title(f"Simulador - {len(self.procesos_originales)} procesos listos")

    def iniciar(self):
        if not self.procesos_originales: return
        
        self.procesos_entrada = [copy.copy(p) for p in self.procesos_originales]
        self.canvas.delete("all")
        self.tabla.delete(*self.tabla.get_children())
        self.tiempo_actual = 0
        self.cola_listos = []
        self.proceso_en_cpu = None
        self.simulando = True
        self.ejecutar_tick()

    def ejecutar_tick(self):
        if not self.simulando: return

        for p in self.procesos_entrada[:]:
            if p.tll == self.tiempo_actual:
                self.cola_listos.append(p)
                self.procesos_entrada.remove(p)

        if self.proceso_en_cpu is None:
            self.proceso_en_cpu = obtener_siguiente_proceso(self.cola_listos, self.politica.get())
            if self.proceso_en_cpu and self.proceso_en_cpu.t_inicio == -1:
                self.proceso_en_cpu.t_inicio = self.tiempo_actual

        ancho, alto = 35, 35
        mx, my = 60, 40
        x = self.tiempo_actual * ancho + mx

        if self.tiempo_actual == 0:
            for i, n in enumerate(self.nombres_ordenados):
                self.canvas.create_text(30, i*alto + my + 17, text=n, font=("Arial", 10, "bold"))

        if self.proceso_en_cpu:
            idx = self.nombres_ordenados.index(self.proceso_en_cpu.nombre)
            y = idx * alto + my
            self.canvas.create_rectangle(x, y, x + ancho, y + alto, fill=self.colores[self.proceso_en_cpu.nombre], outline="white")
            self.proceso_en_cpu.tiempo_restante -= 1
            termina = (self.proceso_en_cpu.tiempo_restante == 0)
        else:
            termina = False

        # Dibujo de Cola Vertical
        cola_vis = []
        if self.proceso_en_cpu: cola_vis.append(self.proceso_en_cpu.nombre)
        cola_vis.extend([p.nombre for p in self.cola_listos])

        y_t = len(self.nombres_ordenados) * alto + my + 25
        self.canvas.create_text(x + 17, y_t, text=str(self.tiempo_actual), font=("Arial", 9, "bold"))
        for i, p_n in enumerate(cola_vis):
            self.canvas.create_text(x + 17, y_t + 25 + (i*18), text=p_n, font=("Arial", 9))
        self.canvas.create_line(x, my, x, y_t + 100, fill="#f5f5f5")

        if termina:
            self.proceso_en_cpu.t_final = self.tiempo_actual + 1
            self.proceso_en_cpu.calcular_metricas()
            p = self.proceso_en_cpu
            self.tabla.insert("", tk.END, values=(p.nombre, p.tll, p.te_ejec, p.tr, p.tw, p.t_inicio, p.t_final))
            self.actualizar_promedios()
            self.proceso_en_cpu = None

        self.tiempo_actual += 1
        self.lbl_reloj.config(text=f"Tiempo: {self.tiempo_actual}")
        
        if not self.procesos_entrada and not self.cola_listos and self.proceso_en_cpu is None:
            self.simulando = False
        else:
            self.root.after(200, self.ejecutar_tick)

    def actualizar_promedios(self):
        items = self.tabla.get_children()
        if not items: return
        n = len(items)
        tr = sum(float(self.tabla.item(i)['values'][3]) for i in items) / n
        tw = sum(float(self.tabla.item(i)['values'][4]) for i in items) / n
        self.lbl_prom_tr.config(text=f"{round(tr, 2)}")
        self.lbl_prom_tw.config(text=f"{round(tw, 2)}")

if __name__ == "__main__":
    root = tk.Tk()
    AppSimulador(root)
    root.mainloop()