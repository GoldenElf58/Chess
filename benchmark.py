from copy import deepcopy
from timeit import timeit
from typing import Any

from fen_utils import game_state_from_line
from statistics import mean, stdev
from scipy import stats  # type: ignore
from game import GameState
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

def benchmark(condition: bool, game_state: GameState) -> None:
    # assert game_state is not None
    # game_state_local: GameState = deepcopy(game_state)
    # game_state_local.last_move = None
    # game_state_v2: GameStatev2 = game_state.to_v2()
    # game_state_v2.get_moves()
    # game_state_local.get_moves()
    move: Any
    # game_state.moves = None
    # game_state.previous_position_count = {}
    # game_state.get_moves()
    assert game_state.moves is not None
    # for move in game_state.moves:
    #     game_state.move(move)
    game_state.get_winner()


def main() -> None:
    t1 = []
    t2 = []
    t3 = []
    for _ in range(50_000_000): pass
    print('Warmup complete')
    for i in range(500):
        game_state = deepcopy(game_states[i % 500])
        game_state_bitboards = game_state.to_bitboards()
        game_state.get_moves()
        game_state_bitboards.get_moves()
        # t1.append(mean([benchmark(True, game_state)[1] for i in range(3)]))
        # t2.append(mean([benchmark(False, game_state)[1] for i in range(3)]))
        t1.append(timeit(lambda: benchmark(True, game_state_bitboards), number=20) * 1_000)
        t2.append(timeit(lambda: benchmark(False, game_state), number=20) * 1_000)
        t3.append(t1[-1] - t2[-1])
        if i > 0 and i % 100 == 0:
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
