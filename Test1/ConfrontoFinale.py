import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


def confronta_algoritmi():
    # Nomi dei file
    file_astar = 'risultati_A_STAR.csv'
    file_greedy = 'risultati_GREEDY.csv'

    # 1. Verifica esistenza file
    if not os.path.exists(file_astar) or not os.path.exists(file_greedy):
        print("⚠️ ERRORE: Mancano i file CSV nella cartella!")
        print(f"Controlla se esistono: {file_astar} e {file_greedy}")
        return

    # 2. Caricamento Dati
    df_astar = pd.read_csv(file_astar)
    df_greedy = pd.read_csv(file_greedy)

    print(f"✅ Dati caricati: {len(df_astar)} partite A*, {len(df_greedy)} partite Greedy.")

    # 3. Calcolo Metriche A*
    wins_astar = df_astar[df_astar['Risultato'] == 'VITTORIA']
    rate_astar = (len(wins_astar) / len(df_astar)) * 100
    moves_astar = wins_astar['Mosse_Impiegate'].mean() if not wins_astar.empty else 0

    # 4. Calcolo Metriche GREEDY
    wins_greedy = df_greedy[df_greedy['Risultato'] == 'VITTORIA']
    rate_greedy = (len(wins_greedy) / len(df_greedy)) * 100
    moves_greedy = wins_greedy['Mosse_Impiegate'].mean() if not wins_greedy.empty else 0

    # Stampa Console
    print("\n--- RISULTATI CONFRONTO ---")
    print(f"🏆 A* (Intelligente): {rate_astar:.1f}% Vittorie | Media Mosse: {moves_astar:.1f}")
    print(f"🍔 Greedy (Ingordo) : {rate_greedy:.1f}% Vittorie | Media Mosse: {moves_greedy:.1f}")

    # 5. Generazione Grafico
    plt.style.use('ggplot')  # Stile professionale
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Titolo Generale
    fig.suptitle('Confronto Prestazioni: A* vs Greedy (su 100 Partite)', fontsize=16, fontweight='bold')

    # --- GRAFICO 1: Tasso di Vittoria ---
    labels = ['A* (Intelligente)', 'Greedy (Ingordo)']
    rates = [rate_astar, rate_greedy]
    colors = ['#2E86C1', '#E74C3C']  # Blu vs Rosso

    bars1 = ax1.bar(labels, rates, color=colors, alpha=0.8, edgecolor='black', width=0.6)
    ax1.set_title('Affidabilità (Percentuale Vittorie)', fontsize=14)
    ax1.set_ylabel('% Vittorie')
    ax1.set_ylim(0, 100)

    # Etichette sui valori
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2., height + 1,
                 f'{height:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

    # --- GRAFICO 2: Efficienza (Mosse) ---
    moves = [moves_astar, moves_greedy]
    colors2 = ['#5DADE2', '#F1948A']  # Versioni più chiare

    bars2 = ax2.bar(labels, moves, color=colors2, alpha=0.8, edgecolor='black', width=0.6)
    ax2.set_title('Velocità (Media Mosse per Vincere)', fontsize=14)
    ax2.set_ylabel('Numero di Mosse')

    # Etichette sui valori
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2., height + 0.5,
                 f'{height:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Salvataggio
    plt.tight_layout()
    output_img = 'confronto_finale_vittorie.png'
    plt.savefig(output_img, dpi=300)
    print(f"\n✅ Grafico salvato come '{output_img}'.")
    plt.show()


if __name__ == "__main__":
    confronta_algoritmi()