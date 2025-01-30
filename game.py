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
    def __init__(self, board=None, white_queen=True, white_king=True, black_queen=True, back_king=True, last_move=None, color=1):
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
                        moves.append(((i, j), (i - color, j)))
                    if forward and (j + 1) % 8 == j + 1 and self.board[i - color][j + 1] * color < 0:
                        moves.append(((i, j), (i - color, j + 1)))
                    if forward and (j - 1) % 8 == j - 1 and self.board[i - color][j - 1] * color < 0:
                        moves.append(((i, j), (i - color, j - 1)))
                    if forward and color == 1 and i == 6 and self.board[4][j] == 0:
                        moves.append(((i, j), (4, j)))
                    if forward and color == -1 and i == 1 and self.board[3][j] == 0:
                        moves.append(((i, j), (3, j)))
                    # En Passant
                    if self.board[self.last_move[1][0]][self.last_move[1][1]] == -color and abs(
                            self.last_move[1][0] - self.last_move[0][0]) == 2 and i == self.last_move[1][0]:
                        if j == self.last_move[1][1] + 1:
                            moves.append(((-2, 1), (i, j)))
                        if j == self.last_move[1][1] - 1:
                            moves.append(((-2, -1), (i, j)))

        return moves

    def move(self, move) -> 'GameState':
        new_board = copy.deepcopy(self.board)
        white_queen = self.white_queen
        white_king = self.white_king
        black_queen = self.black_queen
        black_king = self.black_king
        if move[0][0] == -1: # Castle
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
        if move[0][0] == -2: # En Passant
            new_board[move[1][0]][move[1][1]] = 0
            new_board[move[1][0] - self.color][move[1][1] + move[0][1]] = self.board[move[1][0]][move[1][1]]
            new_board[move[1][0]][move[1][1] + move[0][1]] = 0
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
