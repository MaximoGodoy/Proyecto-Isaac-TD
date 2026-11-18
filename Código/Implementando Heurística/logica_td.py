"""
logica_td.py  -  Lógica de Isaac TD (sin pygame, para poder probarla sola)

Contiene:
  1) El camino de Mapa1 y la generación de casillas para torres junto al camino.
  2) Las torres (Isaac) y sus 2 mejoras: daño (Cain) y rango (Judas).
  3) La heurística de Búsqueda Local "Mejor Mejora" (Best Improvement) del informe,
     con la función objetivo  f(S) = Daño - 10*DañoBase - 0.5*Estados.

Los enemigos todavía no existen, así que el "daño" es una ESTIMACIÓN: cuánto daño
haría la defensa a una oleada de referencia que recorre el camino (ver CFG_OLEADA).
"""
import math

# --------------------------------------------------------------------------- #
# 1) MAPA
# --------------------------------------------------------------------------- #
MAP_W, MAP_H = 1020, 611          # Mapa1.png escalado (proporción original 1543x924)
_ESC = MAP_W / 1000               # los puntos de abajo se midieron en una vista de 1000x599

# límites de la zona de piso donde se pueden poner torres (ya en píxeles del mapa)
LIM_X = (113, 907)
LIM_Y = (108, 504)

PASO_CAMINO = 2.0                 # separación (px) de los puntos del camino resampleado
ANCHO_CAMINO = 50                 # ancho aprox. del camino de ladrillos (px)
RADIO_CASILLA = 26                # radio de una torre / casilla (px)


