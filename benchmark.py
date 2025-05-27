import random
from timeit import timeit

from fen_utils import game_state_from_line
from statistics import mean, stdev
from scipy import stats  # type: ignore
from game import GameState
from game_bitboards import GameStateBitboards
from game_base import GameStateBase

game_states: list = []
coord_to_index: list[list[int]] = [[0 for _ in range(8)] for _ in range(8)]

def populate_game_states():
    global game_states
    global coord_to_index
    game_states = [game_state_from_line(i) for i in range(1, 501)]
    print("Game States created")
    for row in range(8):
        for col in range(8):
            coord_to_index[row][col] = row * 8 + col
    # for game_state in game_states:
    #     game_state.get_moves()
    # print("Moves calculated")

populate_game_states()

def benchmark(condition: bool, game_state: GameState | None) -> None:
    # assert game_state is not None
    # game_state_bitboards: GameStateBitboards = game_state.to_bitboards()
    # game_state_bitboards.get_moves()
    # assert game_state_bitboards.moves is not None
    coord_to_index_local: list[list[int]] = coord_to_index
    row = random.randint(0, 7)
    col = random.randint(0, 7)
    if condition:
        a = coord_to_index_local[row][col]
        # for move in game_state_bitboards.moves:
        #     game_state_bitboards.new_move(move)
        # game_state_bitboards.get_winner()
    else:
        b = row * 8 + col
        # assert game_state_local.moves is not None
        # for move in game_state_local.moves:
        #     game.move(move)
        # game_state_local.get_winner()


def main() -> None:
    t1 = []
    t2 = []
    t3 = []
    for _ in range(50_000_000): pass
    print('Warmup complete')
    for i in range(1000):
        # game_state = game_states[i % 500]
        # t1.append(mean([benchmark(True, game_state)[1] for i in range(3)]))
        # t2.append(mean([benchmark(False, game_state)[1] for i in range(3)]))
        t1.append(timeit(lambda: benchmark(True, None), number=500) * 1_000)
        t2.append(timeit(lambda: benchmark(False, None), number=500) * 1_000)
        t3.append(t1[-1] - t2[-1])
        if i > 0 and i % 10 == 0:
            t, p = stats.ttest_1samp(t3, 0, alternative='less')
            # t, p = stats.ttest_ind(t1, t2, equal_var=False, alternative='less')
            print(f'{i}:\nNew: {mean(t1)}, {stdev(t1)}')
            print(f'Old: {mean(t2)}, {stdev(t2)}\n')
            print(f'T-statistic: {t:.5f}\nP-value: {p:.5f}\n')
    t1 = t1[3:]
    t2 = t2[3:]
    t3 = t3[3:]
    print(f'{t1}\n{t2}\n{t3}')
    print()
    print(f'Mean New: {mean(t1)}\nStdDev New: {stdev(t1)}\nN New: {len(t1)}\n')
    print(f'Mean Old: {mean(t2)}\nStdDev Old: {stdev(t2)}\nN Old: {len(t2)}\n')
    print(f'Mean Diff: {mean(t3)}\nStdDev Diff: {stdev(t3)}\nN Diff: {len(t3)}')
    print()
    t, p = stats.ttest_ind(t1, t2, equal_var=False, alternative='less')
    print(f'2-Sample T-Test:\nT-statistic: {t:.5f}\nP-value: {p:.5f}\n')
    t, p = stats.ttest_1samp(t3, 0, alternative='less')
    print(f'1-Sample T-Test of Difference:\nT-statistic: {t:.5f}\nP-value: {p:.5f}')


if __name__ == '__main__':
    main()
