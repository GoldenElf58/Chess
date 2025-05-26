import threading
import time
from collections import Counter
from itertools import count
from typing import Callable

import numpy as np

from game import GameState
from utils import mirror, negate
from bot import Bot

piece_values: dict[int, int] = {-6: -9999999,
                                -5: -900,
                                -4: -500,
                                -3: -320,
                                -2: -300,
                                -1: -100,
                                0: 0,
                                1: 100,
                                2: 300,
                                3: 320,
                                4: 500,
                                5: 900,
                                6: 9999999
                                }

# Provided piece-square tables for the opening/middlegame

Pawns_flat: tuple[int, ...] = (
    0, 0, 0, 0, 0, 0, 0, 0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5, 5, 10, 25, 25, 10, 5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, -5, -10, 0, 0, -10, -5, 5,
    5, 10, 10, -20, -20, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
)

PawnsEnd_flat: tuple[int, ...] = (
    0, 0, 0, 0, 0, 0, 0, 0,
    80, 80, 80, 80, 80, 80, 80, 80,
    50, 50, 50, 50, 50, 50, 50, 50,
    30, 30, 30, 30, 30, 30, 30, 30,
    20, 20, 20, 20, 20, 20, 20, 20,
    10, 10, 10, 10, 10, 10, 10, 10,
    10, 10, 10, 10, 10, 10, 10, 10,
    0, 0, 0, 0, 0, 0, 0, 0
)

Rooks_flat: tuple[int, ...] = (
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, 10, 10, 10, 10, 5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    0, 0, 0, 5, 5, 0, 0, 0
)

Knights_flat: tuple[int, ...] = (
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
)

Bishops_flat: tuple[int, ...] = (
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
)

Queens_flat: tuple[int, ...] = (
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
)

KingStart_flat: tuple[int, ...] = (
    -80, -70, -70, -70, -70, -70, -70, -80,
    -60, -60, -60, -60, -60, -60, -60, -60,
    -40, -50, -50, -60, -60, -50, -50, -40,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20, -5, -5, -5, -5, 20, 20,
    20, 30, 10, 0, 0, 10, 30, 20
)

KingEnd_flat: tuple[int, ...] = (
    -20, -10, -10, -10, -10, -10, -10, -20,
    -5, 0, 5, 5, 5, 5, 0, -5,
    -10, -5, 20, 30, 30, 20, -5, -10,
    -15, -10, 35, 45, 45, 35, -10, -15,
    -20, -15, 30, 40, 40, 30, -15, -20,
    -25, -20, 20, 25, 25, 20, -20, -25,
    -30, -25, 0, 0, 0, 0, -25, -30,
    -50, -30, -30, -30, -30, -30, -30, -50
)

# Map piece type to its piece-square table.
# (Assuming that in your piece_values dictionary:
#   Pawn   -> ±1, Knight -> ±2, Bishop -> ±3,
#   Rook   -> ±4, Queen  -> ±5, King   -> ±6)
position_values_start: dict[int, tuple[int, ...]] = {
    # White pieces (positive values)
    1: Pawns_flat,
    2: Knights_flat,
    3: Bishops_flat,
    4: Rooks_flat,
    5: Queens_flat,
    6: KingStart_flat,
    # Black pieces (negative values) use the mirrored tables
    -1: negate(mirror(Pawns_flat)),
    -2: negate(mirror(Knights_flat)),
    -3: negate(mirror(Bishops_flat)),
    -4: negate(mirror(Rooks_flat)),
    -5: negate(mirror(Queens_flat)),
    -6: negate(mirror(KingStart_flat))
}

position_values_end: dict[int, tuple[int, ...]] = {
    # White pieces (positive values)
    1: PawnsEnd_flat,
    2: Knights_flat,
    3: Bishops_flat,
    4: Rooks_flat,
    5: Queens_flat,
    6: KingEnd_flat,
    # Black pieces (negative values) use the mirrored tables
    -1: negate(mirror(PawnsEnd_flat)),
    -2: negate(mirror(Knights_flat)),
    -3: negate(mirror(Bishops_flat)),
    -4: negate(mirror(Rooks_flat)),
    -5: negate(mirror(Queens_flat)),
    -6: negate(mirror(KingEnd_flat))
}

# Precompute combined piece and position tables for faster evaluation
combined_tables_start: list[tuple[int, ...]] = [() for _ in range(13)]
combined_tables_end: list[tuple[int, ...]] = [() for _ in range(13)]


def populate_combined_tables():
    global combined_tables_start
    global combined_tables_end
    for piece, base_val in piece_values.items():
        if piece == 0:
            continue
        pos_vals = position_values_start[piece]
        combined_tables_start[piece + 6] = tuple(base_val + pos_vals[i] for i in range(len(pos_vals)))
        pos_vals = position_values_end[piece]
        combined_tables_end[piece + 6] = tuple(base_val + pos_vals[i] for i in range(len(pos_vals)))


