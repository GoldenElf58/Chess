import threading
import time

from game import GameState
from utils import mirror

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

Pawns_flat = [
    0, 0, 0, 0, 0, 0, 0, 0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5, 5, 10, 25, 25, 10, 5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, -5, -10, 0, 0, -10, -5, 5,
    5, 10, 10, -20, -20, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
]

Rooks_flat = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, 10, 10, 10, 10, 5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    0, 0, 0, 5, 5, 0, 0, 0
]

Knights_flat = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

Bishops_flat = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]

Queens_flat = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]

KingStart_flat = [
    -80, -70, -70, -70, -70, -70, -70, -80,
    -60, -60, -60, -60, -60, -60, -60, -60,
    -40, -50, -50, -60, -60, -50, -50, -40,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20, -5, -5, -5, -5, 20, 20,
    20, 30, 10, 0, 0, 10, 30, 20
]

# Map piece type to its piece-square table.
# (Assuming that in your piece_values dictionary:
#   Pawn   -> ±1, Knight -> ±2, Bishop -> ±3,
#   Rook   -> ±4, Queen  -> ±5, King   -> ±6)
position_values: dict[int, list[int]] = {
    # White pieces (positive values)
    1: Pawns_flat,
    2: Knights_flat,
    3: Bishops_flat,
    4: Rooks_flat,
    5: Queens_flat,
    6: KingStart_flat,
    # Black pieces (negative values) use the mirrored tables
    -1: mirror(Pawns_flat),
    -2: mirror(Knights_flat),
    -3: mirror(Bishops_flat),
    -4: mirror(Rooks_flat),
    -5: mirror(Queens_flat),
    -6: mirror(KingStart_flat),
}

class OldBot:
    def __init__(self, transposition_table=None, eval_lookup=None):
        self.transposition_table = transposition_table if transposition_table is not None else {}
        self.eval_lookup = eval_lookup if eval_lookup is not None else {}

    def generate_move(self, game_state, allotted_time=3, depth=-1):
        return self.iterative_deepening(game_state, game_state.color==1, allotted_time=allotted_time, depth=depth)

    def clear_cache(self):
        self.transposition_table.clear()
        self.eval_lookup.clear()

    def evaluate(self, game_state: GameState) -> int:
        evaluation = 0
        if game_state.draw: return 0
        hash_state = game_state.get_efficient_hashable_state_hashed()
        if hash_state in self.eval_lookup:
            return self.eval_lookup[hash_state]
        for i, piece in enumerate(game_state.board):
            if piece != 0:
                evaluation += piece_values[piece] + position_values[piece][i]
        self.eval_lookup[hash_state] = evaluation
        return evaluation


    def iterative_deepening(self, game_state: GameState, maximizing_player: bool, allotted_time: float = 3, depth=-1):
        if depth >= 0:
            result = None
            for i in range(1, depth + 1):
                result = self.minimax_tt(game_state, i, -(1 << 40), (1 << 40), maximizing_player)
            return result, depth
        t0 = time.time()
        results: list[tuple[int, tuple[int, int, int, int]]] = [(0, game_state.get_moves()[0])]
        depth = 0
        minimax_thread = threading.Thread(
            target=lambda: results.append(self.minimax_tt(game_state, depth, -(1 << 40), (1 << 40), maximizing_player)))
        minimax_thread.start()
        while time.time() - t0 < allotted_time:
            depth += 1
            minimax_thread.join(allotted_time - (time.time() - t0))
            minimax_thread = threading.Thread(
                target=lambda: results.append(
                    self.minimax_tt(game_state, depth, -(1 << 40), (1 << 40), maximizing_player)))
            if time.time() - t0 < allotted_time: minimax_thread.start()
        # print(len(results))
        return results[-1], len(results)


    def minimax_tt(self, game_state: GameState, depth: int, alpha: int, beta: int, maximizing_player: bool):
        state_key = hash((tuple(game_state.board),
                          ((game_state.color == 1) << 4) | (game_state.white_queen << 3) | (game_state.white_king << 2) | (
                                  game_state.black_queen << 1 | game_state.black_king) | (
                                  (depth | (maximizing_player << 10)) << 5)))
        if state_key in self.transposition_table:
            return self.transposition_table[state_key]
        moves = game_state.get_moves()
        new_game_states = {move: game_state.move(move) for move in moves}
        evaluations = {move: self.evaluate(new_game_states[move]) for move in moves}  # Cache evaluations

        # Move ordering: Sort moves by evaluation score (best first for maximizing, worst first for minimizing)
        moves.sort(key=lambda move: evaluations[move], reverse=maximizing_player)

        best_eval = -(1 << 40) if maximizing_player else (1 << 40)  # Large negative/positive integers
        best_move = ()

        for move in moves:
            evaluation = evaluations[move] if depth == 0 else \
                self.minimax_tt(new_game_states[move], depth - 1, alpha, beta, not maximizing_player)[0]

            if maximizing_player:
                if evaluation > best_eval:
                    best_eval, best_move = evaluation, move
                    alpha = max(alpha, evaluation)
            else:
                if evaluation < best_eval:
                    best_eval, best_move = evaluation, move
                    beta = min(beta, evaluation)

            if beta <= alpha:  # Alpha-beta pruning
                break

        self.transposition_table[state_key] = best_eval, best_move
        return best_eval, best_move
