import random
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def manhattan(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)


class RandomGuardAI:
    """Guardia che si muove completamente a caso"""

    def __init__(self):
        self.moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]

    def get_best_moves(self, state):
        # Sceglie una mossa a caso valida per G1
        g1_moves = self._get_valid_moves(state.grid, state.g1)
        next_g1 = random.choice(g1_moves) if g1_moves else state.g1

        # Sceglie una mossa a caso valida per G2
        g2_moves = self._get_valid_moves(state.grid, state.g2)
        next_g2 = random.choice(g2_moves) if g2_moves else state.g2

        return next_g1, next_g2

    def _get_valid_moves(self, grid, pos):
        valid = []
        for dx, dy in self.moves:
            nx, ny = pos.x + dx, pos.y + dy
            if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] != 1:
                valid.append(Position(nx, ny))
        return valid


class GreedyGuardAI:
    """Guardia che insegue il ladro se lo vede, altrimenti va a caso"""

    def __init__(self):
        self.moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]

    def get_best_moves(self, state):
        # Calcola mossa per G1
        next_g1 = self._greedy_move(state.grid, state.g1, state.robber)
        # Calcola mossa per G2
        next_g2 = self._greedy_move(state.grid, state.g2, state.robber)
        return next_g1, next_g2

    def _greedy_move(self, grid, pos, target):
        valid_moves = []
        for dx, dy in self.moves:
            nx, ny = pos.x + dx, pos.y + dy
            if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] != 1:
                valid_moves.append(Position(nx, ny))

        if not valid_moves: return pos

        # Se vedo il ladro (target non è None), scelgo la mossa che riduce la distanza
        if target:
            # Ordina le mosse per distanza crescente dal ladro
            valid_moves.sort(key=lambda p: p.manhattan(target))
            return valid_moves[0]  # La prima è la più vicina
        else:
            # Se non vedo il ladro, muovo a caso
            return random.choice(valid_moves)