import pygame

pygame.init()

#Configuración de la ventana
ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Tower Defense Isaac")

#Cargar las imágenes
img_menu = pygame.image.load("Contenido/Elementos del juego/Pantalla_Inicial.png").convert()
img_mapa = pygame.image.load("Contenido/Pruebas/Layout_Prueba.png").convert()

#Escalas de las imágenes
img_menu = pygame.transform.scale(img_menu, (ANCHO, ALTO))
img_mapa = pygame.transform.scale(img_mapa, (ANCHO, ALTO))

#Definir el rectángulo invisible donde se ubica el botón "Iniciar" en tu pantalla
boton_inicio_rect = pygame.Rect(350, 480, 100, 40)

estado_juego = "menu" # Puede ser "menu" o "juego"
reloj = pygame.time.Clock()
ejecutando = True

while ejecutando:
    #Manejo de eventos, clicks
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
            
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1: #Clic izquierdo del mouse
                if estado_juego == "menu" and boton_inicio_rect.collidepoint(evento.pos):
                    estado_juego = "juego" #Cambiamos al estado del nivel

    #Dibujar en pantalla según el estado actual
    if estado_juego == "menu":
        pantalla.blit(img_menu, (0, 0))
        
    elif estado_juego == "juego":
        pantalla.blit(img_mapa, (0, 0))

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
