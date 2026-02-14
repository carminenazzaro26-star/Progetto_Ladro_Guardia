import csv
import random
from collections import deque
import pandas as pd
import matplotlib.pyplot as plt

# Importa le classi
from RobberAgent1 import RobberAgent
from guard1 import MinimaxGuardAI, GameState, Position  # La tua AI originale
from DummyGuards import RandomGuardAI, GreedyGuardAI  # Le AI stupide

# --- CONFIGURAZIONE ---
NUM_PARTITE = 100
MAX_TURNI = 200
GRID_SIZE = 20


def check_path_exists(griglia, start, end):
    q = deque([start])
    visited = {start}
    while q:
        r, c = q.popleft()
        if (r, c) == end: return True
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 20 and 0 <= nc < 20 and griglia[nr][nc] != 1 and (nr, nc) not in visited:
                visited.add((nr, nc))
                q.append((nr, nc))
    return False


def genera_mappa():
    while True:
        g = [[0] * 20 for _ in range(20)]
        for r in range(20):
            for c in range(20):
                if random.random() < 0.25 and (r, c) not in [(0, 0), (19, 19), (10, 5), (5, 10)]:
                    g[r][c] = 1
        if check_path_exists(g, (0, 0), (19, 19)): return g


def esegui_test(tipo_guardia):
    nome_file = f'risultati_guardie_{tipo_guardia}.csv'
    print(f"⚔️ Inizio test contro guardie: {tipo_guardia.upper()}...")

    risultati = []
    catture = 0

    for i in range(NUM_PARTITE):
        griglia = genera_mappa()
        ladro = RobberAgent((0, 0), (19, 19))

        # Scelta dell'AI Guardie
        if tipo_guardia == 'random':
            ai = RandomGuardAI()
        elif tipo_guardia == 'greedy':
            ai = GreedyGuardAI()
        else:
            ai = MinimaxGuardAI(max_depth=2)  # La tua AI forte

        g1 = Position(10, 5)
        g2 = Position(5, 10)

        esito = "VITTORIA"  # Ottimismo per il ladro

        for _ in range(MAX_TURNI):
            # 1. Mossa Ladro
            ladro.pianifica_mossa(griglia, [(g1.x, g1.y), (g2.x, g2.y)])
            if ladro.pos == (19, 19): break  # Vittoria Ladro

            # Check Cattura
            if (abs(ladro.pos[0] - g1.x) + abs(ladro.pos[1] - g1.y) <= 1 or
                    abs(ladro.pos[0] - g2.x) + abs(ladro.pos[1] - g2.y) <= 1):
                esito = "CATTURATO"
                break

            # 2. Mossa Guardie
            # Creiamo lo stato per l'AI
            # Nota: Minimax vuole GameState, le altre AI si adattano
            # Il ladro è visibile solo se vicino (simulazione sensori)
            dist_g1 = abs(ladro.pos[0] - g1.x) + abs(ladro.pos[1] - g1.y)
            dist_g2 = abs(ladro.pos[0] - g2.x) + abs(ladro.pos[1] - g2.y)
            visible_robber = Position(*ladro.pos) if (dist_g1 <= 4 or dist_g2 <= 4) else None

            state = GameState(griglia, g1, g2, visible_robber)
            g1, g2 = ai.get_best_moves(state)

            # Check Cattura dopo mossa guardie
            if (abs(ladro.pos[0] - g1.x) + abs(ladro.pos[1] - g1.y) <= 1 or
                    abs(ladro.pos[0] - g2.x) + abs(ladro.pos[1] - g2.y) <= 1):
                esito = "CATTURATO"
                break

        risultati.append(esito)
        if esito == "CATTURATO": catture += 1

    # Salvataggio CSV
    df = pd.DataFrame(risultati, columns=['Esito'])
    df.to_csv(nome_file, index=False)
    print(f"   ✅ Test {tipo_guardia} finito. Tasso Cattura: {catture}%")
    return catture


# --- MAIN ---
if __name__ == "__main__":
    # Esegue i 3 test
    c_random = esegui_test('random')
    c_greedy = esegui_test('greedy')
    c_minimax = esegui_test('minimax')

    # --- GRAFICO FINALE ---
    print("\n📊 Generazione Grafico Comparativo...")
    plt.figure(figsize=(10, 6))
    strategies = ['Random', 'Greedy', 'Minimax (Tu)']
    scores = [c_random, c_greedy, c_minimax]
    colors = ['grey', 'orange', '#D32F2F']  # Grigio, Arancio, Rosso sangue

    bars = plt.bar(strategies, scores, color=colors, edgecolor='black')

    plt.title('Efficacia delle Guardie: Tasso di Cattura', fontsize=16)
    plt.ylabel('Percentuale di Catture (%)', fontsize=12)
    plt.ylim(0, 100)

    # Numeri sulle barre
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height + 2,
                 f'{height}%', ha='center', va='bottom', fontsize=14, fontweight='bold')

    plt.savefig('confronto_guardie.png')
    plt.show()