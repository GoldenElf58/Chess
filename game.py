import copy

start_board: list[list[int]] = [[-4, -2, -3, -5, -6, -3, -2, -4],
                                [-1, -1, -1, -1, -1, -1, -1, -1],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [1, 1, 1, 1, 1, 1, 1, 1],
                                [4, 2, 3, 5, 6, 3, 2, 4]]


class GameState:
    def __init__(self, board=None, white_queen=True, white_king=True, black_queen=True, back_king=True, last_move=None,
                 color=1):
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
        self.board = board
        self.color = color
        self.white_queen = white_queen
        self.white_king = white_king
        self.black_queen = black_queen
        self.black_king = back_king
        self.last_move = last_move

    def get_moves(self, color: int = None) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        """
        Get all the possible moves for the current player.

        Parameters
        ----------
        color : int, optional
            The color of the player to get the moves for. Defaults to `self.color`.

        Returns
        -------
        list[tuple[tuple[int, int], tuple[int, int]]]
            A list of tuples of two tuples, representing the starting and ending squares of each move.
        """
        if color is None:
            color = self.color
        else:
            self.color = color
        moves: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for i, row in enumerate(self.board):
            for j, piece in enumerate(row):
                if piece * color <= 0:  # If piece is 0, blank so skip; if color doesn't match player color skip
                    continue
                piece_type = abs(piece)
                if piece_type == 6:  # King
                    if (((color == 1 and self.white_king) or (color == -1 and self.black_king))
                            and self.board[i][7] == 4 * color and {self.board[i][5], self.board[i][6]} == {0}):
                        moves.append(((-1, 1), (i, j)))
                    if (((color == 1 and self.white_queen) or (color == -1 and self.black_queen))
                            and self.board[i][7] == 4 * color and {self.board[i][1], self.board[i][2],
                                                                   self.board[i][3]} == {0}):
                        moves.append(((-1, -1), (i, j)))
                    for k in range(-1, 2):
                        for l in range(-1, 2):
                            if (i + k) % 8 != i + k or (j + l) % 8 != j + l:
                                continue
                            if self.board[i + k][j + l] * color <= 0:
                                moves.append(((i, j), (i + k, j + l)))
                if piece_type == 5:  # Queen
                    for k in range(j + 1, 8):
                        if self.board[i][k] * color <= 0:
                            moves.append(((i, j), (i, k)))
                        if self.board[i][k] == 0:
                            continue
                        break
                    for k in range(j - 1, -1, -1):
                        if self.board[i][k] * color <= 0:
                            moves.append(((i, j), (i, k)))
                        if self.board[i][k] == 0:
                            continue
                        break
                    for k in range(i - 1, -1, -1):
                        if self.board[k][j] * color <= 0:
                            moves.append(((i, j), (k, j)))
                        if self.board[k][j] == 0:
                            continue
                        break
                    for k in range(i + 1, 8):
                        if self.board[k][j] * color <= 0:
                            moves.append(((i, j), (k, j)))
                        if self.board[k][j] == 0:
                            continue
                        break
                    for k in range(1, 8):
                        if i + k > 7 or j + k > 7:
                            break
                        if self.board[i + k][j + k] * color <= 0:
                            moves.append(((i, j), (i + k, j + k)))
                        if self.board[i + k][j + k] == 0:
                            continue
                        break
                    for k in range(1, 8):
                        if i - k < 0 or j + k > 7:
                            break
                        if self.board[i - k][j + k] * color <= 0:
                            moves.append(((i, j), (i - k, j + k)))
                        if self.board[i - k][j + k] == 0:
                            continue
                        break
                    for k in range(1, 8):
                        if i + k > 7 or j - k < 0:
                            break
                        if self.board[i + k][j - k] * color <= 0:
                            moves.append(((i, j), (i + k, j - k)))
                        if self.board[i + k][j - k] == 0:
                            continue
                        break
                    for k in range(1, 8):
                        if i - k < 0 or j - k < 0:
                            break
                        if self.board[i - k][j - k] * color <= 0:
                            moves.append(((i, j), (i - k, j - k)))
                        if self.board[i - k][j - k] == 0:
                            continue
                        break
                if piece_type == 4:  # Rook
                    for k in range(j + 1, 8):
                        if self.board[i][k] * color <= 0:
                            moves.append(((i, j), (i, k)))
                        if self.board[i][k] == 0:
                            continue
                        break
                    for k in range(j - 1, -1, -1):
                        if self.board[i][k] * color <= 0:
                            moves.append(((i, j), (i, k)))
                        if self.board[i][k] == 0:
                            continue
                        break
                    for k in range(i - 1, -1, -1):
                        if self.board[k][j] * color <= 0:
                            moves.append(((i, j), (k, j)))
                        if self.board[k][j] == 0:
                            continue
                        break
                    for k in range(i + 1, 8):
                        if self.board[k][j] * color <= 0:
                            moves.append(((i, j), (k, j)))
                        if self.board[k][j] == 0:
                            continue
                        break
                if piece_type == 3:  # Bishop
                    for k in range(1, 8):
                        if i + k > 7 or j + k > 7:
                            break
                        if self.board[i + k][j + k] * color <= 0:
                            moves.append(((i, j), (i + k, j + k)))
                        if self.board[i + k][j + k] == 0:
                            continue
                        break
                    for k in range(1, 8):
                        if i - k < 0 or j + k > 7:
                            break
                        if self.board[i - k][j + k] * color <= 0:
                            moves.append(((i, j), (i - k, j + k)))
                        if self.board[i - k][j + k] == 0:
                            continue
                        break
                    for k in range(1, 8):
                        if i + k > 7 or j - k < 0:
                            break
                        if self.board[i + k][j - k] * color <= 0:
                            moves.append(((i, j), (i + k, j - k)))
                        if self.board[i + k][j - k] == 0:
                            continue
                        break
                    for k in range(1, 8):
                        if i - k < 0 or j - k < 0:
                            break
                        if self.board[i - k][j - k] * color <= 0:
                            moves.append(((i, j), (i - k, j - k)))
                        if self.board[i - k][j - k] == 0:
                            continue
                        break
                if piece_type == 2:  # Knight
                    for k in range(-2, 3, 4):
                        for l in range(-1, 2, 2):
                            if (i + k) % 8 == i + k and (j + l) % 8 == j + l and self.board[i + k][j + l] * color <= 0:
                                moves.append(((i, j), (i + k, j + l)))
                            if (i + l) % 8 == i + l and (j + k) % 8 == j + k and self.board[i + l][j + k] * color <= 0:
                                moves.append(((i, j), (i + l, j + k)))
                if piece_type == 1:  # Pawn
                    forward = (i - color) % 8 == i - color
                    if forward and self.board[i - color][j] == 0:
                        if i - color != 0 and i - color != 7:
                            moves.append(((i, j), (i - color, j)))
                        elif i - color == 0:  # Promotion
                            moves.append(((-3, 2), (i, j)))
                            moves.append(((-3, 3), (i, j)))
                            moves.append(((-3, 4), (i, j)))
                            moves.append(((-3, 5), (i, j)))
                        elif i - color == 7:  # Promotion
                            moves.append(((-3, -2), (i, j)))
                            moves.append(((-3, -3), (i, j)))
                            moves.append(((-3, -4), (i, j)))
                            moves.append(((-3, -5), (i, j)))
                    if forward and (j + 1) % 8 == j + 1 and self.board[i - color][j + 1] * color < 0:
                        if i - color != 0 and i - color != 7:
                            moves.append(((i, j), (i - color, j + 1)))
                        elif i - color == 0:  # Promotion
                            moves.append(((-4, 1), (i, j)))
                            moves.append(((-5, 1), (i, j)))
                            moves.append(((-6, 1), (i, j)))
                            moves.append(((-7, 1), (i, j)))
                        elif i - color == 7:  # Promotion
                            moves.append(((-4, 1), (i, j)))
                            moves.append(((-5, 1), (i, j)))
                            moves.append(((-6, 1), (i, j)))
                            moves.append(((-7, 1), (i, j)))
                    if forward and (j - 1) % 8 == j - 1 and self.board[i - color][j - 1] * color < 0:
                        if i - color != 0 and i - color != 7:
                            moves.append(((i, j), (i - color, j - 1)))
                        elif i - color == 0:  # Promotion
                            moves.append(((-4, -1), (i, j)))
                            moves.append(((-5, -1), (i, j)))
                            moves.append(((-6, -1), (i, j)))
                            moves.append(((-7, -1), (i, j)))
                        elif i - color == 7:  # Promotion
                            moves.append(((-4, -1), (i, j)))
                            moves.append(((-5, -1), (i, j)))
                            moves.append(((-6, -1), (i, j)))
                            moves.append(((-7, -1), (i, j)))
                    if forward and color == 1 and i == 6 and self.board[4][j] == 0:
                        moves.append(((i, j), (4, j)))
                    if forward and color == -1 and i == 1 and self.board[3][j] == 0:
                        moves.append(((i, j), (3, j)))
                    # En Passant
                    if (self.last_move is not None and self.board[self.last_move[1][0]][
                        self.last_move[1][1]] == -color and abs(self.last_move[1][0] - self.last_move[0][0]) == 2
                            and i == self.last_move[1][0]):
                        if j == self.last_move[1][1] + 1 and j < 7:
                            moves.append(((-2, 1), (i, j)))
                        if j == self.last_move[1][1] - 1 and j > 0:
                            moves.append(((-2, -1), (i, j)))

        return moves

    def move(self, move) -> 'GameState':
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
        new_board = copy.deepcopy(self.board)
        white_queen = self.white_queen
        white_king = self.white_king
        black_queen = self.black_queen
        black_king = self.black_king

        if move[0][0] == -1:  # Castle
            if move[1][0] == 7:
                white_queen = False
                white_king = False
            else:
                black_queen = False
                black_king = False
            new_board[move[1][0]][move[1][1]] = 0
            new_board[move[1][0]][move[0][1] * 7] = 0
            new_board[move[1][0]][4 + move[0][1] * 2] = self.board[move[1][0]][move[1][1]]
            new_board[move[1][0]][4 + move[0][1]] = self.board[move[1][0]][move[0][1] * 7]
            return GameState(new_board, white_queen, white_king, black_queen, black_king)

        if move[0][0] == -2:  # En Passant
            new_board[move[1][0]][move[1][1]] = 0
            new_board[move[1][0] - self.color][move[1][1] + move[0][1]] = self.board[move[1][0]][move[1][1]]
            new_board[move[1][0]][move[1][1] + move[0][1]] = 0
            return GameState(new_board, white_queen, white_king, black_queen, black_king, move, color=-self.color)

        if move[0][0] == -3:  # Promotion
            new_board[move[1][0]][move[1][1]] = 0
            new_board[move[1][0] - self.color][move[1][1]] = move[0][1]
            return GameState(new_board, white_queen, white_king, black_queen, black_king, move, color=-self.color)

        if move[0][0] <= -4: # Promotion while taking
            new_board[move[1][0]][move[1][1]] = 0
            new_board[move[1][0] - self.color][move[1][1] + move[0][1]] = (move[0][0] + 2) * -self.color

            return GameState(new_board, white_queen, white_king, black_queen, black_king, move, color=-self.color)

        if new_board[move[1][0]][move[1][1]] in {-4, 4}:  # Can never take kings
            if move[1][0] == 7 and move[1][1] == 0:
                white_queen = False
            if move[1][0] == 7 and move[1][1] == 7:
                white_king = False
            if move[1][0] == 0 and move[1][1] == 0:
                black_queen = False
            if move[1][0] == 0 and move[1][1] == 7:
                black_king = False
        if new_board[move[0][0]][move[0][1]] in {-6, -4, 4, 6}:
            if move[1][0] == 7 and move[1][1] == 0:
                white_queen = False
            if move[1][0] == 7 and move[1][1] == 7:
                white_king = False
            if move[1][0] == 0 and move[1][1] == 0:
                black_queen = False
            if move[1][0] == 0 and move[1][1] == 7:
                black_king = False
            if move[1][0] == 0 and move[1][1] == 4:
                black_queen = False
                black_king = False
            if move[1][0] == 7 and move[1][1] == 4:
                white_queen = False
                white_king = False
        new_board[move[1][0]][move[1][1]] = new_board[move[0][0]][move[0][1]]
        new_board[move[0][0]][move[0][1]] = 0
        return GameState(new_board, white_queen, white_king, black_queen, black_king, last_move=move, color=-self.color)

    def get_winner(self):
        white = False
        black = False
        for row in self.board:
            for piece in row:
                if piece == 6:
                    white = True
                elif piece == -6:
                    black = True
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
        for row in self.board:
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
