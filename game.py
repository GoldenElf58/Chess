import copy

from utils import split_table

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


class GameState:
    def __init__(self, board: tuple | None = None, white_queen: bool = True, white_king: bool = True,
                 black_queen: bool = True, back_king: bool = True, last_move: tuple[int, int, int, int] | None = None,
                 color=1, turn=0, winner: int | None = None, previous_position_count: dict[int, int] | None = None,
                 moves_since_pawn: int = 0) -> None:
        """
        Initialize a GameState object.

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
        back_king : bool, optional
            Whether the black king is still on the board. Defaults to True.
        last_move : tuple[tuple[int, int], tuple[int, int]], optional
            The last move made, as a tuple of two tuples. Defaults to None.
        color : int, optional
            The color of the current player (1 for white, -1 for black). Defaults to 1.
        """
        if board is None:
            board = start_board
        self.board: tuple[int, ...] = board
        self.color: int = color
        self.white_queen: bool = white_queen
        self.white_king: bool = white_king
        self.black_queen: bool = black_queen
        self.black_king: bool = back_king
        self.last_move: tuple[int, int, int, int] = last_move if last_move is not None else (0, 0, 0, 0)
        self.turn: int = turn
        self.winner: int | None = winner
        self.previous_position_count: dict[
            int, int] = previous_position_count if previous_position_count is not None else {}
        self.moves_since_pawn: int = moves_since_pawn
        self.moves: list[tuple[int, int, int, int]] | None = None

    def get_hashable_state(self) -> tuple[tuple[int, ...], int, bool, bool, bool, bool, tuple[int, int, int, int]]:
        """ Convert the game state into a hashable format for caching. """
        board_tuple: tuple[int, ...] = self.board  # Convert board to tuple
        return board_tuple, self.color, self.white_queen, self.white_king, self.black_queen, self.black_king, self.last_move

    def get_efficient_hashable_state_hashed(self) -> int:
        return hash(self.get_efficient_hashable_state())

    def get_efficient_hashable_state(self) -> tuple[tuple[int, ...], int, tuple[int, int, int, int]]:
        return self.board, (((self.color == 1) << 4) | (self.white_queen << 3) | (self.white_king << 2) | (
                self.black_queen << 1) | self.black_king), self.last_move

    def get_moves(self) -> list[tuple[int, int, int, int]]:
        """
        Get all the possible moves for the current player.

        Returns
        -------
        list[tuple[int, int, int, int]]
            A list of tuples, each representing a move in the format (start_row, start_col, end_row, end_col).
        """
        if self.moves is not None: return self.moves
        moves: list[tuple[int, int, int, int]] = self.get_moves_no_check()
        moves_len: int = len(moves)
        winner: int | None = 0
        for i, move_0 in enumerate(reversed(moves)):
            state: GameState = self.move(move_0)
            for move_1 in state.get_moves_no_check():
                if (winner := state.move(move_1).get_winner()) in {-1, 1}:
                    moves.pop(moves_len - i - 1)
                    break
        if len(moves) == 0 and moves_len > 0:
            self.winner = winner
        elif self.moves_since_pawn >= 50:
            self.winner = 0
        self.moves = moves
        return moves

    def get_moves_no_check(self) -> list[tuple[int, int, int, int]]:
        hash_state: tuple[
            tuple[int, ...], int, bool, bool, bool, bool, tuple[int, int, int, int]] = self.get_hashable_state()
        return self.get_moves_no_check_static(*hash_state)

    @staticmethod
    def get_moves_no_check_static(board, color, white_queen, white_king, black_queen, black_king, last_move) -> list[
        tuple[int, int, int, int]]:
        moves: list[tuple[int, int, int, int]] = []
        for h, piece in enumerate(board):
            i, j = h // 8, h % 8
            if piece * color <= 0:  # If piece is 0, blank so skip; if color doesn't match player color skip
                continue
            piece_type: int = abs(piece)
            if piece_type == 6:  # King
                if (((color == 1 and white_king) or (color == -1 and black_king))
                        and board[h - j + 7] == 4 * color and {board[h - j + 5], board[h - j + 6]} == {0}):
                    moves.append((-1, 1, i, j))
                if (((color == 1 and white_queen) or (color == -1 and black_queen))
                        and board[h - j + 7] == 4 * color and {board[h - j + 1], board[h - j + 2],
                                                               board[h - j + 3]} == {0}):
                    moves.append((-1, -1, i, j))
                for k in range(-1, 2):
                    for l in range(-1, 2):
                        if (i + k) % 8 != i + k or (j + l) % 8 != j + l:
                            continue
                        if board[(i + k) * 8 + (j + l)] * color <= 0:
                            moves.append((i, j, i + k, j + l))
            if piece_type == 4 or piece_type == 5:  # Rook and Queen
                for k in range(j + 1, 8):
                    if board[h - j + k] * color <= 0:
                        moves.append((i, j, i, k))
                    if board[h - j + k] == 0:
                        continue
                    break
                for k in range(j - 1, -1, -1):
                    if board[h - j + k] * color <= 0:
                        moves.append((i, j, i, k))
                    if board[h - j + k] == 0:
                        continue
                    break
                for k in range(i - 1, -1, -1):
                    if board[k * 8 + j] * color <= 0:
                        moves.append((i, j, k, j))
                    if board[k * 8 + j] == 0:
                        continue
                    break
                for k in range(i + 1, 8):
                    if board[k * 8 + j] * color <= 0:
                        moves.append((i, j, k, j))
                    if board[k * 8 + j] == 0:
                        continue
                    break
            if piece_type == 3 or piece_type == 5:  # Bishop and Queen
                for k in range(1, 8):
                    if i + k > 7 or j + k > 7:
                        break
                    if board[(i + k) * 8 + (j + k)] * color <= 0:
                        moves.append((i, j, i + k, j + k))
                    if board[(i + k) * 8 + (j + k)] == 0:
                        continue
                    break
                for k in range(1, 8):
                    if i - k < 0 or j + k > 7:
                        break
                    if board[(i - k) * 8 + (j + k)] * color <= 0:
                        moves.append((i, j, i - k, j + k))
                    if board[(i - k) * 8 + (j + k)] == 0:
                        continue
                    break
                for k in range(1, 8):
                    if i + k > 7 or j - k < 0:
                        break
                    if board[(i + k) * 8 + (j - k)] * color <= 0:
                        moves.append((i, j, i + k, j - k))
                    if board[(i + k) * 8 + (j - k)] == 0:
                        continue
                    break
                for k in range(1, 8):
                    if i - k < 0 or j - k < 0:
                        break
                    if board[(i - k) * 8 + (j - k)] * color <= 0:
                        moves.append((i, j, i - k, j - k))
                    if board[(i - k) * 8 + (j - k)] == 0:
                        continue
                    break
            if piece_type == 2:  # Knight
                for k in range(-2, 3, 4):
                    for l in range(-1, 2, 2):
                        if (i + k) % 8 == i + k and (j + l) % 8 == j + l and board[
                            (i + k) * 8 + (j + l)] * color <= 0:
                            moves.append((i, j, i + k, j + l))
            if piece_type == 1:  # Pawn
                forward: bool = (i - color) % 8 == i - color
                if forward and board[(i - color) * 8 + j] == 0:
                    if i - color != 0 and i - color != 7:
                        moves.append((i, j, i - color, j))
                    elif i - color == 0:  # Promotion
                        moves.append((-3, 2, i, j))
                        moves.append((-3, 3, i, j))
                        moves.append((-3, 4, i, j))
                        moves.append((-3, 5, i, j))
                    elif i - color == 7:  # Promotion
                        moves.append((-3, -2, i, j))
                        moves.append((-3, -3, i, j))
                        moves.append((-3, -4, i, j))
                        moves.append((-3, -5, i, j))
                if forward and (j + 1) % 8 == j + 1 and board[(i - color) * 8 + (j + 1)] * color < 0:
                    if i - color != 0 and i - color != 7:
                        moves.append((i, j, i - color, j + 1))
                    elif i - color == 0 or i - color == 7:  # Promotion
                        moves.append((-4, 1, i, j))
                        moves.append((-5, 1, i, j))
                        moves.append((-6, 1, i, j))
                        moves.append((-7, 1, i, j))
                if forward and (j - 1) % 8 == j - 1 and board[(i - color) * 8 + (j - 1)] * color < 0:
                    if i - color != 0 and i - color != 7:
                        moves.append((i, j, i - color, j - 1))
                    elif i - color == 0 or i - color == 7:  # Promotion
                        moves.append((-4, -1, i, j))
                        moves.append((-5, -1, i, j))
                        moves.append((-6, -1, i, j))
                        moves.append((-7, -1, i, j))
                if forward and color == 1 and i == 6 and board[4 * 8 + j] == 0 and board[5 * 8 + j] == 0:
                    moves.append((i, j, 4, j))
                if forward and color == -1 and i == 1 and board[3 * 8 + j] == 0 and board[2 * 8 + j] == 0:
                    moves.append((i, j, 3, j))
                # En Passant
                if (last_move is not None and board[last_move[2] * 8 + last_move[3]] == -color and abs(
                        last_move[2] - last_move[0]) == 2 and i == last_move[2]):
                    if j == last_move[3] + 1 and j < 7:
                        moves.append((-2, 1, i, j))
                    if j == last_move[3] - 1 and j > 0:
                        moves.append((-2, -1, i, j))
        return moves

    def are_captures(self) -> bool:
        moves: list[tuple[int, int, int, int]] = self.get_moves()
        empty_count: int = 0
        for piece in self.board:
            if piece == 0:
                empty_count += 1
        current_empty_count: int = 0
        for move in moves:
            for piece in self.move(move).board:
                if piece == 0:
                    current_empty_count += 1
            if current_empty_count != empty_count:
                return True
        return False

    def move(self, move: tuple[int, int, int, int]) -> 'GameState':
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
        new_board: list[int] = list(self.board)
        white_queen: bool = self.white_queen
        white_king: bool = self.white_king
        black_queen: bool = self.black_queen
        black_king: bool = self.black_king
        new_moves_since_pawn: int = self.moves_since_pawn + 1

        if len(move) == 0:
            return GameState(tuple(new_board), turn=self.turn + 1, winner=self.winner)

        if move[0] == -1:  # Castle
            if move[2] == 7:
                white_queen = False
                white_king = False
            else:
                black_queen = False
                black_king = False
            new_board[move[2] * 8 + move[3]] = 0
            new_board[move[2] * 8 + (0 if move[1] == -1 else 7)] = 0
            new_board[move[2] * 8 + 4 + move[1] * 2] = self.board[move[2] * 8 + move[3]]
            new_board[move[2] * 8 + 4 + move[1]] = self.board[move[2] * 8 + (0 if move[1] == -1 else 7)]
            return GameState(tuple(new_board), white_queen, white_king, black_queen, black_king,
                             color=-self.color, turn=self.turn + 1, moves_since_pawn=new_moves_since_pawn)

        if move[0] == -2:  # En Passant
            new_board[move[2] * 8 + move[3]] = 0
            new_board[(move[2] - self.color) * 8 + move[3] + move[1]] = self.board[move[2] * 8 + move[3]]
            new_board[move[2] * 8 + move[3] + move[1]] = 0
            return GameState(tuple(new_board), white_queen, white_king, black_queen, black_king,
                             color=-self.color, turn=self.turn + 1, moves_since_pawn=0)

        if move[0] == -3:  # Promotion
            new_board[move[2] * 8 + move[3]] = 0
            new_board[(move[2] - self.color) * 8 + move[3]] = move[1]
            return GameState(tuple(new_board), white_queen, white_king, black_queen, black_king, color=-self.color,
                             turn=self.turn + 1, moves_since_pawn=0)

        if move[0] <= -4:  # Promotion while taking
            new_board[move[2] * 8 + move[3]] = 0
            new_board[(move[2] - self.color) * 8 + (move[3] + move[1])] = (move[0] + 2) * -self.color

            return GameState(tuple(new_board), white_queen, white_king, black_queen, black_king,
                             color=-self.color, turn=self.turn + 1, moves_since_pawn=0)

        condition2: bool = new_board[move[0] * 8 + move[1]] in {-6, -4, 4, 6}
        if new_board[move[2] * 8 + move[3]] in {-4, 4} or condition2:  # Can never take kings
            if move[2] == 7 and move[3] == 0:
                white_queen = False
            if move[2] == 7 and move[3] == 7:
                white_king = False
            if move[2] == 0 and move[3] == 0:
                black_queen = False
            if move[2] == 0 and move[3] == 7:
                black_king = False
        if condition2:
            if move[2] == 0 and move[3] == 4:
                black_queen = False
                black_king = False
            if move[2] == 7 and move[3] == 4:
                white_queen = False
                white_king = False

        if self.board[move[0] * 8 + move[1]] in {-1, 1}:
            new_moves_since_pawn = 0

        new_board[move[2] * 8 + move[3]] = new_board[move[0] * 8 + move[1]]
        new_board[move[0] * 8 + move[1]] = 0
        new_previous_position_count = copy.copy(self.previous_position_count)
        if (hash_state := hash(self.board)) in new_previous_position_count:
            new_previous_position_count[hash_state] += 1
            if new_previous_position_count[hash_state] >= 3:
                return GameState(tuple(new_board), winner=0)
        else:
            new_previous_position_count[hash_state] = 1
        last_move: tuple[int, int, int, int] | None = move if (
                self.board[move[0] * 8 + move[1]] == 1 and (move[0] == move[2] - self.color * 2)) else None
        return GameState(tuple(new_board), white_queen, white_king, black_queen, black_king, last_move=last_move,
                         color=-self.color, turn=self.turn + 1, moves_since_pawn=new_moves_since_pawn,
                         previous_position_count=new_previous_position_count)

    def get_winner(self) -> int | None:
        if self.winner is not None:
            return self.winner
        if self.moves_since_pawn >= 50:
            self.winner = 0
            return 0
        white: bool = False
        black: bool = False
        empty: int = 0
        for piece in self.board:
            if piece == 0:
                empty += 1
            elif piece == 6:
                white = True
            elif piece == -6:
                black = True
        if white and not black:
            self.winner = 1
        elif black and not white:
            self.winner = -1
        elif (not black and not white) or empty == 62:
            self.winner = 0
        return self.winner

    def __repr__(self) -> str:
        """
        Return a string representation of the board.

        This string is an 8x8 grid of characters, with each character
        representing a piece on the board. The characters are as follows:

        - K: King
        - Q: Queen
        - R: Rook
        - B: Bishop
        - N: Knight
        - P: Pawn
        -  : Empty space
        - k: Black King
        - q: Black Queen
        - r: Black Rook
        - b: Black Bishop
        - n: Black Knight
        - p: Black Pawn

        The string is formatted with lines separating each row of the board,
        and pipes (|) separating each column.

        :return: A string representation of the board.
        """
        result: str = "_________________________________\n"
        for row in split_table(self.board):
            result += "| "
            for piece in row:
                if piece == 6:
                    result += "K"
                elif piece == 5:
                    result += "Q"
                elif piece == 4:
                    result += "R"
                elif piece == 3:
                    result += "B"
                elif piece == 2:
                    result += "N"
                elif piece == 1:
                    result += "P"
                elif piece == 0:
                    result += " "
                elif piece == -6:
                    result += "k"
                elif piece == -5:
                    result += "q"
                elif piece == -4:
                    result += "r"
                elif piece == -3:
                    result += "b"
                elif piece == -2:
                    result += "n"
                elif piece == -1:
                    result += "p"
                result += " | "
            result += "\n|___|___|___|___|___|___|___|___|\n"

        return result
