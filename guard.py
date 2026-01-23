import math
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class CellType(Enum):
    EMPTY = 0
    WALL = 1
    GUARD = 2
    THIEF = 3


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


class GuardSensor:
    """Gestione sensori delle guardie con raggio di visibilità"""

    def __init__(self, vision_radius: int = 4):
        self.vision_radius = vision_radius

    def can_see_position(self, guard_pos: Position, target_pos: Position,
                         grid: List[List[int]]) -> bool:
        """
        Verifica se una guardia può vedere una posizione target.
        Usa ray-casting per verificare ostacoli tra guardia e target.
        """
        # Controlla se target è nel raggio
        if guard_pos.distance_to(target_pos) > self.vision_radius:
            return False

        # Ray-casting con algoritmo di Bresenham
        return self._line_of_sight(guard_pos, target_pos, grid)

    def _line_of_sight(self, start: Position, end: Position,
                       grid: List[List[int]]) -> bool:
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
            # Se raggiungiamo il target, c'è visibilità
            if x == x1 and y == y1:
                return True

            # Se incontriamo un muro (esclusa posizione di partenza), nessuna visibilità
            if (x != x0 or y != y0) and grid[y][x] == CellType.WALL.value:
                return False

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def get_visible_positions(self, guard_pos: Position,
                              grid: List[List[int]]) -> Set[Position]:
        """Restituisce tutte le posizioni visibili dalla guardia"""
        visible = set()
        height, width = len(grid), len(grid[0])

        # Scansiona area circolare intorno alla guardia
        for dy in range(-self.vision_radius, self.vision_radius + 1):
            for dx in range(-self.vision_radius, self.vision_radius + 1):
                x, y = guard_pos.x + dx, guard_pos.y + dy

                # Verifica bounds
                if 0 <= x < width and 0 <= y < height:
                    target = Position(x, y)
                    if self.can_see_position(guard_pos, target, grid):
                        visible.add(target)

        return visible


class GuardCoordination:
    """Sistema di coordinamento tra le due guardie"""

    def __init__(self):
        self.sensor = GuardSensor(vision_radius=4)

    def share_information(self, state: GameState) -> Tuple[bool, Optional[Position]]:
        """
        Comunicazione perfetta: se almeno una guardia vede il ladro,
        entrambe conoscono la sua posizione.

        Returns:
            (thief_visible, thief_position)
        """
        # Verifica se guardia 1 vede il ladro
        if state.thief_pos:
            g1_sees = self.sensor.can_see_position(
                state.guard1_pos, state.thief_pos, state.grid
            )
            g2_sees = self.sensor.can_see_position(
                state.guard2_pos, state.thief_pos, state.grid
            )

            if g1_sees or g2_sees:
                return True, state.thief_pos

        return False, None

    def calculate_intercept_positions(self, guard1_pos: Position,
                                      guard2_pos: Position,
                                      thief_pos: Position,
                                      grid: List[List[int]]) -> Tuple[Position, Position]:
        """
        Calcola posizioni ottimali per intercettare il ladro.
        Strategia: circondare il ladro da direzioni opposte.
        """
        # Vettore dal ladro al punto medio tra le guardie
        mid_x = (guard1_pos.x + guard2_pos.x) / 2
        mid_y = (guard1_pos.y + guard2_pos.y) / 2

        # Direzione per separare le guardie
        angle = math.atan2(guard2_pos.y - guard1_pos.y,
                           guard2_pos.x - guard1_pos.x)

        # Posizioni target per circondare il ladro
        offset = 2
        target1 = Position(
            int(thief_pos.x + offset * math.cos(angle)),
            int(thief_pos.y + offset * math.sin(angle))
        )
        target2 = Position(
            int(thief_pos.x - offset * math.cos(angle)),
            int(thief_pos.y - offset * math.sin(angle))
        )

        return target1, target2


