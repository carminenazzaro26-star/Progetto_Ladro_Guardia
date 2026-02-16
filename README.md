# 🔦 Robber Simulator: AI in Ambienti Competitivi

Un simulatore sviluppato in Python che mette a confronto algoritmi di ricerca informata e di teoria dei giochi in un ambiente competitivo con informazione parziale. Il progetto esplora le dinamiche classiche di "Guardie e Ladri" all'interno di una griglia 20x20 generata proceduralmente.

Progetto per il corso di **Fondamenti di Intelligenza Artificiale** - Febbraio 2026.
Sviluppato da: Raffaella Maurelli e Carmine Nazzaro.

## 🧠 Algoritmi e Intelligenza Artificiale
Il sistema si basa sull'interazione di tre algoritmi fondamentali, ciascuno con un ruolo specifico:

* **Breadth-First Search (BFS):** Utilizzato esclusivamente nella fase di generazione per validare la mappa e garantire che esista sempre un percorso giocabile tra il ladro e la cassaforte.
* **A* (A-Star) Adattivo:** Guida il Ladro. Utilizza un'euristica personalizzata che valuta la distanza di Manhattan dalla cassaforte e applica penalità dinamiche per evitare le guardie visibili e prevenire loop (tramite heat map e storico mosse).
* **Minimax con Potatura Alfa-Beta:** Gestisce l'intelligenza delle due Guardie. Simula alberi di gioco per anticipare le mosse del ladro, coordinando manovre di accerchiamento e inseguimento.

## 👁️ Meccaniche Principali
* **Informazione Parziale:** Gli agenti non vedono l'intera mappa. Il ladro ha un raggio visivo di 3 celle, mentre le guardie di 4 celle. I muri bloccano la linea di vista (line-of-sight).
* **Stati Comportamentali:** Le guardie passano dinamicamente tra tre stati: *Pattugliamento casuale* (nessuna informazione), *Inseguimento Minimax* (ladro a vista) e *Ricerca* (verso l'ultima posizione nota del ladro).
* **Rendering Grafico:** L'interfaccia, sviluppata con Pygame, mostra i fasci di luce dinamici (torce) per rendere intuitivo il campo visivo degli agenti.

## 🛠️ Tecnologie Utilizzate
* **Python 3**
* **Pygame** (per il rendering grafico a 15 FPS)

## 💻 Installazione e Utilizzo

1. Clona la repository:
   ```bash
   git clone [https://github.com/carminenazzaro26-star/Progetto_Ladro_Guardia.git](https://github.com/carminenazzaro26-star/Progetto_Ladro_Guardia.git)