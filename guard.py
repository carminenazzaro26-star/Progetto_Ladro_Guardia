import heapq
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Position:
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def distance_to(self, other: 'Position') -> float:
        """Distanza euclidea"""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def manhattan_distance_to(self, other: 'Position') -> int:
        """Distanza Manhattan"""
        return abs(self.x - other.x) + abs(self.y - other.y)


@dataclass
class GameState:
    grid: List[List[int]]
    guard1_pos: Position
    guard2_pos: Position
    thief_pos: Optional[Position]
    thief_visible: bool

    def copy(self) -> 'GameState':
        return GameState(
            grid=[row[:] for row in self.grid],
            guard1_pos=Position(self.guard1_pos.x, self.guard1_pos.y),
            guard2_pos=Position(self.guard2_pos.x, self.guard2_pos.y),
            thief_pos=Position(self.thief_pos.x, self.thief_pos.y) if self.thief_pos else None,
            thief_visible=self.thief_visible
        )


class GuardAgent:
    """Agente singola guardia con A* e visione"""

    def __init__(self, guard_id, startPos):
        self.guard_id = guard_id
        self.pos = startPos
        self.vision_radius = 4
        self.last_known_thief_pos = None
        self.last_patrol_target = None  # Ricorda l'ultimo punto visitato

    def can_see_position(self, target_pos, grid):
        """Verifica se la guardia può vedere una posizione target"""
        if self.pos.manhattan_distance_to(target_pos) > self.vision_radius:
            return False
        return self._line_of_sight(self.pos, target_pos, grid)

    def _line_of_sight(self, start, end, grid):
        """Algoritmo di Bresenham per verificare linea di vista"""
        x0, y0 = start.x, start.y
        x1, y1 = end.x, end.y

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0

        while True:
            if x == x1 and y == y1:
                return True
            if (x != x0 or y != y0) and grid[y][x] == 1:
                return False

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def detect_thief(self, thief_pos, grid):
        """Rileva se il ladro è visibile"""
        if thief_pos and self.can_see_position(thief_pos, grid):
            self.last_known_thief_pos = thief_pos
            return True
        return False

    def get_neighbors(self, grid, pos, other_guard_pos):
        """Restituisce le celle vicine valide"""
        neighbors = []
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0

        for dx, dy in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
            new_pos = Position(pos.x + dx, pos.y + dy)

            if 0 <= new_pos.x < width and 0 <= new_pos.y < height:
                if grid[new_pos.y][new_pos.x] != 1 and new_pos != other_guard_pos:
                    neighbors.append(new_pos)
        return neighbors

    def heuristic(self, pos, target_pos, other_guard_pos):
        """Euristica per A*"""
        h = pos.manhattan_distance_to(target_pos)

        if other_guard_pos:
            angle_score = self._calculate_encirclement_bonus(pos, other_guard_pos, target_pos)
            h -= angle_score * 2

        return h

    def _calculate_encirclement_bonus(self, my_pos, other_guard_pos, target_pos):
        """Calcola bonus per circondare il target"""
        v1_x = my_pos.x - target_pos.x
        v1_y = my_pos.y - target_pos.y
        v2_x = other_guard_pos.x - target_pos.x
        v2_y = other_guard_pos.y - target_pos.y

        dot = v1_x * v2_x + v1_y * v2_y
        mag1 = math.sqrt(v1_x ** 2 + v1_y ** 2)
        mag2 = math.sqrt(v2_x ** 2 + v2_y ** 2)

        if mag1 == 0 or mag2 == 0:
            return 0.0

        cos_angle = dot / (mag1 * mag2)
        cos_angle = max(-1.0, min(1.0, cos_angle))

        return (1.0 - cos_angle) / 2.0

    def a_star(self, grid, target_pos, other_guard_pos):
        """Algoritmo A* per trovare il percorso"""
        start = self.pos
        frontier = []
        counter = 0  # Contatore per evitare confronti tra Position
        heapq.heappush(frontier, (0, counter, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            current = heapq.heappop(frontier)[2]  # Prendi il terzo elemento (Position)

            if current == target_pos:
                break

            for next_node in self.get_neighbors(grid, current, other_guard_pos):
                new_cost = cost_so_far[current] + 1

                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + self.heuristic(next_node, target_pos, other_guard_pos)
                    counter += 1  # Incrementa il contatore
                    heapq.heappush(frontier, (priority, counter, next_node))
                    came_from[next_node] = current

        return came_from

    def get_patrol_target(self, grid):
        """Genera obiettivo di pattugliamento, evitando l'ultimo visitato"""
        strategic_points = [
            Position(5, 5), Position(15, 5), Position(5, 15), Position(15, 15),
            Position(10, 10),
            Position(10, 5), Position(10, 15), Position(5, 10), Position(15, 10)
        ]

        best_target = None
        max_distance = 0

        for point in strategic_points:
            # Salta se è lo stesso punto dell'ultima volta (controlla prima se non è None)
            if self.last_patrol_target is not None and point == self.last_patrol_target:
                continue

            if grid[point.y][point.x] != 1:
                dist = self.pos.manhattan_distance_to(point)
                if dist > max_distance:
                    max_distance = dist
                    best_target = point

        # Se non trova nessun punto (tutti bloccati o solo l'ultimo disponibile)
        # allora usa l'ultimo come fallback
        if best_target is None:
            for point in strategic_points:
                if grid[point.y][point.x] != 1:
                    best_target = point
                    break

        # Se ancora non trova niente, usa il centro
        if best_target is None:
            best_target = Position(10, 10)

        # Aggiorna l'ultimo target visitato
        self.last_patrol_target = best_target
        return best_target

    def get_next_move(self, grid, thief_pos, other_guard_pos, thief_visible):
        """Calcola la prossima mossa della guardia"""
        # Decidi il target
        if thief_pos and self.detect_thief(thief_pos, grid):
            target_pos = thief_pos
        elif thief_visible and self.last_known_thief_pos:
            target_pos = thief_pos if thief_pos else self.last_known_thief_pos
        elif self.last_known_thief_pos:
            target_pos = self.last_known_thief_pos
        else:
            target_pos = self.get_patrol_target(grid)

        # Se sei già sul target e non vedi il ladro, nuovo target
        if self.pos == target_pos and not thief_visible:
            target_pos = self.get_patrol_target(grid)

        # Usa A* per trovare il percorso
        came_from = self.a_star(grid, target_pos, other_guard_pos)

        # Controlla se il target è raggiungibile
        if target_pos not in came_from:
            return self.pos  # Resta fermo

        # Ricostruisci percorso
        path = []
        current = target_pos
        while current != self.pos:
            path.append(current)
            if came_from[current] is None:
                break
            current = came_from[current]

        if not path:
            return self.pos  # Resta fermo

        # Ritorna la prossima posizione
        return path[-1]


class MinimaxGuardAI:
    """
    Classe principale per gestire le guardie.
    Mantiene l'interfaccia compatibile con il main.py originale.
    """

    def __init__(self, max_depth: int = 2):
        self.max_depth = max_depth
        self.guard1_agent = None
        self.guard2_agent = None

    def get_best_moves(self, state: GameState) -> Tuple[Position, Position]:
        """
        Calcola le mosse ottimali per entrambe le guardie.
        Questa funzione è chiamata dal main.py.

        Returns:
            (guard1_next_pos, guard2_next_pos)
        """
        # Inizializza gli agenti se non esistono
        if self.guard1_agent is None:
            self.guard1_agent = GuardAgent(1, state.guard1_pos)
        if self.guard2_agent is None:
            self.guard2_agent = GuardAgent(2, state.guard2_pos)

        # Aggiorna le posizioni correnti
        self.guard1_agent.pos = state.guard1_pos
        self.guard2_agent.pos = state.guard2_pos

        # Verifica chi vede il ladro
        g1_sees = self.guard1_agent.detect_thief(state.thief_pos, state.grid) if state.thief_pos else False
        g2_sees = self.guard2_agent.detect_thief(state.thief_pos, state.grid) if state.thief_pos else False
        thief_visible = g1_sees or g2_sees

        # Condividi informazioni tra le guardie
        if g1_sees:
            self.guard2_agent.last_known_thief_pos = state.thief_pos
        if g2_sees:
            self.guard1_agent.last_known_thief_pos = state.thief_pos

        # Calcola le mosse
        guard1_next = self.guard1_agent.get_next_move(
            state.grid, state.thief_pos, state.guard2_pos, thief_visible
        )
        guard2_next = self.guard2_agent.get_next_move(
            state.grid, state.thief_pos, state.guard1_pos, thief_visible
        )

        return guard1_next, guard2_next