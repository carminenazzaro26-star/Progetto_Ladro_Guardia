import os
import random
import pygame
import math
from RobberAgent import RobberAgent
from guard import MinimaxGuardAI, GameState, Position

# --- COSTANTI ---
GRID_SIZE = 20
CELL_SIZE = 35
WINDOW_SIZE = GRID_SIZE * CELL_SIZE
FPS = 15

# COLORI TEMA SCURO
BLACK_BG = (15, 15, 15)  # Sfondo nero profondo
WHITE_WALL = (240, 240, 240)  # Muri bianchi accesi
DARK_GREY = (40, 40, 40)  # Griglia sottile
FLASHLIGHT_COLOR = (255, 255, 150, 80)  # Luce gialla calda semitrasparente


def load_safe_image(path, fallback_color):
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(surf, fallback_color, (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 2)
    return surf


def draw_flashlight(screen, pos, direction, length_cells=4):
    """Disegna il fascio di luce basato sulla direzione attuale"""
    if direction == (0, 0): return  # Non dovrebbe succedere con la logica nuova

    # Centro della cella
    cx = pos[0] * CELL_SIZE + CELL_SIZE // 2
    cy = pos[1] * CELL_SIZE + CELL_SIZE // 2

    # Calcolo angolo della direzione
    angle = math.atan2(direction[1], direction[0])

    # Apertura del fascio (es. 40 gradi)
    spread = math.radians(20)
    length = length_cells * CELL_SIZE

    # Punti del triangolo della luce
    p1 = (cx, cy)
    p2 = (cx + length * math.cos(angle - spread), cy + length * math.sin(angle - spread))
    p3 = (cx + length * math.cos(angle + spread), cy + length * math.sin(angle + spread))

    # Disegno su superficie dedicata per la trasparenza
    light_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
    pygame.draw.polygon(light_surf, FLASHLIGHT_COLOR, [p1, p2, p3])
    screen.blit(light_surf, (0, 0))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Night Infiltration - Torce Fisse")
    clock = pygame.time.Clock()

    img_ladro = load_safe_image("img/ladro.png", (0, 0, 255))
    img_guardia = load_safe_image("img/guardia.png", (255, 0, 0))
    img_cassaforte = load_safe_image("img/cassaforte.png", (0, 255, 0))

    griglia = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if random.random() < 0.25 and (col, row) not in [(0, 0), (19, 19), (10, 5), (5, 10)]:
                if  (row, col)  not in [(10, 4), (4, 10), (0, 1)]:
                 griglia[row][col] = 1

    ladro = RobberAgent((0, 0), (19, 19))
    guard_ai = MinimaxGuardAI(max_depth=2)
    g1_pos = Position(10, 5)
    g2_pos = Position(5, 10)

    # DIREZIONI INIZIALI (Fisse finché non si muovono)
    ladro_dir = (1, 0)
    g1_dir = (0, 1)
    g2_dir = (1, 0)

    running = True
    semaforo_ladro = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        # --- LOGICA MOVIMENTO ---
        old_lp = ladro.pos
        old_g1 = (g1_pos.x, g1_pos.y)
        old_g2 = (g2_pos.x, g2_pos.y)

        if semaforo_ladro:
            ladro.pianifica_mossa(griglia, [(g1_pos.x, g1_pos.y), (g2_pos.x, g2_pos.y)])
            # Aggiorna direzione se si è mosso
            if ladro.pos != old_lp:
                ladro_dir = (ladro.pos[0] - old_lp[0], ladro.pos[1] - old_lp[1])
            semaforo_ladro = False
        else:
            stato = GameState(griglia, g1_pos, g2_pos, Position(*ladro.pos), False)
            g1_pos, g2_pos = guard_ai.get_best_moves(stato)
            # Aggiorna direzioni guardie
            if (g1_pos.x, g1_pos.y) != old_g1:
                g1_dir = (g1_pos.x - old_g1[0], g1_pos.y - old_g1[1])
            if (g2_pos.x, g2_pos.y) != old_g2:
                g2_dir = (g2_pos.x - old_g2[0], g2_pos.y - old_g2[1])
            semaforo_ladro = True

        # --- DISEGNO ---
        screen.fill(BLACK_BG)

        # Disegno Muri e Griglia
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if griglia[r][c] == 1:
                    pygame.draw.rect(screen, WHITE_WALL, rect)
                pygame.draw.rect(screen, DARK_GREY, rect, 1)

        screen.blit(img_cassaforte, (19 * CELL_SIZE, 19 * CELL_SIZE))

        # DISEGNO TORCE (Prima dei personaggi così non coprono le icone)
        draw_flashlight(screen, ladro.pos, ladro_dir)
        draw_flashlight(screen, (g1_pos.x, g1_pos.y), g1_dir)
        draw_flashlight(screen, (g2_pos.x, g2_pos.y), g2_dir)

        # Personaggi
        t = pygame.time.get_ticks() / 200
        rimbalzo = int(math.sin(t) * 3)
        screen.blit(img_ladro, (ladro.pos[0] * CELL_SIZE, ladro.pos[1] * CELL_SIZE + rimbalzo))
        screen.blit(img_guardia, (g1_pos.x * CELL_SIZE, g1_pos.y * CELL_SIZE))
        screen.blit(img_guardia, (g2_pos.x * CELL_SIZE, g2_pos.y * CELL_SIZE))

        # Check Vittoria/Sconfitta
        if abs(ladro.pos[0] - g1_pos.x) + abs(ladro.pos[1] - g1_pos.y) <= 1 or \
                abs(ladro.pos[0] - g2_pos.x) + abs(ladro.pos[1] - g2_pos.y) <= 1:
            print("CATTURATO!")
            running = False
        elif ladro.pos == (19, 19):
            print("VITTORIA!")
            running = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()