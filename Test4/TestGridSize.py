import random
import matplotlib.pyplot as plt
from collections import deque
from RobberAgent3 import RobberAgent
from guard3 import MinimaxGuardAI, GameState, Position

# --- CONFIGURAZIONE ---
NUM_PARTITE = 100
MAX_TURNI = 300  # Aumentiamo i turni perché le mappe grandi richiedono più tempo
DIMENSIONI_DA_TESTARE = [15, 20, 25]


def check_path_exists(griglia, start_pos, end_pos, size):
    queue = deque([start_pos])
    visited = {start_pos}
    while queue:
        r, c = queue.popleft()
        if (r, c) == end_pos: return True
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size and griglia[nr][nc] != 1 and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc))
    return False


def genera_mappa_variabile(size):
    while True:
        griglia = [[0 for _ in range(size)] for _ in range(size)]
        # Coordinate critiche da tenere libere
        start = (0, 0)
        end = (size - 1, size - 1)
        # Posizioniamo le guardie in punti proporzionali
        g1_pos = (size // 2, size // 4)
        g2_pos = (size // 4, size // 2)

        safe_zones = [start, end, g1_pos, g2_pos]

        for row in range(size):
            for col in range(size):
                if random.random() < 0.25 and (col, row) not in safe_zones:
                    griglia[row][col] = 1

        if check_path_exists(griglia, start, end, size):
            return griglia, start, end, g1_pos, g2_pos


def esegui_test_grid():
    risultati = []
    print("📏 AVVIO TEST DIMENSIONE GRIGLIA...")

    for size in DIMENSIONI_DA_TESTARE:
        print(f"\n   Testing Griglia {size}x{size}...")
        catture = 0
        vittorie_ladro = 0

        for i in range(NUM_PARTITE):
            griglia, start, end, pos_g1, pos_g2 = genera_mappa_variabile(size)

            # Passiamo la dimensione al ladro!
            ladro = RobberAgent(start, end, grid_size=size)

            # Le guardie usano la vista standard (R=4)
            guard_ai = MinimaxGuardAI(max_depth=2, visual_range=4)

            g1 = Position(*pos_g1)
            g2 = Position(*pos_g2)

            for _ in range(MAX_TURNI):
                # 1. Ladro
                ladro.pianifica_mossa(griglia, [(g1.x, g1.y), (g2.x, g2.y)])

                if ladro.pos == end:
                    vittorie_ladro += 1
                    break

                # Check Cattura Immediata
                if (abs(ladro.pos[0] - g1.x) + abs(ladro.pos[1] - g1.y) <= 1 or
                        abs(ladro.pos[0] - g2.x) + abs(ladro.pos[1] - g2.y) <= 1):
                    catture += 1
                    break

                # 2. Guardie
                dist_g1 = abs(ladro.pos[0] - g1.x) + abs(ladro.pos[1] - g1.y)
                dist_g2 = abs(ladro.pos[0] - g2.x) + abs(ladro.pos[1] - g2.y)

                visible_robber = Position(*ladro.pos) if (dist_g1 <= 4 or dist_g2 <= 4) else None

                state = GameState(griglia, g1, g2, visible_robber)
                g1, g2 = guard_ai.get_best_moves(state)

                if (abs(ladro.pos[0] - g1.x) + abs(ladro.pos[1] - g1.y) <= 1 or
                        abs(ladro.pos[0] - g2.x) + abs(ladro.pos[1] - g2.y) <= 1):
                    catture += 1
                    break

        tasso_cattura = (catture / NUM_PARTITE) * 100
        risultati.append(tasso_cattura)
        print(f"   --> {size}x{size}: {tasso_cattura}% Catture")

    # --- GRAFICO ---
    plt.figure(figsize=(10, 6))
    labels = [f'{s}x{s}' for s in DIMENSIONI_DA_TESTARE]
    colors = ['#FFCC80', '#FF9800', '#E65100']  # Arancione chiaro -> scuro

    bars = plt.bar(labels, risultati, color=colors, edgecolor='black')

    plt.title('Impatto della Dimensione Griglia sulle Catture', fontsize=16)
    plt.xlabel('Dimensione Mappa')
    plt.ylabel('Tasso di Cattura (%)', fontsize=12)
    plt.ylim(0, 100)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height + 2,
                 f'{height:.0f}%', ha='center', va='bottom', fontsize=14, fontweight='bold')

    plt.savefig('confronto_griglia.png')
    plt.show()


if __name__ == "__main__":
    esegui_test_grid()