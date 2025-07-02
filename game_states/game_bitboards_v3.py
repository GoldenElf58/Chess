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


class GameStateBitboardsV3(GameStateBase):
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
        Initialize a GameStateBitboardsV3 object.

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

    def __hash__(self) -> int:
        return hash((self.white_pieces, self.kings, self.queens, self.rooks, self.bishops,
                     self.knights, self.pawns, self.color, self.white_queen, self.white_king, self.black_queen,
                     self.black_king, self.last_move, self.turn))

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
        king_mask: int = self.kings & (self.white_pieces if color_local == 1 else self.black_pieces)
        coords_local: list[tuple[int, int]] = index_to_coord
        for i, move in enumerate(reversed(moves)):
            white_pieces, black_pieces, kings, queens, rooks, bishops, knights, pawns = self.move_only_board(move)
            bishops |= queens
            rooks |= queens
            pieces: int = white_pieces | black_pieces
            opponent_mask: int = black_pieces if color_local == 1 else white_pieces
            illegal: bool = False
            if move[0] == -1:  # Castle
                check_mask: int = king_mask | (king_mask >> 1 | king_mask >> 2 if move[1] == 1 else
                                               king_mask << 1 | king_mask << 2)
                pieces |= king_mask
                piece_mask = 1 << 64
                for h in range(64):
                    piece_mask >>= 1
                    if not piece_mask & opponent_mask: continue
                    if piece_mask & bishops:
                        for diagonal in bishop_diagonals_local[h]:
                            for target_mask in diagonal:
                                if not target_mask & pieces:
                                    continue
                                if target_mask & check_mask:
                                    illegal = True
                                break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    if piece_mask & rooks:  # and
                        # (coords_local[check_square][0] == coords_local[h][0] or
                        #  coords_local[check_square][1] == coords_local[h][1])):
                        for ray in rook_rays_local[h]:
                            for target_mask in ray:
                                if not target_mask & pieces:
                                    continue
                                if target_mask & check_mask:
                                    illegal = True
                                break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    elif piece_mask & kings:
                        for target_mask in king_targets_local[h]:
                            if target_mask & check_mask:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break
                    elif piece_mask & knights:
                        for target_mask in knight_targets_local[h]:
                            if target_mask & check_mask:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break
                    elif piece_mask & pawns:
                        forward_mask = piece_mask << 8 if color_local == -1 else piece_mask >> 8
                        if ((forward_mask >> 1 & check_mask and coords_local[h][1] != 7) or
                                (forward_mask << 1 & check_mask and coords_local[h][1])):
                            moves.pop(pop_idx_base - i)
                            break
            else:
                check_square: int = kings & (white_pieces if color_local == 1 else black_pieces)
                check_square_idx: int = 64 - check_square.bit_length()
                piece_mask = 1 << 64
                for h in range(64):
                    piece_mask >>= 1
                    if not piece_mask & opponent_mask: continue
                    if piece_mask & bishops:
                        for diagonal in bishop_diagonals_local[h]:
                            for target_mask in diagonal:
                                if not target_mask & pieces:
                                    continue
                                if target_mask == check_square:
                                    illegal = True
                                break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    if piece_mask & pawns:
                        forward_mask = piece_mask << 8 if color_local == -1 else piece_mask >> 8
                        if ((forward_mask >> 1 == check_square and coords_local[h][1] != 7) or
                                (forward_mask << 1 == check_square and coords_local[h][1])):
                            moves.pop(pop_idx_base - i)
                            break
                    elif (piece_mask & rooks and
                        (coords_local[check_square_idx][0] == coords_local[h][0] or
                         coords_local[check_square_idx][1] == coords_local[h][1])):
                        # (bitboard_to_coord_local[check_square][0] == coords_local[h][0] or
                        #  bitboard_to_coord_local[check_square][1] == coords_local[h][1])):
                        for ray in rook_rays_local[h]:
                            for target_mask in ray:
                                if not target_mask & pieces:
                                    continue
                                if target_mask == check_square:
                                    illegal = True
                                break
                            if illegal:
                                break
                        if illegal:
                            moves.pop(pop_idx_base - i)
                            break
                    elif piece_mask & kings:
                        for target_mask in king_targets_local[h]:
                            if target_mask == check_square:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break
                    elif piece_mask & knights:
                        for target_mask in knight_targets_local[h]:
                            if target_mask == check_square:
                                break
                        else:
                            continue
                        moves.pop(pop_idx_base - i)
                        break

        if len(moves) == 0 and pop_idx_base > -1:
            game_state: GameStateBitboardsV3 = GameStateBitboardsV3(self.white_pieces, self.black_pieces, self.kings,
                                                                    self.queens, self.rooks, self.bishops, self.knights,
                                                                    self.pawns, False, False, False,
                                                                    False, color=-color_local)
            for _, dest_mask, _ in game_state.get_moves_no_check():
                if dest_mask == king_mask:
                    self.winner = -color_local
                    return moves
            self.winner = 0
            return moves
        elif self.moves_since_pawn >= 100:
            self.winner = 0
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
        orthagonal_sliders: int = self.rooks | self.queens
        diagonal_sliders: int = self.bishops | self.queens
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
                        moves.append((mask, (dest_square_mask << 8), j + 1))
                elif i == 1 and not (pieces & (dest_square_mask | (dest_square_mask >> 8))):
                    moves.append((mask, (dest_square_mask >> 8), j + 1))
                # En Passant
                if last_move_local is not None and ((i == 3 and color_local == 1) or (i == 4 and color_local == -1)):
                    if 7 != j == last_move_local[2]:
                        moves.append((-2, -1, mask))
                    elif 0 != j == last_move_local[2] - 2:
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
            elif mask & orthagonal_sliders:
                for ray in rook_rays_local[h]:
                    for target_mask in ray:
                        if not target_mask & pieces:
                            moves.append((mask, target_mask, 0))
                            continue
                        if target_mask & opponent_mask:
                            moves.append((mask, target_mask, 0))
                        break
            if mask & diagonal_sliders:
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
            white_pieces, black_pieces, *_ = self.move_only_board(move)
            if self.count_zero_bits(white_pieces | black_pieces) != empty_count:
                return True
        return False

    @staticmethod
    def count_zero_bits(x: int) -> int:
        return 64 - (x & ((1 << 64) - 1)).bit_count()

    def move(self, move: tuple[int, int, int]) -> 'GameStateBitboardsV3':
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
        GameStateBitboardsV3
            A new GameStateBitboardsV3 object, with the move applied.
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
            return GameStateBitboardsV3(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks,
                                        new_bishops,
                                        new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                                        moves_since_pawn=new_moves_since_pawn,
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
            return GameStateBitboardsV3(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks,
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

            return GameStateBitboardsV3(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks,
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

            return GameStateBitboardsV3(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks,
                                        new_bishops,
                                        new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                                        color=-color_local, turn=self.turn + 1, winner=self.winner)

        # ========================================================================
        # This is wierd below. Double check when revisiting
        # ========================================================================
        if new_rooks & move_0:
            # if move_2 == 7 and not move_3:
            if move_0 == 0b1000_0000:
                white_queen = False
            if move_0 == 1:
                white_king = False
            if move_0 == 0b10000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000:
                black_queen = False
            if move_0 == 0b00000001_00000000_00000000_00000000_00000000_00000000_00000000_00000000:
                black_king = False
        elif new_kings & move_0:
            if move_0 == 0b0000_1000_00000000_00000000_00000000_00000000_00000000_00000000_00000000:
                black_queen = False
                black_king = False
            if move_0 == 0b0000_1000:
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

        new_previous_position_count = dict(self.previous_position_count)
        if (hash_state := hash((new_white_pieces, new_kings, new_queens, new_rooks, new_bishops,
                                new_knights, new_pawns))) in new_previous_position_count:
            new_previous_position_count[hash_state] += 1
            if new_previous_position_count[hash_state] >= 3:
                return GameStateBitboardsV3(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks,
                                            new_bishops,
                                            new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                                            color=-self.color, turn=self.turn + 1, winner=0)
        else:
            new_previous_position_count[hash_state] = 1
        last_move: tuple[int, int, int] | None = move if move_2 else None
        return GameStateBitboardsV3(new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks, new_bishops,
                                    new_knights, new_pawns, white_queen, white_king, black_queen, black_king,
                                    last_move=last_move, color=-self.color, turn=self.turn + 1, winner=new_winner,
                                    moves_since_pawn=new_moves_since_pawn,
                                    previous_position_count=new_previous_position_count)

    def move_only_board(self, move: tuple[int, int, int]) -> tuple[int, int, int, int, int, int, int, int]:
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
        GameStateBitboardsV3
            A new GameStateBitboardsV3 object, with the move applied.
        """
        new_white_pieces: int = self.white_pieces
        new_black_pieces: int = self.black_pieces
        new_kings: int = self.kings
        new_queens: int = self.queens
        new_rooks: int = self.rooks
        new_bishops: int = self.bishops
        new_knights: int = self.knights
        new_pawns: int = self.pawns
        color_local: int = self.color
        move_0, move_1, move_2 = move  # type: int, int, int

        if move_0 == -1:  # Castle
            if color_local == 1:
                if move_1 == -1:
                    new_white_pieces = (new_white_pieces & ~0b1000_1000) | 0b0011_0000
                    new_rooks = (new_rooks & ~0b1000_0000) | 0b0001_0000
                    new_kings = (new_kings & ~0b0000_1000) | 0b0010_0000
                else:
                    new_white_pieces = (new_white_pieces & ~0b0000_1001) | 0b0000_0110
                    new_rooks = (new_rooks & ~0b0000_0001) | 0b0000_0100
                    new_kings = (new_kings & ~0b0000_1000) | 0b0000_0010
            else:
                if move_1 == -1:
                    new_black_pieces = ((new_black_pieces &
                                         ~0b1000_1000_00000000_00000000_00000000_00000000_00000000_00000000_00000000) |
                                        0b0011_0000_00000000_00000000_00000000_00000000_00000000_00000000_00000000)
                    new_rooks = ((new_rooks &
                                  ~0b1000_0000_00000000_00000000_00000000_00000000_00000000_00000000_00000000) |
                                 0b0001_0000_00000000_00000000_00000000_00000000_00000000_00000000_00000000)
                    new_kings = ((new_kings &
                                  ~0b0000_1000_00000000_00000000_00000000_00000000_00000000_00000000_00000000) |
                                 0b0010_0000_00000000_00000000_00000000_00000000_00000000_00000000_00000000)
                else:
                    new_black_pieces = ((new_black_pieces &
                                         ~0b0000_1001_00000000_00000000_00000000_00000000_00000000_00000000_00000000) |
                                        0b0000_0110_00000000_00000000_00000000_00000000_00000000_00000000_00000000)
                    new_rooks = ((new_rooks &
                                  ~0b0000_0001_00000000_00000000_00000000_00000000_00000000_00000000_00000000) |
                                 0b0000_0100_00000000_00000000_00000000_00000000_00000000_00000000_00000000)
                new_kings = ((new_kings & ~0b0000_1000_00000000_00000000_00000000_00000000_00000000_00000000_00000000) |
                             0b0000_0010_00000000_00000000_00000000_00000000_00000000_00000000_00000000)
            return (new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks, new_bishops, new_knights,
                    new_pawns)

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
            return (new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks, new_bishops, new_knights,
                    new_pawns)

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

            return (new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks, new_bishops, new_knights,
                    new_pawns)

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

            return (new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks, new_bishops, new_knights,
                    new_pawns)

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

        return (new_white_pieces, new_black_pieces, new_kings, new_queens, new_rooks, new_bishops, new_knights,
                new_pawns)

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
        return f"""GameStateBitboardsV3(white_pieces={self.white_pieces},
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
