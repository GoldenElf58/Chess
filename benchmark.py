# from game import GameState
from timeit import timeit
from game import GameState
from fen_utils import game_state_from_line
from statistics import mean, stdev
from scipy import stats  # type: ignore

game_states: list[GameState] = []

def populate_game_states():
    global game_states
    game_states = [game_state_from_line(i) for i in range(1, 501)]
    print("Game States created")
    for game_state in game_states:
        game_state.get_moves()
    print("Moves calculated")

populate_game_states()

def benchmark(condition: bool) -> None:
    # board: tuple[int, ...] = start_board
    cond: bool = condition
    for game_state in game_states:
        moves = game_state.get_moves()
        if cond:
            for move in moves:
                game_state.new_move(move)
        else:
            for move in moves:
                game_state.move(move)


def main() -> None:
    t1 = []
    t2 = []
    for _ in range(50_000_000): pass
    print('Warmup complete')
    timeit(lambda: benchmark(True), number=1) * 1000
    timeit(lambda: benchmark(False), number=1) * 1000
    for i in range(500):
        t1.append(timeit(lambda: benchmark(True), number=1) * 1_000)
        t2.append(timeit(lambda: benchmark(False), number=1) * 1_000)
        if i % 50 == 0:
            t, p = stats.ttest_ind(t1, t2, equal_var=False, alternative='less')
            print(f'{i}:\nNew: {mean(t1)}\nOld: {mean(t2)}\nT-statistic: {t:.5f}\nP-value: {p:.5f}\n')
    t1 = t1[5:]
    t2 = t2[5:]
    print(t1, '\n', t2)
    print()
    print(f'Mean New: {mean(t1)}\nStdDev New: {stdev(t1)}\nN New: {len(t1)}\n')
    print(f'Mean Old: {mean(t2)}\nStdDev Old: {stdev(t2)}\nN Old: {len(t2)}')
    print()
    t, p = stats.ttest_ind(t1, t2, equal_var=False, alternative='less')
    print(f'T-statistic: {t:.5f}\nP-value: {p:.5f}')


if __name__ == '__main__':
    main()
