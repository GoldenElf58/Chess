# + is white and - is black
# 6 - King
# 5 - Queen
# 4 - Rook
# 3 - Bishop
# 2 - Knight
# 1 - Pawn
# 0 - Empty square
from game import GameState

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

def main() -> None:
    game_state = GameState(game_board)
    moves = game_state.get_moves()
    print(moves)
    for move in moves:
        game_board[move[1][0]][move[1][1]] = 7
    for row in game_board:
        print(row)


if __name__ == '__main__':
    main()
