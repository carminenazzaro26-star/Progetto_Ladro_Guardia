import heapq


class RobberAgent:
    def __init__(self, startPos, endPos):
        self.pos = startPos  # Posizione corrente
        self.endPos = endPos  # Posizione obiettivo
        self.vision_radius = 3  # Raggio di visione del ladro
        self.storico_mosse = []  # Ultime 2 posizioni visitate
        # Heat Map per evitare i cicli (memoria delle zone visitate)
        self.heat_map = [[0 for _ in range(20)] for _ in range(20)]

    def traduzioneCordinate(self, posizione_iniziale, posizione_finale):
        x, y = posizione_finale
        z, r = posizione_iniziale
        dx = x - z
        dy = y - r

        if dx == 0 and dy == -1:
            return "NORD"
        elif dx == 0 and dy == 1:
            return "SUD"
        elif dx == 1 and dy == 0:
            return "EST"
        elif dx == -1 and dy == 0:
            return "OVEST"
        else:
            return "WAIT"

    def get_neighbors(self, grid, pos, visible_guards):
        neighbors = []
        # Movimenti possibili: NORD, SUD, EST, OVEST
        for dx, dy in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
            x, y = pos[0] + dx, pos[1] + dy

            # 1. Controllo confini della griglia 20x20
            if 0 <= x < 20 and 0 <= y < 20:
                # 2. Verifica che la cella non sia un muro (1) e non ci sia una guardia visibile
                if grid[y][x] != 1 and (x, y) not in visible_guards:
                    neighbors.append((x, y))
        return neighbors

    def heuristic(self, pos, guardie_visibili):
        """
        Funzione Euristica: Stima quanto è 'buona' una cella.
        Include: Distanza Manhattan + Penalità Cicli + Penalità Guardie
        """
        # Distanza di Manhattan base
        h = abs(pos[0] - self.endPos[0]) + abs(pos[1] - self.endPos[1])

        # 1. Penalità per le ultime 2 posizioni (evita oscillazioni immediate)
        if pos in self.storico_mosse:
            h += 100

        # 2. HEAT MAP: Penalità cumulativa per zone già visitate
        x, y = pos
        if self.heat_map[y][x] > 0:
            h += self.heat_map[y][x] * 10

            # 3. Penalità guardie nel raggio di visione
        for g_pos in guardie_visibili:
            dist_g = abs(pos[0] - g_pos[0]) + abs(pos[1] - g_pos[1])
            if dist_g <= 3:
                h += (4 - dist_g) * 20
        return h

    def greedy_search(self, griglia, guardie_visibili):
        """
        Algoritmo Greedy Best-First Search.
        Sceglie sempre il nodo che SEMBRA più vicino all'obiettivo (euristica minore),
        ignorando il costo del cammino già percorso.
        """
        start = self.pos
        frontier = []
        # Nella frontiera mettiamo solo la priorità data dall'euristica
        heapq.heappush(frontier, (0, start))

        came_from = {start: None}

        # Nota: Non serve 'cost_so_far' perché il Greedy non calcola il costo reale del percorso

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == self.endPos:
                break

            for next_node in self.get_neighbors(griglia, current, guardie_visibili):
                if next_node not in came_from:
                    # --- CUORE DEL GREEDY ---
                    # La priorità è SOLO l'euristica (h), non c'è g(n)
                    priority = self.heuristic(next_node, guardie_visibili)

                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current

        return came_from

    def pianifica_mossa(self, griglia, guardia_tutte):
        # 1. Filtro guardie visibili (Raggio 3)
        guardia_visibili = []
        for g in guardia_tutte:
            dist = abs(self.pos[0] - g[0]) + abs(self.pos[1] - g[1])
            if dist <= 3:
                guardia_visibili.append(g)

        # 2. Eseguo l'algoritmo GREEDY
        mappa = self.greedy_search(griglia, guardia_visibili)

        # 3. Controllo se l'obiettivo è raggiungibile
        if self.endPos not in mappa:
            return "WAIT"

        # 4. Ricostruzione percorso (backtracking)
        percorso = []
        attuale = self.endPos

        # Protezione: se il greedy si è bloccato e non ha trovato la fine
        if attuale not in mappa:
            return "WAIT"

        while attuale != self.pos:
            percorso.append(attuale)
            attuale = mappa[attuale]

        # 5. Eseguo il primo passo calcolato
        prossima_pos = percorso[-1]

        new_x, new_y = prossima_pos
        mossa = self.traduzioneCordinate(self.pos, prossima_pos)

        # Aggiornamento storico
        if len(self.storico_mosse) > 2:
            self.storico_mosse.pop(0)
        self.storico_mosse.append(self.pos)

        # Aggiornamento Heat Map
        self.heat_map[new_y][new_x] += 1

        # Aggiornamento posizione agente
        self.pos = prossima_pos
        return mossa