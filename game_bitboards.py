import copy
from game_base import GameStateBase

# Precompute index-to-coordinate mapping for faster lookups
index_to_coord: list[tuple[int, int]] = [(h // 8, h % 8) for h in range(64)]

knight_targets: tuple[tuple[tuple[int, int, int], ...], ...]
king_targets: tuple[tuple[tuple[int, int, int], ...], ...]
rook_rays: tuple[tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...],
tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...]], ...]
bishop_diagonals: tuple[tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...],
tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...]], ...]
promotion_forward: tuple[tuple[int, int], ...] = ((-3, 5), (-3, 4), (-3, 3), (-3, 2))
promotion_taking: tuple[tuple[int, int], ...] = ((-7, 1), (-6, 1), (-5, 1), (-4, 1))


def populate_precomputed_tables() -> None:
    global knight_targets
    global king_targets
    global rook_rays
    global bishop_diagonals
    temp_knight: list[tuple[tuple[int, int, int], ...]] = []
    temp_king: list[tuple[tuple[int, int, int], ...]] = []
    temp_rook: list[tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...],
    tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...]]] = []
    temp_bishop: list[tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...],
    tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...]]] = []
    for h in range(64):
        i, j = index_to_coord[h]

        curr: list = []
        for k in range(-2, 3, 4):
            for l in range(-1, 2, 2):
                if 8 > i + k >= 0 <= j + l < 8:
                    curr.append(((1 << 64 - ((i + k) * 8 + j + l)), i + k, j + l))
                if 8 > i + l >= 0 <= j + k < 8:
                    curr.append(((1 << 64 - ((i + l) * 8 + j + k)), i + l, j + k))
        temp_knight.append(tuple(curr))

        curr = []
        for k in range(-1, 2):
            for l in range(-1, 2):
                if 0 <= i + k < 8 and 0 <= j + l < 8:
                    curr.append(((1 << 64 - ((i + k) * 8 + j + l)), i + k, j + l))
        temp_king.append(tuple(curr))

        curr = []
        curr2: list = []
        for k in range(j + 1, 8):
            curr2.append((1 << 64 - (h - j + k), i, k))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(j - 1, -1, -1):
            curr2.append((1 << 64 - (h - j + k), i, k))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(i + 1, 8):
            curr2.append((1 << 64 - (k * 8 + j), k, j))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(i - 1, -1, -1):
            curr2.append((1 << 64 - (k * 8 + j), k, j))
        curr.append(tuple(curr2))
        temp_rook.append(tuple(curr))

        curr = []
        curr2 = []
        for k in range(1, 8):
            if i + k > 7 or j + k > 7: break
            curr2.append((1 << 64 - ((i + k) * 8 + (j + k)), i + k, j + k))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(1, 8):
            if i - k < 0 or j + k > 7: break
            curr2.append((1 << 64 - ((i - k) * 8 + (j + k)), i - k, j + k))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(1, 8):
            if i + k > 7 or j - k < 0: break
            curr2.append((1 << 64 - ((i + k) * 8 + (j - k)), i + k, j - k))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(1, 8):
            if i - k < 0 or j - k < 0: break
            curr2.append((1 << 64 - ((i - k) * 8 + (j - k)), i - k, j - k))
        curr.append(tuple(curr2))
        temp_bishop.append(tuple(curr))

    knight_targets = tuple(temp_knight)
    king_targets = tuple(temp_king)
    rook_rays = tuple(temp_rook)
    bishop_diagonals = tuple(temp_bishop)


populate_precomputed_tables()

start_white_pieces = 0b00000000_00000000_00000000_00000000_00000000_00000000_11111111_11111111
start_black_pieces = 0b11111111_11111111_00000000_00000000_00000000_00000000_00000000_00000000
start_kings = 0b00001000_00000000_00000000_00000000_00000000_00000000_00000000_00001000
start_queens = 0b00010000_00000000_00000000_00000000_00000000_00000000_00000000_00010000
start_rooks = 0b10000001_00000000_00000000_00000000_00000000_00000000_00000000_10000001
start_bishops = 0b00100100_00000000_00000000_00000000_00000000_00000000_00000000_00100100
start_knights = 0b01000010_00000000_00000000_00000000_00000000_00000000_00000000_01000010
start_pawns = 0b00000000_11111111_00000000_00000000_00000000_00000000_11111111_00000000


