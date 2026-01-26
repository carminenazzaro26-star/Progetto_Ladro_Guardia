import os
import random
import pygame
import math

from RobberAgent import RobberAgent
from guard import MinimaxGuardAI, GameState, Position

GRID_SIZE = 20
CELL_SIZE = 35
WINDOW_SIZE = GRID_SIZE * CELL_SIZE
FPS = 15 # Abbassato un po' per vedere meglio le mosse

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)    # Guardia
GREEN = (0, 255, 0)  # Cassaforte
BLUE = (0, 0, 255)   # Ladro
GRIGIO = (200, 200, 200) # Bordo


def load_images(names, fallaback_color, size):
    if  os.path.exists(names):
        img = pygame.image.load(names).convert_alpha()
        return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
    else:
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, fallaback_color, size//2, size//2, size//2)
        return surf


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Simulatore Ladro vs Guardie - A* & Minimax")
    clock = pygame.time.Clock()

    img_ladro = pygame.image.load("img/ladro.png")
    img_ladro = pygame.transform.scale(img_ladro, (CELL_SIZE, CELL_SIZE))
    img_guardia = pygame.image.load("img/guardia.png")
    img_guardia = pygame.transform.scale(img_guardia, (CELL_SIZE, CELL_SIZE))
    img_cassaforte = pygame.image.load("img/cassaforte.png")
    img_cassaforte = pygame.transform.scale(img_cassaforte, (CELL_SIZE, CELL_SIZE))

    overlay_visione = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)

    # Inizializzazione griglia con ostacoli
    griglia = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if random.random() < 0.25 and (col, row) != (0,0) and (col, row) != (19,19):
                if  (row, col) not in [(10,5), (5,10), (0,1)]:
                    griglia[row][col] = 1

    cassaforte = (19, 19)
    ladro = RobberAgent((0, 0), cassaforte)
    guard_ai = MinimaxGuardAI(max_depth=2)


    guardia_1 = Position(10, 5)
    guardia_2 = Position(5, 10)

    running = True
    semaforo_ladro = True


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        if semaforo_ladro:
            guardie_attuali = [(guardia_1.x, guardia_1.y), (guardia_2.x, guardia_2.y)]
            ladro.pianifica_mossa(griglia, guardie_attuali)
            semaforo_ladro = False
        else:
            #visione totale
            stato_corrente = GameState(
                grid=griglia,
                guard1_pos=guardia_1,
                guard2_pos=guardia_2,
                thief_pos=Position(ladro.pos[0], ladro.pos[1]),
                thief_visible=False
            )
            guardia_1, guardia_2 = guard_ai.get_best_moves(stato_corrente)
            semaforo_ladro = True

        # --- DISEGNO ---
        screen.fill(WHITE)
        overlay_visione.fill((0, 0, 0, 0))
        # Disegno Griglia e Ostacoli
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                # Definiamo il rettangolo una sola volta
                recta = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                # 1. Disegniamo prima il colore di riempimento
                if griglia[row][col] == 1:
                    pygame.draw.rect(screen, BLACK, recta)
                else:
                    # Opzionale: disegna uno sfondo bianco/chiaro per le celle libere
                    pygame.draw.rect(screen, WHITE, recta)

                # 2. Disegniamo il bordo grigio SOPRA, così la griglia è sempre definita
                pygame.draw.rect(screen, GRIGIO, recta, 1)

        # Cassaforte (Quadrato)
        screen.blit(img_cassaforte, (cassaforte[0]*CELL_SIZE, cassaforte[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Ladro (Cerchio Blu)
        tempo = pygame.time.get_ticks() / 200
        rimbalzo = int(math.sin(tempo) * 3)  # Effetto respiro/rimbalzo
        screen.blit(img_ladro, (ladro.pos[0] * CELL_SIZE, ladro.pos[1] * CELL_SIZE + rimbalzo))

        # Guardie (Cerchi Rossi)
        screen.blit(img_guardia, (guardia_1.x*CELL_SIZE, guardia_1.y*CELL_SIZE))
        screen.blit(img_guardia, (guardia_2.x*CELL_SIZE, guardia_2.y*CELL_SIZE))

        distanza_guardia_1 = abs(ladro.pos[0] - guardia_1.x) + abs(ladro.pos[1] - guardia_1.y)
        distanza_guardia_2 = abs(ladro.pos[0] - guardia_2.x) + abs(ladro.pos[1] - guardia_2.y)
        #condizioni vittoria e sconfitta
        if distanza_guardia_1 <=1 or distanza_guardia_2 <=1:
            print("hai perso")
            running = False
        elif ladro.pos == cassaforte:
            print("hai vinto")
            running = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()