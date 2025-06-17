import random
from math import log2
from random import choice

from game_states.game_bitboards_v3 import GameStateBitboardsV3 as GameStateTest
from game_states import GameStateCorrect, GameState

base_board: tuple[int, ...] = (
    0, 0, 0, 0, 6, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 1,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 1,
    0, 0, 0, 0, -6, 0, 0, 0,
)


def board_move_matches(board: tuple[int, ...], debug: bool = False,
                       castle: bool = False, **kwargs) -> None:
    game_state_test: GameStateTest = GameState(board, castle, castle, castle, castle, **kwargs).to_bitboards_v3()
    game_state_correct: GameStateCorrect = GameStateCorrect(board, castle, castle, castle, castle, **kwargs)
    if len(game_state_test.get_moves()) != len(game_state_correct.get_moves()):
        print(f'Color: {game_state_test.color}, {game_state_correct.color}')
        print(f'Turn: {game_state_test.turn}, {game_state_correct.turn}')
        print(f'Moves Since Pawn: {game_state_test.moves_since_pawn}, {game_state_correct.moves_since_pawn}')
        print(f'Last Move: {game_state_test.last_move}, {game_state_correct.last_move}')
        print(f'White King: {game_state_test.white_king}, {game_state_correct.white_king}')
        print(f'White Queen: {game_state_test.white_queen}, {game_state_correct.white_queen}')
        print(f'Black King: {game_state_test.black_king}, {game_state_correct.black_king}')
        print(f'Black Queen: {game_state_test.black_queen}, {game_state_correct.black_queen}')
        print(game_state_test)
        if str(game_state_test) != str(game_state_correct):
            print(game_state_correct)
        print(game_state_correct.board)
        print()
        print(f'White Pieces: {bin(game_state_test.white_pieces)}')
        print(f'Black Pieces: {bin(game_state_test.black_pieces)}')
        print(f'Kings       : {bin(game_state_test.kings)}')
        print(f'Queens      : {bin(game_state_test.queens)}')
        print(f'Rooks       : {bin(game_state_test.rooks)}')
        print(f'Bishops     : {bin(game_state_test.bishops)}')
        print(f'Knights     : {bin(game_state_test.knights)}')
        print(f'Pawns       : {bin(game_state_test.pawns)}')
        print()
        print(game_state_test.get_winner(), game_state_correct.get_winner())
        print()
        print(game_state_test.get_moves_no_check())
        print([(63 - int(log2(move_0)) if move_0 > 0 else move_0, 63 - int(log2(move_1)) if move_1 > 0 else move_1,
                move_2) for move_0, move_1, move_2 in game_state_test.get_moves_no_check()])
        if game_state_test.get_moves_no_check() != game_state_correct.get_moves_no_check():
            print(game_state_correct.get_moves_no_check())
        print()
        print(game_state_test.get_moves())
        print([(63 - int(log2(move_0)) if move_0 > 0 else move_0, 63 - int(log2(move_1)) if move_1 > 0
        else move_1, move_2) for move_0, move_1, move_2 in game_state_test.get_moves()])
        print(game_state_correct.get_moves())
        print()
    assert len(game_state_test.get_moves()) == len(game_state_correct.get_moves())
    for move_test, move_correct in zip(game_state_test.get_moves(), game_state_correct.get_moves()):
        game_state_test_2 = game_state_test.move(move_test)
        game_state_correct_2 = game_state_correct.move(move_correct)
        if (str(game_state_test) != str(game_state_correct) or
                len(game_state_test_2.get_moves()) != len(game_state_correct_2.get_moves()) or
                game_state_test_2.get_winner() != game_state_correct_2.get_winner()):
            print(f'Moves: {move_test}, {move_correct}')
            print(f'Color: {game_state_test.color}, {game_state_correct.color}')
            print(f'Turn: {game_state_test.turn}, {game_state_correct.turn}')
            print(f'Moves Since Pawn: {game_state_test.moves_since_pawn}, {game_state_correct.moves_since_pawn}')
            print(f'Last Move: {game_state_test.last_move}, {game_state_correct.last_move}')
            print(f'White King: {game_state_test.white_king}, {game_state_correct.white_king}')
            print(f'White Queen: {game_state_test.white_queen}, {game_state_correct.white_queen}')
            print(f'Black King: {game_state_test.black_king}, {game_state_correct.black_king}')
            print(f'Black Queen: {game_state_test.black_queen}, {game_state_correct.black_queen}')
            print()
            print(f'Color: {game_state_test_2.color}, {game_state_correct_2.color}')
            print(f'Turn: {game_state_test_2.turn}, {game_state_correct_2.turn}')
            print(f'Moves Since Pawn: {game_state_test_2.moves_since_pawn}, {game_state_correct_2.moves_since_pawn}')
            print(f'Last Move: {game_state_test_2.last_move}, {game_state_correct_2.last_move}')
            print(f'White King: {game_state_test_2.white_king}, {game_state_correct_2.white_king}')
            print(f'White Queen: {game_state_test_2.white_queen}, {game_state_correct_2.white_queen}')
            print(f'Black King: {game_state_test_2.black_king}, {game_state_correct_2.black_king}')
            print(f'Black Queen: {game_state_test_2.black_queen}, {game_state_correct_2.black_queen}')
            print(game_state_test)
            if str(game_state_test) != str(game_state_correct):
                print(game_state_correct)
            print(game_state_correct.board)
            print()
            print(f'White Pieces: {bin(game_state_test.white_pieces)}')
            print(f'Black Pieces: {bin(game_state_test.black_pieces)}')
            print(f'Kings       : {bin(game_state_test.kings)}')
            print(f'Queens      : {bin(game_state_test.queens)}')
            print(f'Rooks       : {bin(game_state_test.rooks)}')
            print(f'Bishops     : {bin(game_state_test.bishops)}')
            print(f'Knights     : {bin(game_state_test.knights)}')
            print(f'Pawns       : {bin(game_state_test.pawns)}')
            print()
            print(game_state_test_2)
            if str(game_state_test_2) != str(game_state_correct_2):
                print(game_state_correct_2)
            print(game_state_correct_2.board)
            print(game_state_test_2.get_winner(), game_state_correct_2.get_winner())
            print()
            print(f'White Pieces: {bin(game_state_test_2.white_pieces)}')
            print(f'Black Pieces: {bin(game_state_test_2.black_pieces)}')
            print(f'Kings       : {bin(game_state_test_2.kings)}')
            print(f'Queens      : {bin(game_state_test_2.queens)}')
            print(f'Rooks       : {bin(game_state_test_2.rooks)}')
            print(f'Bishops     : {bin(game_state_test_2.bishops)}')
            print(f'Knights     : {bin(game_state_test_2.knights)}')
            print(f'Pawns       : {bin(game_state_test_2.pawns)}')
            print()
            print(game_state_test_2.get_moves_no_check())
            print([(63 - int(log2(move_0)), 63 - int(log2(move_1)), move_2) for move_0, move_1, move_2 in
                   game_state_test_2.get_moves_no_check()])
            if game_state_test_2.get_moves_no_check() != game_state_correct_2.get_moves_no_check():
                print(game_state_correct_2.get_moves_no_check())
            print()
            print(game_state_test_2.get_moves())
            print([(63 - int(log2(move_0)), 63 - int(log2(move_1)), move_2) for move_0, move_1, move_2 in
                   game_state_test_2.get_moves()])
            print(game_state_correct_2.get_moves())
            print()
        assert str(game_state_test_2) == str(game_state_correct_2)
        assert len(game_state_test_2.get_moves()) == len(game_state_correct_2.get_moves())
        assert game_state_test_2.get_winner() == game_state_correct_2.get_winner()

    assert game_state_test.get_winner() == game_state_correct.get_winner()


