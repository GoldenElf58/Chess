from game_states.game_format_v2 import GameStateFormatV2, start_board
from utils import split_table

# Precompute index-to-coordinate mapping for faster lookups
index_to_coord: list[tuple[int, int]] = [(h // 8, h % 8) for h in range(64)]

knight_targets: tuple[tuple[int, ...], ...]
king_targets: tuple[tuple[int, ...], ...]
rook_rays: tuple[tuple[tuple[int, ...], tuple[int, ...],
tuple[int, ...], tuple[int, ...]], ...]
bishop_diagonals: tuple[tuple[tuple[int, ...], tuple[int, ...],
tuple[int, ...], tuple[int, ...]], ...]
promotion_pieces: tuple[int, ...] = (5, 4, 3, 2)


def populate_precomputed_tables() -> None:
    global knight_targets
    global king_targets
    global rook_rays
    global bishop_diagonals
    temp_knight: list[tuple[int, ...]] = []
    temp_king: list[tuple[int, ...]] = []
    temp_rook: list[tuple[tuple[int, ...], tuple[int, ...],
    tuple[int, ...], tuple[int, ...]]] = []
    temp_bishop: list[tuple[tuple[int, ...], tuple[int, ...],
    tuple[int, ...], tuple[int, ...]]] = []
    for h in range(64):
        i, j = index_to_coord[h]

        curr: list = []
        for k in range(-2, 3, 4):
            for l in range(-1, 2, 2):
                if 8 > i + k >= 0 <= j + l < 8:
                    curr.append((i + k) * 8 + j + l)
                if 8 > i + l >= 0 <= j + k < 8:
                    curr.append((i + l) * 8 + j + k)
        temp_knight.append(tuple(curr))

        curr = []
        for k in range(-1, 2):
            for l in range(-1, 2):
                if 0 <= i + k < 8 and 0 <= j + l < 8:
                    curr.append((i + k) * 8 + j + l)
        temp_king.append(tuple(curr))

        curr = []
        curr2: list[int] = []
        for k in range(j + 1, 8):
            curr2.append(h - j + k)
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(j - 1, -1, -1):
            curr2.append(h - j + k)
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(i + 1, 8):
            curr2.append(k * 8 + j)
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(i - 1, -1, -1):
            curr2.append(k * 8 + j)
        curr.append(tuple(curr2))
        temp_rook.append(tuple(curr))

        curr = []
        curr2 = []
        for k in range(1, 8):
            if i + k > 7 or j + k > 7: break
            curr2.append((i + k) * 8 + (j + k))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(1, 8):
            if i - k < 0 or j + k > 7: break
            curr2.append((i - k) * 8 + (j + k))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(1, 8):
            if i + k > 7 or j - k < 0: break
            curr2.append((i + k) * 8 + (j - k))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(1, 8):
            if i - k < 0 or j - k < 0: break
            curr2.append((i - k) * 8 + (j - k))
        curr.append(tuple(curr2))
        temp_bishop.append(tuple(curr))

    knight_targets = tuple(temp_knight)
    king_targets = tuple(temp_king)
    rook_rays = tuple(temp_rook)
    bishop_diagonals = tuple(temp_bishop)


populate_precomputed_tables()


class GameStateV3(GameStateFormatV2):
    __slots__ = ('board', 'color', 'white_queen', 'white_king', 'black_queen', 'black_king', 'last_move', 'turn',
                 'winner', 'previous_position_count', 'moves_since_pawn', 'moves', 'moves_and_states')

    def __init__(self, board: tuple[int, ...] | None = None, white_queen: bool = True, white_king: bool = True,
                 black_queen: bool = True, black_king: bool = True, last_move: tuple[int, int, int] | None = None,
                 color: int = 1, turn: int = 0, winner: int | None = None,
                 previous_position_count: dict[int, int] | None = None, moves_since_pawn: int = 0) -> None:
        """
        Initialize a GameStateV3 object.

        Parameters
        ----------
        board : list[list[int]], optional
            The starting board. Defaults to `start_board`.
        white_queen : bool, optional
            Whether the white queen is still on the board. Defaults to True.
        white_king : bool, optional
            Whether the white king is still on the board. Defaults to True.
        black_queen : bool, optional
            Whether the black queen is still on the board. Defaults to True.
        black_king : bool, optional
            Whether the black king is still on the board. Defaults to True.
        last_move : tuple[tuple[int, int], tuple[int, int]], optional
            The last move made, as a tuple of two tuples. Defaults to None.
        color : int, optional
            The color of the current player (1 for white, -1 for black). Defaults to 1.
        turn : int, optional
            The turn number. Defaults to 0.
        winner : int | None, optional
            The winner of the game (1 for white, -1 for black, 0 for draw). Defaults to None.
        previous_position_count : dict[int, int] | None, optional
            A dictionary of previous positions and their counts. Defaults to None.
        moves_since_pawn : int, optional
            The number of moves since the last pawn move. Defaults to 0.
        """
        self.moves_and_states: list[tuple[tuple[int, int, int], GameStateV3]] | None = None
        super().__init__(board, white_queen, white_king, black_queen, black_king, last_move,
                         color, turn, winner, previous_position_count, moves_since_pawn)

    def get_hashable_state(self) -> tuple[tuple[int, ...], int, bool, bool, bool, bool,
    tuple[int, int, int] | None, int]:
        """ Convert the game state into a hashable format for caching. """
        return (self.board, self.color, self.white_queen, self.white_king, self.black_queen, self.black_king,
                self.last_move, self.turn)

    def __hash__(self) -> int:
        return hash((self.board, self.color, self.white_queen, self.white_king, self.black_queen, self.black_king,
                     self.last_move, self.turn))

    def get_moves(self) -> list[tuple[int, int, int]]:
        """
        Get all the possible moves for the current player.

        Returns
        -------
        list[tuple[int, int, int]]
            A list of tuples, each representing a move in the format (start_row, start_col, end_row, end_col).
        """
        if self.moves is not None: return self.moves
        moves: list[tuple[int, int, int]] = self.get_moves_no_check()
        self.moves = moves
        pop_idx_base: int = len(moves) - 1
        color_local = self.color
        bishop_diagonals_local: tuple[tuple[tuple[int, ...], tuple[int, ...],
        tuple[int, ...], tuple[int, ...]], ...] = bishop_diagonals
        rook_rays_local: tuple[tuple[tuple[int, ...], tuple[int, ...],
        tuple[int, ...], tuple[int, ...]], ...] = rook_rays
        knight_targets_local: tuple[tuple[int, ...], ...] = knight_targets
        king_targets_local: tuple[tuple[int, ...], ...] = king_targets
        king_idx: int = -1
        coords_local: list[tuple[int, int]] = index_to_coord
        for i, piece in enumerate(self.board):
            if piece * color_local == 6:
                king_idx = i
                break
        for i, move in enumerate(reversed(moves)):
            board_local: list[int] = self.move_only_board(move)
            illegal: bool = False
            if move[0] == -1:  # Castle
                cs0, cs1, cs2 = king_idx, king_idx + move[1], king_idx + move[1] * 2  # type: int, int, int
                for h, piece in enumerate(board_local):
                    piece_type = color_local * piece
                    if piece_type >= 0: continue
                    if piece_type == -3 or piece_type == -5:
                        for diagonal in bishop_diagonals_local[h]:
                            for diagonal_idx in diagonal:
                                if diagonal_idx == cs0 or diagonal_idx == cs1 or diagonal_idx == cs2:
                                    illegal = True
                                    break
                                if board_local[diagonal_idx]:
                                    break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    if (piece_type == -4 or piece_type == -5) and (coords_local[cs0][0] == coords_local[h][0] or
                                                                   coords_local[cs0][1] == coords_local[h][1] or
                                                                   coords_local[cs1][0] == coords_local[h][0] or
                                                                   coords_local[cs1][1] == coords_local[h][1] or
                                                                   coords_local[cs2][0] == coords_local[h][0] or
                                                                   coords_local[cs2][1] == coords_local[h][1]):
                        for ray in rook_rays_local[h]:
                            for ray_idx in ray:
                                if ray_idx == cs0 or ray_idx == cs1 or ray_idx == cs2:
                                    illegal = True
                                    break
                                if board_local[ray_idx]:
                                    break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    elif piece_type == -6:
                        for target_idx in king_targets_local[h]:
                            if target_idx == cs0 or target_idx == cs1 or target_idx == cs2:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break
                    elif piece_type == -2:
                        for target_idx in knight_targets_local[h]:
                            if target_idx == cs0 or target_idx == cs1 or target_idx == cs2:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break
                    elif piece_type == -1:
                        forward_idx = h + color_local * 8
                        if forward_idx + 1 == cs0 or forward_idx + 1 == cs1 or forward_idx + 1 == cs2 or \
                                forward_idx - 1 == cs0 or forward_idx - 1 == cs1 or forward_idx - 1 == cs2:
                            moves.pop(pop_idx_base - i)
                            break
            else:
                check_square: int = move[1] if move[2] == 6 or move[2] == -6 else king_idx
                for h, piece in enumerate(board_local):
                    piece_type = color_local * piece
                    if piece_type >= 0: continue
                    if piece_type == -3 or piece_type == -5 and (
                            check_square % 9 == h % 9 or check_square % 7 == h % 7):
                        for diagonal in bishop_diagonals_local[h]:
                            for diagonal_idx in diagonal:
                                if board_local[diagonal_idx] == 0:
                                    continue
                                if diagonal_idx == check_square:
                                    illegal = True
                                break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    if ((piece_type == -4 or piece_type == -5) and
                            (coords_local[check_square][0] == coords_local[h][0] or
                             coords_local[check_square][1] == coords_local[h][1])):
                        for ray in rook_rays_local[h]:
                            for ray_idx in ray:
                                if board_local[ray_idx] == 0:
                                    continue
                                if ray_idx == check_square:
                                    illegal = True
                                break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    elif piece_type == -6:
                        for target_idx in king_targets_local[h]:
                            if target_idx == check_square:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break
                    elif piece_type == -2:
                        for target_idx in knight_targets_local[h]:
                            if target_idx == check_square:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break
                    elif piece_type == -1:
                        forward_idx = h + color_local * 8
                        if ((forward_idx + 1 == check_square and coords_local[h][1] != 7) or
                            (forward_idx - 1 == check_square and coords_local[h][1] != 0)):
                            moves.pop(pop_idx_base - i)
                            break

        if len(moves) == 0 and pop_idx_base > -1:
            game_state: GameStateV3 = GameStateV3(self.board, False, False, False,
                                                False, color=-self.color)
            for _, dest_idx, _ in game_state.get_moves_no_check():
                if dest_idx == king_idx:
                    self.winner = -self.color
                    return moves
            self.winner = 0
            return moves
        elif self.moves_since_pawn >= 100:
            self.winner = 0
        return moves

    def get_moves_new_a(self) -> list[tuple[int, int, int]]:
        """
        Get all the possible moves for the current player.

        Returns
        -------
        list[tuple[int, int, int]]
            A list of tuples, each representing a move in the format (start_row, start_col, end_row, end_col).
        """
        if self.moves is not None: return self.moves
        moves: list[tuple[int, int, int]] = self.get_moves_no_check()
        self.moves = moves
        pop_idx_base: int = len(moves) - 1
        color_local = self.color
        bishop_diagonals_local: tuple[tuple[tuple[int, ...], tuple[int, ...],
        tuple[int, ...], tuple[int, ...]], ...] = bishop_diagonals
        rook_rays_local: tuple[tuple[tuple[int, ...], tuple[int, ...],
        tuple[int, ...], tuple[int, ...]], ...] = rook_rays
        knight_targets_local: tuple[tuple[int, ...], ...] = knight_targets
        king_targets_local: tuple[tuple[int, ...], ...] = king_targets
        king_idx: int = -1
        coords_local: list[tuple[int, int]] = index_to_coord
        for i, piece in enumerate(self.board):
            if piece * color_local == 6:
                king_idx = i
                break
        for i, move in enumerate(reversed(moves)):
            board_local: list[int] = self.move_only_board(move)
            illegal: bool = False
            if move[0] == -1:  # Castle
                cs0, cs1, cs2 = move[2], move[2] + move[1], move[2] + move[1] * 2  # type: int, int, int
                for h, piece in enumerate(board_local):
                    piece_type = color_local * piece
                    if piece_type >= 0: continue
                    if piece_type == -3 or piece_type == -5:
                        for diagonal in bishop_diagonals_local[h]:
                            for diagonal_idx in diagonal:
                                if board_local[diagonal_idx] == 0:
                                    continue
                                if diagonal_idx == cs0 or diagonal_idx == cs1 or diagonal_idx == cs2:
                                    illegal = True
                                break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    if (piece_type == -4 or piece_type == -5) and (coords_local[cs0][0] == coords_local[h][0] or
                                                                   coords_local[cs0][1] == coords_local[h][1] or
                                                                   coords_local[cs1][0] == coords_local[h][0] or
                                                                   coords_local[cs1][1] == coords_local[h][1] or
                                                                   coords_local[cs2][0] == coords_local[h][0] or
                                                                   coords_local[cs2][1] == coords_local[h][1]):
                        for ray in rook_rays_local[h]:
                            for ray_idx in ray:
                                if board_local[ray_idx] == 0:
                                    continue
                                if ray_idx == cs0 or ray_idx == cs1 or ray_idx == cs2:
                                    illegal = True
                                break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    elif piece_type == -6:
                        for target_idx in king_targets_local[h]:
                            if target_idx == cs0 or target_idx == cs1 or target_idx == cs2:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break
                    elif piece_type == -2:
                        for target_idx in knight_targets_local[h]:
                            if target_idx == cs0:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break
                    elif piece_type == -1:
                        dest_square = h + color_local * 8
                        if dest_square + 1 == cs0 or dest_square + 1 == cs1 or dest_square + 1 == cs2 or \
                                dest_square - 1 == cs0 or dest_square - 1 == cs1 or dest_square - 1 == cs2:
                            moves.pop(pop_idx_base - i)
                            break
            else:
                check_square: int = move[1] if move[2] == 6 or move[2] == -6 else king_idx
                for h, piece in enumerate(board_local):
                    piece_type = color_local * piece
                    if piece_type >= 0: continue
                    if piece_type == -3 or piece_type == -5 and (
                            check_square % 9 == h % 9 or check_square % 7 == h % 7):
                        for diagonal in bishop_diagonals_local[h]:
                            for diagonal_idx in diagonal:
                                if board_local[diagonal_idx] == 0:
                                    continue
                                if diagonal_idx == check_square:
                                    illegal = True
                                break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    if ((piece_type == -4 or piece_type == -5) and
                            (coords_local[check_square][0] == coords_local[h][0] or
                             coords_local[check_square][1] == coords_local[h][1])):
                        for ray in rook_rays_local[h]:
                            for ray_idx in ray:
                                if board_local[ray_idx] == 0:
                                    continue
                                if ray_idx == check_square:
                                    illegal = True
                                break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    elif piece_type == -6:
                        for target_idx in king_targets_local[h]:
                            if target_idx == check_square:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break
                    elif piece_type == -2:
                        for target_idx in knight_targets_local[h]:
                            if target_idx == check_square:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break
                    elif piece_type == -1:
                        dest_square = h + color_local * 8
                        if dest_square + 1 == check_square or dest_square - 1 == check_square:
                            moves.pop(pop_idx_base - i)
                            break

        if len(moves) == 0 and pop_idx_base > -1:
            game_state: GameStateV3 = GameStateV3(self.board, False, False, False,
                                                False, color=-self.color)
            for _, dest_idx, _ in game_state.get_moves_no_check():
                if dest_idx == king_idx:
                    self.winner = -self.color
                    return moves
            self.winner = 0
            return moves
        elif self.moves_since_pawn >= 100:
            self.winner = 0
        return moves

    def get_moves_new(self) -> list[tuple[tuple[int, int, int], 'GameStateV3']]:  # type: ignore
        """
        Get all the possible moves for the current player.

        Returns
        -------
        list[tuple[int, int, int]]
            A list of tuples, each representing a move in the format (start_row, start_col, end_row, end_col).
        """
        if self.moves_and_states is not None: return self.moves_and_states
        moves: list[tuple[int, int, int]] = self.get_moves_no_check()
        pop_idx_base: int = len(moves) - 1
        color_local = self.color
        bishop_diagonals_local: tuple[tuple[tuple[int, ...], tuple[int, ...],
        tuple[int, ...], tuple[int, ...]], ...] = bishop_diagonals
        rook_rays_local: tuple[tuple[tuple[int, ...], tuple[int, ...],
        tuple[int, ...], tuple[int, ...]], ...] = rook_rays
        knight_targets_local: tuple[tuple[int, ...], ...] = knight_targets
        king_targets_local: tuple[tuple[int, ...], ...] = king_targets
        coords_local: list[tuple[int, int]] = index_to_coord
        king_idx: int = self.board.index(6 * color_local)
        moves_and_states: list[tuple[tuple[int, int, int], GameStateV3]] = []
        for i, move in enumerate(reversed(moves)):
            state: GameStateV3 = self.move(move)
            moves_and_states.append((move, state))
            board_local: tuple[int, ...] = state.board
            illegal: bool = False
            if move[0] == -1:  # Castle
                cs0, cs1, cs2 = move[2], move[2] + move[1], move[2] + move[1] * 2  # type: int, int, int
                for h, piece in enumerate(board_local):
                    piece_type = color_local * piece
                    if piece_type >= 0: continue
                    if piece_type == -3 or piece_type == -5:
                        for diagonal in bishop_diagonals_local[h]:
                            for diagonal_idx in diagonal:
                                if board_local[diagonal_idx] == 0:
                                    continue
                                if diagonal_idx == cs0 or diagonal_idx == cs1 or diagonal_idx == cs2:
                                    illegal = True
                                break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    if (piece_type == -4 or piece_type == -5) and (coords_local[cs0][0] == coords_local[h][0] or
                                                                   coords_local[cs0][1] == coords_local[h][1] or
                                                                   coords_local[cs1][0] == coords_local[h][0] or
                                                                   coords_local[cs1][1] == coords_local[h][1] or
                                                                   coords_local[cs2][0] == coords_local[h][0] or
                                                                   coords_local[cs2][1] == coords_local[h][1]):
                        for ray in rook_rays_local[h]:
                            for ray_idx in ray:
                                if board_local[ray_idx] == 0:
                                    continue
                                if ray_idx == cs0 or ray_idx == cs1 or ray_idx == cs2:
                                    illegal = True
                                break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    elif piece_type == -6:
                        for target_idx in king_targets_local[h]:
                            if target_idx == cs0 or target_idx == cs1 or target_idx == cs2:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break
                    elif piece_type == -2:
                        for target_idx in knight_targets_local[h]:
                            if target_idx == cs0:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break
                    elif piece_type == -1:
                        dest_square = h + color_local * 8
                        if dest_square + 1 == cs0 or dest_square + 1 == cs1 or dest_square + 1 == cs2 or \
                                dest_square - 1 == cs0 or dest_square - 1 == cs1 or dest_square - 1 == cs2:
                            moves.pop(pop_idx_base - i)
                            break
            else:
                check_square: int = move[1] if move[2] == 6 or move[2] == -6 else king_idx
                for h, piece in enumerate(board_local):
                    piece_type = color_local * piece
                    if piece_type >= 0: continue
                    if piece_type == -3 or piece_type == -5 and (
                            check_square % 9 == h % 9 or check_square % 7 == h % 7):
                        for diagonal in bishop_diagonals_local[h]:
                            for diagonal_idx in diagonal:
                                if board_local[diagonal_idx] == 0:
                                    continue
                                if diagonal_idx == check_square:
                                    illegal = True
                                break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    if ((piece_type == -4 or piece_type == -5) and
                            (coords_local[check_square][0] == coords_local[h][0] or
                             coords_local[check_square][1] == coords_local[h][1])):
                        for ray in rook_rays_local[h]:
                            for ray_idx in ray:
                                if board_local[ray_idx] == 0:
                                    continue
                                if ray_idx == check_square:
                                    illegal = True
                                break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    elif piece_type == -6:
                        for target_idx in king_targets_local[h]:
                            if target_idx == check_square:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break
                    elif piece_type == -2:
                        for target_idx in knight_targets_local[h]:
                            if target_idx == check_square:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break
                    elif piece_type == -1:
                        dest_square = h + color_local * 8
                        if dest_square + 1 == check_square or dest_square - 1 == check_square:
                            moves.pop(pop_idx_base - i)
                            break

        self.moves_and_states = moves_and_states
        if len(moves) == 0 and pop_idx_base > -1:
            game_state: GameStateV3 = GameStateV3(self.board, self.white_queen, self.white_king,
                                                  self.black_queen, self.black_king,
                                                  color=-self.color, turn=self.turn, winner=self.winner)
            for move in game_state.get_moves_no_check():
                if (winner := game_state.move(move).get_winner()) == -1 or winner == 1:
                    break
            else:
                self.winner = 0
                return moves_and_states
            self.winner = winner
        elif self.moves_since_pawn >= 100:
            self.winner = 0
        return moves_and_states

    def get_new_states(self) -> list[tuple[tuple[int, int, int], 'GameStateV3']]:
        """
        Get all the possible moves for the current player.

        Returns
        -------
        list[tuple[int, int, int]]
            A list of tuples, each representing a move in the format (start_row, start_col, end_row, end_col).
        """
        if self.moves_and_states is not None: return self.moves_and_states
        moves: list[tuple[int, int, int]] = self.get_moves_no_check()
        pop_idx_base: int = len(moves) - 1
        moves_and_states: list[tuple[tuple[int, int, int], GameStateV3]] = []
        color_local: int = self.color
        for i, move in enumerate(reversed(moves)):
            state: GameStateV3 = self.move(move)
            for move_2 in state.get_moves_no_check():
                if (winner := (state_2 := state.move(move_2)).get_winner()) == -1 or winner == 1:
                    moves.pop(pop_idx_base - i)
                    break
                elif move[0] == -1:
                    if move[1] == 1:
                        for idx in range(move[2], move[2] + 2):
                            if state_2.board[idx] * color_local < 0:
                                break
                        else:
                            continue
                    else:
                        for idx in range(move[2] - 1, move[2] + 1):
                            if state_2.board[idx] * color_local < 0:
                                break
                        else:
                            continue
                    moves.pop(pop_idx_base - i)
                    break
            else:
                moves_and_states.append((move, state))
        if len(moves) == 0 and pop_idx_base > -1:
            game_state: GameStateV3 = GameStateV3(self.board, self.white_queen, self.white_king,
                                                  self.black_queen, self.black_king,
                                                  color=-color_local, turn=self.turn, winner=self.winner)
            for move in game_state.get_moves_no_check():
                if (winner := game_state.move(move).get_winner()) == -1 or winner == 1:
                    break
            else:
                self.winner = 0
                self.moves = moves
                return moves_and_states
            self.winner = winner
        elif self.moves_since_pawn >= 100:
            self.winner = 0
        self.moves = moves
        return moves_and_states

    def get_moves_no_check(self) -> list[tuple[int, int, int]]:
        moves: list[tuple[int, int, int]] = []
        # Local binds for speed
        color_local: int = self.color
        board_local: tuple[int, ...] = self.board
        last_move_local: tuple[int, int, int] | None = self.last_move
        coords_local: list[tuple[int, int]] = index_to_coord
        knight_targets_local: tuple[tuple[int, ...], ...] = knight_targets
        king_targets_local: tuple[tuple[int, ...], ...] = king_targets
        rook_rays_local: tuple[tuple[tuple[int, ...], tuple[int, ...],
        tuple[int, ...], tuple[int, ...]], ...] = rook_rays
        bishop_diagonals_local: tuple[tuple[tuple[int, ...], tuple[int, ...],
        tuple[int, ...], tuple[int, ...]], ...] = bishop_diagonals
        for h, (piece, (i, j)) in enumerate(zip(board_local, coords_local)):
            piece_type: int = piece * color_local
            if piece_type <= 0: continue
            if piece_type == 6:  # King
                row_base: int = h - j
                if (((color_local == 1 and self.white_king) or (color_local == -1 and self.black_king)) and
                        board_local[row_base + 7] == 4 * color_local
                        and board_local[row_base + 5] == board_local[row_base + 6] == 0):
                    moves.append((-1, 1, h))
                if (((color_local == 1 and self.white_queen) or (color_local == -1 and self.black_queen)) and
                        board_local[row_base] == 4 * color_local
                        and board_local[row_base + 1] == board_local[row_base + 2] == board_local[row_base + 3] == 0):
                    moves.append((-1, -1, h))
                for target_idx in king_targets_local[h]:
                    if board_local[target_idx] * color_local <= 0:
                        moves.append((h, target_idx, piece))
            elif piece_type == 4 or piece_type == 5:  # Rook and Queen
                for ray in rook_rays_local[h]:
                    for ray_idx in ray:
                        if board_local[ray_idx] * color_local <= 0:
                            moves.append((h, ray_idx, piece))
                        if board_local[ray_idx] == 0:
                            continue
                        break
            if piece_type == 3 or piece_type == 5:  # Bishop and Queen
                for diagonal in bishop_diagonals_local[h]:
                    for diagonal_idx in diagonal:
                        if board_local[diagonal_idx] == 0:
                            moves.append((h, diagonal_idx, piece))
                            continue
                        if board_local[diagonal_idx] * color_local < 0:
                            moves.append((h, diagonal_idx, piece))
                        break
            elif piece_type == 2:  # Knight
                for target_idx in knight_targets_local[h]:
                    if board_local[target_idx] * color_local <= 0:
                        moves.append((h, target_idx, piece))
            elif piece_type == 1:
                dest_square: int = h - color_local * 8
                if board_local[dest_square] == 0:
                    if 7 != i - color_local != 0:
                        moves.append((h, dest_square, piece))
                    else:
                        for promotion_piece in promotion_pieces:
                            moves.append((h, dest_square, promotion_piece * color_local))
                if 8 > (j + 1) and 0 > board_local[dest_square + 1] * color_local:
                    if 7 != i - color_local != 0:
                        moves.append((h, dest_square + 1, piece))
                    else:  # Promotion
                        for promotion_piece in promotion_pieces:
                            moves.append((h, dest_square + 1, promotion_piece * color_local))
                if (j - 1) >= 0 > board_local[dest_square - 1] * color_local:
                    if 7 != i - color_local != 0:
                        moves.append((h, dest_square - 1, piece))
                    else:  # Promotion
                        for promotion_piece in promotion_pieces:
                            moves.append((h, dest_square - 1, promotion_piece * color_local))
                if color_local == 1:
                    if i == 6 and board_local[4 * 8 + j] == 0 == board_local[5 * 8 + j]:
                        moves.append((h, h - 16, piece))  # TODO: Make this count toward 50 move rule
                elif i == 1 and board_local[3 * 8 + j] == 0 == board_local[2 * 8 + j]:
                    moves.append((h, h + 16, piece))
                # En Passant
                if last_move_local is not None and i == last_move_local[1] // 8:
                    if 7 != j == last_move_local[1] % 8 + 1:
                        moves.append((-2, -1, h))
                    elif 0 != j == last_move_local[1] % 8 - 1:
                        moves.append((-2, 1, h))
        return moves

    def are_captures(self) -> bool:
        moves: list[tuple[int, int, int]] = self.get_moves()
        board_local: tuple[int, ...] = self.board
        empty_count: int = board_local.count(0)
        for move in moves:
            new_board: list[int] = self.move_only_board(move)
            if new_board.count(0) != empty_count:
                return True
        return False

    def move(self, move: tuple[int, int, int]) -> 'GameStateV3':
        """
        Make a move on the board.

        Parameters
        ----------
        move : tuple[tuple[int, int], tuple[int, int]]
            The move to make, as a tuple of two tuples. The first tuple is the
            piece to move, with the first element being the row and the second
            element being the column. The second tuple is the destination, with
            the first element being the row and the second element being the
            column.

        Returns
        -------
        GameStateV3
            A new GameState object, with the move applied.
        """
        board_local: tuple[int, ...] = self.board
        new_board: list[int] = list(board_local)
        white_queen: bool = self.white_queen
        white_king: bool = self.white_king
        black_queen: bool = self.black_queen
        black_king: bool = self.black_king
        new_moves_since_pawn: int = self.moves_since_pawn + 1

        if not len(move):
            return GameStateV3(board_local, turn=self.turn + 1, winner=self.winner)

        move_0, move_1, move_2 = move  # type: int, int, int
        if move_0 == -1:  # Castle
            if move_2 == 4:
                black_queen = False
                black_king = False
            else:
                white_queen = False
                white_king = False

            new_board[move_2] = 0
            new_board[move_2 + (3 if move_1 == 1 else -4)] = 0
            new_board[move_2 + move_1] = board_local[move_2 + (3 if move_1 == 1 else -4)]
            new_board[move_2 + 2 * move_1] = board_local[move_2]
            return GameStateV3(tuple(new_board), white_queen, white_king, black_queen, black_king,
                               color=-self.color, turn=self.turn + 1, moves_since_pawn=new_moves_since_pawn)

        if move_0 == -2:  # En Passant
            new_board[move_2] = 0
            new_board[move_2 - 8 * self.color + move_1] = self.color
            new_board[move_2 + move_1] = 0
            return GameStateV3(tuple(new_board), white_queen, white_king, black_queen, black_king,
                               color=-self.color, turn=self.turn + 1)

        if (piece := abs(move_2)) == 6:
            if move_0 == 4:
                black_queen = False
                black_king = False
            elif move_0 == 60:
                white_queen = False
                white_king = False
        elif piece == 4:
            if move_0 == 56:
                white_queen = False
            elif move_0 == 63:
                white_king = False
            elif not move_0:
                black_queen = False
            elif move_0 == 7:
                black_king = False
        elif piece == 1:
            new_moves_since_pawn = 0

        new_board[move_1] = move_2
        new_board[move_0] = 0
        new_previous_position_count = dict(self.previous_position_count)
        if (hash_state := hash(board_local)) in new_previous_position_count:
            new_previous_position_count[hash_state] += 1
            if new_previous_position_count[hash_state] >= 3:
                return GameStateV3(tuple(new_board), winner=0)
        else:
            new_previous_position_count[hash_state] = 1
        last_move: tuple[int, int, int] | None = move if (
                piece == 1 and (move_0 == move_1 + self.color * 16)) else None
        return GameStateV3(tuple(new_board), white_queen, white_king, black_queen, black_king, last_move=last_move,
                           color=-self.color, turn=self.turn + 1, moves_since_pawn=new_moves_since_pawn,
                           previous_position_count=new_previous_position_count)

    def move_only_board(self, move: tuple[int, int, int]) -> list[int]:
        """
        Make a move on the board.

        Parameters
        ----------
        move : tuple[tuple[int, int], tuple[int, int]]
            The move to make, as a tuple of two tuples. The first tuple is the
            piece to move, with the first element being the row and the second
            element being the column. The second tuple is the destination, with
            the first element being the row and the second element being the
            column.

        Returns
        -------
        GameStateV3
            A new GameState object, with the move applied.
        """
        new_board: list[int] = list(self.board)

        move_0, move_1, move_2 = move  # type: int, int, int
        if move_0 == -1:  # Castle
            new_board[move_2] = 0
            new_board[move_2 + (3 if move_1 == 1 else -4)] = 0
            new_board[move_2 + move_1] = self.board[move_2 + (3 if move_1 == 1 else -4)]
            new_board[move_2 + 2 * move_1] = self.board[move_2]
            return new_board

        if move_0 == -2:  # En Passant
            new_board[move_2] = 0
            new_board[move_2 - 8 * self.color + move_1] = self.color
            new_board[move_2 + move_1] = 0
            return new_board

        new_board[move_0] = 0
        new_board[move_1] = move_2
        return new_board

    def move_only_board_new(self, move: tuple[int, int, int]) -> list[int]:
        """
        Make a move on the board.

        Parameters
        ----------
        move : tuple[tuple[int, int], tuple[int, int]]
            The move to make, as a tuple of two tuples. The first tuple is the
            piece to move, with the first element being the row and the second
            element being the column. The second tuple is the destination, with
            the first element being the row and the second element being the
            column.

        Returns
        -------
        GameStateV3
            A new GameState object, with the move applied.
        """
        new_board: list[int] = list(self.board)

        move_0, move_1, move_2 = move  # type: int, int, int
        if move_0 == -1:  # Castle
            new_board[move_2] = 0
            new_board[move_2 + (3 if move_1 == 1 else -4)] = 0
            new_board[move_2 + move_1] = self.board[move_2 + (3 if move_1 == 1 else -4)]
            new_board[move_2 + 2 * move_1] = self.board[move_2]
            return new_board

        if move_0 == -2:  # En Passant
            new_board[move_2] = 0
            new_board[move_2 - 8 * self.color + move_1] = self.color
            new_board[move_2 + move_1] = 0
            return new_board

        new_board[move_0] = 0
        new_board[move_1] = move_2
        return new_board

    def get_winner(self) -> int | None:
        if self.winner is not None:
            return self.winner
        if self.moves_since_pawn >= 100:
            self.winner = 0
            return 0
        white: bool = 6 in self.board
        black: bool = -6 in self.board
        if white and not black:
            self.winner = 1
        elif black and not white:
            self.winner = -1
        else:
            for piece in self.board:
                if 0 != piece != 6 and piece != -6:
                    return None
            self.winner = 0
        return self.winner

    def __repr__(self) -> str:
        return f"""GameStateV3(board={self.board}
          color={self.color},
          turn={self.turn},
          winner={self.winner},
          previous_position_count={self.previous_position_count},
          moves_since_pawn={self.moves_since_pawn},
          moves={self.moves},
          white_queen={self.white_queen},
          white_king={self.white_king},
          black_queen={self.black_queen},
          black_king={self.black_king},
          last_move={self.last_move})
"""

    def __str__(self) -> str:
        """
        Return a string representation of the board.

        This string is an 8x8 grid of characters, with each character
        representing a piece on the board. The characters are as follows:

        - K: King
        - Q: Queen
        - R: Rook
        - B: Bishop
        - N: Knight
        - P: Pawn
        -  : Empty space
        - k: Black King
        - q: Black Queen
        - r: Black Rook
        - b: Black Bishop
        - n: Black Knight
        - p: Black Pawn

        The string is formatted with lines separating each row of the board,
        and pipes (|) separating each column.

        :return: A string representation of the board.
        """
        result: str = "_________________________________\n"
        for row in split_table(self.board):
            result += "| "
            for piece in row:
                if piece == 6:
                    result += "K"
                elif piece == 5:
                    result += "Q"
                elif piece == 4:
                    result += "R"
                elif piece == 3:
                    result += "B"
                elif piece == 2:
                    result += "N"
                elif piece == 1:
                    result += "P"
                elif piece == 0:
                    result += " "
                elif piece == -6:
                    result += "k"
                elif piece == -5:
                    result += "q"
                elif piece == -4:
                    result += "r"
                elif piece == -3:
                    result += "b"
                elif piece == -2:
                    result += "n"
                elif piece == -1:
                    result += "p"
                result += " | "
            result += "\n|___|___|___|___|___|___|___|___|\n"

        return result
