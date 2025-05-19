# from game import GameState
from timeit import timeit
from game import index_to_coord, populate_precomputed_tables, bishop_diagonals
import statistics
from scipy import stats

populate_precomputed_tables()

def benchmark(condition: bool) -> None:
    board: tuple[int, ...] = ( # Unsure
        -2, -2, -2, -2, -2, -2, -2, -2,
        2, 2, 2, 2, 2, 2, 2, 2,
        -2, -2, -2, -2, -2, -2, -2, -2,
        2, 2, 2, 2, 2, 2, 2, 2,
        -2, -2, -2, -2, -2, -2, -2, -2,
        2, 2, 2, 2, 2, 2, 2, 2,
        -2, -2, -2, -2, -2, -2, -2, -2,
        2, 2, 2, 2, 2, 2, 2, 2
    )
    # board: tuple[int, ...] = ( # Unsure
    #     -2, 0, 0, 0, 0, 0, 0, 0,
    #     0, -2, 0, 0, 0, 0, 0, 0,
    #     0, 0, -2, 0, 0, 0, 0, 0,
    #     0, 0, 0, -2, 0, 0, 0, 0,
    #     0, 0, 0, 0, 2, 0, 0, 0,
    #     0, 0, 0, 0, 0, 2, 0, 0,
    #     0, 0, 0, 0, 0, 0, 2, 0,
    #     0, 0, 0, 0, 0, 0, 0, 2
    # )
    # board: tuple[int, ...] = ( # New method better
    #     -2, -2, -2, -2, -2, -2, -2, -2,
    #     0, 0, 0, 0, 0, 0, 0, 0,
    #     0, 0, 0, 0, 0, 0, 0, 0,
    #     0, 0, 0, 0, 0, 0, 0, 0,
    #     2, 2, 2, 2, 2, 2, 2, 2,
    #     0, 0, 0, 0, 0, 0, 0, 0,
    #     0, 0, 0, 0, 0, 0, 0, 0,
    #     -2, -2, -2, -2, -2, -2, -2, -2
    # )
    # game_state: GameState = GameState(board=board)
#     rook_rays_local:  tuple[tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...],
# tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...]], ...] = rook_rays
    bishop_diagonals_local: tuple[tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...],
    tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...]], ...] = bishop_diagonals
    board_local: tuple[int, ...] = board
    coords_local: list[tuple[int, int]] = index_to_coord
    color_local: int = 1
    cond: bool = condition
    for _ in range(5_000):
        moves = []
        color_local *= -1
        for h in range(64):
            i, j = coords_local[h]
            piece_type: int = board[h] * color_local
            if piece_type <= 0:  # If piece is 0, blank so skip; if color doesn't match player color skip
                continue
            if piece_type == 3:
                if not cond:
                    for diagonal in bishop_diagonals_local[h]:
                        for (idx, diagonal_i, diagonal_j) in diagonal:
                            if board_local[idx] == 0:
                                moves.append((i, j, diagonal_i, diagonal_j))
                                continue
                            if board_local[idx] * color_local < 0:
                                moves.append((i, j, diagonal_i, diagonal_j))
                            break
                else:
                    for k in range(1, 8):
                        if i + k > 7 or j + k > 7: break
                        if (target := board_local[(i + k) * 8 + (j + k)]) == 0:
                            moves.append((i, j, i + k, j + k))
                            continue
                        if target * color_local < 0:
                            moves.append((i, j, i + k, j + k))
                        break
                    for k in range(1, 8):
                        if i - k < 0 or j + k > 7: break
                        if (target := board_local[(i - k) * 8 + (j + k)]) == 0:
                            moves.append((i, j, i - k, j + k))
                            continue
                        if target * color_local < 0:
                            moves.append((i, j, i - k, j + k))
                        break
                    for k in range(1, 8):
                        if i + k > 7 or j - k < 0: break
                        if (target := board_local[(i + k) * 8 + (j - k)]) == 0:
                            moves.append((i, j, i + k, j - k))
                            continue
                        if target * color_local < 0:
                            moves.append((i, j, i + k, j - k))
                        break
                    for k in range(1, 8):
                        if i - k < 0 or j - k < 0: break
                        if (target := board_local[(i - k) * 8 + (j - k)]) == 0:
                            moves.append((i, j, i - k, j - k))
                            continue
                        if target * color_local < 0:
                            moves.append((i, j, i - k, j - k))
                        break


def main() -> None:
    t1 = []
    t2 = []
    for _ in range(100_000_000): pass
    print('Warmup complete')
    for i in range(5_000):
        t2.append(timeit(lambda: benchmark(True), number=1) * 1000)
        t1.append(timeit(lambda: benchmark(False), number=1) * 1000)
        if i % 250 == 0:
            t, p = stats.ttest_ind(t1, t2, equal_var=False, alternative='less')
            print(f'{i}:\nT-statistic: {t:.5f}\nP-value: {p:.5f}\n')
    t1 = t1[10:]
    t2 = t2[10:]
    print(t1, '\n', t2)
    print()
    print(f'Mean 1: {statistics.mean(t1)}\nStdDev 1: {statistics.stdev(t1)}\nN 1: {len(t1)}')
    print(f'Mean 2: {statistics.mean(t2)}\nStdDev 2: {statistics.stdev(t2)}\nN 2: {len(t2)}')
    print()
    t, p = stats.ttest_ind(t1, t2, equal_var=False, alternative='less')
    print(f'T-statistic: {t:.5f}\nP-value: {p:.5f}')

if __name__ == '__main__':
    main()
