"""
juego_td.py  -  Isaac TD (versión con torres)

Qué hace esta versión:
  * Pantalla de inicio (la de siempre) y luego el Mapa1 con el panel "Torres Aliadas".
  * Se compra a Isaac ($250) en el panel y se coloca en una de las casillas junto al camino.
  * Al hacer clic en una torre colocada aparecen las 2 mejoras a elección:
        Cain  -> mejora de DAÑO  ($300)      Judas -> mejora de RANGO ($200)
  * La heurística de Búsqueda Local "Mejor Mejora" (logica_td.py) evalúa ambas opciones con
    f(S) y marca cuál conviene (el jugador igual elige). Al colocar una torre también sugiere
    la mejor casilla.

Controles:
  Clic izq.  : comprar / colocar / seleccionar / mejorar
  Esc o clic derecho : cancelar compra o deseleccionar
  M          : +100 monedas (solo para pruebas, aún no hay enemigos que den dinero)

Ejecutar:  python juego_td.py   (necesita:  pip install pygame)
Los archivos de imagen se buscan en la carpeta "Contenido" del proyecto, esté donde esté este .py.
"""
import os
import pygame

from logica_td import (MAP_W, MAP_H, RADIO_CASILLA, PASO_CAMINO, COSTO_ISAAC, MAX_NIVEL_MEJORA,
                       MEJORAS, TORRE_BASE, CASILLAS_MAPA1, Torre, construir_camino, resamplear,
                       mejor_mejora_torre, mejor_posicion)

# --------------------------------------------------------------------------- #
# Configuración
# --------------------------------------------------------------------------- #
PANEL_W = 180
ANCHO, ALTO = MAP_W + PANEL_W, MAP_H            # 1200 x 611
DINERO_INICIAL = 650
VIDA_INICIAL = 100
TAM_SPRITE = 56                                  # caja donde se dibuja cada torre (px)

# Rectángulos del panel derecho
R_ISAAC = pygame.Rect(MAP_W + 28, 62, 124, 126)
R_CAIN = pygame.Rect(MAP_W + 10, 196, 160, 137)      # carta mejora de daño
R_JUDAS = pygame.Rect(MAP_W + 10, 341, 160, 137)     # carta mejora de rango
R_INFO = pygame.Rect(MAP_W + 8, 506, 164, 99)

BLANCO, NEGRO = (255, 255, 255), (0, 0, 0)
DORADO, VERDE, ROJO = (255, 215, 60), (120, 230, 120), (235, 80, 80)
MARRON_OSC = (70, 40, 20)


def raiz_proyecto():
    """Sube carpetas hasta encontrar 'Contenido' (así funciona desde Código/ o Código/Pruebas_Codigo/)."""
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(4):
        if os.path.isdir(os.path.join(d, "Contenido")):
            return d
        d = os.path.dirname(d)
    return os.getcwd()


RAIZ = raiz_proyecto()


def ruta(*partes):
    return os.path.join(RAIZ, "Contenido", *partes)


def cargar(*partes, alpha=True):
    img = pygame.image.load(ruta(*partes))
    return img.convert_alpha() if alpha else img.convert()


def encajar(img, caja):
    """Escala `img` para que quepa en caja x caja manteniendo la proporción."""
    w, h = img.get_size()
    k = caja / max(w, h)
    return pygame.transform.smoothscale(img, (max(1, int(w * k)), max(1, int(h * k))))


