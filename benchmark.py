# from game import GameState
from timeit import timeit
from game import index_to_coord, populate_precomputed_tables, rook_rays
from statistics import mean, stdev
from scipy import stats  # type: ignore

populate_precomputed_tables()

def benchmark(condition: bool) -> None:
    board: tuple[int, ...] = ( # Unsure
        -2, 0, 0, 0, 0, 0, 0, 0,
        0, -2, 0, 0, 0, 0, 0, 0,
        0, 0, -2, 0, 0, 0, 0, 0,
        0, 0, 0, -2, 0, 0, 0, 0,
        0, 0, 0, 0, 2, 0, 0, 0,
        0, 0, 0, 0, 0, 2, 0, 0,
        0, 0, 0, 0, 0, 0, 2, 0,
        0, 0, 0, 0, 0, 0, 0, 2
    )
    # game_state: GameState = GameState(board=board)
    rook_rays_local:  tuple[tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...],
tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...]], ...] = rook_rays
#     bishop_diagonals_local: tuple[tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...],
#     tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...]], ...] = bishop_diagonals
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
            if piece_type <= 0:  # If piece is 0, blank so skip; if color doesn't match player color skip
                continue
            if piece_type == 2:
                if cond:
                    for ray in rook_rays_local[h]:
                        for (idx, ray_i, ray_j) in ray:
                            if (target_piece := board_local[idx]) * color_local <= 0:
                                moves.append((i, j, ray_i, ray_j))
                            if target_piece == 0:
                                continue
                            break
                else:
                    for ray in rook_rays_local[h]:
                        for (idx, ray_i, ray_j) in ray:
                            if board_local[idx] * color_local <= 0:
                                moves.append((i, j, ray_i, ray_j))
                            if board_local[idx] == 0:
                                continue
                            break


def main() -> None:
    t1 = []
    t2 = []
    for _ in range(100_000_000): pass
    print('Warmup complete')
    for i in range(100):
        t1.append(timeit(lambda: benchmark(True), number=1))
        t2.append(timeit(lambda: benchmark(False), number=1))
        if i % 10 == 0:
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
