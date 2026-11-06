Objetivo del Proyecto:
Como proyecto 4, realizaremos el Tower Defense (nombre momentáneo) diseñando un videojuego donde el usuario debe ubicar torres defensivas en posiciones estratégicas, para así poder evitar el avance enemigo.


Objetivos principales:
Implementación de algoritmos como el voraz, búsqueda local, y diferentes heurísticas.
Compararemos diferentes alternativas de rendimiento, cómo medir la ubicación de las torres, enemigos, mapa presentado, etc.





Problema presentado:
Al plantear el sistema para un tower defense, nuestra principal problemática es la ubicación en general, tanto a la hora de posicionar torres aliadas, como para determinar ubicaciones de los enemigos. Incluso temas esenciales para este tipo de juegos, como suelen ser las mejoras de las torres, las mejoras de los enemigos, el daño generado, dinero ganado, rondas, entre muchos otros factores numéricos que afectan al juego momento a momento.

Como medida ante estos problemas hemos decidido emplear las siguientes heurísticas:

Algoritmo A) Primera mejora vs Mejor mejora: Escogimos este algoritmo porque nos evalúa cada situación para determinar la mejor, esto nos ayuda para el sistema de rondas que posee el juego, ya que al avanzar las rondas dentro del juego, no se mantienen las mismas mejoras, ni estadísticas, ni dinero, entre otros. Este algoritmo nos ayuda a mostrar de mejor manera esa mejor inicial, a la final.
 
Algoritmo B) A Estrella: El planteamiento de este algoritmo nos ayudará para que los enemigos determinen el camino a seguir dentro del juego.

Algoritmo C) Algoritmo AoE / Last (Área): Este algoritmo es una forma de demostrar geometría dentro del sistema, ya que planteamos hacer que las torres tengan y hagan cierto daño a X distancia, como también tendrán su radio de ataque.







Heurísticas utilizadas: (Apto a cambios)
 
Algoritmo A) Primera mejora vs Mejor mejora:

Este algoritmo nos ayuda mucho para un juego de característica Tower Defense, la primera mejora suele concentrarse en sistemas internos como puede ser la economía, utilidad, y mejoras de daño.
Un ejemplo de cómo poderse aplicar, sería identificar los objetivos principales dentro del juego, y el cómo irá evolucionando, en fases tempranas del juego, se busca estabilizar una buena defensa, para en las rondas posteriores poder derrotar un enemigo más fuerte de lo normal (boss) mediante las mejoras conseguidas ronda a ronda.

Algoritmo B) A Estrella: 

Este algoritmo nos ayuda en la planeación de caminos para los enemigos, calculando el menor costo continuamente, ya que será un solo camino con una ruta definida, y todos los enemigos idealmente deberán seguir ese camino siempre. 
También podría aplicarse para las torres aliadas usadas para generar la defensa, si contamos que estas tengan algún tipo de movimiento.

Algoritmo C) Algoritmo AoE / Last (Área):

Este algoritmo tiene un uso más geométrico para las torres de defensa, por ejemplo, una torre busca un enemigo dentro de su área de ataque, pero ese ataque no va netamente a ese objetivo, sino que genera un impacto en área concentrado en esa posición.
Si nos mantenemos apegados a la idea del daño en área y mejoras de una torre cualquiera, podemos plantear como mejora de diseño el aumentar el rango, ampliar la capacidad de daño dentro del área. También nos ayudará mucho para plantear el rango de cada torre, como su rango de ataque.







Descripción del problema
Como problema para este proyecto de Tower Defense, podemos determinar que la principal forma y estrategia a resolver es la forma de optimizar recursos, por eso nos enfocamos tanto en el algoritmo de primera mejora vs segunda mejora, ya que generamos un cambio constante durante cada fase del juego. Es por eso que este tipo de juego no va dirigido a un público muy extenso, sino a gente aficionada a este tipo de juegos y sin un valor más que sea el de entretenimiento y planeación de objetivos.
Usamos una solución algorítmica porque la mayoría de apartados dentro del juego usan una forma de proceso para ser representados, un enemigo x siempre llegará del punto A al punto B, el cual no cambia, pero una torre aliada, puede cambiar y mejorarse durante el transcurso de las rondas.

Buscamos que el algoritmo de primera mejora vs segunda mejora nos sirva para diferenciar el proceso y evolución de las rondas dentro del tower defense, ya que es lo más clave cuando se trata de torres aliadas, porque es nuestra forma de medir el avance progresivo que tendrá el juego, es nuestro valor medible, como el dinero, torres aliadas colocadas y rondas superadas.
Lo que buscamos para garantizar una buena solución es maximizar el uso de recursos, empleando los menos posibles para tener una defensa aliada lo mejor posible por ronda, como la economía generada por ronda, y el daño empleado.

