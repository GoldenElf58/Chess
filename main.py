from game import GameState


def evaluate(board: list[list[int]]) -> float:
    evaluation = 0
    for row in board:
        for piece in row:
            evaluation += piece
    return evaluation

def main() -> None:
    game_state = GameState()
    while True:
        print(game_state)
        moves = game_state.get_moves()
        print(moves)
        choice = int(input("Enter move index:  "))
        game_state = game_state.move(moves[choice])

if __name__ == '__main__':
    main()
