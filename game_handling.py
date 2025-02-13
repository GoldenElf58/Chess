import pygame
from pygame import Surface
from pygame.font import Font

from enum import Enum, auto
import sys
import threading
import time

import evaluationv1
from fen_utils import game_state_from_line
from game import GameState

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


def display_board(screen, board, selected_square=(), offset=0):
    for i in range(8):
        for j in range(8):
            if selected_square == (j, i):
                pygame.draw.rect(screen, (245, 157, 131) if (i + j) % 2 == 0 else (211, 116, 79),
                                 (j * 60 + offset, i * 60, 60, 60 + offset))
            else:
                pygame.draw.rect(screen, (240, 217, 181) if (i + j) % 2 == 0 else (181, 136, 99),
                                 (j * 60 + offset, i * 60, 60, 60 + offset))
            if board[i * 8 + j] != 0:
                screen.blit(images[board[i * 8 + j] + 6], (j * 60 + offset, i * 60))


def display_info(screen: Surface, game_state: GameState, last_eval, font: Font, t0, game_mode, wins, draws, losses,
                 depths=None):
    info_x = 667
    info_rect = pygame.Rect(info_x, 0, screen.get_width() - info_x, screen.get_height())

    pygame.draw.rect(screen, (0, 0, 0), info_rect)

    eval_text = f"Evaluation: {last_eval / 100}"
    turn_text = f"Turn: {game_state.turn}"
    time_text = f"Time: {time.time() - t0:.0f}"
    eval_surf = font.render(eval_text, True, "white")
    turn_surf = font.render(turn_text, True, "white")
    time_surf = font.render(time_text, True, "white")
    screen.blit(eval_surf, (info_rect.x + 10, 10))
    screen.blit(turn_surf, (info_rect.x + 10, 40))
    screen.blit(time_surf, (info_rect.x + 10, 70))

    if depths is not None and len(depths) != 0:
        depths_text = f"Depth Average: {sum(depths) / len(depths):.1f}"
        depths_surf = font.render(depths_text, True, "white")
        screen.blit(depths_surf, (info_rect.x + 10, 100))

    if game_mode == GameMode.DEEP_TEST:
        wins_text = f"Wins: {wins}"
        draws_text = f"Draws: {draws}"
        losses_text = f"Losses: {losses}"
        wins__surf = font.render(wins_text, True, "white")
        draws_surf = font.render(draws_text, True, "white")
        losses_surf = font.render(losses_text, True, "white")
        screen.blit(wins__surf, (info_rect.x + 10, 130))
        screen.blit(draws_surf, (info_rect.x + 10, 160))
        screen.blit(losses_surf, (info_rect.x + 10, 190))


# Define a simple Button class.
class Button:
    def __init__(self, rect, text, color, hover_color, text_color):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color

    def draw(self, screen, font):
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.rect(screen, self.hover_color if self.check_hover(mouse_pos) else self.color, self.rect)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos) -> bool:
        return self.rect.collidepoint(pos)


class GameMode(Enum):
    MENU = auto()
    HUMAN = auto()
    PLAY_WHITE = auto()
    PLAY_BLACK = auto()
    AI_VS_AI = auto()
    DEEP_TEST = auto()


