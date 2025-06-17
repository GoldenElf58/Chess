import cProfile
import random
import time
from statistics import mean, stdev
from timeit import timeit
# from typing import Any

from scipy import stats  # type: ignore
from pstats import Stats
from io import StringIO
import numpy as np
from numpy import int8, int64

from fen_utils import game_state_from_line
from game_states import GameState, GameStateBase, GameStateV2, GameStateV3, GameStateBitboardsV3
from bots import *

game_states: list[GameState] = []
coord_to_index: list[list[int]] = [[0 for _ in range(8)] for _ in range(8)]


def populate_game_states():
    global game_states
    global coord_to_index
    game_states = [game_state_from_line(i) for i in range(1, 501)]
    print("Game States created")
    for game_state in game_states:
        game_state.get_moves()
    print("Moves calculated")
    for row in range(8):
        for col in range(8):
            coord_to_index[row][col] = row * 8 + col


def benchmark(condition: bool, game_state: GameStateV3 | GameStateBitboardsV3, move) -> None:
    # pass
    # game_state.moves = None
    # game_state.moves_and_states = None
    # game_state.are_captures()
    # game_state.move(move)
    # game_state = GameStateV2()
    # bot = BotV2p3()
    # while game_state.get_winner() is None:
    #     game_state.move(bot.generate_move(game_state, depth=2)[0][1])

    # move = random.choice(game_state.get_moves())
    # check = 1 << random.randint(0, 63)
    # target = 1 << random.randint(0, 63)
    if condition:
        # bot.minimax_new(game_state, 5, -(1 << 31), (1 << 31), game_state.color == 1)
        # a = 3 ** 33
        # game_state & move
        game_state.get_moves()
    else:
        # bot.minimax(game_state, 5, -(1 << 31), (1 << 31), game_state.color == 1)
        # game_state == move
        game_state.get_moves()

    # game_state.get_moves()
    # game_state.get_moves_no_check()
    # game_state.move(random.choice(moves))
    # game_state.get_moves_no_check()
    # while game_state.get_winner() is None:
    #     game_state = game_state.move(random.choice(game_state.get_moves()))
    #     game_state.get_moves()
    # BotV1().generate_move(game_state, depth=2)
    # for move in game_state.get_moves():
    #     game_state.move(move)
    # game_state.get_winner()


def test():
    game_state = GameStateV3()
    moves = 0
    # bot = BotV1()
    t0 = time.time_ns()
    # for i in range(7):
    #     game_state.get_winner()
    while game_state.get_winner() is None:
        game_state = game_state.move(
            random.choice(game_state.get_moves()))  # game_state.move(bot.generate_move(game_state, depth=2)[0][1])
        game_state.get_moves()
        moves += 1
    t1 = time.time_ns()
    print(f'Total time (µs): {(t1 - t0) / 1_000:#.5g}')
    # print(f'Moves: {moves}')
    print(f'Average time (µs): {((t1 - t0) / 1_000) / moves:#.5g}')
    return (t1 - t0), (t1 - t0) / moves


def deep_test():
    game_times = []
    turn_times = []
    for i in range(1_000):
        test()
        game_time, turn_time = test()
        game_times.append(game_time)
        turn_times.append(turn_time)
    print()
    print(f'Average game time (µs): {mean(game_times) / 1_000:#.5g}')
    print(f'Std dev game time (µs): {stdev(game_times) / 1_000:#.5g}')
    print()
    print(f'Average turn time (µs): {mean(turn_times) / 1_000:#.5g}')
    print(f'Std dev turn time (µs): {stdev(turn_times) / 1_000:#.5g}')