populate_combined_tables()


class Botv3_3(Bot):
    def __init__(self, transposition_table: dict | None = None, eval_lookup: dict | None = None) -> None:
        self.transposition_table: dict[
            int, tuple[int, tuple[int, int, int, int]]] = transposition_table if transposition_table is not None else {}
        self.eval_lookup: dict[int, int] = eval_lookup if eval_lookup is not None else {}

    def generate_move(self, game_state: GameState, allotted_time: float = 3.0, depth: int = -1) -> tuple[
        tuple[int, tuple[int, int, int, int]], int]:
        return self.iterative_deepening(game_state, game_state.color == 1, allotted_time=allotted_time, depth=depth)

    def clear_cache(self) -> None:
        self.transposition_table = {}
        self.eval_lookup = {}

    def evaluate(self, game_state: GameState) -> int:
        if game_state.winner is not None:
            return game_state.winner * 9999999
        hash_state: int = game_state.get_hashed()
        if (cached_eval := self.eval_lookup.get(hash_state)) is not None:
            return cached_eval
        board: tuple[int, ...] = game_state.board
        combined: list[tuple[int, ...]] = combined_tables_end if np.count_nonzero(
            board not in [0, -1, 1, -6, 6]) < 3 else combined_tables_start
        self.eval_lookup[hash_state] = (evaluation := sum([combined[piece + 6][i] for (i, piece) in enumerate(board) if piece]))
        return evaluation

    def iterative_deepening(self, game_state: GameState, maximizing_player: bool, allotted_time: float = 3.0,
                            depth: int = -1) -> tuple[tuple[int, tuple[int, int, int, int]], int]:
        if depth >= 0:
            result: tuple[int, tuple[int, int, int, int]] = (0, game_state.get_moves()[0])
            for i in range(min(depth, 2), depth + 1):
                result = self.minimax(game_state, i, -(1 << 31), (1 << 31), maximizing_player)
            return result, depth
        t0: float = time.time()
        results: list[tuple[int, tuple[int, int, int, int]]] = [(0, game_state.get_moves()[0])]
        depth = 2
        minimax_thread: threading.Thread = threading.Thread(
            target=lambda: results.append(self.minimax(game_state, depth, -(1 << 31), (1 << 31), maximizing_player)))
        minimax_thread.start()
        while time.time() - t0 < allotted_time:
            depth += 1
            minimax_thread.join(allotted_time - (time.time() - t0))
            minimax_thread = threading.Thread(
                target=lambda: results.append(
                    self.minimax(game_state, depth, -(1 << 31), (1 << 31), maximizing_player)))
            if time.time() - t0 < allotted_time: minimax_thread.start()
        if minimax_thread.is_alive():
            minimax_thread.join(0)
        return results[-1], (len(results) if len(results) != 1 else 0)

    def minimax(self, game_state: GameState, depth: int, alpha: int, beta: int, maximizing_player: bool,
                first_call: bool = True) -> tuple[int, tuple[int, int, int, int]]:
        if game_state.get_winner() is not None:
            return self.evaluate(game_state), game_state.last_move
        state_key: int = hash((game_state.board, game_state.white_queen, game_state.white_king,
                               game_state.black_queen, game_state.black_king, depth, maximizing_player))
        transposition_table: dict[int, tuple[int, tuple[int, int, int, int]]] = self.transposition_table
        if (cached := transposition_table.get(state_key)) is not None:
            return cached
        moves: tuple[tuple[int, int, int, int], ...] = tuple(game_state.get_moves() if first_call else
                                                             game_state.get_moves_no_check())
        move_fn: Callable[[tuple[int, int, int, int]], GameState] = game_state.move
        eval_fn: Callable[[GameState], int] = self.evaluate
        child_data: list[tuple[tuple[int, int, int, int], GameState, int]] = [
            (move, child_state := move_fn(move), eval_fn(child_state)) for move in moves]  # Cache evaluations

        child_data.sort(key=lambda move: move[2], reverse=maximizing_player)

        best_eval: int = -(1 << 31) if maximizing_player else (1 << 31)
        best_move: tuple[int, int, int, int] | tuple = ()
        recurse: Callable = self.minimax

        for move, child, score in child_data:
            evaluation = score if depth <= 1 else \
                recurse(child, depth - 1, alpha, beta, not maximizing_player, first_call=False)[0]

            if maximizing_player:
                if evaluation > best_eval:
                    best_eval, best_move = evaluation, move
                    alpha = max(alpha, evaluation)
            elif evaluation < best_eval:
                    best_eval, best_move = evaluation, move
                    beta = min(beta, evaluation)

            if beta <= alpha:
                break

        transposition_table[state_key] = best_eval, best_move
        return best_eval, best_move
