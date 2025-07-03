import random
from typing import Callable

import pygame
from pygame import Surface, Rect
from pygame.font import Font

from enum import IntFlag, auto
import sys
import threading
import time
from scipy.stats import binomtest  # type: ignore

from bots import *

from fen_utils import game_state_from_line
from game_states import GameState, GameStateBase, GameStateBitboardsV2, GameStateFormatV2, GameStateV3, \
    GameStateBitboardsV3

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


def display_board(screen, game_state: GameStateBase, selected_square=(), offset=0):
    for i in range(8):
        for j in range(8):
            if selected_square == (i, j):
                pygame.draw.rect(screen, (245, 157, 131) if (i + j) % 2 == 0 else (211, 116, 79),
                                 (j * 60 + offset, i * 60, 60, 60 + offset))
            else:
                pygame.draw.rect(screen, (240, 217, 181) if (i + j) % 2 == 0 else (181, 136, 99),
                                 (j * 60 + offset, i * 60, 60, 60 + offset))
            if isinstance(game_state, GameState) or isinstance(game_state, GameStateFormatV2):
                if game_state.board[i * 8 + j] != 0:
                    screen.blit(images[game_state.board[i * 8 + j] + 6], (j * 60 + offset, i * 60))
            elif isinstance(game_state, GameStateBitboardsV2) or isinstance(game_state, GameStateBitboardsV3):
                piece = 0
                piece_mask = 1 << (63 - (i * 8 + j))
                if not piece_mask & (game_state.white_pieces | game_state.black_pieces):
                    continue
                if piece_mask & game_state.pawns:
                    piece = 1
                elif piece_mask & game_state.knights:
                    piece = 2
                elif piece_mask & game_state.bishops:
                    piece = 3
                elif piece_mask & game_state.rooks:
                    piece = 4
                elif piece_mask & game_state.kings:
                    piece = 6
                elif piece_mask & game_state.queens:
                    piece = 5
                if piece_mask & game_state.black_pieces:
                    piece *= -1
                screen.blit(images[piece + 6], (j * 60 + offset, i * 60))


class GameMode(IntFlag):
    MENU = auto()
    HUMAN = auto()
    PLAY_WHITE = auto()
    PLAY_BLACK = auto()
    AI_VS_AI = auto()
    DEEP_TEST = auto()
    MAIN = auto()
    OPTIONS = auto()
    MAIN_MENU = MAIN | MENU
    OPTIONS_MENU = OPTIONS | MENU


