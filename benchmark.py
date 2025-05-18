# from game import GameState
from timeit import timeit
from game import index_to_coord, populate_precomputed_tables, rook_rays

populate_precomputed_tables()

def benchmark(condition: bool) -> None:
    board: tuple[int, ...] = (
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
    coords_local: list[tuple[int, int]] = index_to_coord
    color_local: int = 1
    for _ in range(500_000):
        moves = []
        color_local *= -1
        for h in range(64):
            i, j = coords_local[h]
            piece_type: int = board[h] * color_local
            if piece_type <= 0:  # If piece is 0, blank so skip; if color doesn't match player color skip
                continue
            if piece_type == 2 and condition:  # Really knight but pretending rook
                for ray in rook_rays_local[h]:
                    for (idx, ray_i, ray_j) in ray:
                        if board[idx] * color_local <= 0:
                            moves.append((i, j, ray_i, ray_j))
                        if board[idx] == 0:
                            continue
                        break
            elif piece_type == 2:  # Really knight but pretending rook
                pass


def main() -> None:
    for _ in range(1_000_000):
        ...
    print(timeit(lambda: benchmark(True), number=1))
    print(timeit(lambda: benchmark(False), number=1))


if __name__ == '__main__':
    main()
