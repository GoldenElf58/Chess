import copy
from game_states.game_base import GameStateBase

# Precompute index-to-coordinate mapping for faster lookups
index_to_coord: list[tuple[int, int]] = [(h // 8, h % 8) for h in range(64)]

knight_targets: tuple[tuple[int, ...], ...]
king_targets: tuple[tuple[int, ...], ...]
rook_rays: tuple[tuple[tuple[int, ...], tuple[int, ...],
tuple[int, ...], tuple[int, ...]], ...]
bishop_diagonals: tuple[tuple[tuple[int, ...], tuple[int, ...],
tuple[int, ...], tuple[int, ...]], ...]
promotion_forward: tuple[tuple[int, int], ...] = ((-3, 5), (-3, 4), (-3, 3), (-3, 2))
promotion_taking: tuple[tuple[int, int], ...] = ((-7, 1), (-6, 1), (-5, 1), (-4, 1))

# Precomputed bit mask for each square
bit_masks: list[int] = [1 << (63 - h) for h in range(64)]


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
    a8 = 1 << 63
    for h in range(64):
        i, j = index_to_coord[h]

        curr: list = []
        for k in range(-2, 3, 4):
            for l in range(-1, 2, 2):
                if 8 > i + k >= 0 <= j + l < 8:
                    curr.append((a8 >> ((i + k) * 8 + j + l)))
                if 8 > i + l >= 0 <= j + k < 8:
                    curr.append((a8 >> ((i + l) * 8 + j + k)))
        temp_knight.append(tuple(curr))

        curr = []
        for k in range(-1, 2):
            for l in range(-1, 2):
                if 0 <= i + k < 8 and 0 <= j + l < 8:
                    curr.append((a8 >> ((i + k) * 8 + j + l)))
        temp_king.append(tuple(curr))

        curr = []
        curr2: list = []
        for k in range(j + 1, 8):
            curr2.append(a8 >> (h - j + k))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(j - 1, -1, -1):
            curr2.append(a8 >> (h - j + k))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(i + 1, 8):
            curr2.append(a8 >> (k * 8 + j))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(i - 1, -1, -1):
            curr2.append(a8 >> (k * 8 + j))
        curr.append(tuple(curr2))
        temp_rook.append(tuple(curr))

        curr = []
        curr2 = []
        for k in range(1, 8):
            if i + k > 7 or j + k > 7: break
            curr2.append(a8 >> ((i + k) * 8 + (j + k)))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(1, 8):
            if i - k < 0 or j + k > 7: break
            curr2.append(a8 >> ((i - k) * 8 + (j + k)))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(1, 8):
            if i + k > 7 or j - k < 0: break
            curr2.append(a8 >> ((i + k) * 8 + (j - k)))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(1, 8):
            if i - k < 0 or j - k < 0: break
            curr2.append(a8 >> ((i - k) * 8 + (j - k)))
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


class GameStateBitboardsV2(GameStateBase):
    __slots__ = ('white_pieces', 'black_pieces', 'kings', 'queens', 'rooks', 'bishops', 'knights', 'pawns',
                 'color', 'white_queen', 'white_king', 'black_queen', 'black_king', 'last_move', 'turn',
                 'winner', 'previous_position_count', 'moves_since_pawn', 'moves', 'hash_state')

    def __init__(self, white_pieces: int | None = None, black_pieces: int | None = None, kings: int | None = None,
                 queens: int | None = None, rooks: int | None = None, bishops: int | None = None,
                 knights: int | None = None, pawns: int | None = None, white_queen: bool = True,
                 white_king: bool = True, black_queen: bool = True, black_king: bool = True,
                 last_move: tuple[int, int, int] | None = None, color=1, turn=0, winner: int | None = None,
                 previous_position_count: dict[int, int] | None = None, moves_since_pawn: int = 0) -> None:
        """
        Initialize a GameStateBitboardsV2 object.

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
        black_king : bool, optional
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
        self.last_move: tuple[int, int, int] | None = last_move
        self.moves: list[tuple[int, int, int]] | None = None
        super().__init__(white_queen, white_king, black_queen, black_king, color, turn, winner,
                         previous_position_count, moves_since_pawn)

    def get_hashable_state(self) -> tuple[int, int, int, int, int, int, int, int, int, bool, bool, bool, bool,
    tuple[int, int, int] | None]:
        """ Convert the game state into a hashable format for caching. """
        return (self.white_pieces, self.black_pieces, self.kings, self.queens, self.rooks, self.bishops, self.knights,
                self.pawns, self.color, self.white_queen, self.white_king, self.black_queen, self.black_king,
                self.last_move)

    def get_hashed(self) -> int:
        return hash((self.white_pieces, self.black_pieces, self.kings, self.queens, self.rooks, self.bishops,
                     self.knights, self.pawns, (((self.color == 1) << 4) | (self.white_queen << 3) | (
                    self.white_king << 2) | (self.black_queen << 1) | self.black_king),
                     self.last_move))

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
        moves_len: int = len(moves)
        for i, move_0 in enumerate(reversed(moves)):
            state: GameStateBitboardsV2 = self.move(move_0)
            for move_1 in state.get_moves_no_check():
                if (winner := (state_2 := state.move(move_1)).get_winner()) == -1 or winner == 1:
                    moves.pop(moves_len - i - 1)
                    break
                elif move_0[0] == -1:
                    opponent_pieces: int = state_2.black_pieces if self.color == 1 else state_2.white_pieces
                    if move_0[1] == 1:
                        for shift in range(0, 2):
                            if opponent_pieces & (move_0[2] >> shift):
                                break
                        else:
                            continue
                    else:
                        for shift in range(0, 2):
                            if opponent_pieces & (move_0[2] << shift):
                                break
                        else:
                            continue
                    moves.pop(moves_len - i - 1)
                    break
        if len(moves) == 0 and moves_len > 0:
            game_state: GameStateBitboardsV2 = GameStateBitboardsV2(self.white_pieces, self.black_pieces, self.kings,
                                                                    self.queens, self.rooks,
                                                                    self.bishops, self.knights, self.pawns,
                                                                    self.white_queen, self.white_king, self.black_queen,
                                                                    self.black_king, color=-self.color,
                                                                    winner=self.winner)
            for move in game_state.get_moves_no_check():
                if (winner := game_state.move(move).get_winner()) == -1 or winner == 1:
                    break
            else:
                self.winner = 0
                self.moves = moves
                return moves
            self.winner = winner
        elif self.moves_since_pawn >= 100:
            self.winner = 0
        self.moves = moves
        return moves

    def get_moves_no_check(self) -> list[tuple[int, int, int]]:
        moves: list[tuple[int, int, int]] = []
        # Local binds for speed
        color_local: int = self.color
        last_move_local: tuple[int, int, int] | None = self.last_move
        coords_local: list[tuple[int, int]] = index_to_coord
        knight_targets_local: tuple[tuple[int, ...], ...] = knight_targets
        king_targets_local: tuple[tuple[int, ...], ...] = king_targets
        rook_rays_local: tuple[tuple[tuple[int, ...], tuple[int, ...],
        tuple[int, ...], tuple[int, ...]], ...] = rook_rays
        bishop_diagonals_local: tuple[tuple[tuple[int, ...], tuple[int, ...],
        tuple[int, ...], tuple[int, ...]], ...] = bishop_diagonals
        masks_local: list[int] = bit_masks
        color_mask: int = self.white_pieces if self.color == 1 else self.black_pieces
        opponent_mask: int = self.black_pieces if self.color == 1 else self.white_pieces
        kings: int = self.kings
        colored_rooks: int = self.rooks & color_mask
        rooks: int = self.rooks
        bishops: int = self.bishops
        queens: int = self.queens
        knights: int = self.knights
        pawns: int = self.pawns
        pieces: int = (color_mask | opponent_mask)
        mask: int = 1 << 64
        for h in range(64):
            mask >>= 1
            if not color_mask & mask:
                continue
            i, j = coords_local[h]
            if mask & pawns:
                dest_square_mask = masks_local[h - 8 * color_local]
                # Forward
                if not pieces & dest_square_mask:
                    if 7 != i - color_local != 0:
                        moves.append((mask, dest_square_mask, 0))
                    else:  # Promotion
                        for move_id, promotion_piece in promotion_forward:
                            moves.append((move_id, promotion_piece * color_local, mask))
                # Right capture
                if 8 > (j + 1) and opponent_mask & (dest_square_mask >> 1):
                    if 7 != i - color_local != 0:
                        moves.append((mask, (dest_square_mask >> 1), 0))
                    else:  # Promotion
                        for promotion_piece, direction in promotion_taking:
                            moves.append((promotion_piece, direction, mask))
                # Left capture
                if (j - 1) >= 0 and opponent_mask & (dest_square_mask << 1):
                    if 7 != i - color_local != 0:
                        moves.append((mask, (dest_square_mask << 1), 0))
                    else:  # Promotion
                        for promotion_piece, direction in promotion_taking:
                            moves.append((promotion_piece, -direction, mask))
                # Double push
                if color_local == 1:
                    if i == 6 and not (pieces & (dest_square_mask | (dest_square_mask << 8))):
                        moves.append((mask, (dest_square_mask << 8), j))
                elif i == 1 and not (pieces & (dest_square_mask | (dest_square_mask >> 8))):
                    moves.append((mask, (dest_square_mask >> 8), j))
                # En Passant
                if last_move_local is not None and (i == 3 or i == 4):
                    if 7 != j == last_move_local[2] + 1:
                        moves.append((-2, -1, mask))
                    elif 0 != j == last_move_local[2] - 1:
                        moves.append((-2, 1, mask))
            elif kings & mask:
                if (((color_local == 1 and self.white_king) or (
                        color_local == -1 and self.black_king)) and colored_rooks &
                        (mask >> 3) and not (pieces & ((mask >> 1) | (mask >> 2)))):
                    moves.append((-1, 1, mask))
                if (((color_local == 1 and self.white_queen) or (
                        color_local == -1 and self.black_queen)) and colored_rooks &
                        (mask << 4) and not (pieces & ((mask << 1) | (mask << 2) | (mask << 3)))):
                    moves.append((-1, -1, mask))
                for target_mask in king_targets_local[h]:
                    if not target_mask & color_mask:
                        moves.append((mask, target_mask, 0))
            elif mask & (rooks | queens):
                for ray in rook_rays_local[h]:
                    for target_mask in ray:
                        if not target_mask & pieces:
                            moves.append((mask, target_mask, 0))
                            continue
                        if target_mask & opponent_mask:
                            moves.append((mask, target_mask, 0))
                        break
            if mask & (bishops | queens):
                for diagonal in bishop_diagonals_local[h]:
                    for target_mask in diagonal:
                        if not target_mask & pieces:
                            moves.append((mask, target_mask, 0))
                            continue
                        if target_mask & opponent_mask:
                            moves.append((mask, target_mask, 0))
                        break
            elif mask & knights:
                for target_mask in knight_targets_local[h]:
                    if not target_mask & color_mask:
                        moves.append((mask, target_mask, 0))
        return moves

    def are_captures(self) -> bool:
        moves: list[tuple[int, int, int]] = self.get_moves()
        empty_count: int = self.count_zero_bits(self.white_pieces | self.black_pieces)
        for move in moves:
            if self.count_zero_bits(
                    (new_state := self.move(move)).white_pieces | new_state.black_pieces) != empty_count:
                return True
        return False

    @staticmethod
    def count_zero_bits(x: int) -> int:
        return 64 - (x & ((1 << 64) - 1)).bit_count()

    def move(self, move: tuple[int, int, int]) -> 'GameStateBitboardsV2':
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
        GameStateBitboardsV2
            A new GameStateBitboardsV2 object, with the move applied.
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
        move_0, move_1, move_2 = move  # type: int, int, int

        if len(move) == 0:
            return GameStateBitboardsV2(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks,
                                        new_bishops,
                                        new_knights, new_pawns, color=-color_local, turn=self.turn + 1, winner=0)

        a8: int = 1 << 63
        if move_0 == -1:  # Castle
            if color_local == 1:
                white_queen = False
                white_king = False
                if move_1 == -1:
                    new_white_pieces = (new_white_pieces & ~0b1000_1000) | 0b0011_0000
                    new_rooks = (new_rooks & ~0b1000_0000) | 0b0001_0000
                    new_kings = (new_kings & ~0b0000_1000) | 0b0010_0000
                else:
                    new_white_pieces = (new_white_pieces & ~0b0000_1001) | 0b0000_0110
                    new_rooks = (new_rooks & ~0b0000_0001) | 0b0000_0100
                    new_kings = (new_kings & ~0b0000_1000) | 0b0000_0010
            else:
                black_queen = False
                black_king = False
                if move_1 == -1:
                    new_black_pieces = ((new_black_pieces &
                                         ~0b1000_1000_00000000_00000000_00000000_00000000_00000000_00000000_00000000) |
                                        0b0011_0000_00000000_00000000_00000000_00000000_00000000_00000000_00000000)
                    new_rooks = ((
                                             new_rooks & ~0b1000_0000_00000000_00000000_00000000_00000000_00000000_00000000_00000000) |
                                 0b0001_0000_00000000_00000000_00000000_00000000_00000000_00000000_00000000)
                    new_kings = ((
                                             new_kings & ~0b0000_1000_00000000_00000000_00000000_00000000_00000000_00000000_00000000) |
                                 0b0010_0000_00000000_00000000_00000000_00000000_00000000_00000000_00000000)
                else:
                    new_black_pieces = ((new_black_pieces &
                                         ~0b0000_1001_00000000_00000000_00000000_00000000_00000000_00000000_00000000) |
                                        0b0000_0110_00000000_00000000_00000000_00000000_00000000_00000000_00000000)
                    new_rooks = ((
                                             new_rooks & ~0b0000_0001_00000000_00000000_00000000_00000000_00000000_00000000_00000000) |
                                 0b0000_0100_00000000_00000000_00000000_00000000_00000000_00000000_00000000)
                new_kings = ((new_kings & ~0b0000_1000_00000000_00000000_00000000_00000000_00000000_00000000_00000000) |
                             0b0000_0010_00000000_00000000_00000000_00000000_00000000_00000000_00000000)
            return GameStateBitboardsV2(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks,
                                        new_bishops,
                                        new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                                        color=-color_local, turn=self.turn + 1, winner=self.winner)

        if move_0 == -2:  # En Passant
            if color_local == 1:
                dest_square = (move_2 << 8 - move_1)
                new_white_pieces = (new_white_pieces & ~move_2) | dest_square
                new_black_pieces &= ~(dest_square >> 8)
                new_pawns = (new_pawns & ~move_2 & ~(dest_square >> 8)) | dest_square
            else:
                dest_square = (move_2 >> 8 + move_1)
                new_black_pieces = (new_black_pieces & ~move_2) | dest_square
                new_white_pieces &= ~(dest_square << 8)
                new_pawns = (new_pawns & ~move_2 & ~(dest_square << 8)) | dest_square
            return GameStateBitboardsV2(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks,
                                        new_bishops,
                                        new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                                        color=-color_local, turn=self.turn + 1, winner=self.winner)

        if move_0 == -3:  # Promotion
            new_piece_mask = move_2 << 8 if color_local == 1 else move_2 >> 8
            if color_local == 1:
                new_white_pieces = (new_white_pieces & ~move_2) | new_piece_mask
            else:
                new_black_pieces = (new_black_pieces & ~move_2) | new_piece_mask
            new_pawns &= ~move_2
            promotion_piece_type: int = abs(move_1)
            if promotion_piece_type == 2:
                new_knights |= new_piece_mask
            elif promotion_piece_type == 3:
                new_bishops |= new_piece_mask
            elif promotion_piece_type == 4:
                new_rooks |= new_piece_mask
            elif promotion_piece_type == 5:
                new_queens |= new_piece_mask

            return GameStateBitboardsV2(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks,
                                        new_bishops,
                                        new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                                        color=-color_local, turn=self.turn + 1, winner=self.winner)

        if move_0 <= -4:  # Promotion while taking
            new_piece_mask = (move_2 << 8 - move_1) if color_local == 1 else (move_2 >> 8 + move_1)
            if color_local == 1:
                new_white_pieces = (new_white_pieces & ~move_2) | new_piece_mask
                new_black_pieces &= ~new_piece_mask
            else:
                new_black_pieces = (new_black_pieces & ~move_2) | new_piece_mask
                new_white_pieces &= ~new_piece_mask
            new_pawns &= ~move_2
            if move_0 == -7:
                new_queens |= new_piece_mask
            elif move_0 == -4:
                new_knights |= new_piece_mask
            elif move_0 == -5:
                new_bishops |= new_piece_mask
            elif move_0 == -6:
                new_rooks |= new_piece_mask

            return GameStateBitboardsV2(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks,
                                        new_bishops,
                                        new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                                        color=-color_local, turn=self.turn + 1, winner=self.winner)

        # ========================================================================
        # This is wierd below. Double check when revisiting
        # ========================================================================
        condition2: int = (new_kings | new_rooks) & move_0
        if (new_rooks | move_0) or condition2:
            # if move_2 == 7 and not move_3:
            if move_1 == 0b1000_0000:
                white_queen = False
            if move_1 == 1:
                white_king = False
            if move_1 == 0b10000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000:
                black_queen = False
            if move_1 == 0b00000001_00000000_00000000_00000000_00000000_00000000_00000000_00000000:
                black_king = False
        if condition2:
            if move_1 == 0b0000_1000_00000000_00000000_00000000_00000000_00000000_00000000_00000000:
                black_queen = False
                black_king = False
            if move_1 == 0b0000_1000:
                white_queen = False
                white_king = False

        if self.pawns & move_0:
            new_moves_since_pawn = 0

        new_winner: int | None = self.winner
        if color_local == 1:
            new_white_pieces = (new_white_pieces & ~move_0) | move_1
            new_black_pieces &= ~move_1
            if new_black_pieces != self.black_pieces:
                if new_pawns & move_1:
                    new_pawns &= ~move_1
                elif new_rooks & move_1:
                    new_rooks &= ~move_1
                elif new_queens & move_1:
                    new_queens &= ~move_1
                elif new_bishops & move_1:
                    new_bishops &= ~move_1
                elif new_knights & move_1:
                    new_knights &= ~move_1
                else:
                    new_winner = 1
                    new_kings &= ~move_1
        else:
            new_black_pieces = (new_black_pieces & ~move_0) | move_1
            new_white_pieces &= ~move_1
            if new_white_pieces != self.white_pieces:
                if new_pawns & move_1:
                    new_pawns &= ~move_1
                elif new_rooks & move_1:
                    new_rooks &= ~move_1
                elif new_queens & move_1:
                    new_queens &= ~move_1
                elif new_bishops & move_1:
                    new_bishops &= ~move_1
                elif new_knights & move_1:
                    new_knights &= ~move_1
                else:
                    new_winner = -1
                    new_kings &= ~move_1

        if new_pawns & move_0:
            new_pawns &= ~move_0
            new_pawns |= move_1
        elif new_rooks & move_0:
            new_rooks &= ~move_0
            new_rooks |= move_1
        elif new_queens & move_0:
            new_queens &= ~move_0
            new_queens |= move_1
        elif new_bishops & move_0:
            new_bishops &= ~move_0
            new_bishops |= move_1
        elif new_knights & move_0:
            new_knights &= ~move_0
            new_knights |= move_1
        else:
            new_kings &= ~move_0
            new_kings |= move_1

        new_previous_position_count = copy.copy(self.previous_position_count)
        if (hash_state := hash((new_white_pieces, new_kings, new_queens, new_rooks, new_bishops,
                                new_knights, new_pawns))) in new_previous_position_count:
            new_previous_position_count[hash_state] += 1
            if new_previous_position_count[hash_state] >= 3:
                return GameStateBitboardsV2(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks,
                                            new_bishops,
                                            new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                                            color=-self.color, turn=self.turn + 1, winner=new_winner)
        else:
            new_previous_position_count[hash_state] = 1
        last_move: tuple[int, int, int] | None = move if move_2 else None
        return GameStateBitboardsV2(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks, new_bishops,
                                    new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                                    last_move=last_move, color=-self.color, turn=self.turn + 1, winner=new_winner,
                                    moves_since_pawn=new_moves_since_pawn,
                                    previous_position_count=new_previous_position_count)

    def get_winner(self) -> int | None:
        if self.winner is not None:
            return self.winner
        if self.moves_since_pawn >= 100:
            self.winner = 0
            return 0
        white: int = self.kings & self.white_pieces
        black: int = self.kings & self.black_pieces
        empty: bool = not (self.white_pieces | self.black_pieces) & ~self.kings
        if white and not black:
            self.winner = 1
        elif black and not white:
            self.winner = -1
        elif empty:
            self.winner = 0
        return self.winner

    def __repr__(self) -> str:
        return f"""GameStateBitboardsV2(white_pieces={self.white_pieces},
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
                piece_idx_mask = 1 << (63 - (row * 8 + column))
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