def board_move_matches_both_colors(board: tuple[int, ...], *, color: int = 1, **kwargs) -> None:
    board_move_matches(board, color=color, **kwargs)
    board_move_matches(tuple(-piece for piece in board), color=-color, **kwargs)


def board_result_matches(board: tuple[int, ...], debug: bool = False, **kwargs) -> None:
    game_state: GameStateTest = GameState(board, **kwargs).to_bitboards_v3()
    game_state_correct: GameStateCorrect = GameStateCorrect(board, **kwargs)
    game_state.get_moves()
    game_state_correct.get_moves()
    if debug:
        print(game_state)
        print(game_state.get_moves())
        print(game_state_correct.get_moves())
        print(game_state.get_winner())
        print(game_state_correct.get_winner())
    assert game_state.get_winner() == game_state_correct.get_winner()


def test_piece_moves_white(debug: bool = False) -> None:
    board_move_matches(tuple(1 * piece if -6 != piece != 6 else piece for piece in base_board), debug=debug)  # Pawn
    board_move_matches(tuple(2 * piece if -6 != piece != 6 else piece for piece in base_board), debug=debug)  # Knight
    board_move_matches(tuple(3 * piece if -6 != piece != 6 else piece for piece in base_board), debug=debug)  # Bishop
    board_move_matches(tuple(4 * piece if -6 != piece != 6 else piece for piece in base_board), debug=debug)  # Rook
    board_move_matches(tuple(5 * piece if -6 != piece != 6 else piece for piece in base_board), debug=debug)  # Queen
    board_move_matches(tuple(6 * piece if -6 != piece != 6 else piece for piece in base_board), debug=debug)  # King