def display_info(screen: Surface, game_state: GameStateBase, last_eval: int, font: Font, t0: float, game_mode: GameMode,
                 wins: int, draws: int, losses: int, bots: list[Bot], reverse: bool,
                 depths: list[list[int]] | None = None) -> None:
    """
    Displays information about the game

    :param screen: The screen to display the information on
    :param game_state: The current game state
    :param last_eval: The last evaluation from the bot
    :param font: The font to use
    :param t0: The time the game started
    :param game_mode: The game mode
    :param wins: The number of wins bots[0] has
    :param draws: The number of draws
    :param losses: The number of losses bots[0] has
    :param bots: The two bots that are playing against each other
    :param reverse: Whether the bots are playing in reverse (bots[0] is blaak, bots[1] is white)
    :param depths: The previous depths the bots searched to
    """
    info_x = 667
    info_rect = pygame.Rect(info_x, 0, screen.get_width() - info_x, screen.get_height())

    pygame.draw.rect(screen, (0, 0, 0), info_rect)

    eval_text: str = f"Evaluation: {last_eval / 100}"
    turn_text: str = f"Turn: {game_state.turn / 2}"
    time_text: str = f"Time: {time.time() - t0:.{1 if time.time() - t0 < 10 else 0}f}"
    eval_surf: Surface = font.render(eval_text, True, "white")
    turn_surf: Surface = font.render(turn_text, True, "white")
    time_surf: Surface = font.render(time_text, True, "white")
    screen.blit(eval_surf, (info_rect.x + 10, 10))
    screen.blit(turn_surf, (info_rect.x + 10, 40))
    screen.blit(time_surf, (info_rect.x + 10, 70))

    if depths is not None and len(depths) != 0:
        if len(depths[0]) != 0:
            depths_text: str = f"Depth {bots[0].get_version()}: {sum(depths[0]) / len(depths[0]):.1f}"
            depths_surf: Surface = font.render(depths_text, True, "white")
            screen.blit(depths_surf, (info_rect.x + 10, 100))

        if len(depths[1]) != 0:
            depths_text = f"Depth {bots[1].get_version()}: {sum(depths[1]) / len(depths[1]):.1f}"
            depths_surf = font.render(depths_text, True, "white")
            screen.blit(depths_surf, (info_rect.x + 10, 130))

    if game_mode & GameMode.DEEP_TEST:
        # --- two‑sided binomial test for wins vs. losses ---
        n_games: int = wins + losses
        p_value: float = 1.0 if n_games == 0 else binomtest(wins, n_games).pvalue

        wins_text: str = f"{bots[0].get_version()} ({"B" if reverse else "W"}): {wins}"
        draws_text: str = f"Draws: {draws}"
        losses_text: str = f"{bots[1].get_version()} ({"W" if reverse else "B"}): {losses}"
        p_value_text: str = f"P-Value: {p_value:.4f}"

        wins_surf: Surface = font.render(wins_text, True, "white")
        draws_surf: Surface = font.render(draws_text, True, "white")
        losses_surf: Surface = font.render(losses_text, True, "white")
        p_value_surf: Surface = font.render(p_value_text, True, "white")

        screen.blit(wins_surf, (info_rect.x + 10, 160))
        screen.blit(draws_surf, (info_rect.x + 10, 190))
        screen.blit(losses_surf, (info_rect.x + 10, 220))
        screen.blit(p_value_surf, (info_rect.x + 10, 250))




class Button:
    def __init__(self, rect, text, color="gray", hover_color="lightgray", text_color=(0, 0, 0)) -> None:
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color

    def draw(self, screen: Surface, font: Font) -> None:
        """
        Draws the button

        :param screen: The screen to draw the button on
        :param font: The font to use to draw the text
        """
        mouse_pos: tuple[int, int] = pygame.mouse.get_pos()
        pygame.draw.rect(screen, self.hover_color if self.check_hover(mouse_pos) else self.color, self.rect)
        text_surf: Surface = font.render(self.text, True, self.text_color)
        text_rect: Rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos: tuple[int, int]) -> bool:
        """
        Checks if the mouse is hovering over the button

        :param pos: Position of the mouse, represented as (x, y)
        :return: Whether or not the mouse is hovering over the button
        """
        return self.rect.collidepoint(pos)


def get_square(x: int, y: int, offset: int) -> tuple[int, int]:
    """
    Gets the square of the board at a given position

    :param x: Screen x position
    :param y: Screen y position
    :param offset: X offset from the top left corner of the screen
    :return: (row, col)
    """
    return y // 60, (x - offset) // 60


def can_select_square(row: int, col: int, game_state: GameStateBase, game_mode: GameMode) -> bool:
    """
    Whether or not a square can be selected by a user given the current game state and game mode

    :param row: Row index of the square on the interval [0, 7]
    :param col: Column index of the square on the interval [0, 7]
    :param game_state: Game state of the current game
    :param game_mode: Current game mode
    :return: Whether or not the square can be selected
    """
    color = game_state.color
    if isinstance(game_state, GameStateBitboardsV2) or isinstance(game_state, GameStateBitboardsV3):
        selected_piece_mask = 1 << (63 - (row * 8 + col))
        return bool(((game_mode & (GameMode.HUMAN | GameMode.PLAY_WHITE)) and
                     ((selected_piece_mask & game_state.white_pieces) and color == 1) or (
                             (game_mode & (GameMode.PLAY_BLACK | GameMode.HUMAN)) and
                             (selected_piece_mask & game_state.black_pieces) and color == -1)))
    elif isinstance(game_state, GameState) or isinstance(game_state, GameStateFormatV2):
        selected_piece = game_state.board[row * 8 + col]
        return bool((game_mode & GameMode.HUMAN and ((selected_piece > 0 and color == 1) or (
                selected_piece < 0 and color == -1))) or (selected_piece > 0 and color == 1 and
                                                          game_mode & GameMode.PLAY_WHITE) or (
                            selected_piece < 0 and color == -1 and
                            game_mode & GameMode.PLAY_BLACK))
    return False


