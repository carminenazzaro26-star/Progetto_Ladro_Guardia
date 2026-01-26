import heapq
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Position:
    x: int
    y: int

    def __hash__(self): return hash((self.x, self.y))

    def __eq__(self, other): return isinstance(other, Position) and self.x == other.x and self.y == other.y

    def manhattan_distance_to(self, other: 'Position') -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)


@dataclass
class GameState:
    grid: List[List[int]]
    guard1_pos: Position
    guard2_pos: Position
    thief_pos: Optional[Position]
    thief_visible: bool


class GuardAgent:
    def __init__(self, guard_id, startPos):
        self.guard_id = guard_id
        self.pos = startPos
        self.vision_radius = 6  # Aumentato leggermente per rendere le guardie più efficaci
        self.last_known_thief_pos = None
        self.last_patrol_target = None

    def _line_of_sight(self, start, end, grid):
        x0, y0 = start.x, start.y
        x1, y1 = end.x, end.y
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx - dy
        x, y = x0, y0
        while True:
            if x == x1 and y == y1: return True
            # Correzione: grid[y][x] perché la griglia è [row][col]
            if (x != x0 or y != y0) and grid[y][x] == 1: return False
            e2 = 2 * err
            if e2 > -dy: err -= dy; x += sx
            if e2 < dx: err += dx; y += sy

    def detect_thief(self, thief_pos, grid):
        if thief_pos and self.pos.manhattan_distance_to(thief_pos) <= self.vision_radius:
            if self._line_of_sight(self.pos, thief_pos, grid):
                self.last_known_thief_pos = thief_pos
                return True
        return False

    def get_neighbors(self, grid, pos, other_guard_pos):
        neighbors = []
        # Invertito height/width per coerenza con grid[y][x]
        height = len(grid)
        width = len(grid[0])
        for dx, dy in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
            nx, ny = pos.x + dx, pos.y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if grid[ny][nx] != 1:
                    # Permettiamo di pianificare sulla posizione dell'altra guardia
                    # ma con un costo alto, altrimenti A* fallisce se non ha altre strade
                    neighbors.append(Position(nx, ny))
        return neighbors

    def a_star(self, grid, target_pos, other_guard_pos):
        start = self.pos
        frontier = []
        heapq.heappush(frontier, (0, 0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        counter = 0

        while frontier:
            _, _, current = heapq.heappop(frontier)
            if current == target_pos: break

            for next_node in self.get_neighbors(grid, current, other_guard_pos):
                # Penalità se la cella è occupata dall'altra guardia
                move_cost = 10 if next_node == other_guard_pos else 1
                new_cost = cost_so_far[current] + move_cost

                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + next_node.manhattan_distance_to(target_pos)
                    counter += 1
                    heapq.heappush(frontier, (priority, counter, next_node))
                    came_from[next_node] = current
        return came_from

    def get_patrol_target(self, grid):
        points = [Position(2, 2), Position(17, 2), Position(2, 17), Position(10, 10), Position(17, 17)]
        # Sceglie un punto lontano dalla posizione attuale ma non quello già visitato
        valid_points = [p for p in points if grid[p.y][p.x] != 1 and p != self.last_patrol_target]
        if not valid_points: return Position(10, 10)
        import random
        target = random.choice(valid_points)
        self.last_patrol_target = target
        return target

    def get_next_move(self, grid, thief_pos, other_guard_pos, thief_visible):
        # 1. Determinazione Target
        if thief_visible and thief_pos:
            target_pos = thief_pos
        elif self.last_known_thief_pos:
            target_pos = self.last_known_thief_pos
            if self.pos == target_pos: self.last_known_thief_pos = None  # Raggiunto l'ultimo avvistamento
        else:
            if self.last_patrol_target is None or self.pos == self.last_patrol_target:
                target_pos = self.get_patrol_target(grid)
            else:
                target_pos = self.last_patrol_target

        # 2. Calcolo Percorso
        came_from = self.a_star(grid, target_pos, other_guard_pos)
        if target_pos not in came_from: return self.pos

        path = []
        curr = target_pos
        while curr != self.pos:
            path.append(curr)
            curr = came_from[curr]

        if not path: return self.pos
        next_step = path[-1]

        # Evita collisione fisica immediata
        if next_step == other_guard_pos:
            return self.pos
        return next_step


class MinimaxGuardAI:
    def __init__(self, max_depth: int = 2):
        self.guard1_agent = None
        self.guard2_agent = None

    def get_best_moves(self, state: GameState) -> Tuple[Position, Position]:
        if self.guard1_agent is None:
            self.guard1_agent = GuardAgent(1, state.guard1_pos)
            self.guard2_agent = GuardAgent(2, state.guard2_pos)

        self.guard1_agent.pos = state.guard1_pos
        self.guard2_agent.pos = state.guard2_pos

        g1_sees = self.guard1_agent.detect_thief(state.thief_pos, state.grid)
        g2_sees = self.guard2_agent.detect_thief(state.thief_pos, state.grid)

        # Sincronizzazione memoria
        if g1_sees or g2_sees:
            self.guard1_agent.last_known_thief_pos = state.thief_pos
            self.guard2_agent.last_known_thief_pos = state.thief_pos

        m1 = self.guard1_agent.get_next_move(state.grid, state.thief_pos, state.guard2_pos, g1_sees or g2_sees)
        # Passiamo la mossa appena calcolata di m1 per evitare che m2 ci vada sopra
        m2 = self.guard2_agent.get_next_move(state.grid, state.thief_pos, m1, g1_sees or g2_sees)

        return m1, m2