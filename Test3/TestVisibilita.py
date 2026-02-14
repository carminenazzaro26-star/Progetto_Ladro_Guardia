import csv
import random
import pandas as pd
import matplotlib.pyplot as plt
from collections import deque

# Import delle tue classi
from RobberAgent2 import RobberAgent
from guard2 import MinimaxGuardAI, GameState, Position

# --- CONFIGURAZIONE ---
NUM_PARTITE = 100
MAX_TURNI = 200
RAGGI_DA_TESTARE = [2, 4, 25]  # Raggio 2 (Miope), 4 (Normale), 25 (Tutta la mappa)


def check_path_exists(griglia, start_pos, end_pos):
    """BFS veloce per garantire che la mappa sia risolvibile"""
    rows = len(griglia)
    cols = len(griglia[0])
    queue = deque([start_pos])
    visited = set()
    visited.add(start_pos)

    while queue:
        r, c = queue.popleft()
        if (r, c) == end_pos: return True
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and griglia[nr][nc] != 1 and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc))
    return False


def genera_mappa_valida():
    while True:
        griglia = [[0 for _ in range(20)] for _ in range(20)]
        for row in range(20):
            for col in range(20):
                if random.random() < 0.25 and (row, col) not in [(0, 0), (19, 19), (10, 5), (5, 10)]:
                    griglia[row][col] = 1
        if check_path_exists(griglia, (0, 0), (19, 19)):
            return griglia


def esegui_test_visibilita():
    risultati_finali = []
    print("👁️  AVVIO TEST VISIBILITÀ (Sensori)...")

    for raggio in RAGGI_DA_TESTARE:
        print(f"\n   Testing Raggio Visivo: {raggio}...")
        catture = 0

        for i in range(NUM_PARTITE):
            griglia = genera_mappa_valida()
            ladro = RobberAgent((0, 0), (19, 19))

            # --- QUI CREIAMO LA GUARDIA CON IL RAGGIO VARIABILE ---
            guard_ai = MinimaxGuardAI(max_depth=2, visual_range=raggio)

            g1 = Position(10, 5)
            g2 = Position(5, 10)

            for _ in range(MAX_TURNI):
                # 1. Turno Ladro
                ladro.pianifica_mossa(griglia, [(g1.x, g1.y), (g2.x, g2.y)])

                # Check vittoria ladro
                if ladro.pos == (19, 19):
                    break

                # Check cattura immediata
                if (abs(ladro.pos[0] - g1.x) + abs(ladro.pos[1] - g1.y) <= 1 or
                        abs(ladro.pos[0] - g2.x) + abs(ladro.pos[1] - g2.y) <= 1):
                    catture += 1
                    break

                # 2. Turno Guardie
                # Simula la percezione limitata (passiamo il ladro solo se è nel raggio)
                dist_g1 = abs(ladro.pos[0] - g1.x) + abs(ladro.pos[1] - g1.y)
                dist_g2 = abs(ladro.pos[0] - g2.x) + abs(ladro.pos[1] - g2.y)

                if dist_g1 <= raggio or dist_g2 <= raggio:
                    visible_robber = Position(*ladro.pos)
                else:
                    visible_robber = None

                state = GameState(griglia, g1, g2, visible_robber)
                g1, g2 = guard_ai.get_best_moves(state)

                # Check cattura dopo mossa guardie
                if (abs(ladro.pos[0] - g1.x) + abs(ladro.pos[1] - g1.y) <= 1 or
                        abs(ladro.pos[0] - g2.x) + abs(ladro.pos[1] - g2.y) <= 1):
                    catture += 1
                    break

        perc = (catture / NUM_PARTITE) * 100
        risultati_finali.append(perc)
        print(f"   --> Raggio {raggio}: {perc:.0f}% Catture")

    # --- GRAFICO ---
    plt.figure(figsize=(10, 6))
    labels = ['Miope (R=2)', 'Normale (R=4)', 'Cecchino (R=25)']
    colors = ['#81C784', '#4CAF50', '#1B5E20']  # Verde chiaro -> scuro

    bars = plt.bar(labels, risultati_finali, color=colors, edgecolor='black')

    plt.title('Impatto dei Sensori: Visibilità delle Guardie', fontsize=16)
    plt.ylabel('Tasso di Cattura (%)', fontsize=12)
    plt.ylim(0, 100)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height + 2,
                 f'{height:.0f}%', ha='center', va='bottom', fontsize=14, fontweight='bold')

    plt.savefig('confronto_visibilita.png')
    plt.show()
    print("\n✅ Grafico salvato come 'confronto_visibilita.png'")


if __name__ == "__main__":
    esegui_test_visibilita()