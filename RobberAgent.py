import heapq


class RobberAgent:
    def __init__(self, startPos, endPos):
        self.pos = startPos  # Posizione corrente
        self.endPos = endPos  # Posizione obiettivo [cite: 42]
        self.vision_radius = 3  # Raggio di visione del ladro [cite: 40, 69]

    def traduzioneCordinate(self, posizione_iniziale, posizione_finale):
        x, y = posizione_finale
        z, r = posizione_iniziale
        dx = x - z
        dy = y - r  # Corretto: era y - z

        if dx == 0 and dy == -1:
            return "NORD"  # [cite: 116]
        elif dx == 0 and dy == 1:
            return "SUD"  # [cite: 117]
        elif dx == 1 and dy == 0:
            return "EST"  # [cite: 118]
        elif dx == -1 and dy == 0:
            return "OVEST"  # [cite: 119]
        else:
            return "WAIT"  # [cite: 120]

    def get_neighbors(self, griglia, pos, guardie_visibili):
        directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]
        vicini = []

        for dx, dy in directions:
            x, y = pos[0] + dx, pos[1] + dy

            # Controllo confini griglia 20x20 [cite: 29, 122]
            if 0 <= x < 20 and 0 <= y < 20:
                # Deve essere DIVERSO da muro per passare [cite: 34, 123]
                if griglia[x][y] != "muro":

                    # Controllo se c'è una guardia nella cella [cite: 124]
                    occupata_da_guardia = False
                    for gPos in guardie_visibili:
                        if (x, y) == gPos:
                            occupata_da_guardia = True
                            break

                    if not occupata_da_guardia:
                        vicini.append((x, y))
        return vicini

    def heuristic(self, pos, guardie_visibili):
        # Distanza di Manhattan base [cite: 15, 157]
        h = abs(pos[0] - self.endPos[0]) + abs(pos[1] - self.endPos[1])

        # Penalità guardie nel raggio di visione [cite: 15, 43]
        for g_pos in guardie_visibili:
            dist_g = abs(pos[0] - g_pos[0]) + abs(pos[1] - g_pos[1])
            if dist_g <= 3:
                h += (4 - dist_g) * 20
        return h

    def a_star(self, griglia, guardie_visibili):
        start = self.pos
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}  # g(n) [cite: 25, 144]

        while frontier:
            current = heapq.heappop(frontier)[1]
            if current == self.endPos: break

            for next_node in self.get_neighbors(griglia, current, guardie_visibili):
                new_cost = cost_so_far[current] + 1
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    # f(n) = g(n) + h(n) [cite: 15]
                    priority = new_cost + self.heuristic(next_node, guardie_visibili)
                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current
        return came_from

    def pianifica_mossa(self, griglia, guardia_tutte):
        # 1. Filtro guardie visibili (Raggio 3) [cite: 40, 69]
        guardia_visibili = []
        for g in guardia_tutte:
            dist = abs(self.pos[0] - g[0]) + abs(self.pos[1] - g[1])
            if dist <= 3:
                guardia_visibili.append(g)

        # 2. Eseguo A*
        mappa = self.a_star(griglia, guardia_visibili)

        # 3. Controllo se l'obiettivo è raggiungibile
        if self.endPos not in mappa:
            return "WAIT"

        # 4. Ricostruzione percorso (torno indietro) [cite: 82]
        percorso = []
        attuale = self.endPos
        while attuale != self.pos:
            percorso.append(attuale)
            attuale = mappa[attuale]

        # 5. Prendo il primo passo e aggiorno la posizione
        prossima_pos = percorso[-1]
        mossa = self.traduzioneCordinate(self.pos, prossima_pos)

        # IMPORTANTE: self.pos deve restare una coordinata (x, y), non la stringa "NORD"
        self.pos = prossima_pos
        return mossa