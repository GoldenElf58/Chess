from game_states.game_v3 import GameStateV3 as GameStateTest
from game_states.correct_game_v2 import GameStateCorrect

base_board: tuple[int, ...] = (
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 1,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 1,
    0, 0, 0, 0, 0, 0, 0, 0,
)


def test_create_start_board() -> None:
    assert GameStateTest().board == GameStateCorrect().board


def board_move_matches(board: tuple[int, ...], debug: bool = False, **kwargs) -> None:
    game_state: GameStateTest = GameStateTest(board, **kwargs)
    game_state_correct: GameStateCorrect = GameStateCorrect(board, **kwargs)
    if debug:
        print(game_state.board)
        print(game_state_correct.board)
        print(game_state.get_moves())
        print(game_state_correct.get_moves())
        print(game_state.get_winner())
        print(game_state_correct.get_winner())
    assert game_state.get_moves() == game_state_correct.get_moves()
    for move in game_state.get_moves():
        game_state_2 = game_state.move(move)
        game_state_correct_2 = game_state_correct.move(move)
        if debug:
            print(move)
            print(game_state_2)
            print(game_state_correct_2)
            print(game_state_2.get_moves())
            print(game_state_correct_2.get_moves())
            print(game_state_2.get_winner())
            print(game_state_correct_2.get_winner())
            print()
        assert game_state_2.board == game_state_correct_2.board
        assert game_state_2.get_moves() == game_state_correct_2.get_moves()
        assert game_state_2.get_winner() == game_state_correct_2.get_winner()

    assert game_state.get_winner() == game_state_correct.get_winner()


def board_move_matches_both_colors(board: tuple[int, ...], *, color: int = 1, **kwargs) -> None:
    board_move_matches(board, color=color, **kwargs)
    board_move_matches(tuple(-piece for piece in board), color=-color, **kwargs)


def board_result_matches(board: tuple[int, ...], **kwargs) -> None:
    game_state: GameStateTest = GameStateTest(board, **kwargs)
    game_state_correct: GameStateCorrect = GameStateCorrect(board, **kwargs)
    assert game_state.get_winner() == game_state_correct.get_winner()


def test_piece_moves_white(debug: bool = False) -> None:
    board_move_matches(tuple(1 * piece for piece in base_board), debug=debug)  # Pawn
    board_move_matches(tuple(2 * piece for piece in base_board), debug=debug)  # Knight
    board_move_matches(tuple(3 * piece for piece in base_board), debug=debug)  # Bishop
    board_move_matches(tuple(4 * piece for piece in base_board), debug=debug)  # Rook
    board_move_matches(tuple(5 * piece for piece in base_board), debug=debug)  # Queen
    board_move_matches(tuple(6 * piece for piece in base_board), debug=debug)  # King


def test_piece_moves_black(debug: bool = False) -> None:
    board_move_matches(tuple(-1 * piece for piece in base_board), color=-1, debug=debug)  # Pawn
    board_move_matches(tuple(-2 * piece for piece in base_board), color=-1, debug=debug)  # Knight
    board_move_matches(tuple(-3 * piece for piece in base_board), color=-1, debug=debug)  # Bishop
    board_move_matches(tuple(-4 * piece for piece in base_board), color=-1, debug=debug)  # Rook
    board_move_matches(tuple(-5 * piece for piece in base_board), color=-1, debug=debug)  # Queen
    board_move_matches(tuple(-6 * piece for piece in base_board), color=-1, debug=debug)  # King


def test_castling_white(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        4, 0, 0, 0, 6, 0, 0, 4
    )
    board_move_matches(board, debug=debug)


