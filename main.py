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
game_board: list[list[int]] = [[0, 0, -2, 0, 0, 0, 0, 0],
                               [0, 0, 0, 1, 0, 0, 0, 0],
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
    print(game_state)
    move = moves[7]
    new_game_state = game_state.move(move)
    print(move)
    print(new_game_state)


if __name__ == '__main__':
    main()