class GameState(GameStateBase):
    __slots__ = ('white_pieces', 'black_pieces', 'kings', 'queens', 'rooks', 'bishops', 'knights', 'pawns',
                 'color', 'white_queen', 'white_king', 'black_queen', 'black_king', 'last_move', 'turn',
                 'winner', 'previous_position_count', 'moves_since_pawn', 'moves', 'hash_state')

    def __init__(self, white_pieces: int | None = None, black_pieces: int | None = None, kings: int | None = None,
                 queens: int | None = None, rooks: int | None = None, bishops: int | None = None,
                 knights: int | None = None, pawns: int | None = None, white_queen: bool = True,
                 white_king: bool = True, black_queen: bool = True, back_king: bool = True,
                 last_move: tuple[int, int, int, int] | None = None, color=1, turn=0, winner: int | None = None,
                 previous_position_count: dict[int, int] | None = None, moves_since_pawn: int = 0) -> None:
        """
        Initialize a GameState object.

        Parameters
        ----------
        white_pieces : int, optional
            Location of white pieces on the board. Defaults to 0b00000000_00000000_00000000_00000000_00000000_00000000_11111111_11111111.
        black_pieces : int, optional
            Location of black pieces on the board. Defaults to 0b11111111_11111111_00000000_00000000_00000000_00000000_00000000_00000000.
        kings : int, optional
            Location of kings on the board. Defaults to 0b00001000_00000000_00000000_00000000_00000000_00000000_00000000_00001000.
        queens : int, optional
            Location of queens on the board. Defaults to 0b00010000_00000000_00000000_00000000_00000000_00000000_00000000_00010000.
        rooks : int, optional
            Location of rooks on the board. Defaults to 0b10000001_00000000_00000000_00000000_00000000_00000000_00000000_10000001.
        bishops : int, optional
            Location of bishops on the board. Defaults to 0b00100100_00000000_00000000_00000000_00000000_00000000_00000000_00100100.
        knights : int, optional
            Location of knights on the board. Defaults to 0b01000010_00000000_00000000_00000000_00000000_00000000_00000000_01000010.
        pawns : int, optional
            Location of pawns on the board. Defaults to 0b00000000_11111111_00000000_00000000_00000000_00000000_11111111_00000000.
        white_queen : bool, optional
            Whether the white queen is still on the board. Defaults to True.
        white_king : bool, optional
            Whether the white king is still on the board. Defaults to True.
        black_queen : bool, optional
            Whether the black queen is still on the board. Defaults to True.
        back_king : bool, optional
            Whether the black king is still on the board. Defaults to True.
        last_move : tuple[tuple[int, int], tuple[int, int]], optional
            The last move made, as a tuple of two tuples. Defaults to None.
        color : int, optional
            The color of the current player (1 for white, -1 for black). Defaults to 1.
        """
        self.white_pieces: int = start_white_pieces if white_pieces is None else white_pieces
        self.black_pieces: int = start_black_pieces if black_pieces is None else black_pieces
        self.kings: int = start_kings if kings is None else kings
        self.queens: int = start_queens if queens is None else queens
        self.rooks: int = start_rooks if rooks is None else rooks
        self.bishops: int = start_bishops if bishops is None else bishops
        self.knights: int = start_knights if knights is None else knights
        self.pawns: int = start_pawns if pawns is None else pawns
        self.color: int = color
        self.white_queen: bool = white_queen
        self.white_king: bool = white_king
        self.black_queen: bool = black_queen
        self.black_king: bool = back_king
        self.last_move: tuple[int, int, int, int] = last_move if last_move is not None else (0, 0, 0, 0)
        self.turn: int = turn
        self.winner: int | None = winner
        self.previous_position_count: dict[
            int, int] = previous_position_count if previous_position_count is not None else {}
        self.moves_since_pawn: int = moves_since_pawn
        self.moves: list[tuple[int, int, int, int]] | None = None
        self.hash_state: int | None = None

    def get_hashable_state(self) -> tuple[int, int, int, int, int, int, int, int, int, bool, bool, bool, bool,
    tuple[int, int, int, int]]:
        """ Convert the game state into a hashable format for caching. """
        return (self.white_pieces, self.black_pieces, self.kings, self.queens, self.rooks, self.bishops, self.knights,
                self.pawns, self.color, self.white_queen, self.white_king, self.black_queen, self.black_king,
                self.last_move)

    def get_hashed(self) -> int:
        return hash((self.white_pieces, self.black_pieces, self.kings, self.queens, self.rooks, self.bishops,
                     self.knights, self.pawns, (((self.color == 1) << 4) | (self.white_queen << 3) | (
                    self.white_king << 2) | (self.black_queen << 1) | self.black_king),
                     self.last_move)) if self.hash_state is None else self.hash_state

    def get_moves(self) -> list[tuple[int, int, int, int]]:
        """
        Get all the possible moves for the current player.

        Returns
        -------
        list[tuple[int, int, int, int]]
            A list of tuples, each representing a move in the format (start_row, start_col, end_row, end_col).
        """
        if self.moves is not None: return self.moves
        moves: list[tuple[int, int, int, int]] = self.get_moves_no_check()
        moves_len: int = len(moves)
        for i, move_0 in enumerate(reversed(moves)):
            state: GameState = self.move(move_0)
            for move_1 in state.get_moves_no_check():
                if (winner := (state_2 := state.move(move_1)).get_winner()) == -1 or winner == 1:
                    moves.pop(moves_len - i - 1)
                    break
                elif move_0[0] == -1:
                    king_mask: int = 1 << (64 - (move_0[2] * 8 + move_0[3]))
                    opponent_pieces: int = state_2.black_pieces if self.color == 1 else state_2.white_pieces
                    if move_0[1] == 1:
                        for shift in range(0, 2):
                            if opponent_pieces & (king_mask >> shift) != 0:  # state_2.board[idx] * self.color < 0:
                                break
                        else:
                            continue
                    else:
                        for shift in range(0, 2):
                            if opponent_pieces & (king_mask << shift) != 0:  # state_2.board[idx] * self.color < 0:
                                break
                    moves.pop(moves_len - i - 1)
                    break
        if len(moves) == 0 and moves_len > 0:
            game_state: GameState = GameState(self.white_pieces, self.black_pieces, self.kings, self.queens, self.rooks,
                                              self.bishops, self.knights, self.pawns,
                                              self.white_queen, self.white_king, self.black_queen,
                                             self.black_king, color=-self.color, winner=self.winner)
            for move in game_state.get_moves_no_check():
                if (winner := game_state.move(move).get_winner()) == -1 or winner == 1:
                    break
            else:
                self.winner = 0
                return moves
            self.winner = winner
        elif self.moves_since_pawn >= 50:
            self.winner = 0
        self.moves = moves
        return moves

    def get_moves_no_check(self) -> list[tuple[int, int, int, int]]:
        hash_state: tuple[int, int, int, int, int, int, int, int, int, bool, bool, bool, bool,
        tuple[int, int, int, int]] = self.get_hashable_state()
        return self.get_moves_no_check_static(*hash_state)

    @staticmethod
    def get_moves_no_check_static(
            white_pieces: int,
            black_pieces: int,
            kings: int,
            queens: int,
            rooks: int,
            bishops: int,
            knights: int,
            pawns: int,
            color: int,
            white_queen: bool,
            white_king: bool,
            black_queen: bool,
            black_king: bool,
            last_move: tuple[int, int, int, int] | None
    ) -> list[tuple[int, int, int, int]]:
        moves: list[tuple[int, int, int, int]] = []
        # Local binds for speed
        color_local: int = color
        last_move_local: tuple[int, int, int, int] | None = last_move
        coords_local: list[tuple[int, int]] = index_to_coord
        knight_targets_local: tuple[tuple[tuple[int, int, int], ...], ...] = knight_targets
        king_targets_local: tuple[tuple[tuple[int, int, int], ...], ...] = king_targets
        rook_rays_local: tuple[tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...],
        tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...]], ...] = rook_rays
        bishop_diagonals_local: tuple[tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...],
        tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...]], ...] = bishop_diagonals
        color_mask: int = white_pieces if color == 1 else black_pieces
        opponent_mask: int = black_pieces if color == 1 else white_pieces
        pieces: int = white_pieces | black_pieces
        for h in range(64):
            i, j = coords_local[h]
            piece_mask = 1 << 64 - h
            if color_mask & piece_mask == 0:
                continue
            if kings & color_mask & piece_mask != 0:  # King
                if (((color_local == 1 and white_king) or (color_local == -1 and black_king)) and rooks & color_mask &
                        (piece_mask >> 3) != 0 == pieces & ((piece_mask >> 1) | (piece_mask >> 2))):
                    moves.append((-1, 1, i, j))
                if (((color_local == 1 and white_queen) or (color_local == -1 and black_queen)) and rooks & color_mask &
                        (piece_mask << 4) != 0 == pieces & ((piece_mask << 1) | (piece_mask << 2))):
                    moves.append((-1, -1, i, j))
                for (target_mask, target_i, target_j) in king_targets_local[h]:
                    if target_mask & color_mask == 0:
                        moves.append((i, j, target_i, target_j))
            elif (rooks | queens) & color_mask & piece_mask != 0:  # Rook and Queen
                for ray in rook_rays_local[h]:
                    for (target_mask, ray_i, ray_j) in ray:
                        if target_mask & color_mask == 0:
                            moves.append((i, j, ray_i, ray_j))
                        if target_mask & opponent_mask == 0:
                            continue
                        break
            if (bishops | queens) & color_mask & piece_mask != 0:  # Bishop and Queen
                for diagonal in bishop_diagonals_local[h]:
                    for (target_mask, diagonal_i, diagonal_j) in diagonal:
                        if target_mask & pieces == 0:
                            moves.append((i, j, diagonal_i, diagonal_j))
                            continue
                        if target_mask & opponent_mask == 0:
                            moves.append((i, j, diagonal_i, diagonal_j))
                        break
            elif knights & color_mask & piece_mask != 0:  # Knight
                for (target_mask, target_i, target_j) in knight_targets_local[h]:
                    if target_mask & color_mask == 0:
                        moves.append((i, j, target_i, target_j))
            elif pawns & color_mask & piece_mask != 0:  # Pawn
                dest_square_mask: int = 1 << 64 - ((i - color_local) * 8 + j)
                if pieces & dest_square_mask == 0:
                    if 7 != i - color_local != 0:
                        moves.append((i, j, i - color_local, j))
                    else:
                        for move_id, promotion_piece in promotion_forward:
                            moves.append((move_id, promotion_piece * color_local, i, j))
                if 8 > (j + 1) and 0 != opponent_mask & (dest_square_mask >> 1):
                    if 7 != i - color_local != 0:
                        moves.append((i, j, i - color_local, j + 1))
                    else:  # Promotion
                        for promotion_piece, direction in promotion_taking:
                            moves.append((promotion_piece, direction, i, j))
                if (j - 1) >= 0 != opponent_mask & (dest_square_mask << 1):
                    if 7 != i - color_local != 0:
                        moves.append((i, j, i - color_local, j - 1))
                    else:  # Promotion
                        for promotion_piece, direction in promotion_taking:
                            moves.append((promotion_piece, -direction, i, j))
                if color_local == 1:
                    if i == 6 and pieces & (1 << 32 - j) == 0 == (1 << 24 - j):
                        moves.append((i, j, 4, j))
                elif i == 1 and pieces & (1 << 40 - j) == 0 == (1 << 48 - j):
                    moves.append((i, j, 3, j))
                # En Passant
                if (last_move_local is not None and (
                        1 << 64 - last_move_local[2] * 8 - last_move_local[3]) & opponent_mask
                        & pawns != 0 and abs(last_move_local[2] - last_move_local[0]) == 2 and i == last_move_local[2]):
                    if 7 != j == last_move_local[3] + 1:
                        moves.append((-2, -1, i, j))
                    elif 0 != j == last_move_local[3] - 1:
                        moves.append((-2, 1, i, j))
        return moves

    def are_captures(self) -> bool:
        moves: list[tuple[int, int, int, int]] = self.get_moves()
        empty_count: int = self.count_zero_bits(self.white_pieces | self.black_pieces)
        for move in moves:
            if self.count_zero_bits(
                    (new_state := self.move(move)).white_pieces | new_state.black_pieces) != empty_count:
                return True
        return False

    @staticmethod
    def count_zero_bits(x: int) -> int:
        # mask off to 64 bits
        masked = x & ((1 << 64) - 1)
        # number of ones in those 64 bits
        ones = masked.bit_count()
        # zeros = 64 total bits minus the ones
        return 64 - ones

    def move(self, move: tuple[int, int, int, int]) -> 'GameState':
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
        GameState
            A new GameState object, with the move applied.
        """
        new_white_pieces: int = self.white_pieces
        new_black_pieces: int = self.black_pieces
        new_kings: int = self.kings
        new_queens: int = self.queens
        new_rooks: int = self.rooks
        new_bishops: int = self.bishops
        new_knights: int = self.knights
        new_pawns: int = self.pawns
        white_queen: bool = self.white_queen
        white_king: bool = self.white_king
        black_queen: bool = self.black_queen
        black_king: bool = self.black_king
        new_moves_since_pawn: int = self.moves_since_pawn + 1
        color_local: int = self.color
        move_0, move_1, move_2, move_3 = move

        if len(move) == 0:
            return GameState(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks, new_bishops,
                             new_knights, new_pawns, color=-color_local, turn=self.turn + 1, winner=0)

        second_idx_mask = (1 << 64 - (move_2 * 8 + move_3))
        if move_0 == -1:  # Castle
            if color_local == 1:
                white_queen = False
                white_king = False
                if move_1 == -1:
                    new_white_pieces = (new_white_pieces & ~0b1000_1000) | 0b0011_0000
                    new_rooks = (new_rooks & ~0b1000_0000) | 0b0001_0000
                else:
                    new_white_pieces = (new_white_pieces & ~0b0000_1001) | 0b0000_0110
                    new_rooks = (new_rooks & ~0b0000_0001) | 0b0000_0100
                new_kings = (new_kings & ~0b0000_1000) | 0b0010_0000
            else:
                black_queen = False
                black_king = False
                if move_1 == -1:
                    new_black_pieces = ((new_black_pieces &
                                         ~0b1000_1000_00000000_00000000_00000000_00000000_00000000_00000000) |
                                        0b0011_0000_00000000_00000000_00000000_00000000_00000000_00000000)
                    new_rooks = ((new_rooks & ~0b1000_0000_00000000_00000000_00000000_00000000_00000000_00000000) |
                                 0b0001_0000_00000000_00000000_00000000_00000000_00000000_00000000)
                else:
                    new_black_pieces = ((new_black_pieces &
                                         ~0b0000_1001_00000000_00000000_00000000_00000000_00000000_00000000) |
                                        0b0000_0110_00000000_00000000_00000000_00000000_00000000_00000000)
                    new_rooks = ((new_rooks & ~0b0000_0001_00000000_00000000_00000000_00000000_00000000_00000000) |
                                 0b0000_0100_00000000_00000000_00000000_00000000_00000000_00000000)
                new_kings = ((new_kings & ~0b0000_1000_00000000_00000000_00000000_00000000_00000000_00000000) |
                             0b0010_0000_00000000_00000000_00000000_00000000_00000000_00000000)
            return GameState(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks, new_bishops,
                             new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                             color=-color_local, turn=self.turn + 1, winner=self.winner)

        if move_0 == -2:  # En Passant
            if color_local == 1:
                new_white_pieces = (new_white_pieces & ~second_idx_mask) | (
                        1 << 64 - ((move_2 - color_local) * 8 + move_3 + move_1))
                new_black_pieces &= ~(1 << 64 - (move_2 * 8 + move_3 + move_1))
            else:
                new_black_pieces = (new_black_pieces & ~second_idx_mask) | (
                        1 << 64 - ((move_2 - color_local) * 8 + move_3 + move_1))
                new_white_pieces &= ~(1 << 64 - (move_2 * 8 + move_3 + move_1))
            new_pawns = (new_pawns & ~second_idx_mask & ~(
                    1 << 64 - (move_2 * 8 + move_3 + move_1))) | (
                                1 << 64 - ((move_2 - color_local) * 8 + move_3 + move_1))
            return GameState(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks, new_bishops,
                             new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                             color=-color_local, turn=self.turn + 1, winner=self.winner)

        if move_0 == -3:  # Promotion
            if color_local == 1:
                new_white_pieces = ((new_white_pieces & ~second_idx_mask) |
                                    (1 << 64 - ((move_2 - color_local) * 8 + move_3)))
            else:
                new_black_pieces = ((new_black_pieces & ~second_idx_mask) |
                                    (1 << 64 - ((move_2 - color_local) * 8 + move_3)))
            new_pawns &= ~second_idx_mask
            if abs(move_1) == 2:
                new_knights |= 1 << 64 - ((move_2 - color_local) * 8 + move_3)
            elif abs(move_1) == 3:
                new_bishops |= 1 << 64 - ((move_2 - color_local) * 8 + move_3)
            elif abs(move_1) == 4:
                new_rooks |= 1 << 64 - ((move_2 - color_local) * 8 + move_3)
            elif abs(move_1) == 5:
                new_queens |= 1 << 64 - ((move_2 - color_local) * 8 + move_3)

            return GameState(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks, new_bishops,
                             new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                             color=-color_local, turn=self.turn + 1, winner=self.winner)
            # new_board[move_2 * 8 + move_3] = 0
            # new_board[(move_2 - self.color) * 8 + move_3] = move_1
            # return GameState(tuple(new_board), white_queen, white_king, black_queen, black_king, color=-self.color,
            #                  turn=self.turn + 1, moves_since_pawn=0)

        if move_0 <= -4:  # Promotion while taking
            new_piece_mask: int = 1 << 64 - ((move_2 - color_local) * 8 + (move_3 + move_1))
            remove_piece_mask: int = ~second_idx_mask
            if color_local == 1:
                new_white_pieces = (new_white_pieces & remove_piece_mask) | new_piece_mask
                new_black_pieces &= ~new_piece_mask
            else:
                new_black_pieces = (new_black_pieces & remove_piece_mask) | new_piece_mask
                new_white_pieces &= ~new_piece_mask
            new_pawns &= remove_piece_mask
            promotion_piece_type: int = abs(move_1)
            if promotion_piece_type == 2:
                new_knights |= new_piece_mask
            elif promotion_piece_type == 3:
                new_bishops |= new_piece_mask
            elif promotion_piece_type == 4:
                new_rooks |= new_piece_mask
            elif promotion_piece_type == 5:
                new_queens |= new_piece_mask

            return GameState(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks, new_bishops,
                             new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                             color=-color_local, turn=self.turn + 1, winner=self.winner)

        first_idx_mask: int = (1 << 64 - (move_0 * 8 + move_1))
        condition2: bool = ((new_kings | new_rooks) & first_idx_mask) != 0
        if (new_rooks | first_idx_mask) or condition2:
            if move_2 == 7 and not move_3:
                white_queen = False
            if move_2 == 7 and move_3 == 7:
                white_king = False
            if not (move_2 or move_3): # Both are 0
                black_queen = False
            if not move_2 and move_3 == 7:
                black_king = False
        if condition2:
            if not move_2 and move_3 == 4:
                black_queen = False
                black_king = False
            if move_2 == 7 and move_3 == 4:
                white_queen = False
                white_king = False

        if self.pawns & first_idx_mask:
            new_moves_since_pawn = 0

        new_winner = self.winner
        if color_local == 1:
            new_white_pieces = (new_white_pieces & ~first_idx_mask) | second_idx_mask
            new_black_pieces &= ~second_idx_mask
            if new_black_pieces != self.black_pieces:
                if new_pawns & second_idx_mask:
                    new_pawns &= ~second_idx_mask
                elif new_rooks & second_idx_mask:
                    new_rooks &= ~second_idx_mask
                elif new_queens & second_idx_mask:
                    new_queens &= ~second_idx_mask
                elif new_bishops & second_idx_mask:
                    new_bishops &= ~second_idx_mask
                elif new_knights & second_idx_mask:
                    new_knights &= ~second_idx_mask
                else:
                    new_winner = 1
                    new_kings &= ~second_idx_mask
        else:
            new_black_pieces = (new_black_pieces & ~first_idx_mask) | second_idx_mask
            new_white_pieces &= ~second_idx_mask
            if new_white_pieces != self.white_pieces:
                if new_pawns & second_idx_mask:
                    new_pawns &= ~second_idx_mask
                elif new_rooks & second_idx_mask:
                    new_rooks &= ~second_idx_mask
                elif new_queens & second_idx_mask:
                    new_queens &= ~second_idx_mask
                elif new_bishops & second_idx_mask:
                    new_bishops &= ~second_idx_mask
                elif new_knights & second_idx_mask:
                    new_knights &= ~second_idx_mask
                else:
                    new_winner = -1
                    new_kings &= ~second_idx_mask

        if new_pawns & first_idx_mask:
            new_pawns &= ~first_idx_mask
            new_pawns |= second_idx_mask
        elif new_rooks & first_idx_mask:
            new_rooks &= ~first_idx_mask
            new_rooks |= second_idx_mask
        elif new_queens & first_idx_mask:
            new_queens &= ~first_idx_mask
            new_queens |= second_idx_mask
        elif new_bishops & first_idx_mask:
            new_bishops &= ~first_idx_mask
            new_bishops |= second_idx_mask
        elif new_knights & first_idx_mask:
            new_knights &= ~first_idx_mask
            new_knights |= second_idx_mask
        else:
            new_kings &= ~first_idx_mask
            new_kings |= second_idx_mask


        new_previous_position_count = copy.copy(self.previous_position_count)
        if (hash_state := hash((new_white_pieces, new_kings, new_queens, new_rooks, new_bishops,
                                new_knights, new_pawns))) in new_previous_position_count:
            new_previous_position_count[hash_state] += 1
            if new_previous_position_count[hash_state] >= 3:
                return GameState(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks, new_bishops,
                                 new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                                 color=-self.color, turn=self.turn + 1, winner=new_winner)
        else:
            new_previous_position_count[hash_state] = 1
        last_move: tuple[int, int, int, int] | None = move if (
                self.pawns & first_idx_mask and (move_0 == move_2 - self.color * 2)) else None
        return GameState(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks, new_bishops,
                                 new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                         last_move=last_move, color=-self.color, turn=self.turn + 1, winner=new_winner,
                         moves_since_pawn=new_moves_since_pawn, previous_position_count=new_previous_position_count)

    def get_winner(self) -> int | None:
        if self.winner is not None:
            return self.winner
        if self.moves_since_pawn >= 50:
            self.winner = 0
            return 0
        white: bool = self.kings & self.white_pieces != 0
        black: bool = self.kings & self.black_pieces != 0
        empty: bool = (self.white_pieces | self.black_pieces) & ~self.kings != 0
        if white and not black:
            self.winner = 1
        elif black and not white:
            self.winner = -1
        elif empty:
            self.winner = 0
        return self.winner

    def __repr__(self) -> str:
        return f"""GameState(white_pieces={self.white_pieces},
          white_pieces={self.white_pieces},
          black_pieces={self.black_pieces},
          kings={self.kings},
          queens={self.queens},
          rooks={self.rooks},
          bishops={self.bishops},
          knights={self.knights},
          pawns={self.pawns},
          white_queen={self.white_queen},
          white_king={self.white_king},
          black_queen={self.black_queen},
          black_king={self.black_king},
          last_move={self.last_move},
          color={self.color},
          turn={self.turn},
          winner={self.winner},
          previous_position_count={self.previous_position_count},
          moves={self.moves},
          hash_state={self.hash_state},
          moves_since_pawn={self.moves_since_pawn})"""

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
        for row in range(8):
            result += "| "
            for column in range(8):
                piece_idx_mask = 1 << (64 - (row * 8 + column))
                if piece_idx_mask & self.white_pieces:
                    if piece_idx_mask & self.kings:
                        result += "K"
                    elif piece_idx_mask & self.queens:
                        result += "Q"
                    elif piece_idx_mask & self.rooks:
                        result += "R"
                    elif piece_idx_mask & self.bishops:
                        result += "B"
                    elif piece_idx_mask & self.knights:
                        result += "N"
                    elif piece_idx_mask & self.pawns:
                        result += "P"
                elif piece_idx_mask & self.black_pieces:
                    if piece_idx_mask & self.kings:
                        result += "k"
                    elif piece_idx_mask & self.queens:
                        result += "q"
                    elif piece_idx_mask & self.rooks:
                        result += "r"
                    elif piece_idx_mask & self.bishops:
                        result += "b"
                    elif piece_idx_mask & self.knights:
                        result += "n"
                    elif piece_idx_mask & self.pawns:
                        result += "p"
                else:
                    result += " "
                result += " | "
            result += "\n|___|___|___|___|___|___|___|___|\n"

        return result
