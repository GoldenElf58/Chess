from copy import copy

from game_states.game_base import GameStateBase
from archive.game_bitboards import GameStateBitboards
from game_states.game_bitboards_v2 import GameStateBitboardsV2
from game_states.game_v3 import GameStateV3
from game_states.game_v2 import GameStateV2
from utils import split_table

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
                    curr.append((((i + k) * 8 + j + l), i + k, j + l))
                if 8 > i + l >= 0 <= j + k < 8:
                    curr.append((((i + l) * 8 + j + k), i + l, j + k))
        temp_knight.append(tuple(curr))

        curr = []
        for k in range(-1, 2):
            for l in range(-1, 2):
                if 0 <= i + k < 8 and 0 <= j + l < 8:
                    curr.append(((i + k) * 8 + j + l, i + k, j + l))
        temp_king.append(tuple(curr))

        curr = []
        curr2: list = []
        for k in range(j + 1, 8):
            curr2.append((h - j + k, i, k))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(j - 1, -1, -1):
            curr2.append((h - j + k, i, k))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(i + 1, 8):
            curr2.append((k * 8 + j, k, j))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(i - 1, -1, -1):
            curr2.append((k * 8 + j, k, j))
        curr.append(tuple(curr2))
        temp_rook.append(tuple(curr))

        curr = []
        curr2 = []
        for k in range(1, 8):
            if i + k > 7 or j + k > 7: break
            curr2.append(((i + k) * 8 + (j + k), i + k, j + k))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(1, 8):
            if i - k < 0 or j + k > 7: break
            curr2.append(((i - k) * 8 + (j + k), i - k, j + k))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(1, 8):
            if i + k > 7 or j - k < 0: break
            curr2.append(((i + k) * 8 + (j - k), i + k, j - k))
        curr.append(tuple(curr2))
        curr2 = []
        for k in range(1, 8):
            if i - k < 0 or j - k < 0: break
            curr2.append(((i - k) * 8 + (j - k), i - k, j - k))
        curr.append(tuple(curr2))
        temp_bishop.append(tuple(curr))

    knight_targets = tuple(temp_knight)
    king_targets = tuple(temp_king)
    rook_rays = tuple(temp_rook)
    bishop_diagonals = tuple(temp_bishop)


populate_precomputed_tables()

start_board: tuple[int, ...] = (
    -4, -2, -3, -5, -6, -3, -2, -4,
    -1, -1, -1, -1, -1, -1, -1, -1,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 1, 1, 1, 1,
    4, 2, 3, 5, 6, 3, 2, 4
)


