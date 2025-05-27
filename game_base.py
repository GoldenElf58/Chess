from typing import Any

class GameStateBase:
    def __init__(self, white_queen: bool = True, white_king: bool = True,
                 black_queen: bool = True, black_king: bool = True, last_move: tuple[int, int, int, int] | None = None,
                 color: int = 1, turn: int = 0, winner: int | None = None,
                 previous_position_count: dict[int, int] | None = None, moves_since_pawn: int = 0) -> None:
        self.color: int = color
        self.white_queen: bool = white_queen
        self.white_king: bool = white_king
        self.black_queen: bool = black_queen
        self.black_king: bool = black_king
        self.last_move: tuple[int, int, int, int] = last_move if last_move is not None else (0, 0, 0, 0)
        self.turn: int = turn
        self.winner: int | None = winner
        self.previous_position_count: dict[
            int, int] = previous_position_count if previous_position_count is not None else {}
        self.moves_since_pawn: int = moves_since_pawn
        self.moves: list[tuple[int, int, int, int]] | None = None


    def get_hashable_state(self) -> Any:
        """ Convert the game state into a hashable format for caching. """
        raise NotImplementedError

    def get_hashed(self) -> int:
        raise NotImplementedError

    def get_moves(self) -> list[tuple[int, int, int, int]]:
        """
        Get all the possible moves for the current player.

        Returns
        -------
        list[tuple[int, int, int, int]]
            A list of tuples, each representing a move in the format (start_row, start_col, end_row, end_col).
        """
        raise NotImplementedError

    def get_moves_no_check(self) -> list[tuple[int, int, int, int]]:
        raise NotImplementedError

    def are_captures(self) -> bool:
        raise NotImplementedError

    def move(self, move: tuple[int, int, int, int]) -> 'GameStateBase':
        """
        Make a move on the board.

        Parameters
        ----------
        move : tuple[tuple[int, int], tuple[int, int]]
            The move to make, as a tuple of two tuples. The first tuple is the
            piece to move, with the first element being the row and the second
            element being the column. The second tuple is the destination, with
            the first element being the row and the second element being the
            column.

        Returns
        -------
        GameState
            A new GameState object, with the move applied.
        """
        raise NotImplementedError

    def get_winner(self) -> int | None:
        raise NotImplementedError
