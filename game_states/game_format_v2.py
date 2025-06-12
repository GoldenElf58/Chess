from game_states.game_base import GameStateBase

start_board: tuple[int, ...] = (
    -4, -2, -3, -5, -6, -3, -2, -4,
    -1, -1, -1, -1, -1, -1, -1, -1,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 1, 1, 1, 1,
    4, 2, 3, 5, 6, 3, 2, 4
)


class GameStateFormatV2(GameStateBase):
    def __init__(self, board: tuple[int, ...] | None = None, white_queen: bool = True, white_king: bool = True,
                 black_queen: bool = True, black_king: bool = True,
                 last_move: tuple[int, int, int] | None = None,
                 color: int = 1, turn: int = 0, winner: int | None = None,
                 previous_position_count: dict[int, int] | None = None, moves_since_pawn: int = 0) -> None:
        """
        Initialize a GameStatev2 object.

        Parameters
        ----------
        board : list[list[int]], optional
            The starting board. Defaults to `start_board`.
        white_queen : bool, optional
            Whether the white queen is still on the board. Defaults to True.
        white_king : bool, optional
            Whether the white king is still on the board. Defaults to True.
        black_queen : bool, optional
            Whether the black queen is still on the board. Defaults to True.
        black_king : bool, optional
            Whether the black king is still on the board. Defaults to True.
        last_move : tuple[tuple[int, int], tuple[int, int]], optional
            The last move made, as a tuple of two tuples. Defaults to None.
        color : int, optional
            The color of the current player (1 for white, -1 for black). Defaults to 1.
        turn : int, optional
            The turn number. Defaults to 0.
        winner : int | None, optional
            The winner of the game (1 for white, -1 for black, 0 for draw). Defaults to None.
        previous_position_count : dict[int, int] | None, optional
            A dictionary of previous positions and their counts. Defaults to None.
        moves_since_pawn : int, optional
            The number of moves since the last pawn move. Defaults to 0.
        """
        self.board: tuple[int, ...] = start_board if board is None else board
        self.moves: list[tuple[int, int, int]] | None = None
        self.last_move: tuple[int, int, int] | None = last_move
        super().__init__(white_queen, white_king, black_queen, black_king, color, turn, winner,
                         previous_position_count, moves_since_pawn)

    def get_hashable_state(self) -> tuple[tuple[int, ...], int, bool, bool, bool, bool,
    tuple[int, int, int] | None, int]:
        raise NotImplementedError

    def get_moves(self) -> list[tuple[int, int, int]]:
        raise NotImplementedError

    def get_moves_new(self) -> list[tuple[tuple[int, int, int], 'GameStateFormatV2']]:
        raise NotImplementedError

    def get_moves_no_check(self) -> list[tuple[int, int, int]]:
        raise NotImplementedError

    def are_captures(self) -> bool:
        raise NotImplementedError

    def move(self, move: tuple[int, int, int]) -> 'GameStateFormatV2':
        raise NotImplementedError

    def get_winner(self) -> int | None:
        raise NotImplementedError
