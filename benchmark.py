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
                    if 0 <= (i - color_local) < 8:
                        dest_square: int = (i - color_local) * 8 + j
                        if board_local[dest_square] == 0:
                            if 7 != i - color_local != 0:
                                moves.append((i, j, i - color_local, j))
                            else:
                                for id, promotion_piece in promotion_forward:
                                    moves.append((id, promotion_piece, i, j))
                        if 8 > (j + 1) >= 0 > board_local[dest_square + 1] * color_local:
                            if 7 != i - color_local != 0:
                                moves.append((i, j, i - color_local, j + 1))
                            else:  # Promotion
                                for promotion_piece, direction in promotion_taking:
                                    moves.append((promotion_piece, direction, i, j))
                        if 8 > (j - 1) >= 0 > board_local[dest_square - 1] * color_local:
                            if 7 != i - color_local != 0:
                                moves.append((i, j, i - color_local, j - 1))
                            else:  # Promotion
                                for promotion_piece, direction in promotion_taking:
                                    moves.append((promotion_piece, direction, i, j))
                        if color_local == 1:
                            if i == 6 and board_local[4 * 8 + j] == 0 == board_local[5 * 8 + j]:
                                moves.append((i, j, 4, j))
                        elif i == 1 and board_local[3 * 8 + j] == 0 == board_local[2 * 8 + j]:
                            moves.append((i, j, 3, j))
                    # En Passant
                    if (last_move_local is not None and board_local[
                        last_move_local[2] * 8 + last_move_local[3]] == -color_local and abs(
                        last_move_local[2] - last_move_local[0]) == 2 and i == last_move_local[2]):
                        if 7 != j == last_move_local[3] + 1:
                            moves.append((-2, 1, i, j))
                        elif 0 != j == last_move_local[3] - 1:
                            moves.append((-2, -1, i, j))
                else:
                    if 0 <= (i - color_local) < 8:
                        dest_square: int = (i - color_local) * 8 + j  # type: ignore
                        if board_local[dest_square] == 0:
                            if 7 != i - color_local != 0:
                                moves.append((i, j, i - color_local, j))
                            elif i - color_local == 0:  # Promotion
                                moves.append((-3, 5, i, j))
                                moves.append((-3, 4, i, j))
                                moves.append((-3, 3, i, j))
                                moves.append((-3, 2, i, j))
                            else:  # Promotion
                                moves.append((-3, -5, i, j))
                                moves.append((-3, -4, i, j))
                                moves.append((-3, -3, i, j))
                                moves.append((-3, -2, i, j))
                        if 8 > (j + 1) >= 0 > board_local[dest_square + 1] * color_local:
                            if 7 != i - color_local != 0:
                                moves.append((i, j, i - color_local, j + 1))
                            else:  # Promotion
                                moves.append((-7, 1, i, j))
                                moves.append((-6, 1, i, j))
                                moves.append((-5, 1, i, j))
                                moves.append((-4, 1, i, j))
                        if 8 > (j - 1) >= 0 > board_local[dest_square - 1] * color_local:
                            if 7 != i - color_local != 0:
                                moves.append((i, j, i - color_local, j - 1))
                            else:  # Promotion
                                moves.append((-7, -1, i, j))
                                moves.append((-6, -1, i, j))
                                moves.append((-5, -1, i, j))
                                moves.append((-4, -1, i, j))
                        if color_local == 1:
                            if i == 6 and board_local[4 * 8 + j] == 0 == board_local[5 * 8 + j]:
                                moves.append((i, j, 4, j))
                        elif i == 1 and board_local[3 * 8 + j] == 0 == board_local[2 * 8 + j]:
                            moves.append((i, j, 3, j))
                    # En Passant
                    if (last_move_local is not None and board_local[
                        last_move_local[2] * 8 + last_move_local[3]] == -color_local and abs(
                        last_move_local[2] - last_move_local[0]) == 2 and i == last_move_local[2]):
                        if 7 != j == last_move_local[3] + 1:
                            moves.append((-2, 1, i, j))
                        elif 0 != j == last_move_local[3] - 1:
                            moves.append((-2, -1, i, j))


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