def test_piece_moves_black(debug: bool = False) -> None:
    board_move_matches(tuple(-1 * piece if -6 != piece != 6 else piece for piece in base_board), color=-1,
                       debug=debug)  # Pawn
    board_move_matches(tuple(-2 * piece if -6 != piece != 6 else piece for piece in base_board), color=-1,
                       debug=debug)  # Knight
    board_move_matches(tuple(-3 * piece if -6 != piece != 6 else piece for piece in base_board), color=-1,
                       debug=debug)  # Bishop
    board_move_matches(tuple(-4 * piece if -6 != piece != 6 else piece for piece in base_board), color=-1,
                       debug=debug)  # Rook
    board_move_matches(tuple(-5 * piece if -6 != piece != 6 else piece for piece in base_board), color=-1,
                       debug=debug)  # Queen
    board_move_matches(tuple(-6 * piece if -6 != piece != 6 else piece for piece in base_board), color=-1,
                       debug=debug)  # King


def test_castling_white(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, -6, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        4, 0, 0, 0, 6, 0, 0, 4
    )
    board_move_matches(board, castle=True, debug=debug)


def test_castling_black(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        -4, 0, 0, 0, -6, 0, 0, -4,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 6, 0, 0, 0
    )
    board_move_matches(board, color=-1, castle=True, debug=debug)