def _arco(cx, cy, r, a0, a1, n=10):
    """Puntos de un arco (ángulos en grados, eje Y hacia abajo como en pantalla)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def construir_camino():
    """Línea central del camino por el que pasarán los enemigos (entrada izq -> salida der)."""
    p = [(78, 303), (456, 303)]
    p += _arco(456, 238, 65, 90, 0, 8)[1:]        # sube por la derecha del bucle
    p += [(521, 200)]
    p += _arco(439, 200, 82, 0, -180, 18)[1:]     # arco superior del bucle
    p += [(357, 385)]                             # baja cruzando el tramo horizontal
    p += _arco(402, 385, 45, 180, 90, 8)[1:]
    p += [(775, 430)]
    p += _arco(775, 380, 50, 90, 0, 8)[1:]        # curva hacia arriba (derecha)
    p += [(825, 350)]
    p += _arco(872, 350, 47, 180, 270, 8)[1:]
    p += [(925, 303)]
    return [(x * _ESC, y * _ESC) for x, y in p]


def resamplear(puntos, paso=2.0):
    """Devuelve puntos equiespaciados cada `paso` px a lo largo de la polilínea."""
    out = [puntos[0]]
    resto = paso
    for (x0, y0), (x1, y1) in zip(puntos, puntos[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        d = resto
        while d <= seg:
            t = d / seg
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
            d += paso
        resto = d - seg
    return out


def distancia_al_camino(p, pts):
    return min(math.hypot(p[0] - x, p[1] - y) for x, y in pts)


def generar_casillas(pts, cada=64, offset=62, dist_min=52, sep_min=58):
    """
    Genera las posiciones donde se pueden colocar torres: CERCA del camino pero NO sobre él.
    Recorre el camino y, cada `cada` px, prueba un punto a cada lado (a `offset` px de la
    línea central). Se descarta si cae fuera del piso, si queda a menos de `dist_min` del
    camino (pisaría el ladrillo) o si queda a menos de `sep_min` de otra casilla.
    """
    casillas = []
    salto = max(1, int(cada / PASO_CAMINO))
    for i in range(0, len(pts), salto):
        a = pts[max(0, i - 6)]
        b = pts[min(len(pts) - 1, i + 6)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        n = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / n, tx / n
        for lado in (1, -1):
            c = (pts[i][0] + lado * nx * offset, pts[i][1] + lado * ny * offset)
            if not (LIM_X[0] <= c[0] <= LIM_X[1] and LIM_Y[0] <= c[1] <= LIM_Y[1]):
                continue
            if distancia_al_camino(c, pts) < dist_min:
                continue
            if any(math.hypot(c[0] - q[0], c[1] - q[1]) < sep_min for q in casillas):
                continue
            casillas.append((round(c[0]), round(c[1])))
    return casillas


# Casillas elegidas para Mapa1 (son las nº 1, 4, 7, 16 y 23 de las que genera
# generar_casillas; se dejan fijas para que no cambien si se ajusta el generador).
CASILLAS_MAPA1 = [(144, 247), (272, 371), (461, 247), (575, 501), (767, 377)]


# --------------------------------------------------------------------------- #
# 2) TORRES Y MEJORAS
# --------------------------------------------------------------------------- #
COSTO_ISAAC = 250
MAX_NIVEL_MEJORA = 3              # máximo de veces que se puede mejorar cada rama

TORRE_BASE = {"nombre": "Isaac", "daño": 6.0, "cadencia": 1.5, "rango": 110.0}

# Las 2 formas de mejorar (coinciden con las cartas Cain y Judas del layout)
MEJORAS = {
    "daño":  {"personaje": "Cain",  "costo": 300, "delta": 3.0},    # +3 de daño por disparo
    "rango": {"personaje": "Judas", "costo": 200, "delta": 35.0},   # +35 px de alcance
}


class Torre:
    def __init__(self, pos, nombre="Isaac"):
        self.pos = pos
        self.nombre = nombre
        self.nivel = {"daño": 0, "rango": 0}
        self.ultima = None            # última rama mejorada (para elegir el sprite)

    @property
    def daño(self):
        return TORRE_BASE["daño"] + self.nivel["daño"] * MEJORAS["daño"]["delta"]

    @property
    def rango(self):
        return TORRE_BASE["rango"] + self.nivel["rango"] * MEJORAS["rango"]["delta"]

    @property
    def cadencia(self):
        return TORRE_BASE["cadencia"]

    @property
    def dps(self):
        return self.daño * self.cadencia

    def puede_mejorar(self, tipo):
        return self.nivel[tipo] < MAX_NIVEL_MEJORA

    def mejorar(self, tipo):
        self.nivel[tipo] += 1
        self.ultima = tipo

    def stats(self):
        """Copia liviana (pos, daño, cadencia, rango) para simular sin tocar la torre real."""
        return (self.pos, self.daño, self.cadencia, self.rango)


# --------------------------------------------------------------------------- #
# 3) HEURÍSTICA: BÚSQUEDA LOCAL - MEJOR MEJORA
# --------------------------------------------------------------------------- #
# Oleada de referencia (placeholder hasta que existan los enemigos). Mismos valores
# del ejemplo del informe: 5 enemigos de 100 HP.
CFG_OLEADA = {
    "n_enemigos": 5,
    "hp": 100,
    "velocidad": 80.0,            # px/s con que recorren el camino
    "factor_fuga": 0.10,          # 10% del HP no mitigado se convierte en daño a la base
}
PESO_DAÑO_BASE = 10.0             # f(S) = Daño - 10*DañoBase - 0.5*Estados
PESO_ESTADOS = 0.5


def largo_cubierto(pos, rango, pts):
    """Largo de camino (px) que queda dentro del círculo de ataque de la torre."""
    r2 = rango * rango
    n = sum(1 for x, y in pts if (x - pos[0]) ** 2 + (y - pos[1]) ** 2 <= r2)
    return n * PASO_CAMINO


def daño_proyectado(stats, pts):
    """Daño estimado de UNA torre sobre toda la oleada de referencia."""
    pos, daño, cadencia, rango = stats
    tiempo_en_rango = largo_cubierto(pos, rango, pts) / CFG_OLEADA["velocidad"]
    return daño * cadencia * tiempo_en_rango * CFG_OLEADA["n_enemigos"]


def evaluar_defensa(lista_stats, pts, estados=0):
    """
    Función objetivo del informe:  f(S) = DañoGenerado - 10*DañoRecibidoEnBase - 0.5*Estados
    DañoRecibidoEnBase = 10% del HP de la oleada que la defensa no alcanza a mitigar.
    """
    total = sum(daño_proyectado(s, pts) for s in lista_stats)
    hp_total = CFG_OLEADA["n_enemigos"] * CFG_OLEADA["hp"]
    no_mitigado = max(0.0, hp_total - total)
    daño_base = no_mitigado * CFG_OLEADA["factor_fuga"]
    f = total - PESO_DAÑO_BASE * daño_base - PESO_ESTADOS * estados
    return {"daño": total, "daño_base": daño_base, "f": f}


def mejor_mejora_torre(torres, indice, dinero, pts):
    """
    MEJOR MEJORA sobre la torre `torres[indice]`: simula las 2 mejoras posibles (daño y rango),
    las compara con f(S) y devuelve cuál conviene. NO aplica nada: el jugador decide.

    Respeta las restricciones obligatorias: presupuesto (costo <= dinero) y nivel máximo.
    Condición de término: si ninguna opción supera la defensa actual, no recomienda ninguna.
    """
    torre = torres[indice]
    actual = evaluar_defensa([t.stats() for t in torres], pts)
    resultados, estados = {}, 0

    for tipo, m in MEJORAS.items():
        if not torre.puede_mejorar(tipo):
            resultados[tipo] = {"disponible": False, "factible": False}
            continue
        estados += 1                                   # Nodos/Estados evaluados
        pos, d, c, r = torre.stats()
        if tipo == "daño":
            d += m["delta"]
        else:
            r += m["delta"]
        stats = [t.stats() for i, t in enumerate(torres) if i != indice] + [(pos, d, c, r)]
        ev = evaluar_defensa(stats, pts)
        resultados[tipo] = {"disponible": True, "factible": m["costo"] <= dinero,
                            "costo": m["costo"], "daño": ev["daño"], "f": ev["f"],
                            "ganancia": ev["daño"] - actual["daño"]}

    # el término de estados penaliza igual a todas las opciones de esta búsqueda
    for r in resultados.values():
        if r["disponible"]:
            r["f"] -= PESO_ESTADOS * estados

    candidatas = [(t, r) for t, r in resultados.items() if r["disponible"] and r["factible"]]
    mejor = None
    if candidatas:
        t, r = max(candidatas, key=lambda x: (x[1]["f"], -x[1]["costo"]))
        if r["f"] > actual["f"]:
            mejor = t
    return {"mejor": mejor, "opciones": resultados, "actual": actual, "estados": estados}


def mejor_posicion(torres, casillas, dinero, pts):
    """
    MEJOR MEJORA para colocar una torre nueva: prueba Isaac en cada casilla libre y devuelve
    la que maximiza f(S). Devuelve (indice_casilla, f, estados) o (None, None, estados).
    """
    ocupadas = {t.pos for t in torres}
    stats_actuales = [t.stats() for t in torres]
    mejor_i, mejor_f, estados = None, None, 0
    if dinero < COSTO_ISAAC:
        return None, None, 0
    for i, c in enumerate(casillas):
        if c in ocupadas:
            continue
        estados += 1
        nueva = (c, TORRE_BASE["daño"], TORRE_BASE["cadencia"], TORRE_BASE["rango"])
        f = evaluar_defensa(stats_actuales + [nueva], pts, estados=0)["f"]
        if mejor_f is None or f > mejor_f:
            mejor_i, mejor_f = i, f
    if mejor_f is not None:
        mejor_f -= PESO_ESTADOS * estados
    return mejor_i, mejor_f, estados
