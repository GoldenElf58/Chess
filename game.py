import copy

from utils import flatten, split_table

start_board: list[list[int]] = [[-4, -2, -3, -5, -6, -3, -2, -4],
                                [-1, -1, -1, -1, -1, -1, -1, -1],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [1, 1, 1, 1, 1, 1, 1, 1],
                                [4, 2, 3, 5, 6, 3, 2, 4]]

move_lookup_white: dict[int, list[tuple[int, int, int, int]]] = {}
move_lookup_black: dict[int, list[tuple[int, int, int, int]]] = {}


class GameState:
    def __init__(self, board=None, white_queen=True, white_king=True, black_queen=True, back_king=True, last_move=None,
                 color=1, turn=0, draw=False):
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
            board = flatten(start_board)
        self.board: list[int] = board
        self.color = color
        self.white_queen: bool = white_queen
        self.white_king: bool = white_king
        self.black_queen: bool = black_queen
        self.black_king: bool = back_king
        self.last_move = last_move
        self.turn = turn
        self.draw = draw

    def get_hashable_state(self):
        """ Convert the game state into a hashable format for caching. """
        board_tuple = tuple(self.board)  # Convert board to tuple
        return board_tuple, self.color, self.white_queen, self.white_king, self.black_queen, self.black_king, self.last_move

    def get_efficient_hashable_state_hashed(self):
        return hash(self.get_efficient_hashable_state())

    def get_efficient_hashable_state(self):
        return tuple(self.board), (((self.color == 1) << 4) | (self.white_queen << 3) | (self.white_king << 2) | (
                    self.black_queen << 1) | self.black_king), self.last_move

    def get_moves(self):
        """
        Get all possible moves, using caching based on the board's state.
        """
        hash_state = self.get_hashable_state()
        # hash_state_efficient = hash(hash_state)
        return GameState.get_moves_cached(*hash_state)

    @staticmethod
    def get_moves_cached(board, color, white_queen, white_king, black_queen, black_king, last_move) -> list[
        tuple[int, int, int, int]]:
        # global move_lookup_white, move_lookup_black
        """
        Get all the possible moves for the current player.

        Parameters
        ----------
        board : list[int]
            A flat list of 64 integers representing the board state.
        color : int, optional
            The color of the player to get the moves for (1 for white, -1 for black). Defaults to `self.color`.
        white_queen : bool
            Indicates if the white queen is still on the board.
        white_king : bool
            Indicates if the white king is still on the board.
        black_queen : bool
            Indicates if the black queen is still on the board.
        black_king : bool
            Indicates if the black king is still on the board.
        last_move : tuple[int, int, int, int] or None
            The last move made on the board, represented as a tuple of four integers, or None if no move has been made.

        Returns
        -------
        list[tuple[int, int, int, int]]
            A list of tuples, each representing a move in the format (start_row, start_col, end_row, end_col).
        """
        # if color == 1 and hash_state in move_lookup_white:
        #     return move_lookup_white[hash_state]
        # elif hash_state in move_lookup_black:
        #     return move_lookup_black[hash_state]
        moves: list[tuple[int, int, int, int]] = []
        for h, piece in enumerate(board):
            i, j = h // 8, h % 8
            if piece * color <= 0:  # If piece is 0, blank so skip; if color doesn't match player color skip
                continue
            piece_type = abs(piece)
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
            if piece_type == 5:  # Queen
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
            if piece_type == 4:  # Rook
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
            if piece_type == 3:  # Bishop
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
                        if (i + l) % 8 == i + l and (j + k) % 8 == j + k and board[
                            (i + l) * 8 + (j + k)] * color <= 0:
                            moves.append((i, j, i + l, j + k))
            if piece_type == 1:  # Pawn
                forward = (i - color) % 8 == i - color
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
                    elif i - color == 0:  # Promotion
                        moves.append((-4, 1, i, j))
                        moves.append((-5, 1, i, j))
                        moves.append((-6, 1, i, j))
                        moves.append((-7, 1, i, j))
                    elif i - color == 7:  # Promotion
                        moves.append((-4, 1, i, j))
                        moves.append((-5, 1, i, j))
                        moves.append((-6, 1, i, j))
                        moves.append((-7, 1, i, j))
                if forward and (j - 1) % 8 == j - 1 and board[(i - color) * 8 + (j - 1)] * color < 0:
                    if i - color != 0 and i - color != 7:
                        moves.append((i, j, i - color, j - 1))
                    elif i - color == 0:  # Promotion
                        moves.append((-4, -1, i, j))
                        moves.append((-5, -1, i, j))
                        moves.append((-6, -1, i, j))
                        moves.append((-7, -1, i, j))
                    elif i - color == 7:  # Promotion
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
        # if color == 1: move_lookup_white[hash_state] = moves
        # else: move_lookup_black[hash_state] = moves
        return moves

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
        new_board = copy.copy(self.board)
        white_queen = self.white_queen
        white_king = self.white_king
        black_queen = self.black_queen
        black_king = self.black_king

        if len(move) == 0:
            return GameState(new_board, draw=True)

        if move[0] == -1:  # Castle
            if move[2] == 7:
                white_queen = False
                white_king = False
            else:
                black_queen = False
                black_king = False
            new_board[move[2] * 8 + move[3]] = 0
            new_board[move[2] * 8 + move[1] * 7] = 0
            new_board[move[2] * 8 + 4 + move[1] * 2] = self.board[move[2] * 8 + move[3]]
            new_board[move[2] * 8 + 4 + move[1]] = self.board[move[2] * 8 + move[1] * 7]
            return GameState(new_board, white_queen, white_king, black_queen, black_king, last_move=move,
                             color=-self.color, turn=self.turn + 1)

        if move[0] == -2:  # En Passant
            new_board[move[2] * 8 + move[3]] = 0
            new_board[(move[2] - self.color) * 8 + move[3] + move[1]] = self.board[move[2] * 8 + move[3]]
            new_board[move[2] * 8 + move[3] + move[1]] = 0
            return GameState(new_board, white_queen, white_king, black_queen, black_king, last_move=move,
                             color=-self.color, turn=self.turn + 1)

        if move[0] == -3:  # Promotion
            new_board[move[2] * 8 + move[3]] = 0
            new_board[(move[2] - self.color) * 8 + move[3]] = move[1]
            return GameState(new_board, white_queen, white_king, black_queen, black_king, move, color=-self.color)

        if move[0] <= -4:  # Promotion while taking
            new_board[move[2] * 8 + move[3]] = 0
            new_board[(move[2] - self.color) * 8 + (move[3] + move[1])] = (move[0] + 2) * -self.color

            return GameState(new_board, white_queen, white_king, black_queen, black_king, last_move=move,
                             color=-self.color, turn=self.turn + 1)

        if new_board[move[2] * 8 + move[3]] in {-4, 4}:  # Can never take kings
            if move[2] == 7 and move[3] == 0:
                white_queen = False
            if move[2] == 7 and move[3] == 7:
                white_king = False
            if move[2] == 0 and move[3] == 0:
                black_queen = False
            if move[2] == 0 and move[3] == 7:
                black_king = False
        if new_board[move[0] * 8 + move[1]] in {-6, -4, 4, 6}:
            if move[2] == 7 and move[3] == 0:
                white_queen = False
            if move[2] == 7 and move[3] == 7:
                white_king = False
            if move[2] == 0 and move[3] == 0:
                black_queen = False
            if move[2] == 0 and move[3] == 7:
                black_king = False
            if move[2] == 0 and move[3] == 4:
                black_queen = False
                black_king = False
            if move[2] == 7 and move[3] == 4:
                white_queen = False
                white_king = False
        new_board[move[2] * 8 + move[3]] = new_board[move[0] * 8 + move[1]]
        new_board[move[0] * 8 + move[1]] = 0
        return GameState(new_board, white_queen, white_king, black_queen, black_king, last_move=move, color=-self.color,
                         turn=self.turn + 1)

    def get_winner(self):
        white = True
        black = True
        for piece in self.board:
            if piece == 6:
                white = False
            elif piece == -6:
                black = False
        if white and not black:
            return 1
        elif black and not white:
            return -1
        elif black and white:
            return 0
        return None

    def __repr__(self):
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
        result = "_________________________________\n"
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
