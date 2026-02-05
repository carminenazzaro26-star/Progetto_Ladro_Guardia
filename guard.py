import random
from dataclasses import dataclass
from typing import List, Tuple, Optional
import game_state

@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def manhattan(self, other: "Position") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __repr__(self):
        return f"({self.x},{self.y})"


# 2. DEFINISCI POI GAMESTATE
class GameState:
    def __init__(self, grid, g1, g2, robber, prev_g1=None, prev_g2=None):
        self.grid = grid
        self.g1 = g1
        self.g2 = g2
        self.robber = robber
        self.prev_g1 = prev_g1
        self.prev_g2 = prev_g2


# 3. INFINE DEFINISCI LA CLASSE AI
class MinimaxGuardAI:
    def __init__(self, max_depth=2, visual_range = 5):
        self.max_depth = max_depth
        self.visual_range = visual_range
        self.moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]
        self.last_known_pos = None

    def can_see(self, grid, g1, robber_pos):
        if self.visual_range >= g1.manhattan(robber_pos) :
            return True
        else:
            return g1.manhattan(robber_pos) <= self.visual_range

    def has_line_of_sight(self, grid, start: Position, end: Position):
        curr_x, curr_y = start.x, start.y
        target_x, target_y = end.x, end.y

        dx = 1 if target_x > curr_x else -1 if target_x < curr_x else 0
        dy = 1 if target_y > curr_y else -1 if target_y < curr_y else 0

        temp_x, temp_y = curr_x, curr_y
        while (temp_x != target_x or temp_y != target_y):
            if temp_x != target_x:
                temp_x += dx
            if temp_y != target_y:
                temp_y += dy

            # Controllo se la cella corrente è un muro
            if grid[temp_y][temp_x] == 1:
                return False
        return True



    def valid(self, grid, x, y):
        return 0 <= x < len(grid[0]) and 0 <= y < len(grid) and grid[y][x] != 1

    def get_moves(self, grid, pos, other_pos=None):
        res = []
        for dx, dy in self.moves:
            nx, ny = pos.x + dx, pos.y + dy
            if self.valid(grid, nx, ny):
                new_pos = Position(nx, ny)
                if other_pos is None or new_pos != other_pos:
                    res.append(new_pos)
        random.shuffle(res)
        return res

    def evaluate(self, state: GameState):
        if state.robber is None: return 100000.0

        d1 = state.g1.manhattan(state.robber)
        d2 = state.g2.manhattan(state.robber)

        if d1 == 0 or d2 == 0: return 80000.0

        # Punteggio vicinanza
        score = -(d1 + d2) * 50 - (min(d1, d2) * 100)

        # Bonus Accerchiamento
        dx1, dx2 = state.g1.x - state.robber.x, state.g2.x - state.robber.x
        dy1, dy2 = state.g1.y - state.robber.y, state.g2.y - state.robber.y
        if (dx1 * dx2 < 0) or (dy1 * dy2 < 0):
            score += 1000

            # Anti-oscillazione
        if state.prev_g1 and state.g1 == state.prev_g1: score -= 2000
        if state.prev_g2 and state.g2 == state.prev_g2: score -= 2000

        # Distanziamento guardie
        if state.g1.manhattan(state.g2) < 2:
            score -= 1500

        return float(score)

    def minimax(self, state, depth, maximizing, alpha, beta):
        if depth == 0 or state.robber is None:
            return self.evaluate(state)

        if maximizing:
            best = -float("inf")
            for g1 in self.get_moves(state.grid, state.g1, state.g2):
                for g2 in self.get_moves(state.grid, state.g2, g1):
                    new_state = GameState(state.grid, g1, g2, state.robber, state.g1, state.g2)
                    val = self.minimax(new_state, depth - 1, False, alpha, beta)
                    best = max(best, val)
                    alpha = max(alpha, val)
                    if beta <= alpha: break
                if beta <= alpha: break
            return best
        else:
            best = float("inf")
            for r_pos in self.get_moves(state.grid, state.robber):
                new_state = GameState(state.grid, state.g1, state.g2, r_pos, state.prev_g1, state.prev_g2)
                val = self.minimax(new_state, depth - 1, True, alpha, beta)
                best = min(best, val)
                beta = min(beta, val)
                if beta <= alpha: break
            return best

    def _muoviti_a_caso(self, state):
        # Prende mosse casuali per G1 e G2
        m1 = self.get_moves(state.grid, state.g1, state.g2)
        new_g1 = random.choice(m1) if m1 else state.g1
        m2 = self.get_moves(state.grid, state.g2, new_g1)
        new_g2 = random.choice(m2) if m2 else state.g2
        return new_g1, new_g2


    def get_best_moves(self, state: GameState):
        visible = self.can_see(state.grid, state.g1, state.robber) or self.can_see(state.grid, state.g2, state.robber)
        if visible: #ho aggiornato la posizione del ladro in memoria, avvio il minimax normale e il ladro si attiva per scappare
            self.last_known_pos = state.robber
            target_robber = state.robber
            is_chasing_ghost = False
        elif self.last_known_pos is not None:
            if state.g1 == self.last_known_pos or state.g2 == self.last_known_pos:
                self.last_known_pos = None
                return self._muoviti_a_caso(state)
            target_robber = self.last_known_pos
            is_chasing_ghost = True
        else:
            return self._muoviti_a_caso(state)
        best_value = -float("inf")
        best_g1, best_g2 = state.g1, state.g2
        alpha, beta = -float("inf"), float("inf")

        m1_list = self.get_moves(state.grid, state.g1, state.g2)
        for g1 in m1_list:
            m2_list = self.get_moves(state.grid, state.g2, g1)
            for g2 in m2_list:
                # Creo lo stato usando target_robber invece di state.robber reale
                temp_state = GameState(state.grid, g1, g2, target_robber, state.g1, state.g2)

                # Se stiamo inseguendo una memoria, il ladro NON deve muoversi nel minimax
                # quindi ho messo depth=0 per valutare solo la posizione attuale
                attuale_depth = self.max_depth - 1 if not is_chasing_ghost else 0

                val = self.minimax(temp_state, attuale_depth, False, alpha, beta)
                if val > best_value:
                    best_value = val
                    best_g1, best_g2 = g1, g2
                alpha = max(alpha, best_value)

        return best_g1, best_g2