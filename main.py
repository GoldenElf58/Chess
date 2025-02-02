import sys
import time

import pygame

from game import GameState, split_table, flatten

images = [
    pygame.image.load("piece_images/-6.png"),
    pygame.image.load("piece_images/-5.png"),
    pygame.image.load("piece_images/-4.png"),
    pygame.image.load("piece_images/-3.png"),
    pygame.image.load("piece_images/-2.png"),
    pygame.image.load("piece_images/-1.png"),
    0,
    pygame.image.load("piece_images/1.png"),
    pygame.image.load("piece_images/2.png"),
    pygame.image.load("piece_images/3.png"),
    pygame.image.load("piece_images/4.png"),
    pygame.image.load("piece_images/5.png"),
    pygame.image.load("piece_images/6.png"),
]

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


# For black pieces, we mirror the white table vertically.
def mirror(table):
    """Mirrors an 8x8 table vertically."""
    return table[::-1]


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
    -1: flatten(mirror(split_table(Pawns_flat))),
    -2: flatten(mirror(split_table(Knights_flat))),
    -3: flatten(mirror(split_table(Bishops_flat))),
    -4: flatten(mirror(split_table(Rooks_flat))),
    -5: flatten(mirror(split_table(Queens_flat))),
    -6: flatten(mirror(split_table(KingStart_flat))),
}


def evaluate(game_state: GameState) -> int:
    evaluation = 0
    for i, row in enumerate(split_table(game_state.board)):
        for j, piece in enumerate(row):
            if piece != 0:
                evaluation += piece_values[piece] + position_values[piece][i * 8 + j]
    return evaluation


def minimax(game_state: GameState, depth: int, alpha: int, beta: int, maximizing_player: bool) -> tuple[
    int, tuple[tuple[int, int], tuple[int, int]]]:
    moves = game_state.get_moves()
    new_game_states = {move: game_state.move(move) for move in moves}
    evaluations = {move: evaluate(new_game_states[move]) for move in moves}  # Cache evaluations

    # Move ordering: Sort moves by evaluation score (best first for maximizing, worst first for minimizing)
    moves.sort(key=lambda move: evaluations[move], reverse=maximizing_player)

    best_eval = -(1 << 30) if maximizing_player else (1 << 30)  # Large negative/positive integers
    best_move = ()

    for move in moves:
        evaluation = evaluations[move] if depth == 0 else \
            minimax(new_game_states[move], depth - 1, alpha, beta, not maximizing_player)[0]

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

    return best_eval, best_move


def display_board(screen, board, selected_square=()):
    for i in range(8):
        for j in range(8):
            if selected_square == (j, i):
                pygame.draw.rect(screen, (245, 157, 131) if (i + j) % 2 == 0 else (211, 116, 79),
                                 (j * 60, i * 60, 60, 60))
            else:
                pygame.draw.rect(screen, (240, 217, 181) if (i + j) % 2 == 0 else (181, 136, 99),
                                 (j * 60, i * 60, 60, 60))
            if board[i * 8 + j] != 0:
                screen.blit(images[board[i * 8 + j] + 6], (j * 60, i * 60))


def main() -> None:
    pygame.init()
    clock: pygame.time.Clock = pygame.time.Clock()
    screen = pygame.display.set_mode((480, 480))

    game_state = GameState()

    t0 = time.time()
    move = 0
    while True:
        move += 1
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    print(evaluate(game_state))  # Removed redundant rounding

        eval_result, best_move = minimax(game_state, 4, -(1 << 30), (1 << 30), game_state.color == 1)
        game_state = game_state.move(best_move)

        print(eval_result)

        screen.fill(0)
        display_board(screen, game_state.board)
        pygame.display.flip()

        if move == 10:
            print(time.time() - t0)
            break


if __name__ == '__main__':
    main()