def circulo_alpha(dest, color, centro, radio, ancho=0):
    """Círculo semitransparente (color = RGBA)."""
    s = pygame.Surface((radio * 2 + 4, radio * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(s, color, (radio + 2, radio + 2), radio, ancho)
    dest.blit(s, (centro[0] - radio - 2, centro[1] - radio - 2))


def velo(dest, rect, alpha):
    s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    dest.blit(s, (rect.x, rect.y))


def texto(dest, s, fuente, color, pos, centrado=False, sombra=True):
    if sombra:
        sup = fuente.render(s, True, NEGRO)
        x, y = pos
        if centrado:
            x -= sup.get_width() // 2
        dest.blit(sup, (x + 1, y + 1))
    sup = fuente.render(s, True, color)
    x, y = pos
    if centrado:
        x -= sup.get_width() // 2
    dest.blit(sup, (x, y))


# --------------------------------------------------------------------------- #
# Juego
# --------------------------------------------------------------------------- #
class Juego:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Tower Defense Isaac")
        self.reloj = pygame.time.Clock()

        # fuentes
        self.f_chica = pygame.font.SysFont("arial", 13, bold=True)
        self.f_media = pygame.font.SysFont("arial", 16, bold=True)
        self.f_grande = pygame.font.SysFont("arial", 24, bold=True)

        # imágenes
        self.img_menu = pygame.transform.smoothscale(
            cargar("Elementos del juego", "Pantalla_Inicial.png", alpha=False), (ANCHO, ALTO))
        self.img_mapa = pygame.transform.smoothscale(
            cargar("Mapas", "Mapa1.png", alpha=False), (MAP_W, MAP_H))
        self.img_panel = pygame.transform.smoothscale(
            cargar("Elementos del juego", "Layout_Torres.png"), (PANEL_W, ALTO))
        self.img_recuadro = pygame.transform.smoothscale(
            cargar("Elementos del juego", "Recuadro_De_Torre.png"), (R_ISAAC.w, R_ISAAC.h))
        self.img_carta = {
            "daño": pygame.transform.smoothscale(
                cargar("Elementos del juego", "Mejora(Daño).png"), (R_CAIN.w, R_CAIN.h)),
            "rango": pygame.transform.smoothscale(
                cargar("Elementos del juego", "Mejora(Rango).png"), (R_JUDAS.w, R_JUDAS.h)),
        }
        self.ico_dinero = encajar(cargar("Elementos del juego", "Dinero.png"), 36)
        self.ico_vida = encajar(cargar("Elementos del juego", "Vida_Jugador.png"), 32)

        isaac = cargar("Personajes", "Torres aliadas", "TorreInicial_Isaac.png")
        self.sprites = {
            None: encajar(isaac, TAM_SPRITE),
            "daño": encajar(cargar("Elementos del juego", "Cain_Daño+.png"), TAM_SPRITE),
            "rango": encajar(cargar("Elementos del juego", "Judas_Rango+.png"), TAM_SPRITE),
        }
        self.sprite_carta_isaac = encajar(isaac, 66)

        # camino y casillas (se generan una sola vez a partir del Mapa1)
        self.pts = resamplear(construir_camino(), PASO_CAMINO)
        self.casillas = list(CASILLAS_MAPA1)

        # botón "Inicio" de la pantalla inicial (posición relativa a la imagen)
        self.r_inicio = pygame.Rect(int(ANCHO * 0.388), int(ALTO * 0.814),
                                    int(ANCHO * 0.224), int(ALTO * 0.108))

        # estado
        self.estado = "menu"                      # "menu" o "juego"
        self.dinero = DINERO_INICIAL
        self.vida = VIDA_INICIAL
        self.torres = []
        self.colocando = False                    # ¿está eligiendo casilla para comprar?
        self.sel = None                           # índice de la torre seleccionada
        self.rec = None                           # resultado de Mejor Mejora (mejora)
        self.sug = None                           # resultado de Mejor Mejora (casilla)
        self.mensaje, self.mensaje_hasta = "", 0

    # ------------------------------ utilidades ------------------------------ #
    def aviso(self, s, ms=2200):
        self.mensaje = s
        self.mensaje_hasta = pygame.time.get_ticks() + ms

    def recalcular(self):
        """Corre la heurística Mejor Mejora cuando cambia algo (no cada frame)."""
        self.sug = None
        self.rec = None
        if self.colocando:
            self.sug = mejor_posicion(self.torres, self.casillas, self.dinero, self.pts)
        if self.sel is not None:
            self.rec = mejor_mejora_torre(self.torres, self.sel, self.dinero, self.pts)

    def casilla_libre_en(self, pos):
        ocupadas = {t.pos for t in self.torres}
        mejor, md = None, RADIO_CASILLA + 4
        for c in self.casillas:
            if c in ocupadas:
                continue
            d = ((c[0] - pos[0]) ** 2 + (c[1] - pos[1]) ** 2) ** 0.5
            if d <= md:
                mejor, md = c, d
        return mejor

    def torre_en(self, pos):
        for i, t in enumerate(self.torres):
            if ((t.pos[0] - pos[0]) ** 2 + (t.pos[1] - pos[1]) ** 2) ** 0.5 <= RADIO_CASILLA:
                return i
        return None

    # ------------------------------- acciones ------------------------------- #
    def alternar_compra(self):
        if self.colocando:
            self.cancelar()
            return
        if self.dinero < COSTO_ISAAC:
            self.aviso("Dinero insuficiente (Isaac cuesta $%d)" % COSTO_ISAAC)
            return
        if len(self.torres) >= len(self.casillas):
            self.aviso("No quedan casillas libres")
            return
        self.colocando = True
        self.sel = None
        self.recalcular()

    def colocar(self, pos):
        c = self.casilla_libre_en(pos)
        if c is None:
            self.aviso("Coloca la torre en una casilla marcada")
            return
        if self.dinero < COSTO_ISAAC:               # restricción obligatoria: presupuesto
            self.aviso("Dinero insuficiente")
            self.cancelar()
            return
        self.dinero -= COSTO_ISAAC
        self.torres.append(Torre(c))
        self.colocando = False
        self.sel = len(self.torres) - 1             # queda seleccionada para ver sus mejoras
        self.recalcular()

    def mejorar(self, tipo):
        if self.sel is None:
            return
        t = self.torres[self.sel]
        m = MEJORAS[tipo]
        if not t.puede_mejorar(tipo):
            self.aviso("Esa mejora ya está al máximo")
        elif self.dinero < m["costo"]:
            self.aviso("Dinero insuficiente (cuesta $%d)" % m["costo"])
        else:
            self.dinero -= m["costo"]
            t.mejorar(tipo)
        self.recalcular()

    def cancelar(self):
        self.colocando = False
        self.sel = None
        self.recalcular()

    # -------------------------------- eventos ------------------------------- #
    def clic(self, pos, boton):
        if self.estado == "menu":
            if boton == 1 and self.r_inicio.collidepoint(pos):
                self.estado = "juego"
            return
        if boton == 3:
            self.cancelar()
            return
        if boton != 1:
            return
        if R_ISAAC.collidepoint(pos):
            self.alternar_compra()
            return
        if self.sel is not None:
            if R_CAIN.collidepoint(pos):
                self.mejorar("daño")
                return
            if R_JUDAS.collidepoint(pos):
                self.mejorar("rango")
                return
        if pos[0] < MAP_W:
            if self.colocando:
                self.colocar(pos)
            else:
                self.sel = self.torre_en(pos)
                self.recalcular()

    def tecla(self, k):
        if self.estado != "juego":
            return
        if k == pygame.K_ESCAPE:
            self.cancelar()
        elif k == pygame.K_m:                       # solo pruebas
            self.dinero += 100
            self.recalcular()

    # -------------------------------- dibujo -------------------------------- #
    def sprite_de(self, torre):
        if torre.ultima is None:
            return self.sprites[None]
        d, r = torre.nivel["daño"], torre.nivel["rango"]
        rama = "daño" if d > r else "rango" if r > d else torre.ultima
        return self.sprites[rama]

    def dibujar_casillas(self, mouse):
        ocupadas = {t.pos for t in self.torres}
        sug = None
        if self.colocando and self.sug and self.sug[0] is not None:
            sug = self.casillas[self.sug[0]]
        for c in self.casillas:
            if c in ocupadas:
                continue
            if not self.colocando:
                circulo_alpha(self.pantalla, (255, 255, 255, 55), c, RADIO_CASILLA - 4, 2)
                continue
            hover = ((c[0] - mouse[0]) ** 2 + (c[1] - mouse[1]) ** 2) ** 0.5 <= RADIO_CASILLA + 4
            circulo_alpha(self.pantalla, (255, 255, 255, 70 if hover else 35), c, RADIO_CASILLA - 2)
            circulo_alpha(self.pantalla, (255, 255, 255, 230), c, RADIO_CASILLA - 2, 2)
            if c == sug:
                circulo_alpha(self.pantalla, DORADO + (255,), c, RADIO_CASILLA, 4)
                texto(self.pantalla, "*", self.f_grande, DORADO, (c[0], c[1] - 14), centrado=True)

    def dibujar_torres(self):
        for i, t in enumerate(self.torres):
            if i == self.sel:
                circulo_alpha(self.pantalla, (255, 255, 255, 40), t.pos, int(t.rango))
                circulo_alpha(self.pantalla, (255, 255, 255, 200), t.pos, int(t.rango), 2)
                circulo_alpha(self.pantalla, DORADO + (255,), t.pos, RADIO_CASILLA, 3)
        for t in self.torres:
            sp = self.sprite_de(t)
            self.pantalla.blit(sp, (t.pos[0] - sp.get_width() // 2, t.pos[1] - sp.get_height() // 2))
            if t.ultima is not None:
                texto(self.pantalla, "D%d R%d" % (t.nivel["daño"], t.nivel["rango"]),
                      self.f_chica, BLANCO, (t.pos[0], t.pos[1] + 24), centrado=True)

    def dibujar_hud(self):
        p = self.pantalla
        p.blit(self.ico_dinero, (640, 14))
        texto(p, "$%d" % self.dinero, self.f_grande, BLANCO, (682, 18))
        p.blit(self.ico_vida, (775, 16))
        texto(p, "%d" % self.vida, self.f_grande, ROJO, (813, 18))
        texto(p, "M: +100 monedas (prueba)   Esc: cancelar", self.f_chica, (225, 190, 150),
              (14, MAP_H - 24))

    def dibujar_panel(self):
        p = self.pantalla
        p.blit(self.img_panel, (MAP_W, 0))
        # texto sobre la nota del panel
        texto(p, "Torres", self.f_chica, (60, 60, 75), (MAP_W + 88, 20), centrado=True, sombra=False)
        texto(p, "Aliadas", self.f_chica, (60, 60, 75), (MAP_W + 88, 36), centrado=True, sombra=False)

        # carta de compra de Isaac
        p.blit(self.img_recuadro, R_ISAAC.topleft)
        p.blit(self.sprite_carta_isaac, (R_ISAAC.centerx - self.sprite_carta_isaac.get_width() // 2,
                                         R_ISAAC.y + 8))
        texto(p, "Isaac", self.f_media, BLANCO, (R_ISAAC.x + 12, R_ISAAC.y + 94))
        texto(p, "$%d" % COSTO_ISAAC, self.f_media, DORADO, (R_ISAAC.right - 14 - 40, R_ISAAC.y + 94))
        if self.dinero < COSTO_ISAAC:
            velo(p, R_ISAAC, 120)
        if self.colocando:
            pygame.draw.rect(p, DORADO, (R_ISAAC.x, R_ISAAC.y, R_ISAAC.w, R_ISAAC.h), 4)

        # cartas de mejora (solo con una torre seleccionada)
        if self.sel is not None:
            t = self.torres[self.sel]
            for tipo, r in (("daño", R_CAIN), ("rango", R_JUDAS)):
                p.blit(self.img_carta[tipo], r.topleft)
                nv = t.nivel[tipo]
                texto(p, "Nv %d/%d" % (nv, MAX_NIVEL_MEJORA), self.f_chica, MARRON_OSC,
                      (r.x + 16, r.y + 16), sombra=False)
                op = self.rec["opciones"][tipo] if self.rec else None
                if nv >= MAX_NIVEL_MEJORA:
                    velo(p, r, 140)
                    texto(p, "MAX", self.f_grande, BLANCO, r.center, centrado=True)
                elif self.dinero < MEJORAS[tipo]["costo"]:
                    velo(p, r, 120)
                if self.rec and self.rec["mejor"] == tipo:
                    pygame.draw.rect(p, DORADO, (r.x, r.y, r.w, r.h), 4)
                    texto(p, "MEJOR", self.f_chica, DORADO, (r.right - 52, r.y + 16))
        else:
            texto(p, "Clic en una torre", self.f_chica, BLANCO, (MAP_W + 90, 250), centrado=True)
            texto(p, "colocada para ver", self.f_chica, BLANCO, (MAP_W + 90, 268), centrado=True)
            texto(p, "sus mejoras", self.f_chica, BLANCO, (MAP_W + 90, 286), centrado=True)

        # cuadro de información (abajo)
        for i, (s, col) in enumerate(self.lineas_info()):
            texto(p, s, self.f_chica, col, (R_INFO.x + 6, R_INFO.y + 6 + i * 15), sombra=False)

    def lineas_info(self):
        oscuro, verde = MARRON_OSC, (30, 110, 30)
        if self.colocando:
            i, f, n = self.sug if self.sug else (None, None, 0)
            out = [("Elige una casilla", oscuro), ("Mejor Mejora (casilla):", oscuro)]
            if i is None:
                out.append(("  sin sugerencia", oscuro))
            else:
                out += [("  * dorada  f=%.0f" % f, verde), ("  estados: %d" % n, oscuro)]
            return out
        if self.sel is not None:
            t = self.torres[self.sel]
            out = [("%s  D%d R%d" % (t.nombre, t.nivel["daño"], t.nivel["rango"]), oscuro),
                   ("Daño %.0f  Rango %.0f" % (t.daño, t.rango), oscuro),
                   ("DPS %.1f" % t.dps, oscuro)]
            if self.rec:
                m = self.rec["mejor"]
                if m:
                    out.append(("Mejor: %s (%s)" % (MEJORAS[m]["personaje"], m), verde))
                else:
                    ops = [o for o in self.rec["opciones"].values() if o["disponible"]]
                    out.append(("Sin fondos" if ops and not any(o["factible"] for o in ops)
                                else "Sin mejora útil", oscuro))
                fd = self.rec["opciones"]["daño"].get("f")
                fr = self.rec["opciones"]["rango"].get("f")
                out.append(("f(S) D:%s R:%s" % ("-" if fd is None else "%.0f" % fd,
                                                "-" if fr is None else "%.0f" % fr), oscuro))
            return out
        return [("Torres: %d" % len(self.torres), oscuro),
                ("Compra a Isaac y", oscuro), ("ponlo junto al camino", oscuro)]

    def dibujar_fantasma(self, mouse):
        """Torre semitransparente + rango sobre la casilla bajo el mouse al comprar."""
        c = self.casilla_libre_en(mouse)
        if c is None:
            return
        circulo_alpha(self.pantalla, (255, 255, 255, 40), c, int(TORRE_BASE["rango"]))
        circulo_alpha(self.pantalla, (255, 255, 255, 200), c, int(TORRE_BASE["rango"]), 2)
        sp = self.sprites[None].copy()
        sp.set_alpha(170)
        self.pantalla.blit(sp, (c[0] - sp.get_width() // 2, c[1] - sp.get_height() // 2))

    def dibujar(self):
        p = self.pantalla
        if self.estado == "menu":
            p.blit(self.img_menu, (0, 0))
            return
        mouse = pygame.mouse.get_pos()
        p.blit(self.img_mapa, (0, 0))
        self.dibujar_casillas(mouse)
        self.dibujar_torres()
        if self.colocando and mouse[0] < MAP_W:
            self.dibujar_fantasma(mouse)
        self.dibujar_hud()
        self.dibujar_panel()
        if self.mensaje and pygame.time.get_ticks() < self.mensaje_hasta:
            w = self.f_media.size(self.mensaje)[0] + 28
            fondo = pygame.Rect(MAP_W // 2 - w // 2, 72, w, 32)
            velo(p, fondo, 190)
            texto(p, self.mensaje, self.f_media, BLANCO, (MAP_W // 2, 80), centrado=True)

    # ------------------------------- bucle ---------------------------------- #
    def ejecutar(self):
        corriendo = True
        while corriendo:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    corriendo = False
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    self.clic(e.pos, e.button)
                elif e.type == pygame.KEYDOWN:
                    self.tecla(e.key)
            self.dibujar()
            pygame.display.flip()
            self.reloj.tick(60)
        pygame.quit()


if __name__ == "__main__":
    Juego().ejecutar()