def main() -> None:
    random.seed(42)
    t1 = []
    t2 = []
    t3 = []
    for _ in range(50_000_000): pass
    print('Warmup complete')
    N = 25_000
    n = 20
    move = random.choice(GameStateV3().get_moves())
    timeit(lambda: benchmark(True, GameStateV3(), move), number=n * 5)
    test = timeit(lambda: benchmark(True, GameStateV3(), move), number=n * 10) / n / 10
    scale = 1_000_000_000 if test < .000001 else (1_000_000 if test < .001 else (1_000 if test < 1 else 1))
    unit = 'ns' if test < .000001 else ('µs' if test < .001 else ('ms' if test < 1 else 's'))
    print(f'Test: {test}')
    print(f'Scale: {scale:,}')
    print(f'Unit: {unit}\n')
    start = random.randint(0, 500)
    boards = [
        (
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 6, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, -6, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
        ),
        (
            6, 0, 0, 0, 0, 0, 0, 0,
            0, 0, -5, -6, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
        ),
        (
            -6, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 4, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 6, 0, 0,
            0, 0, 4, 0, 6, 0, 0, 0,
        ),
        (
            0, 0, 0, 4, 0, 0, 0, 5,
            6, 0, -6, 0, 0, 0, 0, 0,
            4, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, -1, 1, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
        ),
        (
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 1, -1, 0, 0, 0,
            -4, 0, 0, 0, 0, 0, 0, 0,
            -6, 0, 6, 0, 0, 0, 0, 0,
            0, 0, 0, -4, 0, 0, 0, -5,
        ),
    ]
    # game_state = GameStateV3(board)
    for i in range(start, start + N):
        game_state = game_states[i % 500]

        # timeit(lambda: benchmark(True, game_state_a), number=500) * 1_000
        # game_state_a.get_moves()
        # game_state_b.get_moves()
        # t1.append(mean([benchmark(True, game_state)[1] for i in range(3)]))
        # t2.append(mean([benchmark(False, game_state)[1] for i in range(3)]))
        # timeit(lambda: benchmark(True, game_state_a), number=20)
        game_state_a = game_state.to_bitboards_v3()
        move = random.choice(game_state_a.get_moves())
        t1.append(timeit(lambda: benchmark(True, game_state_a, move), number=n) * scale / n)
        game_state_b = game_state.to_v3()
        move = random.choice(game_state_b.get_moves())
        t2.append(timeit(lambda: benchmark(False,game_state_b, move), number=n) * scale / n)
        t3.append(t1[-1] - t2[-1])
        if (i - start) > 0 and (i - start) % max(1, (N // 50)) == 0:
            t, p = stats.ttest_1samp(t3, 0, alternative='less')
            # t, p = stats.ttest_ind(t1, t2, equal_var=False, alternative='less')
            print(f'{(i - start)}:')
            print(f'New: {mean(t1):#.5g}{unit}, {stdev(t1):#.5g}{unit}')
            print(f'Old: {mean(t2):#.5g}{unit}, {stdev(t2):#.5g}{unit}\n')
            print(f'T-statistic: {t:#.5g}\nP-value: {p:#.5g}\n')
    t1 = t1[N // 100:]
    t2 = t2[N // 100:]
    t3 = t3[N // 100:]
    # print(f'{t1}\n{t2}\n{t3}')
    print()
    print(f'Mean New: {mean(t1):#.5g}{unit}\nStdDev New: {stdev(t1):#.5g}{unit}\nN New: {len(t1):}\n')
    print(f'Mean Old: {mean(t2):#.5g}{unit}\nStdDev Old: {stdev(t2):#.5g}{unit}\nN Old: {len(t2)}\n')
    print(f'Mean Diff: {mean(t3):#.5g}{unit}\nStdDev Diff: {stdev(t3):#.5g}{unit}\nN Diff: {len(t3)}')
    print()
    t, p = stats.ttest_ind(t1, t2, equal_var=False, alternative='less')
    print(f'2-Sample T-Test:\nT-statistic: {t:#.5g}\nP-value: {p:#.5g}\n')
    t, p = stats.ttest_1samp(t3, 0, alternative='less')
    print(f'1-Sample T-Test of Difference:\nT-statistic: {t:#.5g}\nP-value: {p:#.5g}')
    print()
    print(f'Speedup: {mean(t2) / mean(t1):#.5g}')
    print(f'Slowdown: {mean(t1) / mean(t2):#.5g}')


def profile():
    # bot = BotV2p3()
    # game_states_local = game_states

    profiler = cProfile.Profile()

    profiler.enable()

    deep_test()
    # for i in range(10_000):
    #     game_state = game_states_local[i % 500].to_v3()
    #     game_state.moves = None
    #     game_state.get_moves()

    profiler.disable()

    s = StringIO()
    stats = Stats(profiler, stream=s)
    stats.strip_dirs().sort_stats('tottime')
    stats.print_stats()
    print('\n\n')

    lines = s.getvalue().splitlines()
    printed_header = False
    for line in lines:
        if line.startswith(" " * 3) or line.strip().startswith("ncalls"):
            parts = line.split()
            if len(parts) >= 6:
                if not printed_header:
                    print(f"{'function':45}  {'tottime':7}  {'cumtime':8}  {'ncalls':8}")
                    printed_header = True
                if parts[-1].startswith("seconds") or parts[-1].startswith("filename"):
                    continue
                print(f"{parts[-1]:45}  {parts[1]:7}  {parts[3]:8}  {parts[0]:8}")
            elif not printed_header and line.strip().startswith("ncalls"):
                # fallback in case headers appear in-line unexpectedly
                print(f"{'function':45}  {'tottime':7}  {'cumtime':8}  {'ncalls':8}")
                printed_header = True


if __name__ == '__main__':
    # deep_test()
    populate_game_states()
    main()
    # profile()
