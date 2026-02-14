import heapq


class RobberAgent:
    def __init__(self, startPos, endPos, grid_size=20):
        self.pos = startPos
        self.endPos = endPos
        self.grid_size = grid_size  # Nuova variabile per la dimensione
        self.vision_radius = 3
        self.storico_mosse = []
        # La heat_map ora si adatta alla dimensione della griglia
        self.heat_map = [[0 for _ in range(grid_size)] for _ in range(grid_size)]

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
        for dx, dy in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
            x, y = pos[0] + dx, pos[1] + dy

            # Usa self.grid_size invece di 20
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                if grid[y][x] != 1 and (x, y) not in visible_guards:
                    neighbors.append((x, y))
        return neighbors

    def heuristic(self, pos, guardie_visibili):
        h = abs(pos[0] - self.endPos[0]) + abs(pos[1] - self.endPos[1])

        if pos in self.storico_mosse:
            h += 100
        if self.heat_map[pos[0]][pos[1]] > 0:
            h += self.heat_map[pos[0]][pos[1]] * 5

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
        cost_so_far = {start: 0}

        while frontier:
            current = heapq.heappop(frontier)[1]
            if current == self.endPos: break

            for next_node in self.get_neighbors(griglia, current, guardie_visibili):
                new_cost = cost_so_far[current] + 1
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + self.heuristic(next_node, guardie_visibili)
                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current
        return came_from

    def pianifica_mossa(self, griglia, guardia_tutte):
        guardia_visibili = []
        for g in guardia_tutte:
            dist = abs(self.pos[0] - g[0]) + abs(self.pos[1] - g[1])
            if dist <= 3:
                guardia_visibili.append(g)

        mappa = self.a_star(griglia, guardia_visibili)

        if self.endPos not in mappa:
            return "WAIT"

        percorso = []
        attuale = self.endPos
        while attuale != self.pos:
            percorso.append(attuale)
            attuale = mappa[attuale]

        prossima_pos = percorso[-1]
        mossa = self.traduzioneCordinate(self.pos, prossima_pos)

        if len(self.storico_mosse) > 2:
            self.storico_mosse.pop(0)

        self.storico_mosse.append(prossima_pos)
        self.heat_map[prossima_pos[1]][prossima_pos[0]] += 1
        self.pos = prossima_pos
        return mossa