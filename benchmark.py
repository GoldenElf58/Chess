# from game import GameState
from timeit import timeit
from game import index_to_coord, populate_precomputed_tables, promotion_forward, promotion_taking
from statistics import mean, stdev
from scipy import stats  # type: ignore

populate_precomputed_tables()

def benchmark(condition: bool) -> None:
    board: tuple[int, ...] = (
        0, 0, 0, 0, 0, 0, 0, 0,
        1, 1, 1, 1, 1, 1, 1, 1,
        -1, -1, -1, -1, -1, -1, -1, -1,
        0, 0, 0, 0, 0, 0, 0, 0,
        1, 1, 1, 1, 1, 1, 1, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        -1, -1, -1, -1, -1, -1, -1, -1,
        1, 1, 1, 1, 1, 1, 1, 1
    )
    # game_state: GameState = GameState(board=board)
    #     rook_rays_local:  tuple[tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...],
    # tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...]], ...] = rook_rays
    #     bishop_diagonals_local: tuple[tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...],
    #     tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...]], ...] = bishop_diagonals
    last_move_local = None
    board_local: tuple[int, ...] = board
    coords_local: list[tuple[int, int]] = index_to_coord
    color_local: int = 1
    cond: bool = condition
    for _ in range(10_000):
        moves = []
        color_local *= -1
        for h in range(64):
            i, j = coords_local[h]
            piece_type: int = board[h] * color_local
            if piece_type <= 0: continue  # If piece is 0, blank so skip; if color doesn't match player color skip
            if piece_type == 2:
                if cond:
                    pass
                else:
                    pass


def main() -> None:
    t1 = []
    t2 = []
    for _ in range(100_000_000): pass
    print('Warmup complete')
    for i in range(500):
        t1.append(timeit(lambda: benchmark(True), number=1) * 1000)
        t2.append(timeit(lambda: benchmark(False), number=1) * 1000)
        if i % 50 == 0:
            t, p = stats.ttest_ind(t1, t2, equal_var=False, alternative='less')
            print(f'{i}:\nNew: {mean(t1)}\nOld: {mean(t2)}\nT-statistic: {t:.5f}\nP-value: {p:.5f}\n')
    print(t1, '\n', t2)
    print()
    print(f'Mean New: {mean(t1)}\nStdDev New: {stdev(t1)}\nN New: {len(t1)}\n')
    print(f'Mean Old: {mean(t2)}\nStdDev Old: {stdev(t2)}\nN Old: {len(t2)}')
    print()
    t, p = stats.ttest_ind(t1, t2, equal_var=False, alternative='less')
    print(f'T-statistic: {t:.5f}\nP-value: {p:.5f}')


if __name__ == '__main__':
    main()
