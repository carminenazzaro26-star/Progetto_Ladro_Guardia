import random
import csv
from collections import deque
import pandas as pd
import matplotlib.pyplot as plt

# --- MODIFICA FONDAMENTALE ---
try:
    from Test1.RobberAgentGreedy import RobberAgent as GreedyAgent
except ImportError:
    print("ERRORE: Non trovo il file 'RobberAgentGreedy.py'. Controlla il nome!")
    exit()

from guard import MinimaxGuardAI, GameState, Position

# --- CONFIGURAZIONE TEST ---
NUMERO_PARTITE = 1000
MAX_TURNI = 200
GRID_SIZE = 20
NOME_FILE_CSV = 'risultati_GREEDY.csv'
NOME_FILE_GRAFICO = 'grafico_greedy.png'  # Nome dell'immagine salvata

# --- FUNZIONI DI UTILITÀ ---

def check_path_exists(griglia, start_pos, end_pos):
    """BFS per verificare che la mappa sia risolvibile"""
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
            if (0 <= nr < rows and 0 <= nc < cols and
                    griglia[nr][nc] != 1 and (nr, nc) not in visited):
                visited.add((nr, nc))
                queue.append((nr, nc))
    return False


def genera_mappa_valida():
    while True:
        griglia = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if (row, col) in [(0, 0), (0, 1), (1, 0), (19, 19), (10, 5), (5, 10)]:
                    continue
                if random.random() < 0.25:
                    griglia[row][col] = 1

        if check_path_exists(griglia, (0, 0), (19, 19)):
            return griglia


# --- MOTORE DI SIMULAZIONE ---

def esegui_simulazione_greedy():
    print(f"🚀 AVVIO TEST GREEDY: {NUMERO_PARTITE} partite...")
    risultati = []

    for i in range(NUMERO_PARTITE):
        griglia = genera_mappa_valida()

        # Qui usiamo il GreedyAgent importato all'inizio
        ladro = GreedyAgent((0, 0), (19, 19))

        guard_ai = MinimaxGuardAI(max_depth=2)
        g1_pos = Position(10, 5)
        g2_pos = Position(5, 10)

        mosse_ladro = 0
        stato_finale = "PAREGGIO"

        for turno in range(MAX_TURNI):
            # 1. Turno Ladro
            old_pos = ladro.pos
            ladro.pianifica_mossa(griglia, [(g1_pos.x, g1_pos.y), (g2_pos.x, g2_pos.y)])
            if ladro.pos != old_pos:
                mosse_ladro += 1

            if ladro.pos == (19, 19):
                stato_finale = "VITTORIA"
                break

            if (abs(ladro.pos[0] - g1_pos.x) + abs(ladro.pos[1] - g1_pos.y) <= 1 or
                    abs(ladro.pos[0] - g2_pos.x) + abs(ladro.pos[1] - g2_pos.y) <= 1):
                stato_finale = "CATTURATO"
                break

            # 2. Turno Guardie
            stato = GameState(griglia, g1_pos, g2_pos, Position(*ladro.pos), False)
            g1_pos, g2_pos = guard_ai.get_best_moves(stato)

            if (abs(ladro.pos[0] - g1_pos.x) + abs(ladro.pos[1] - g1_pos.y) <= 1 or
                    abs(ladro.pos[0] - g2_pos.x) + abs(ladro.pos[1] - g2_pos.y) <= 1):
                stato_finale = "CATTURATO"
                break

        risultati.append([i + 1, stato_finale, mosse_ladro])
        if (i + 1) % 20 == 0:
            print(f"   ...completate {i + 1}/{NUMERO_PARTITE} partite.")

    with open(NOME_FILE_CSV, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID_Partita", "Risultato", "Mosse_Impiegate"])
        writer.writerows(risultati)

    print(f"✅ Dati Greedy salvati in '{NOME_FILE_CSV}'")


# --- MOTORE GRAFICO (NUOVO) ---

def genera_grafici():
    print("📊 Generazione grafici Greedy in corso...")
    try:
        # Legge il file appena creato
        df = pd.read_csv(NOME_FILE_CSV)
    except FileNotFoundError:
        print("Errore: File CSV non trovato. Esegui la simulazione prima.")
        return

    # Setup Grafico
    plt.style.use('ggplot')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    fig.suptitle(f'Analisi Prestazioni Ladro GREEDY su {len(df)} Partite', fontsize=18)

    # GRAFICO 1: Torta (Percentuali)
    counts = df['Risultato'].value_counts()
    colors = {'VITTORIA': '#4CAF50', 'CATTURATO': '#F44336', 'PAREGGIO': 'grey'}
    col_list = [colors.get(x, 'blue') for x in counts.index]

    ax1.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90,
            colors=col_list, explode=[0.05] * len(counts), textprops={'fontsize': 12})
    ax1.set_title('Tasso di Successo', fontsize=14)

    # GRAFICO 2: Istogramma (Mosse)
    wins = df[df['Risultato'] == 'VITTORIA']
    if not wins.empty:
        media = wins['Mosse_Impiegate'].mean()
        ax2.hist(wins['Mosse_Impiegate'], bins=15, color='#FFA500', edgecolor='black', alpha=0.7) # Arancione per Greedy
        ax2.axvline(media, color='red', linestyle='dashed', linewidth=2, label=f'Media: {media:.1f} mosse')
        ax2.set_title('Distribuzione Mosse (Solo Vittorie)', fontsize=14)
        ax2.set_xlabel('Numero di Mosse')
        ax2.set_ylabel('Frequenza')
        ax2.legend()
    else:
        ax2.text(0.5, 0.5, "NESSUNA VITTORIA", ha='center', fontsize=20)
        ax2.set_title('Distribuzione Mosse', fontsize=14)

    plt.tight_layout()
    plt.savefig(NOME_FILE_GRAFICO)
    print(f"✅ Grafico salvato come '{NOME_FILE_GRAFICO}'")
    plt.show()


if __name__ == "__main__":
    # 1. Esegue la simulazione
    esegui_simulazione_greedy()
    # 2. Genera subito il grafico
    genera_grafici()