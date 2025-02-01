import sys

import pygame
from game import GameState, start_board

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

piece_values = {-6: -9999999,
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


def evaluate(game_state: GameState) -> float:
    evaluation = 0
    for row in game_state.board:
        for piece in row:
            evaluation += piece_values[piece]
    return evaluation


def minimax(game_state: GameState, depth: int, alpha: float, beta: float, maximizing_player: bool) -> tuple[
    float, tuple[tuple[int, int], tuple[int, int]]]:
    moves = game_state.get_moves()
    best_eval = float("inf") * (-1 if maximizing_player else 1)
    best_move = ()
    for _move in moves:
        new_game_state = game_state.move(_move)
        evaluation = evaluate(new_game_state) if depth == 0 else minimax(game_state.move(_move), depth - 1, alpha, beta, not maximizing_player)[0]
        if maximizing_player and evaluation > best_eval:
            best_eval = evaluation
            best_move = _move
            alpha = max(alpha, evaluation)
        elif not maximizing_player and evaluation < best_eval:
            best_eval = evaluation
            best_move = _move
            beta = min(beta, evaluation)
        if beta <= alpha:
            break
    return round(best_eval, 5), best_move


def display_board(screen, board, selected_square):
    for i in range(8):
        for j in range(8):
            if selected_square == (j, i):
                pygame.draw.rect(screen, (245, 157, 131) if (i + j) % 2 == 0 else (211, 116, 79),
                                 (j * 60, i * 60, 60, 60))
            else:
                pygame.draw.rect(screen, (240, 217, 181) if (i + j) % 2 == 0 else (181, 136, 99),
                                 (j * 60, i * 60, 60, 60))
            if board[i][j] != 0:
                screen.blit(images[board[i][j] + 6], (j * 60, i * 60))


def game_loop():
    game_state = GameState()
    while game_state.get_winner() is None:
        print(game_state)
        moves = game_state.get_moves()
        print(moves)
        choice = int(input("Enter move index:  "))
        game_state = game_state.move(moves[choice])


def main() -> None:
    pygame.init()
    clock: pygame.time.Clock = pygame.time.Clock()
    screen = pygame.display.set_mode((480, 480))
    selected_square = None

    game_state = GameState()
    moves = game_state.get_moves()
    print(moves)

    # player_move = []

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # if event.type == pygame.MOUSEBUTTONDOWN:
                # if event.button == 1:
                #     game_state = game_state.move(minimax(game_state, 4, float("-inf"), float("inf"), game_state.color == 1)[1])
                #     square = (event.pos[0] // 60, event.pos[1] // 60)
                #     if selected_square == square:
                #         selected_square = None
                #         player_move = []
                #     else:
                #         selected_square = square
                #         player_move.append((selected_square[1], selected_square[0]))
                #     if len(player_move) == 2 and tuple(player_move) in moves:
                #         game_state = game_state.move(tuple(player_move))
                #         player_move = []
                #         moves = game_state.get_moves()
                #         print(minimax(game_state, 3, float("-inf"), float("inf"), game_state.color == 1))
                #     elif len(player_move) == 2:
                #         player_move = [player_move[1]]
                # if event.button == 3:
                #     selected_square = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    print(round(evaluate(game_state), 2))

        game_state = game_state.move(minimax(game_state, 3, float("-inf"), float("inf"), game_state.color == 1)[1])
        print(round(evaluate(game_state), 2))
        screen.fill(0)
        display_board(screen, game_state.board, selected_square)
        pygame.display.flip()


if __name__ == '__main__':
    main()