class GameState(GameStateBase):
    __slots__ = ('board', 'color', 'white_queen', 'white_king', 'black_queen', 'black_king', 'last_move', 'turn',
                 'winner', 'previous_position_count', 'moves_since_pawn', 'moves')

    def __init__(self, board: tuple | None = None, white_queen: bool = True, white_king: bool = True,
                 black_queen: bool = True, black_king: bool = True, last_move: tuple[int, int, int, int] | None = None,
                 color: int = 1, turn: int = 0, winner: int | None = None,
                 previous_position_count: dict[int, int] | None = None, moves_since_pawn: int = 0) -> None:
        """
        Initialize a GameState object.

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
        """
        self.board: tuple[int, ...] = start_board if board is None else board
        self.moves: list[tuple[int, int, int, int]] | None = None
        self.last_move: tuple[int, int, int, int] | None = last_move
        super().__init__(white_queen, white_king, black_queen, black_king, color, turn, winner,
                         previous_position_count, moves_since_pawn)

    def get_hashable_state(self) -> tuple[
        tuple[int, ...], int, bool, bool, bool, bool, tuple[int, int, int, int] | None]:
        """ Convert the game state into a hashable format for caching. """
        return self.board, self.color, self.white_queen, self.white_king, self.black_queen, self.black_king, self.last_move

    def get_hashed(self) -> int:
        return hash((self.board, (((self.color == 1) << 4) | (self.white_queen << 3) | (self.white_king << 2) | (
                self.black_queen << 1) | self.black_king),
                     self.last_move))

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
                    king_idx: int = move_0[2] * 8 + move_0[3]
                    if move_0[1] == 1:
                        for idx in range(king_idx, king_idx + 2):
                            if state_2.board[idx] * self.color < 0:
                                break
                        else:
                            continue
                    else:
                        for idx in range(king_idx - 1, king_idx + 1):
                            if state_2.board[idx] * self.color < 0:
                                break
                        else:
                            continue
                    moves.pop(moves_len - i - 1)
                    break
        if len(moves) == 0 and moves_len > 0:
            game_state: GameState = GameState(self.board, self.white_queen, self.white_king, self.black_queen,
                                              self.black_king, None, -self.color, self.turn, self.winner)
            for move in game_state.get_moves_no_check():
                if (winner := game_state.move(move).get_winner()) == -1 or winner == 1:
                    break
            else:
                self.winner = 0
                self.moves = moves
                return moves
            self.winner = winner
        elif self.moves_since_pawn >= 50:
            self.winner = 0
        self.moves = moves
        return moves

    def get_moves_no_check(self) -> list[tuple[int, int, int, int]]:
        hash_state: tuple[
            tuple[int, ...], int, bool, bool, bool, bool, tuple[int, int, int, int] | None] = self.get_hashable_state()
        return self.get_moves_no_check_static(*hash_state)

    @staticmethod
    def get_moves_no_check_static(
            board: tuple[int, ...],
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
        board_local: tuple[int, ...] = board
        last_move_local: tuple[int, int, int, int] | None = last_move
        coords_local: list[tuple[int, int]] = index_to_coord
        knight_targets_local: tuple[tuple[tuple[int, int, int], ...], ...] = knight_targets
        king_targets_local: tuple[tuple[tuple[int, int, int], ...], ...] = king_targets
        rook_rays_local: tuple[tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...],
        tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...]], ...] = rook_rays
        bishop_diagonals_local: tuple[tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...],
        tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...]], ...] = bishop_diagonals
        for h, piece in enumerate(board_local):
            piece_type: int = piece * color_local
            if piece_type <= 0: continue
            i, j = coords_local[h]
            if piece_type == 6:  # King
                row_base: int = h - j
                if (((color_local == 1 and white_king) or (color_local == -1 and black_king)) and board_local[
                    row_base + 7] == 4 * color_local
                        and board_local[row_base + 5] == board_local[row_base + 6] == 0):
                    moves.append((-1, 1, i, j))
                if (((color_local == 1 and white_queen) or (color_local == -1 and black_queen)) and board_local[
                    row_base + 7] == 4 * color_local
                        and board_local[row_base + 1] == board_local[row_base + 2] == board_local[row_base + 3] == 0):
                    moves.append((-1, -1, i, j))
                for (index, target_i, target_j) in king_targets_local[h]:
                    if board_local[index] * color_local <= 0:
                        moves.append((i, j, target_i, target_j))
            elif piece_type == 4 or piece_type == 5:  # Rook and Queen
                for ray in rook_rays_local[h]:
                    for (idx, ray_i, ray_j) in ray:
                        if board_local[idx] == 0:
                            moves.append((i, j, ray_i, ray_j))
                            continue
                        if board_local[idx] * color_local < 0:
                            moves.append((i, j, ray_i, ray_j))
                        break
            if piece_type == 3 or piece_type == 5:  # Bishop and Queen
                for diagonal in bishop_diagonals_local[h]:
                    for (idx, diagonal_i, diagonal_j) in diagonal:
                        if board_local[idx] == 0:
                            moves.append((i, j, diagonal_i, diagonal_j))
                            continue
                        if board_local[idx] * color_local < 0:
                            moves.append((i, j, diagonal_i, diagonal_j))
                        break
            elif piece_type == 2:  # Knight
                for (idx, target_i, target_j) in knight_targets_local[h]:
                    if board_local[idx] * color_local <= 0:
                        moves.append((i, j, target_i, target_j))
            elif piece_type == 1:
                dest_square: int = (i - color_local) * 8 + j
                if not board_local[dest_square]:
                    if 7 != i - color_local != 0:
                        moves.append((i, j, i - color_local, j))
                    else:
                        for move_id, promotion_piece in promotion_forward:
                            moves.append((move_id, promotion_piece * color_local, i, j))
                if 8 > (j + 1) and 0 > board_local[dest_square + 1] * color_local:
                    if 7 != i - color_local != 0:
                        moves.append((i, j, i - color_local, j + 1))
                    else:  # Promotion
                        for promotion_piece, direction in promotion_taking:
                            moves.append((promotion_piece, direction, i, j))
                if (j - 1) >= 0 > board_local[dest_square - 1] * color_local:
                    if 7 != i - color_local != 0:
                        moves.append((i, j, i - color_local, j - 1))
                    else:  # Promotion
                        for promotion_piece, direction in promotion_taking:
                            moves.append((promotion_piece, -direction, i, j))
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
                        moves.append((-2, -1, i, j))
                    elif 0 != j == last_move_local[3] - 1:
                        moves.append((-2, 1, i, j))
        return moves

    def are_captures(self) -> bool:
        moves: list[tuple[int, int, int, int]] = self.get_moves()
        board_local: tuple[int, ...] = self.board
        empty_count: int = board_local.count(0)
        for move in moves:
            new_board: tuple[int, ...] = self.move(move).board
            if new_board.count(0) != empty_count:
                return True
        return False

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
        board_local: tuple[int, ...] = self.board
        new_board: list[int] = list(board_local)
        white_queen: bool = self.white_queen
        white_king: bool = self.white_king
        black_queen: bool = self.black_queen
        black_king: bool = self.black_king
        new_moves_since_pawn: int = self.moves_since_pawn + 1
        move_0, move_1, move_2, move_3 = move

        if not len(move):
            return GameState(board_local, turn=self.turn + 1, winner=self.winner)

        second_idx: int = move_2 * 8 + move_3
        if move_0 == -1:  # Castle
            if move_2 == 7:
                white_queen = False
                white_king = False
            else:
                black_queen = False
                black_king = False

            new_board[second_idx] = 0
            new_board[move_2 * 8 + (0 if move_1 == -1 else 7)] = 0
            new_board[move_2 * 8 + 4 + move_1 * 2] = board_local[second_idx]
            new_board[move_2 * 8 + 4 + move_1] = board_local[move_2 * 8 + (0 if move_1 == -1 else 7)]
            return GameState(tuple(new_board), white_queen, white_king, black_queen, black_king,
                             color=-self.color, turn=self.turn + 1, moves_since_pawn=new_moves_since_pawn)

        if move_0 == -2:  # En Passant
            new_board[second_idx] = 0
            new_board[(move_2 - self.color) * 8 + move_3 + move_1] = self.color
            new_board[second_idx + move_1] = 0
            return GameState(tuple(new_board), white_queen, white_king, black_queen, black_king,
                             color=-self.color, turn=self.turn + 1, moves_since_pawn=0)

        if move_0 == -3:  # Promotion
            new_board[second_idx] = 0
            new_board[(move_2 - self.color) * 8 + move_3] = move_1
            return GameState(tuple(new_board), white_queen, white_king, black_queen, black_king, color=-self.color,
                             turn=self.turn + 1, moves_since_pawn=0)

        if move_0 <= -4:  # Promotion while taking
            new_board[second_idx] = 0
            new_board[(move_2 - self.color) * 8 + (move_3 + move_1)] = (move_0 + 2) * -self.color

            return GameState(tuple(new_board), white_queen, white_king, black_queen, black_king,
                             color=-self.color, turn=self.turn + 1, moves_since_pawn=0)

        first_idx: int = move_0 * 8 + move_1
        if (piece := abs(new_board[first_idx])) in (4, 6):
            if move_2 == 7 and not move_3:
                white_queen = False
            if move_2 == 7 and move_3 == 7:
                white_king = False
            if not (move_2 or move_3):
                black_queen = False
            if not move_2 and move_3 == 7:
                black_king = False
            if not move_2 and move_3 == 4:
                black_queen = False
                black_king = False
            if move_2 == 7 and move_3 == 4:
                white_queen = False
                white_king = False
        if new_board[second_idx] in (-4, 4):
            if move_2 == 7 and not move_3:
                white_queen = False
            if move_2 == 7 and move_3 == 7:
                white_king = False
            if not (move_2 or move_3):
                black_queen = False
            if not move_2 and move_3 == 7:
                black_king = False

        if piece == 1:
            new_moves_since_pawn = 0

        new_board[second_idx] = new_board[first_idx]
        new_board[first_idx] = 0
        new_previous_position_count = copy(self.previous_position_count)
        if (hash_state := hash(board_local)) in new_previous_position_count:
            new_previous_position_count[hash_state] += 1
            if new_previous_position_count[hash_state] >= 3:
                return GameState(tuple(new_board), winner=0)
        else:
            new_previous_position_count[hash_state] = 1
        last_move: tuple[int, int, int, int] | None = move if (
                piece == 1 and (move_0 == move_2 + self.color * 2)) else None
        return GameState(tuple(new_board), white_queen, white_king, black_queen, black_king, last_move=last_move,
                         color=-self.color, turn=self.turn + 1, moves_since_pawn=new_moves_since_pawn,
                         previous_position_count=new_previous_position_count)

    def get_winner(self) -> int | None:
        if self.winner is not None:
            return self.winner
        if self.moves_since_pawn >= 50:
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
                if -6 != piece != 6:
                    return None
            self.winner = 0
        return self.winner

    def to_bitboards(self) -> GameStateBitboards:
        pawns: int = 0
        knights: int = 0
        bishops: int = 0
        rooks: int = 0
        queens: int = 0
        kings: int = 0
        white: int = 0
        black: int = 0
        for i, piece in enumerate(self.board):
            if not piece:
                continue
            piece_mask = 1 << (64 - i)
            if piece > 0:
                white |= piece_mask
            else:
                black |= piece_mask
            piece_type = abs(piece)
            if piece_type == 1:
                pawns |= piece_mask
            elif piece_type == 2:
                knights |= piece_mask
            elif piece_type == 3:
                bishops |= piece_mask
            elif piece_type == 4:
                rooks |= piece_mask
            elif piece_type == 5:
                queens |= piece_mask
            elif piece_type == 6:
                kings |= piece_mask
        return GameStateBitboards(white, black, pawns, knights, bishops, rooks, queens, kings, self.white_queen,
                                  self.white_king, self.black_queen, self.black_king, self.last_move,
                                  self.color, self.turn, self.winner, self.previous_position_count,
                                  self.moves_since_pawn)

    def to_bitboards_v2(self) -> GameStateBitboardsV2:
        return self.to_bitboards().to_bitboards_v2()

    def to_v2(self) -> GameStateV2:
        return GameStateV2(self.board, self.white_queen, self.white_king, self.black_queen, self.black_king,
                           None, self.color, self.turn, self.winner, copy(self.previous_position_count),
                           self.moves_since_pawn)

    def to_v3(self) -> GameStateV3:
        return GameStateV3(self.board, self.white_queen, self.white_king, self.black_queen, self.black_king,
                           None, self.color, self.turn, self.winner, copy(self.previous_position_count),
                           self.moves_since_pawn)

    def copy(self) -> 'GameState':
        return GameState(self.board, self.white_queen, self.white_king, self.black_queen, self.black_king,
                         self.last_move, self.color, self.turn, self.winner, copy(self.previous_position_count),
                         self.moves_since_pawn)

    def __repr__(self) -> str:
        return f"""GameState(board={self.board}
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