def find_move(user_src: tuple[int, int], user_dest: tuple[int, int], legal_moves: list[tuple[int, int, int, int]],
              game_state) -> tuple[int, int, int, int] | None:
    """
    Given a user’s source and destination (as (row, col) tuples),
    return a matching legal move (one of the tuples produced by get_moves())
    taking into account special moves (castle, promotion, en passant).
    The matching is done by checking the source and destination coordinates.
    """
    color = game_state.color
    # Loop through legal moves.
    for move in legal_moves:
        # For normal moves the tuple is (src_row, src_col, dest_row, dest_col)
        if move[0] >= 0:
            if (move[0], move[1]) == user_src and (move[2], move[3]) == user_dest:
                return move
        # Castle moves are encoded with a negative first element (-1)
        elif move[0] == -1:
            # In your get_moves(), a castle move is added as (-1, offset, src_row, src_col)
            # We assume the user clicks the king and then a square two columns away.
            if (move[2], move[3]) == user_src:
                # King moves two squares horizontally.
                if user_dest[0] == user_src[0]:
                    if user_dest[1] == user_src[1] + 2 and move[1] > 0:
                        return move
                    if user_dest[1] == user_src[1] - 2 and move[1] < 0:
                        return move
        # En passant moves are encoded as (-2, offset, src_row, src_col)
        elif move[0] == -2:
            if (move[2], move[3]) == user_src:
                # The pawn moves diagonally: its destination is one row forward (depending on color)
                expected_dest = (user_src[0] - color, user_src[1] + move[1])
                if user_dest == expected_dest:
                    return move
        # Promotion moves are encoded as (-3, code, src_row, src_col) for non–capture.
        elif move[0] == -3:
            if (move[2], move[3]) == user_src:
                # For a pawn moving forward into promotion:
                expected_dest = (user_src[0] - color, user_src[1])
                if user_dest == expected_dest:
                    # Auto–select queen: for white, choose code 5; for black, code -5.
                    if (color == 1 and move[1] == 5) or (color == -1 and move[1] == -5):
                        return move
        # Promotion while capturing (your code uses moves with first element <= -4)
        elif move[0] <= -4:
            if (move[2], move[3]) == user_src:
                # For a capture, the pawn moves diagonally.
                if user_dest == (user_src[0] - color, user_src[1] + 1) and move[1] > 0:
                    # Auto–select queen capture promotion (for white, e.g. code 1 in your moves)
                    return move
                if user_dest == (user_src[0] - color, user_src[1] - 1) and move[1] < 0:
                    return move
    return None


