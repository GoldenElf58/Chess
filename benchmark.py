import random
from copy import deepcopy
from itertools import repeat
from statistics import mean, stdev
from timeit import timeit
from typing import Any

from scipy import stats  # type: ignore

from fen_utils import game_state_from_line
from game import GameStateV2
from game_base import GameStateBase
from game_bitboards import GameStateBitboards

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

def benchmark(condition: bool, game_state: GameStateBase) -> None:
    # game_state.moves = None
    # game_state.previous_position_count = {}
    # game_state.are_captures()
    # game_state.get_moves()
    # if condition:
    #     game_state.get_moves_no_check_new()
    # else:
    #     game_state.get_moves_no_check()
    game_state.get_moves_no_check()
    # game_state.move(random.choice(moves))
    # for move in game_state.get_moves_no_check():
    #     game_state.move(move)
    # game_state.get_winner()


def main() -> None:
    t1 = []
    t2 = []
    t3 = []
    for _ in range(50_000_000): pass
    print('Warmup complete')
    N = 10_000
    n = 100
    for i in range(N):
        game_state = game_states[i % 500]#.copy()

        # timeit(lambda: benchmark(True, game_state_a), number=500) * 1_000
        # game_state_a.get_moves()
        # game_state_b.get_moves()
        # t1.append(mean([benchmark(True, game_state)[1] for i in range(3)]))
        # t2.append(mean([benchmark(False, game_state)[1] for i in range(3)]))
        # timeit(lambda: benchmark(True, game_state_a), number=20)
        game_state_a = game_state.to_bitboards()
        t1.append(timeit(lambda: benchmark(True, game_state_a), number=n) * 1_000_000 / n)
        game_state_b = game_state
        t2.append(timeit(lambda: benchmark(False, game_state_b), number=n) * 1_000_000 / n)
        t3.append(t1[-1] - t2[-1])
        if i > 0 and i % 1000 == 0:
            t, p = stats.ttest_1samp(t3, 0, alternative='less')
            # t, p = stats.ttest_ind(t1, t2, equal_var=False, alternative='less')
            print(f'{i}:\nNew: {mean(t1)}, {stdev(t1)}')
            print(f'Old: {mean(t2)}, {stdev(t2)}\n')
            print(f'T-statistic: {t:.5f}\nP-value: {p:.5f}\n')
    t1 = t1[N // 100:]
    t2 = t2[N // 100:]
    t3 = t3[N // 100:]
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