class MinimaxGuardAI:
    """
    Algoritmo Minimax con potatura Alfa-Beta per le guardie.
    Le guardie cercano di minimizzare la distanza dal ladro (catturarlo).
    """

    def __init__(self, max_depth: int = 4):
        self.max_depth = max_depth
        self.coordination = GuardCoordination()
        self.nodes_explored = 0
        self.nodes_pruned = 0

    def get_best_moves(self, state: GameState) -> Tuple[Position, Position]:
        """
        Calcola le mosse ottimali per entrambe le guardie.

        Returns:
            (guard1_next_pos, guard2_next_pos)
        """
        self.nodes_explored = 0
        self.nodes_pruned = 0

        # Aggiorna informazioni condivise
        thief_visible, thief_pos = self.coordination.share_information(state)
        state.thief_visible = thief_visible
        if thief_pos:
            state.thief_pos = thief_pos

        # Esegui minimax con alfa-beta
        _, best_move = self.minimax(
            state,
            depth=0,
            alpha=-math.inf,
            beta=math.inf,
            maximizing=False  # False perché le guardie minimizzano
        )

        return best_move

    def minimax(self, state: GameState, depth: int,
                alpha: float, beta: float,
                maximizing: bool) -> Tuple[float, Optional[Tuple[Position, Position]]]:
        """
        Algoritmo Minimax con potatura Alfa-Beta.

        Args:
            state: stato corrente del gioco
            depth: profondità corrente
            alpha: valore alfa per potatura
            beta: valore beta per potatura
            maximizing: True se turno del ladro (max), False se turno guardie (min)
        """
        self.nodes_explored += 1

        # Condizioni terminali
        if depth >= self.max_depth:
            return self.evaluate_state(state), None

        if self.is_terminal_state(state):
            return self.evaluate_state(state), None

        if maximizing:
            # Turno del ladro (massimizzare distanza dalle guardie)
            # In questo caso semplificato, assumiamo mosse casuali del ladro
            return self.evaluate_state(state), None
        else:
            # Turno delle guardie (minimizzare distanza dal ladro)
            min_eval = math.inf
            best_move = None

            # Genera tutte le possibili combinazioni di mosse delle guardie
            for g1_move, g2_move in self.generate_guard_moves(state):
                new_state = self.apply_guard_moves(state, g1_move, g2_move)

                # Ricorsione (assumendo risposta del ladro)
                eval_score, _ = self.minimax(
                    new_state, depth + 1, alpha, beta, True
                )

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (g1_move, g2_move)

                # Potatura Beta
                beta = min(beta, eval_score)
                if beta <= alpha:
                    self.nodes_pruned += 1
                    break  # Potatura alfa

            return min_eval, best_move

    def evaluate_state(self, state: GameState) -> float:
        """
        Funzione euristica per valutare lo stato.
        Valori più bassi = migliore per le guardie.
        """
        if not state.thief_pos:
            # Se non vediamo il ladro, valore neutro
            return 0.0

        # Distanza minima guardia-ladro
        d1 = state.guard1_pos.distance_to(state.thief_pos)
        d2 = state.guard2_pos.distance_to(state.thief_pos)
        min_distance = min(d1, d2)

        # Cattura = valore ottimale
        if min_distance <= 1:
            return -1000.0

        # Fattore di coordinamento: meglio se le guardie accerchiano
        angle_diff = self._calculate_encirclement_angle(state)
        coordination_bonus = abs(angle_diff - math.pi) / math.pi * 10

        # Score finale
        score = min_distance - coordination_bonus

        return score

    def _calculate_encirclement_angle(self, state: GameState) -> float:
        """Calcola angolo tra le due guardie rispetto al ladro"""
        if not state.thief_pos:
            return 0.0

        # Vettori dal ladro alle guardie
        v1_x = state.guard1_pos.x - state.thief_pos.x
        v1_y = state.guard1_pos.y - state.thief_pos.y
        v2_x = state.guard2_pos.x - state.thief_pos.x
        v2_y = state.guard2_pos.y - state.thief_pos.y

        # Prodotto scalare e angolo
        dot = v1_x * v2_x + v1_y * v2_y
        mag1 = math.sqrt(v1_x ** 2 + v1_y ** 2)
        mag2 = math.sqrt(v2_x ** 2 + v2_y ** 2)

        if mag1 == 0 or mag2 == 0:
            return 0.0

        cos_angle = dot / (mag1 * mag2)
        cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp

        return math.acos(cos_angle)

    def is_terminal_state(self, state: GameState) -> bool:
        """Verifica se lo stato è terminale (cattura)"""
        if not state.thief_pos:
            return False

        d1 = state.guard1_pos.manhattan_distance_to(state.thief_pos)
        d2 = state.guard2_pos.manhattan_distance_to(state.thief_pos)

        return d1 <= 1 or d2 <= 1

    def generate_guard_moves(self, state: GameState) -> List[Tuple[Position, Position]]:
        """Genera tutte le mosse valide per entrambe le guardie"""
        moves = []
        g1_moves = self._get_valid_moves(state.guard1_pos, state.grid, state.guard2_pos)
        g2_moves = self._get_valid_moves(state.guard2_pos, state.grid, state.guard1_pos)

        # Combinazioni di mosse
        for g1_move in g1_moves:
            for g2_move in g2_moves:
                # Le guardie non possono occupare la stessa casella
                if g1_move != g2_move:
                    moves.append((g1_move, g2_move))

        return moves

    def _get_valid_moves(self, pos: Position, grid: List[List[int]], other_guard_pos: Position) -> List[Position]:
        moves = [pos]  # L'azione "stai fermo" è sempre valida
        # Direzioni: Su, Giù, Destra, Sinistra
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x, new_y = pos.x + dx, pos.y + dy

            # --- QUESTA È LA RIGA DA SOSTITUIRE ---
            if 0 <= new_x < 20 and 0 <= new_y < 20 and grid[new_y][new_x] != 1:
                new_pos = Position(new_x, new_y)
                # Evita che le guardie si sovrappongano tra loro
                if new_pos != other_guard_pos:
                    moves.append(new_pos)

        return moves

    def apply_guard_moves(self, state: GameState,
                          g1_move: Position, g2_move: Position) -> GameState:
        """Applica le mosse delle guardie e restituisce nuovo stato"""
        new_state = state.copy()
        new_state.guard1_pos = g1_move
        new_state.guard2_pos = g2_move

        # Aggiorna visibilità
        new_state.thief_visible, new_state.thief_pos = \
            self.coordination.share_information(new_state)

        return new_state