def test_castling_black(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        -4, 0, 0, 0, -6, 0, 0, -4,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    board_move_matches(board, color=-1, debug=debug)


def test_en_passant_left_white(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, -1, 1, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    board_move_matches(board, last_move=(11, 27, -1), debug=debug)


def test_en_passant_right_white(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 1, -1, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    board_move_matches(board, last_move=(13, 29, -1), debug=debug)


def test_en_passant_left_black(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 1, -1, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )

    board_move_matches(board, last_move=(51, 35, 1), color=-1, debug=debug)


def test_en_passant_right_black(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, -1, 1, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )

    board_move_matches(board, last_move=(53, 37, 1), color=-1, debug=debug)


def test_en_passant_wrap(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        1, 0, 0, 0, 0, 0, 0, -1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    board_move_matches(board, last_move=(48, 32, 1), color=-1, debug=debug)

    board = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        -1, 0, 0, 0, 0, 0, 0, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    board_move_matches(board, last_move=(55, 39, 1), color=-1, debug=debug)

    board = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        -1, 0, 0, 0, 0, 0, 0, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    board_move_matches(board, last_move=(8, 24, 1), color=1, debug=debug)

    board = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        1, 0, 0, 0, 0, 0, 0, -1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    board_move_matches(board, last_move=(15, 31, 1), color=1, debug=debug)


def test_pawn_double_push_white(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        1, 1, 1, 1, 1, 1, 1, 1,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    board_move_matches(board, color=1, debug=debug)


def test_pawn_double_push_black(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        -1, -1, -1, -1, -1, -1, -1, -1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    board_move_matches(board, color=-1, debug=debug)


def test_pawn_promotion_white(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        1, 1, 1, 1, 1, 1, 1, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    board_move_matches(board, color=1, debug=debug)


def test_pawn_promotion_black(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        -1, -1, -1, -1, -1, -1, -1, -1,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    board_move_matches(board, color=-1, debug=debug)


def test_pawn_promotion_taking_white(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        -2, -2, -2, -2, -2, -2, -2, -2,
        1, 1, 1, 1, 1, 1, 1, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        6, 0, 0, 0, 0, 0, 0, -6
    )
    board_move_matches(board, debug=debug, color=1)


def test_pawn_promotion_taking_black(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        6, 0, 0, 0, 0, 0, 0, -6,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        -1, -1, -1, -1, -1, -1, -1, -1,
        2, 2, 2, 2, 2, 2, 2, 2
    )
    board_move_matches(board, color=-1, debug=debug)


def test_stalemate(debug: bool = False) -> None:
    boards: list[tuple[int, ...]] = [
        (
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 6, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, -6, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
        ),
        (
            6, 0, 0, 0, 0, 0, 0, 0,
            0, 0, -5, -6, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
        ),
    ]
    for board in boards:
        board_result_matches(board, debug=debug, color=1)


def test_castle_through_check(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, -6, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, -5, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        4, 0, 0, 0, 6, 0, 0, 4
    )
    board_move_matches(board, color=1, debug=debug)
    board = (
        -4, 0, 0, 0, -6, 0, 0, -4,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 5, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 6, 0, 0, 0, 0,
    )
    board_move_matches(board, color=-1, debug=debug)


def test_en_passant_discover_check(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        6, 1, -1, 0, -5, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, -6
    )
    board_move_matches(board, color=1, last_move=(10, 26, -1), debug=debug)


def test_check_pin_rook(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        -6, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, -4, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 3, 0, 0, 0, 0,
        0, 0, 0, 6, 0, 0, 0, 0
    )
    board_move_matches_both_colors(board, debug=debug)


def test_check_pin_bishop(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        -6, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, -3, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 4, 0, 0, 0, 0,
        0, 0, 0, 0, 6, 0, 0, 0,
    )
    board_move_matches_both_colors(board, debug=debug)


def test_walk_into_knight(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        -6, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, -2, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 6, 0, 0, 0, 0,
    )
    board_move_matches_both_colors(board, debug=debug)


def test_walk_into_king(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, -6, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 6, 0, 0, 0, 0,
    )
    board_move_matches_both_colors(board, debug=debug)
    board_move_matches_both_colors(board, color=-1, debug=debug)


def test_walk_into_pawn(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        -6, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, -1, 0, 0, 0, 0,
        0, 0, 0, 6, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
    )
    board_move_matches(board, color=1, debug=debug)

    board = (
        6, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, -6, 0, 0, 0, 0,
        0, 0, 0, 1, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
    )
    board_move_matches(board, color=-1, debug=debug)


def test_check_rook_block(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        -6, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, -4, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 2, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 4, 0,
        0, 0, 0, 3, 6, 0, 0, 0,
    )
    board_move_matches_both_colors(board, debug=debug)


def test_check_bishop_block(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        -6, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, -3,
        0, 0, 0, 2, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 4, 0,
        0, 0, 0, 0, 6, 0, 3, 0,
    )
    board_move_matches_both_colors(board, debug=debug)


def test_avoid_rook_check(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        -6, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, -4, 0, 0, 2,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 6, 0, 0, 0,
    )
    board_move_matches_both_colors(board, debug=debug)


def test_avoid_bishop_check(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        -6, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, -3, 0, 0, 0, 0, 0, 2,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 6, 0, 0, 0,
    )
    board_move_matches_both_colors(board, debug=debug)


def test_avoid_knight_check(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        -6, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        2, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, -2, 0,
        0, 0, 0, 0, 6, 0, 0, 0,
    )
    board_move_matches_both_colors(board, debug=debug)


def test_avoid_pawn_check(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        -6, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        1, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, -1, 0, 0,
        0, 0, 0, 0, 6, 0, 0, 0,
    )
    board_move_matches(board, color=1, debug=debug)

    board = (
        6, 0, 0, 0, 0, -6, 0, 0,
        0, 0, 0, 0, 1, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        -1, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
    )
    board_move_matches(board, color=-1, debug=debug)


def test_latter_checkmate(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        -6, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 4, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 6, 0, 0,
        0, 0, 4, 0, 6, 0, 0, 0,
    )
    board_move_matches_both_colors(board, debug=debug)


def test_en_passant_checkmate(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 4, 0, 0, 0, 5,
        6, 0, -6, 0, 0, 0, 0, 0,
        4, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, -1, 1, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
    )
    board_move_matches(board, last_move=(11, 27, -1), color=1, debug=debug)

    board = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 1, -1, 0, 0, 0,
        -4, 0, 0, 0, 0, 0, 0, 0,
        -6, 0, 6, 0, 0, 0, 0, 0,
        0, 0, 0, -4, 0, 0, 0, -5,
    )
    board_move_matches(board, last_move=(51, 35, 1), color=-1, debug=debug)