def find_move(user_src: tuple[int, int], user_dest: tuple[int, int],
              game_state) -> tuple[int, int, int] | tuple[int, int, int, int] | None:
    """
    Given a user’s source and destination (as (row, col) tuples),
    return a matching legal move (one of the tuples produced by get_moves())
    taking into account special moves (castle, promotion, en passant).
    The matching is done by checking the source and destination coordinates.
    """
    color = game_state.color
    legal_moves: list = game_state.get_moves()
    # Loop through legal moves.
    if isinstance(game_state, GameState):
        for move in legal_moves:  # type: tuple[int, int, int, int]
            if move[0] >= 0:
                if (move[0], move[1]) == user_src and (move[2], move[3]) == user_dest:
                    return move
            elif (move[2], move[3]) == user_src:
                if move[0] == -1:
                    if user_dest[0] == user_src[0]:
                        if user_dest[1] == user_src[1] + 2 * move[1]:
                            return move
                elif move[0] == -2:
                    expected_dest = (user_src[0] - color, user_src[1] + move[1])
                    if user_dest == expected_dest:
                        return move
                elif move[0] == -3:
                    expected_dest = (user_src[0] - color, user_src[1])
                    if user_dest == expected_dest and move[1] in (-5, 5):
                        return move
                elif move[0] <= -4:
                    if user_dest == (user_src[0] - color, user_src[1] + move[1]):
                        return move
    elif isinstance(game_state, GameStateFormatV2):
        user_src_idx: int = user_src[0] * 8 + user_src[1]
        user_dest_idx: int = user_dest[0] * 8 + user_dest[1]
        for move_ in legal_moves:  # type: tuple[int, int, int]
            if move_[0] >= 0:
                if move_[0] == user_src_idx and move_[1] == user_dest_idx:
                    return move_
            elif move_[2] == user_src_idx:
                if move_[0] == -1:
                    if user_dest[0] == user_src[0] and user_dest[1] == user_src[1] + 2 * move_[1]:
                        return move_
                elif move_[0] == -2:
                    expected_dest = (user_src[0] - color, user_src[1] + move_[1])
                    if user_dest == expected_dest:
                        return move_
    elif isinstance(game_state, GameStateBitboardsV2) or isinstance(game_state, GameStateBitboardsV3):
        a8 = 1 << 63
        user_src_mask: int = a8 >> user_src[0] * 8 + user_src[1]
        user_dest_mask: int = a8 >> user_dest[0] * 8 + user_dest[1]
        for move_ in legal_moves:
            if move_[0] >= 0:
                if move_[0] == user_src_mask and move_[1] == user_dest_mask:
                    return move_
            elif move_[2] == user_src_mask:
                if move_[0] == -1:
                    if user_dest[0] == user_src[0] and user_dest[1] == user_src[1] + 2 * move_[1]:
                        return move_
                elif move_[0] == -2:
                    expected_dest = (user_src[0] - color, user_src[1] + move_[1])
                    if user_dest == expected_dest:
                        return move_
                elif move_[0] == -3:
                    expected_dest = (user_src[0] - color, user_src[1])
                    if user_dest == expected_dest and move_[1] in (-5, 5):
                        return move_
                elif move_[0] <= -4:
                    expected_dest = (user_src[0] - color, user_src[1] + move_[1])
                    if user_dest == expected_dest and move_[0] in (-8, 8):
                        return move_

    return None


