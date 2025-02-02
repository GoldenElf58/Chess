import sys
import threading
from enum import Enum, auto

import pygame
from pygame import Surface
from pygame.font import Font
from pygame.time import Clock

from game import GameState
from evaluation import minimax, evaluate

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


def display_info(screen: Surface, game: GameState, last_eval, font: Font):
    # Define the info area as the right-hand side of the screen.
    info_x = 667  # Adjust this to where you want the info area to start.
    info_rect = pygame.Rect(info_x, 0, screen.get_width() - info_x, screen.get_height())

    # Draw a background for the info area.
    pygame.draw.rect(screen, (0, 0, 0), info_rect)

    # Render and blit your text. Here we're showing the evaluation value.
    info_text = f"Evaluation: {last_eval / 100}"
    text_surf = font.render(info_text, True, "white")
    screen.blit(text_surf, (info_rect.x + 10, 10))


# Define a simple Button class.
class Button:
    def __init__(self, rect, text, color, hover_color, text_color, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.callback = callback

    def draw(self, screen, font):
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.rect(screen, self.hover_color if self.check_hover(mouse_pos) else self.color, self.rect)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()

    def check_hover(self, pos):
        return self.rect.collidepoint(pos)


class GameMode(Enum):
    MENU = auto()
    PLAY_WHITE = auto()
    PLAY_BLACK = auto()
    AI_VS_AI = auto()


# Example callback functions for each button.
def play_white():
    global game_mode, game_state, selected_square
    game_mode = GameMode.PLAY_WHITE
    # Reset game_state or set up mode-specific settings here.
    game_state = GameState()  # Assuming starting position has white to move.
    selected_square = None
    print("Play White selected.")


def play_black():
    global game_mode, game_state, selected_square
    game_mode = GameMode.PLAY_BLACK
    # Reset game_state and possibly flip the board so black is human.
    game_state = GameState()  # You may need additional logic to let human play black.
    selected_square = None
    print("Play Black selected.")


def ai_vs_ai():
    global game_mode, game_state, selected_square
    game_mode = GameMode.AI_VS_AI
    # Reset game_state for AI vs AI.
    game_state = GameState()
    selected_square = None
    print("AI vs AI selected.")


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


# In your main function, create the buttons and handle clicks.
def main() -> None:
    pygame.init()
    clock: Clock = Clock()
    screen: Surface = pygame.display.set_mode((854, 480))
    offset = 187
    global game_state, selected_square, game_mode
    game_state = GameState()
    selected_square = None  # For human move selection (as (col, row))
    game_mode = GameMode.MENU  # Will be set when a button is clicked
    font = Font(None, 24)

    # Create the three buttons.
    buttons = [
        Button((43, 190, 100, 20), "Play White", "gray", "lightgray", (0, 0, 0), play_white),
        Button((43, 230, 100, 20), "Play Black", "gray", "lightgray", (0, 0, 0), play_black),
        Button((43, 270, 100, 20), "AI vs AI", "gray", "lightgray", (0, 0, 0), ai_vs_ai)
    ]

    computer_thread = None
    computer_move_result = []  # Container to hold the minimax result
    last_eval = 0

    running = True
    while running:
        clock.tick(60)
        # Process events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # If no game mode is chosen yet, check for button clicks.
            if game_mode == GameMode.MENU and event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for btn in buttons:
                    btn.check_click(pos)

            # Human move events after a game mode has been selected.
            # (Assuming human plays when game_state.color == 1; adjust if needed.)
            if game_mode != GameMode.MENU and game_state.color == 1 and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                col, row = (x - offset) // 60, y // 60
                # Store selected square as (col, row)
                if selected_square is None:
                    # Only select a piece if it belongs to the human.
                    if game_state.board[row * 8 + col] > 0:
                        selected_square = (col, row)
                else:
                    # Convert selected_square (col, row) to (row, col)
                    user_src = (selected_square[1], selected_square[0])
                    user_dest = (row, col)
                    legal = game_state.get_moves()
                    chosen_move = find_move(user_src, user_dest, legal, game_state)
                    if chosen_move is not None:
                        game_state = game_state.move(chosen_move)
                    selected_square = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    print(evaluate(game_state))

        # For AI moves: when it's black's turn, spawn a thread for minimax.
        if game_mode in {GameMode.AI_VS_AI, GameMode.PLAY_WHITE} and game_state.color == -1:
            if computer_thread is None:
                computer_move_result.clear()
                computer_thread = threading.Thread(target=lambda: computer_move_result.append(
                    minimax(game_state, 4, -(1 << 30), (1 << 30), False)))
                computer_thread.start()
            elif not computer_thread.is_alive():
                if computer_move_result:
                    last_eval, best_move = computer_move_result.pop(0)
                    game_state = game_state.move(best_move)
                computer_thread = None

        if game_mode in {GameMode.AI_VS_AI, GameMode.PLAY_BLACK} and game_state.color == 1:
            if computer_thread is None:
                computer_move_result.clear()
                computer_thread = threading.Thread(target=lambda: computer_move_result.append(
                    minimax(game_state, 4, -(1 << 30), (1 << 30), True)))
                computer_thread.start()
            elif not computer_thread.is_alive():
                if computer_move_result:
                    last_eval, best_move = computer_move_result.pop(0)
                    game_state = game_state.move(best_move)
                computer_thread = None

        screen.fill(0)
        display_board(screen, game_state.board, selected_square, offset)
        if game_state.get_winner() is not None:
            game_mode = GameMode.MENU
        # If game mode is not selected yet, draw the buttons.
        if game_mode == GameMode.MENU:
            for btn in buttons:
                btn.draw(screen, font)
        else:
            display_info(screen, game_state, last_eval, font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
