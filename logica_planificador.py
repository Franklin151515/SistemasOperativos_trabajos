class Proceso:
    def __init__(self, nombre, tll, te_ejec):
        self.nombre = nombre
        self.tll = tll
        self.te_ejec = te_ejec
        self.tiempo_restante = te_ejec
        self.t_inicio = -1
        self.t_final = -1
        self.tr = 0
        self.tw = 0

    def calcular_metricas(self):
        # Fórmulas TR = TF - TLL,     TW = TI - TLL
        self.tr = self.t_final - self.tll
        self.tw = self.t_inicio - self.tll

def leer_archivo(ruta):
    procesos = []
    try:
        with open(ruta, 'r') as f:
            for linea in f:
                fila = linea.split()
                if not fila or len(fila) < 3: continue
                nombre = fila[0].strip()
                tll = int(fila[1].strip())
                te = int(fila[2].strip())
                procesos.append(Proceso(nombre, tll, te))
        return procesos
    except Exception:
        return None

def obtener_siguiente_proceso(cola_listos, politica):
    if not cola_listos: return None
    if politica == "FCFS":
        return cola_listos.pop(0)
    elif politica == "SPN":
        # Selección por el tiempo de ejecución más corto (Shortest Process Next)
        proceso_mas_corto = min(cola_listos, key=lambda p: p.te_ejec)
        cola_listos.remove(proceso_mas_corto)
        return proceso_mas_corto