def game_loop():
    pygame.init()
    screen: Surface = pygame.display.set_mode((854, 480))
    offset = 187
    game_state = GameState()
    selected_square = None  # For human move selection (as (col, row))
    game_mode = GameMode.MENU  # Will be set when a button is clicked
    font = Font(None, 24)

    # Create the three buttons.
    buttons = [
        Button((43, 190, 100, 20), "Play White", "gray", "lightgray", (0, 0, 0)),
        Button((43, 230, 100, 20), "Play Black", "gray", "lightgray", (0, 0, 0)),
        Button((43, 270, 100, 20), "AI vs AI", "gray", "lightgray", (0, 0, 0)),
        Button((43, 310, 100, 20), "Deep Test", "gray", "lightgray", (0, 0, 0)),
        Button((43, 150, 100, 20), "Human", "gray", "lightgray", (0, 0, 0))
    ]

    computer_thread = None
    computer_move_result = []  # Container to hold the minimax result
    last_eval = 0
    depths = []
    t0 = time.time()

    line = 1
    num_lines = 500
    reverse = False
    bots = (evaluationv1.Bot(), evaluationv1.Bot())
    wins = 0
    draws = 0
    losses = 0

    running = True
    while running:
        # clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_mode == GameMode.MENU and event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                t0 = time.time()
                if buttons[0].check_hover(pos):
                    game_mode = GameMode.PLAY_WHITE
                    game_state = GameState()
                    bots[0].clear_cache()
                    bots[1].clear_cache()
                elif buttons[1].check_hover(pos):
                    reverse = False
                    game_mode = GameMode.PLAY_BLACK
                    game_state = GameState()
                    bots[0].clear_cache()
                    bots[1].clear_cache()
                elif buttons[2].check_hover(pos):
                    reverse = False
                    game_mode = GameMode.AI_VS_AI
                    game_state = GameState()
                    bots[0].clear_cache()
                    bots[1].clear_cache()
                elif buttons[3].check_hover(pos):
                    game_mode = GameMode.DEEP_TEST
                    line = 1
                    reverse = False
                    game_state = game_state_from_line(line, "fens.txt")
                    bots[0].clear_cache()
                    bots[1].clear_cache()
                elif buttons[4].check_hover(pos):
                    game_mode = GameMode.HUMAN
                    game_state = GameState()

            if game_mode in {GameMode.PLAY_WHITE, GameMode.PLAY_BLACK, GameMode.HUMAN} and (
                    event.type == pygame.MOUSEBUTTONDOWN):
                x, y = event.pos
                col, row = (x - offset) // 60, y // 60
                selected_piece = game_state.board[row * 8 + col]
                color = game_state.color
                # Store selected square as (col, row)
                if selected_square is None:
                    # Only select a piece if it belongs to the human.
                    if ((game_mode == GameMode.HUMAN and ((selected_piece > 0 and color == 1) or (
                            selected_piece < 0 and color == -1))) or (selected_piece > 0 and color == 1
                            and game_mode == GameMode.PLAY_WHITE) or (selected_piece < 0 and color == -1 and
                            game_mode == GameMode.PLAY_BLACK)):
                        selected_square = (col, row)
                else:
                    # Convert selected_square (col, row) to (row, col)
                    user_src = (selected_square[1], selected_square[0])
                    user_dest = (row, col)
                    legal = game_state.get_moves()
                    chosen_move = find_move(user_src, user_dest, legal, game_state)
                    if chosen_move is not None:
                        game_state = game_state.move(chosen_move)
                        game_state.get_moves()
                    selected_square = None
                    if ((game_mode == GameMode.HUMAN and ((selected_piece > 0 and color == 1) or (
                            selected_piece < 0 and color == -1))) or (selected_piece > 0 and color == 1
                            and game_mode == GameMode.PLAY_WHITE) or (selected_piece < 0 and color == -1 and
                            game_mode == GameMode.PLAY_BLACK)):
                        selected_square = user_dest[1], user_dest[0]

        if game_mode != GameMode.MENU:
            if computer_thread is None:
                if game_mode in {GameMode.AI_VS_AI, GameMode.DEEP_TEST} or (
                        game_mode == GameMode.PLAY_WHITE and game_state.color == -1) or (
                        game_mode == GameMode.PLAY_BLACK and game_state.color == 1):
                    computer_move_result.clear()
                    # print(0 if (game_state.color == 1) != reverse else 1)
                    computer_thread = threading.Thread(target=lambda: computer_move_result.append(
                        bots[0 if (game_state.color == 1) != reverse else 1].generate_move(game_state, .1)))
                    computer_thread.start()
            elif not computer_thread.is_alive():
                if computer_move_result:
                    computer_thread.join()
                    (last_eval, best_move), depth = computer_move_result.pop(0)
                    depths.append(depth)
                    game_state = game_state.move(best_move)
                    if game_state.turn == 10 and game_mode == GameMode.AI_VS_AI: print(time.time() - t0)
                computer_thread = None

        screen.fill(0)
        display_board(screen, game_state.board, selected_square, offset)

        game_state.get_moves()
        if (winner := game_state.get_winner()) is not None and game_mode != GameMode.MENU:
            if game_mode != GameMode.DEEP_TEST:
                game_mode = GameMode.MENU
            elif game_mode == GameMode.DEEP_TEST:
                if game_mode == GameMode.DEEP_TEST:
                    # Determine bot[0]'s color for this game.
                    computer_move_result.clear()
                    bot0_color = 1 if not reverse else -1
                    if winner == 0:
                        draws += 1
                    elif winner == bot0_color:
                        wins += 1
                    else:
                        losses += 1
                    if reverse:
                        line += 1
                    reverse = not reverse
                    if line > num_lines:
                        line = 1
                        game_mode = GameMode.MENU
                    print(wins, draws, losses)
                game_state = game_state_from_line(line, "fens.txt")
                bots[0].clear_cache()
                bots[1].clear_cache()

        if game_mode == GameMode.MENU:
            for btn in buttons: btn.draw(screen, font)
        else:
            display_info(screen, game_state, last_eval, font, t0, game_mode, wins, draws, losses, depths=depths)

        pygame.display.flip()

    pygame.quit()
    sys.exit()