def game_loop() -> None:
    pygame.init()
    screen: Surface = pygame.display.set_mode((854, 480))
    offset: int = 187
    game_state_type: Callable[[], GameStateBase] = GameStateV3
    game_state: GameStateBase = game_state_type()
    selected_square: tuple[int, int] | None = None
    """For human move selection, represented as (col, row)"""

    game_mode: GameMode = GameMode.MAIN_MENU
    font: Font = Font(None, 24)

    computer_thread: threading.Thread | None = None
    computer_move_result: list[tuple[tuple[int, tuple[int, int, int, int] | tuple[int, int, int]], int]] = []
    last_eval: int = 0
    depths: list[list[int]] = [[], []]
    t0: float = time.time()

    num_lines: int = 500
    line: int = random.randint(1, num_lines)
    reverse: bool = False
    wins: int = 0
    draws: int = 0
    losses: int = 0

    bot_options: tuple[Callable[[], Bot], ...] = (
        BotV5,
        BotV5p1,
        BotV5p3,
        BotV5p4,
        BotV1,
        BotV2p3,
        BotV3p5,
        BotV3p6,
        BotV3p7,
        BotV4,
        BotV4p2,
        BotV4p3,
    )
    bot_idxs: list[int] = [5, 5]
    bots: list[Bot] = [bot_options[bot_idxs[0]](), bot_options[bot_idxs[1]]()]

    test_mode: bool = False
    test_depth = 5
    test_allotted_time = .1
    normal_depth = -1
    normal_allotted_time = .1

    main_buttons: list[Button] = [
        Button((43, 190, 100, 20), "Play White"),
        Button((43, 230, 100, 20), "Play Black"),
        Button((43, 270, 100, 20), "AI vs AI"),
        Button((43, 310, 100, 20), "Deep Test"),
        Button((43, 150, 100, 20), "Human"),
        Button((43, 110, 100, 20), "Options"),
    ]

    options_buttons: list[Button] = [
        Button((43, 110, 100, 20), "Main Menu"),
        Button((43, 230, 100, 20), "Test" if test_mode else "Normal"),
        Button((43, 150, 100, 20), bots[0].get_version()),
        Button((43, 190, 100, 20), bots[1].get_version()),
    ]

    running: bool = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_mode == GameMode.MAIN_MENU and event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                t0 = time.time()
                if main_buttons[0].check_hover(pos):
                    reverse = False
                    game_mode = GameMode.PLAY_WHITE
                    game_state = game_state_type()
                    bots[0].clear_cache()
                    bots[1].clear_cache()
                elif main_buttons[1].check_hover(pos):
                    reverse = False
                    game_mode = GameMode.PLAY_BLACK
                    game_state = game_state_type()
                    bots[0].clear_cache()
                    bots[1].clear_cache()
                elif main_buttons[2].check_hover(pos):
                    reverse = False
                    game_mode = GameMode.AI_VS_AI
                    game_state = game_state_type()
                    bots[0].clear_cache()
                    bots[1].clear_cache()
                elif main_buttons[3].check_hover(pos):
                    game_mode = GameMode.DEEP_TEST
                    line = 1
                    reverse = False
                    game_state = game_state_from_line(line)
                    assert isinstance(game_state, GameState)
                    if game_state_type == GameState:
                        game_state = game_state.to_v2()
                    elif game_state_type == GameStateBitboardsV2:
                        game_state = game_state.to_bitboards_v2()
                    elif game_state_type == GameStateV3:
                        game_state = game_state.to_v3()
                    bots[0].clear_cache()
                    bots[1].clear_cache()
                elif main_buttons[4].check_hover(pos):
                    game_mode = GameMode.HUMAN
                    game_state = game_state_type()
                elif main_buttons[5].check_hover(pos):
                    game_mode = GameMode.OPTIONS_MENU
            elif game_mode == GameMode.OPTIONS_MENU and event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if options_buttons[0].check_hover(pos):
                    game_mode = GameMode.MAIN_MENU
                elif options_buttons[1].check_hover(pos):
                    test_mode = not test_mode
                    options_buttons[1].text = "Test" if test_mode else "Normal"
                elif options_buttons[2].check_hover(pos):
                    bot_idxs[0] = (bot_idxs[0] + 1) % len(bot_options)
                    bots[0] = bot_options[bot_idxs[0]]()
                    options_buttons[2].text = bots[0].get_version()
                elif options_buttons[3].check_hover(pos):
                    bot_idxs[1] = (bot_idxs[1] + 1) % len(bot_options)
                    bots[1] = bot_options[bot_idxs[1]]()
                    options_buttons[3].text = bots[1].get_version()

            if game_mode & (GameMode.PLAY_WHITE | GameMode.PLAY_BLACK | GameMode.HUMAN) and (
                    event.type == pygame.MOUSEBUTTONDOWN):
                row, col = get_square(event.pos[0], event.pos[1], offset)  # type: int, int
                can_select: bool = can_select_square(row, col, game_state, game_mode)

                if selected_square is None:
                    if can_select: selected_square = (row, col)
                else:
                    user_src: tuple[int, int] = selected_square
                    user_dest: tuple[int, int] = (row, col)
                    chosen_move: tuple[int, int, int, int] | tuple[int, int, int] | None = find_move(
                        user_src, user_dest, game_state)
                    if chosen_move is not None:
                        game_state = game_state.move(chosen_move)
                        game_state.get_moves()
                    selected_square = None
                    if can_select: selected_square = user_dest

        if not game_mode & GameMode.MENU:
            if computer_thread is None:
                if game_mode & (GameMode.AI_VS_AI | GameMode.DEEP_TEST) or (
                        game_mode & GameMode.PLAY_WHITE and game_state.color == -1) or (
                        game_mode & GameMode.PLAY_BLACK and game_state.color == 1):
                    computer_move_result.clear()
                    computer_thread = threading.Thread(target=lambda: computer_move_result.append(
                        bots[0 if (game_state.color == 1) is not reverse else 1]
                        .generate_move(game_state, test_allotted_time if test_mode else normal_allotted_time,
                                       depth=test_depth if test_mode else normal_depth)))
                    computer_thread.start()
            elif not computer_thread.is_alive():
                if computer_move_result:
                    computer_thread.join()
                    (last_eval, best_move), depth = computer_move_result.pop(0)
                    depths[0 if (game_state.color == 1) is not reverse else 1].append(depth)
                    game_state = game_state.move(best_move)
                    if game_state.turn % 10 == 0 and game_mode & GameMode.AI_VS_AI and test_mode:
                        print(time.time() - t0)
                        game_mode = GameMode.MAIN_MENU
                computer_thread = None

        screen.fill(0)
        display_board(screen, game_state, selected_square, offset)

        game_state.get_moves()
        if not game_mode & GameMode.MENU and (winner := game_state.get_winner()) is not None:
            if not game_mode & GameMode.DEEP_TEST:
                print(winner, game_state.turn, time.time() - t0)
                game_mode = GameMode.MAIN_MENU
                depths[0].clear()
                depths[1].clear()
            else:
                computer_move_result.clear()
                bot0_color: int = 1 if not reverse else -1
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
                if wins + draws + losses == num_lines * 2:
                    game_mode = GameMode.MAIN_MENU
                    print(f"{bots[0].get_version()}: {wins}")
                    print(f"Draws: {draws}")
                    print(f"{bots[1].get_version()}: {losses}")
                    print(f"P-Value: {binomtest(wins, wins + losses)}")
                else:
                    print(wins, draws, losses)
                game_state = game_state_from_line(line)
                assert isinstance(game_state, GameState)
                if game_state_type == GameState:
                    game_state = game_state.to_v2()
                elif game_state_type == GameStateBitboardsV2:
                    game_state = game_state.to_bitboards_v2()
                elif game_state_type == GameStateV3:
                    game_state = game_state.to_v3()
                bots[0].clear_cache()
                bots[1].clear_cache()

        if game_mode & GameMode.MENU:
            if game_mode & GameMode.MAIN:
                for btn in main_buttons: btn.draw(screen, font)
            elif game_mode & GameMode.OPTIONS:
                for btn in options_buttons: btn.draw(screen, font)
        else:
            display_info(screen, game_state, last_eval, font, t0, game_mode, wins, draws, losses, bots, reverse,
                         depths=depths)

        pygame.display.flip()

    pygame.quit()
    sys.exit()