def est_en_passant_left_white(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, -1, 1, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 6, 0, -6, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    board_move_matches(board, last_move=(11, 27, -1), debug=debug)


def est_en_passant_right_white(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 1, -1, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 6, 0, -6, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    board_move_matches(board, last_move=(13, 29, -1), debug=debug)


def est_en_passant_left_black(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 6, 0, -6, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 1, -1, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )

    board_move_matches(board, last_move=(51, 35, 1), color=-1, debug=debug)


def ant_right_black(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        6, 0, -6, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, -1, 1, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )

    board_move_matches(board, last_move=(53, 37, 1), color=-1, debug=debug)


def est_en_passant_wrap(debug: bool = True) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 6, 0, -6, 0, 0, 0,
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
        0, 0, 6, 0, -6, 0, 0, 0,
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
        0, 0, -6, 0, 6, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        -1, 0, 0, 0, 0, 0, 0, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    board_move_matches(board, last_move=(8, 24, 1), color=1, debug=debug)

    board = (
        6, 0, 0, 0, 0, 0, 0, -6,
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
        0, 0, 6, 0, -6, 0, 0, 0,
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
        0, 0, 6, 0, -6, 0, 0, 0,
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
        0, 0, 6, 0, -6, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    board_move_matches(board, color=1, debug=debug)


def test_pawn_promotion_black(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 6, 0, -6, 0, 0, 0,
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
    board_move_matches(board, castle=True, color=1, debug=debug)
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
    board_move_matches(board, castle=True, color=-1, debug=debug)


def test_castle_from_pawn_check(debug: bool = False) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, -6, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, -1, 0, 0, 0, 0,
        4, 0, 0, 0, 6, 0, 0, 4
    )
    board_move_matches(board, castle=True, color=1, debug=debug)
    board = (
        -4, 0, 0, 0, -6, 0, 0, -4,
        0, 0, 0, 0, 0, 1, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 6, 0, 0, 0, 0,
    )
    board_move_matches(board, castle=True, color=-1, debug=debug)


def ant_discover_check(debug: bool = False) -> None:
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


def ant_checkmate(debug: bool = False) -> None:
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


def test_other_games(debug: bool = False) -> None:
    boards: list[tuple[int, ...]] = [
        (0, 0, 0, 0, 0, 0, 0, -6,
         0, 0, 2, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 2, 0, 4, 0, 0,
         1, 0, 3, 0, 0, 0, 0, 1,
         0, 0, 0, 0, 0, 0, 0, 1,
         0, 0, 0, 0, 0, 0, 6, 0,),
        (0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, -6, 0, 0,
         -4, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 6, 0,
         0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0,),
        (0, 0, 0, 0, 0, 0, -6, 0,
         0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0,
         0, -1, 0, 0, 0, 0, 0, 0,
         0, 1, 0, -5, 0, 0, 0, 0,
         0, -2, 0, 0, 0, 6, 0, 0,
         0, 0, -4, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -6, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, -6, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (-4, 0, 0, -5, -6, 0, -2, -4, -1, -1, 0, -3, 0, 0, 0, -1, 0, 0, -1, 0, -1, 0, -1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
         0, 0, 0, 0, -1, 1, 0, 2, 0, 0, 1, -2, 2, 0, 3, 1, -3, 5, 0, 1, 1, 0, 1, 4, 0, 3, 0, 6, 0, 0, 4),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -6, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0,
         0, 0, 0, -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (-4, -2, -3, 0, -6, -3, 0, -4, 0, -1, -1, -1, 0, -1, -1, 0, 0, 0, 0, 0, 0, -2, 0, 0, -1, 3, 0, 0, 0, 0, 2, -1,
         1, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 4, 2, 3, 5, 6, 0, 0, 4),
        (-4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -6, 0, -5, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
         0, -6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -6, 0, 0, 0, -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0),
        (0, 0, -5, 0, -6, 0, 0, -4, -4, 0, -1, -3, -2, -1, -1, 0, 0, 0, 1, 0, -1, -3, 3, 0, -1, 2, 0, 0, 0, 0, 0, -1,
         -2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 2, 0, 0, 0, 1, 0, 4, 0, 3, 5, 6, 4, 0, 0),
        (0, 0, 0, 0, 0, 0, -6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
         -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -6, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0,
         0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         -6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (0, -4, 0, 0, 0, -3, -2, 0, 0, -3, 0, -1, 0, -6, 0, -4, -2, -1, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1, -5, 0, 0, 2,
         0, -1, 0, 0, -1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 6, 0, 0, 0, 4, 0, 3, 0, 0, -4, 2, 4),
    ]

    for i, board in enumerate(boards):
        if i in (7, 11):
            board_move_matches(board, castle=True, debug=debug)
        board_move_matches_both_colors(board, debug=debug)


def test_random_games(debug: bool = False, n: int = 1) -> None:
    for i in range(n):
        if debug:
            print(i)
        game_state_test = GameStateTest()
        game_state_correct = GameStateCorrect()
        while game_state_test.get_winner() is None:
            move_idx = random.randint(0, len(game_state_test.get_moves()) - 1)
            game_state_last = game_state_correct
            game_state_test = game_state_test.move(game_state_test.get_moves()[move_idx])
            game_state_correct = game_state_correct.move(game_state_correct.get_moves()[move_idx])
            if (str(game_state_test) != str(game_state_correct) or
                    len(game_state_test.get_moves()) != len(game_state_correct.get_moves()) or
                    game_state_test.get_winner() != game_state_correct.get_winner() or not
                    (game_state_test.white_king == game_state_correct.white_king and
                     game_state_test.white_queen == game_state_correct.white_queen and
                     game_state_test.black_king == game_state_correct.black_king and
                     game_state_test.black_queen == game_state_correct.black_queen)):
                print()
                print(game_state_test.__repr__())
                print()
                print(game_state_correct.__repr__())
                print()
                print(f'Index: {i}')
                print(f'Move Index: {move_idx}')
                print(f'Color: {game_state_test.color}, {game_state_correct.color}')
                print(f'Turn: {game_state_test.turn}, {game_state_correct.turn}')
                print(f'Moves Since Pawn: {game_state_test.moves_since_pawn}, {game_state_correct.moves_since_pawn}')
                print(f'Last Move: {game_state_test.last_move}, {game_state_correct.last_move}')
                print(f'White King: {game_state_test.white_king}, {game_state_correct.white_king}')
                print(f'White Queen: {game_state_test.white_queen}, {game_state_correct.white_queen}')
                print(f'Black King: {game_state_test.black_king}, {game_state_correct.black_king}')
                print(f'Black Queen: {game_state_test.black_queen}, {game_state_correct.black_queen}')
                print(game_state_last)
                print(game_state_last.board)
                print(game_state_test)
                if str(game_state_test) != str(game_state_correct):
                    print(game_state_correct)
                print(game_state_correct.board)
                print()
                print(f'White Pieces: {bin(game_state_test.white_pieces)}')
                print(f'Black Pieces: {bin(game_state_test.black_pieces)}')
                print(f'Kings       : {bin(game_state_test.kings)}')
                print(f'Queens      : {bin(game_state_test.queens)}')
                print(f'Rooks       : {bin(game_state_test.rooks)}')
                print(f'Bishops     : {bin(game_state_test.bishops)}')
                print(f'Knights     : {bin(game_state_test.knights)}')
                print(f'Pawns       : {bin(game_state_test.pawns)}')
                print()
                print(game_state_test.get_winner(), game_state_correct.get_winner())
                print()
                print(game_state_test.get_moves_no_check())
                print([(63 - int(log2(move_0)) if move_0 > 0 else move_0,
                        63 - int(log2(move_1)) if move_1 > 0 else move_1,
                        move_2) for move_0, move_1, move_2 in game_state_test.get_moves_no_check()])
                if game_state_test.get_moves_no_check() != game_state_correct.get_moves_no_check():
                    print(game_state_correct.get_moves_no_check())
                print()
                print(game_state_test.get_moves())
                print([(63 - int(log2(move_0)) if move_0 > 0 else move_0, 63 - int(log2(move_1)) if move_1 > 0
                else move_1, move_2) for move_0, move_1, move_2 in game_state_test.get_moves()])
                print(game_state_correct.get_moves())
                print()
            assert game_state_test.get_winner() == game_state_correct.get_winner()
            if game_state_test.get_winner() is not None:
                break
            assert str(game_state_test) == str(game_state_correct)
            assert (game_state_test.white_king == game_state_correct.white_king and
                    game_state_test.white_queen == game_state_correct.white_queen and
                    game_state_test.black_king == game_state_correct.black_king and
                    game_state_test.black_queen == game_state_correct.black_queen)
            assert len(game_state_test.get_moves()) == len(game_state_correct.get_moves())


def test_deep_positions(debug: bool = False) -> None:
    game_state_test = GameStateTest()
    game_state_correct = GameStateCorrect()

    deep_test(game_state_test, game_state_correct, depth=2, debug=debug)


def deep_test(game_state_test, game_state_correct, depth, debug) -> None:
    if debug:
        print(game_state_test)
        print(game_state_test.get_moves())
        print(game_state_correct.get_moves())
        print(game_state_test.get_winner())
        print(game_state_correct.get_winner())

    moves_test = game_state_test.get_moves()
    moves_correct = game_state_correct.get_moves()
    assert len(moves_test) == len(moves_correct)
    assert game_state_test.get_winner() == game_state_correct.get_winner()

    if depth > 0:
        for move_test, move_correct in zip(moves_test, moves_correct):
            deep_test(game_state_test.move(move_test), game_state_correct.move(move_correct), depth - 1, debug)


def main() -> None:
    test_random_games(True, 10_000)


if __name__ == '__main__':
    main()
