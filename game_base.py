from typing import Any

class GameStateBase:
    def get_hashable_state(self) -> Any:
        """ Convert the game state into a hashable format for caching. """
        ...

    def get_hashed(self) -> int:
        ...

    def get_moves(self) -> list[tuple[int, int, int, int]]:
        """
        Get all the possible moves for the current player.

        Returns
        -------
        list[tuple[int, int, int, int]]
            A list of tuples, each representing a move in the format (start_row, start_col, end_row, end_col).
        """
        ...

    def get_moves_no_check(self) -> list[tuple[int, int, int, int]]:
        ...

    def are_captures(self) -> bool:
        ...

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
        ...

    def get_winner(self) -> int | None:
        ...
