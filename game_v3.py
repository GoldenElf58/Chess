from copy import copy

from game_format_v2 import GameStateFormatV2
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
        curr2: list = []
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
                 'winner', 'previous_position_count', 'moves_since_pawn', 'moves')

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
        moves_len: int = len(moves)
        color_local = self.color
        bishop_diagonals_local: tuple[tuple[tuple[int, ...], tuple[int, ...],
        tuple[int, ...], tuple[int, ...]], ...] = bishop_diagonals
        rook_rays_local: tuple[tuple[tuple[int, ...], tuple[int, ...],
        tuple[int, ...], tuple[int, ...]], ...] = rook_rays
        for i, move in enumerate(reversed(moves)):
            state: GameStateV3 = self.move(move)
            additional_squares: list[int] = []
            illegal: bool = False
            if move[0] == -1:  # Castle
                additional_squares = [move[2], move[2] + move[1], move[2] + move[1] * 2]
            king_moved = move[2] == 6 or move[2] == -6 or move[0] == -1
            for h, piece in enumerate(state.board):
                piece_type = color_local * piece
                if piece_type >= 0: continue
                if piece_type == -3 or piece_type == -5:
                    for diagonal in bishop_diagonals_local[h]:
                        for diagonal_idx in diagonal:
                            if king_moved and diagonal_idx in additional_squares:
                                illegal = True
                                break
                            if state.board[diagonal_idx] == 0:
                                continue
                            if state.board[diagonal_idx] * color_local == 6:
                                illegal = True
                            break
                        if illegal:
                            break
                    if illegal:
                        moves.pop(moves_len - i - 1)
                        break
                if piece_type == -4 or piece_type == -5:
                    for ray in rook_rays_local[h]:
                        for ray_idx in ray:
                            if king_moved and ray_idx in additional_squares:
                                illegal = True
                                break
                            if state.board[ray_idx] == 0:
                                continue
                            if state.board[ray_idx] * color_local == 6:
                                illegal = True
                            break
                        if illegal:
                            break
                    if illegal:
                        moves.pop(moves_len - i - 1)
                        break
                elif king_moved:
                    if piece_type == -6:
                        for target_idx in king_targets[h]:
                            if state.board[target_idx] * color_local == 6:
                                break
                        else:
                            continue
                        moves.pop(moves_len - i - 1)
                        break
                    elif piece_type == -2:
                        for target_idx in knight_targets[h]:
                            if state.board[target_idx] * color_local == 6:
                                break
                        else:
                            continue
                        moves.pop(moves_len - i - 1)
                        break
                    elif piece_type == -1:
                        dest_square = h + color_local * 8
                        if state.board[dest_square + 1] * color_local == 6:
                            moves.pop(moves_len - i - 1)
                            break
                        if state.board[dest_square - 1] * color_local == 6:
                            moves.pop(moves_len - i - 1)
                            break

        if len(moves) == 0 and moves_len > 0:
            game_state: GameStateV3 = GameStateV3(self.board, self.white_queen, self.white_king, self.black_queen,
                                                  self.black_king, None, -color_local, self.turn, self.winner)
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

    def get_moves_new(self) -> list[tuple[int, int, int]]:
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
        color_local = self.color
        bishop_diagonals_local: tuple[tuple[tuple[int, ...], tuple[int, ...],
        tuple[int, ...], tuple[int, ...]], ...] = bishop_diagonals
        rook_rays_local: tuple[tuple[tuple[int, ...], tuple[int, ...],
        tuple[int, ...], tuple[int, ...]], ...] = rook_rays
        for i, move in enumerate(reversed(moves)):
            state: GameStateV3 = self.move(move)
            additional_squares: list[int] = []
            illegal: bool = False
            if move[0] == -1:  # Castle
                additional_squares = [move[2], move[2] + move[1], move[2] + move[1] * 2]
            king_moved = move[2] == 6 or move[2] == -6 or move[0] == -1
            for h, piece in enumerate(state.board):
                piece_type = color_local * piece
                if piece_type >= 0: continue
                if piece_type == -3 or piece_type == -5:
                    for diagonal in bishop_diagonals_local[h]:
                        for diagonal_idx in diagonal:
                            if king_moved and diagonal_idx in additional_squares:
                                illegal = True
                                break
                            if state.board[diagonal_idx] == 0:
                                continue
                            if state.board[diagonal_idx] * color_local == 6:
                                illegal = True
                            break
                        if illegal:
                            break
                    if illegal:
                        moves.pop(moves_len - i - 1)
                        break
                if piece_type == -4 or piece_type == -5:
                    for ray in rook_rays_local[h]:
                        for ray_idx in ray:
                            if king_moved and ray_idx in additional_squares:
                                illegal = True
                                break
                            if state.board[ray_idx] == 0:
                                continue
                            if state.board[ray_idx] * color_local == 6:
                                illegal = True
                            break
                        if illegal:
                            break
                    if illegal:
                        moves.pop(moves_len - i - 1)
                        break
                elif king_moved:
                    if piece_type == -6:
                        for target_idx in king_targets[h]:
                            if state.board[target_idx] * color_local == 6:
                                break
                        else:
                            continue
                        moves.pop(moves_len - i - 1)
                        break
                    elif piece_type == -2:
                        for target_idx in knight_targets[h]:
                            if state.board[target_idx] * color_local == 6:
                                break
                        else:
                            continue
                        moves.pop(moves_len - i - 1)
                        break
                    elif piece_type == -1:
                        dest_square = h + color_local * 8
                        if state.board[dest_square + 1] * color_local == 6:
                            moves.pop(moves_len - i - 1)
                            break
                        if state.board[dest_square - 1] * color_local == 6:
                            moves.pop(moves_len - i - 1)
                            break

        if len(moves) == 0 and moves_len > 0:
            game_state: GameStateV3 = GameStateV3(self.board, self.white_queen, self.white_king, self.black_queen,
                                                  self.black_king, None, -color_local, self.turn, self.winner)
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
                if (((color_local == 1 and self.white_king) or (color_local == -1 and self.black_king)) and board_local[
                    row_base + 7] == 4 * color_local
                        and board_local[row_base + 5] == board_local[row_base + 6] == 0):
                    moves.append((-1, 1, h))
                if (((color_local == 1 and self.white_queen) or (color_local == -1 and self.black_queen)) and board_local[
                    row_base + 7] == 4 * color_local
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
                        moves.append((h, h - 16, piece))
                elif i == 1 and board_local[3 * 8 + j] == 0 == board_local[2 * 8 + j]:
                    moves.append((h, h + 16, piece))
                # En Passant
                if (last_move_local is not None and board_local[last_move_local[1]] == -color_local and abs(
                        last_move_local[1] - last_move_local[0]) == 16 and i == last_move_local[1] // 8):
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
            new_board: tuple[int, ...] = self.move(move).board
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
                               color=-self.color, turn=self.turn + 1, moves_since_pawn=0)

        if (piece := abs(move_2)) in (4, 6):
            if move_1 == 56:
                white_queen = False
            elif move_1 == 63:
                white_king = False
            elif not move_1:
                black_queen = False
            elif move_1 == 7:
                black_king = False
            elif move_1 == 4:
                black_queen = False
                black_king = False
            elif move_1 == 60:
                white_queen = False
                white_king = False
        if move_2 in (-4, 4):
            if move_1 == 56:
                white_queen = False
            elif move_1 == 63:
                white_king = False
            elif not move_1:
                black_queen = False
            elif move_1 == 7:
                black_king = False

        if piece == 1:
            new_moves_since_pawn = 0

        new_board[move_1] = move_2
        new_board[move_0] = 0
        new_previous_position_count = copy(self.previous_position_count)
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
