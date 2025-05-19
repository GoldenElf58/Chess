from game import GameState
from timeit import timeit
from game import start_board

def benchmark() -> None:
    board = start_board
    game_state: GameState = GameState(board=board)
    for i in range(30_000):
        game_state.get_moves()
        game_state.moves = None

def main() -> None:
    print(timeit(benchmark, number=1))


if __name__ == '__main__':
    main()
