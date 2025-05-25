from timeit import timeit

from fen_utils import game_state_from_line
from statistics import mean, stdev
from scipy import stats  # type: ignore

game_states: list = []

def populate_game_states():
    global game_states
    game_states = [game_state_from_line(i) for i in range(1, 501)]
    print("Game States created")
    for game_state in game_states:
        game_state.get_moves()
    print("Moves calculated")

populate_game_states()

def benchmark(condition: bool, game_state) -> None:
    if condition:
        game_state.get_moves_new()
    else:
        game_state.get_moves()
        # bot = Botv1()
        # bot.minimax(game_state, 3, -(1 << 40), (1 << 40), game_state.color == 1)


def main() -> None:
    t1 = []
    t2 = []
    t3 = []
    for _ in range(50_000_000): pass
    print('Warmup complete')
    for i in range(5000):
        game_state = game_states[i % 500]
        # t1.append(mean([benchmark(True, game_state)[1] for i in range(3)]))
        # t2.append(mean([benchmark(False, game_state)[1] for i in range(3)]))
        t1.append(timeit(lambda: benchmark(True, game_state), number=30_000) * 1_000)
        t2.append(timeit(lambda: benchmark(False, game_state), number=30_000) * 1_000)
        t3.append(t1[-1] - t2[-1])
        if i > 0 and i % 500 == 0:
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
