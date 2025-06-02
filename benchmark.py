import random
import time
from copy import deepcopy
from itertools import repeat
from statistics import mean, stdev
from timeit import timeit
from typing import Any

from scipy import stats  # type: ignore

from bots import BotV5p1
from fen_utils import game_state_from_line
from game import GameState
from game_v2 import GameStateV2
from game_base import GameStateBase
from game_bitboards import GameStateBitboards
from game_bitboards_v2 import GameStateBitboardsV2

game_states: list[GameState] = []
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

def benchmark(condition: bool, game_state: GameState | GameStateV2 | GameStateBitboards | GameStateBitboardsV2) -> None:
    # game_state.moves = None
    # game_state.previous_position_count = {}
    # game_state.are_captures()
    # game_state.get_moves()
    bot = BotV5p1()
    if condition:
        bot.evaluate_new(game_state)
    else:
        bot.evaluate(game_state)
    # game_state.get_moves()
    # game_state.get_moves_no_check()
    # game_state.move(random.choice(moves))
    # game_state.get_moves_no_check()
    # while game_state.get_winner() is None:
    #     game_state.move(random.choice(game_state.get_moves()))
    #     game_state.get_moves()
    # BotV1().generate_move(game_state, depth=2)
    # for move in game_state.get_moves():
    #     game_state.move(move)
    # game_state.get_winner()


def test():
    game_state = GameStateV2()
    t0 = time.time_ns()
    moves = 0
    while game_state.get_winner() is None:
        game_state = game_state.move(random.choice(game_state.get_moves()))
        game_state.get_moves()
        moves += 1
    t1 = time.time_ns()
    print(f'Total time (ms): {(t1 - t0) / 1_000_000:.5f}')
    print(f'Average time (µs): {((t1 - t0) / 1_000) / moves:.5f}')
    return t1 - t0, (t1 - t0) / moves

def deep_test():
    game_times = []
    turn_times = []
    for i in range(100):
        game_time, turn_time = test()
        game_times.append(game_time)
        turn_times.append(turn_time)
    print()
    print(f'Average game time (ms): {mean(game_times) / 1_000_000:.5f}')
    print(f'Std dev game time (ms): {stdev(game_times) / 1_000_000:.5f}')
    print()
    print(f'Average turn time (µs): {mean(turn_times) / 1_000:.5f}')
    print(f'Std dev turn time (µs): {stdev(turn_times) / 1_000:.5f}')

def main() -> None:
    t1 = []
    t2 = []
    t3 = []
    for _ in range(50_000_000): pass
    print('Warmup complete')
    N = 25_000
    n = 50
    timeit(lambda: benchmark(True, game_states[0].to_v2()), number=n*10)
    test = timeit(lambda: benchmark(True, game_states[0].to_v2()), number=n * N // 200) / n / N * 200
    scale = 1_000_000 if test < .001 else (1_000 if test < 1 else 1)
    print(f'Test: {test}')
    print(f'Scale: {scale}')
    for i in range(N):
        game_state = GameState()#game_states[i % 500]#.copy()

        # timeit(lambda: benchmark(True, game_state_a), number=500) * 1_000
        # game_state_a.get_moves()
        # game_state_b.get_moves()
        # t1.append(mean([benchmark(True, game_state)[1] for i in range(3)]))
        # t2.append(mean([benchmark(False, game_state)[1] for i in range(3)]))
        # timeit(lambda: benchmark(True, game_state_a), number=20)
        game_state_a = game_state.to_v2()
        t1.append(timeit(lambda: benchmark(True, game_state_a), number=n) * scale / n)
        game_state_b = game_state.to_v2()
        t2.append(timeit(lambda: benchmark(False, game_state_b), number=n) * scale / n)
        t3.append(t1[-1] - t2[-1])
        if i > 0 and i % (N // 50) == 0:
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
    print(f'Scale: {scale:,}')
    print()
    print(f'Mean New: {mean(t1)}\nStdDev New: {stdev(t1)}\nN New: {len(t1)}\n')
    print(f'Mean Old: {mean(t2)}\nStdDev Old: {stdev(t2)}\nN Old: {len(t2)}\n')
    print(f'Mean Diff: {mean(t3)}\nStdDev Diff: {stdev(t3)}\nN Diff: {len(t3)}')
    print()
    t, p = stats.ttest_ind(t1, t2, equal_var=False, alternative='less')
    print(f'2-Sample T-Test:\nT-statistic: {t:.5f}\nP-value: {p:.5f}\n')
    t, p = stats.ttest_1samp(t3, 0, alternative='less')
    print(f'1-Sample T-Test of Difference:\nT-statistic: {t:.5f}\nP-value: {p:.5f}')
    print()
    print(f'Speedup: {mean(t2) / mean(t1):.5f}')
    print(f'Slowdown: {mean(t1) / mean(t2):.5f}')


if __name__ == '__main__':
    # deep_test()
    main()
