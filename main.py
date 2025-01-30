# + is white and - is black
# 6 - King
# 5 - Queen
# 4 - Rook
# 3 - Bishop
# 2 - Knight
# 1 - Pawn
# 0 - Empty square

start_board: list[list[int]] = [[-4, -2, -3, -5, -6, -3, -2, -4],
                                [-1, -1, -1, -1, -1, -1, -1, -1],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [1, 1, 1, 1, 1, 1, 1, 1],
                                [4, 2, 3, 5, 6, 3, 2, 4]]
game_board: list[list[int]] = [[0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0]]


def evaluate(board: list[list[int]]) -> float:
    evaluation = 0
    for row in board:
        for piece in row:
            evaluation += piece
    return evaluation


def get_moves(board: list[list[int]], color: int) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    moves: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            if piece * color <= 0:  # If piece is 0, blank so skip; if color doesn't match player color skip
                continue
            piece_type = abs(piece)
            if piece_type == 6: # King
                for k in range(-1, 2):
                    for l in range(-1, 2):
                        if (i + k) % 8 != i + k or (j + l) % 8 != j + l:
                            continue
                        if board[i + k][j + l] * color <= 0:
                            moves.append(((i, j), (i + k, j + l)))
            if piece_type == 5: # Queen
                for k in range(j + 1, 8):
                    if board[i][k] * color <= 0:
                        moves.append(((i, j), (i, k)))
                    if board[i][k] == 0:
                        continue
                    break
                for k in range(j - 1, -1, -1):
                    if board[i][k] * color <= 0:
                        moves.append(((i, j), (i, k)))
                    if board[i][k] == 0:
                        continue
                    break
                for k in range(i - 1, -1, -1):
                    if board[k][j] * color <= 0:
                        moves.append(((i, j), (k, j)))
                    if board[k][j] == 0:
                        continue
                    break
                for k in range(i + 1, 8):
                    if board[k][j] * color <= 0:
                        moves.append(((i, j), (k, j)))
                    if board[k][j] == 0:
                        continue
                    break
                for k in range(1, 8):
                    if i + k > 7 or j + k > 7:
                        break
                    if board[i + k][j + k] * color <= 0:
                        moves.append(((i, j), (i + k, j + k)))
                    if board[i + k][j + k] == 0:
                        continue
                    break
                for k in range(1, 8):
                    if i - k < 0 or j + k > 7:
                        break
                    if board[i - k][j + k] * color <= 0:
                        moves.append(((i, j), (i - k, j + k)))
                    if board[i - k][j + k] == 0:
                        continue
                    break
                for k in range(1, 8):
                    if i + k > 7 or j - k < 0:
                        break
                    if board[i + k][j - k] * color <= 0:
                        moves.append(((i, j), (i + k, j - k)))
                    if board[i + k][j - k] == 0:
                        continue
                    break
                for k in range(1, 8):
                    if i - k < 0 or j  - k < 0:
                        break
                    if board[i - k][j - k] * color <= 0:
                        moves.append(((i, j), (i - k, j - k)))
                    if board[i - k][j - k] == 0:
                        continue
                    break
            if piece_type == 4:  # Rook
                for k in range(j + 1, 8):
                    if board[i][k] * color <= 0:
                        moves.append(((i, j), (i, k)))
                    if board[i][k] == 0:
                        continue
                    break
                for k in range(j - 1, -1, -1):
                    if board[i][k] * color <= 0:
                        moves.append(((i, j), (i, k)))
                    if board[i][k] == 0:
                        continue
                    break
                for k in range(i - 1, -1, -1):
                    if board[k][j] * color <= 0:
                        moves.append(((i, j), (k, j)))
                    if board[k][j] == 0:
                        continue
                    break
                for k in range(i + 1, 8):
                    if board[k][j] * color <= 0:
                        moves.append(((i, j), (k, j)))
                    if board[k][j] == 0:
                        continue
                    break
            if piece_type == 3: # Bishop
                for k in range(1, 8):
                    if i + k > 7 or j + k > 7:
                        break
                    if board[i + k][j + k] * color <= 0:
                        moves.append(((i, j), (i + k, j + k)))
                    if board[i + k][j + k] == 0:
                        continue
                    break
                for k in range(1, 8):
                    if i - k < 0 or j + k > 7:
                        break
                    if board[i - k][j + k] * color <= 0:
                        moves.append(((i, j), (i - k, j + k)))
                    if board[i - k][j + k] == 0:
                        continue
                    break
                for k in range(1, 8):
                    if i + k > 7 or j - k < 0:
                        break
                    if board[i + k][j - k] * color <= 0:
                        moves.append(((i, j), (i + k, j - k)))
                    if board[i + k][j - k] == 0:
                        continue
                    break
                for k in range(1, 8):
                    if i - k < 0 or j  - k < 0:
                        break
                    if board[i - k][j - k] * color <= 0:
                        moves.append(((i, j), (i - k, j - k)))
                    if board[i - k][j - k] == 0:
                        continue
                    break
            if piece_type == 2: # Knight
                for k in range(-2, 3, 4):
                    for l in range(-1, 2, 2):
                        if (i + k) % 8 == i + k and (j + l) % 8 == j + l and board[i + k][j + l] * color <= 0:
                            moves.append(((i, j), (i + k, j + l)))
                        if (i + l) % 8 == i + l and (j + k) % 8 == j + k and board[i + l][j + k] * color <= 0:
                            moves.append(((i, j), (i + l, j + k)))
            if piece_type == 1: # Pawn
                forward = (i - color) % 8 == i - color
                if forward and board[i - color][j] == 0:
                    moves.append(((i, j), (i - color, j)))
                # if forward and board[i - color][]



    return moves


def main() -> None:
    moves = get_moves(game_board, 1)
    print(moves)
    for move in moves:
        game_board[move[1][0]][move[1][1]] = 7
    for row in game_board:
        print(row)


if __name__ == '__main__':
    main()
