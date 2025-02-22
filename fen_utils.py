from game import GameState

# Mapping from FEN characters to GameState piece values.
fen_piece_to_int = {
    'K': 6,
    'Q': 5,
    'R': 4,
    'B': 3,
    'N': 2,
    'P': 1,
    'k': -6,
    'q': -5,
    'r': -4,
    'b': -3,
    'n': -2,
    'p': -1
}


def algebraic_to_index(square: str) -> int:
    """
    Convert algebraic notation (e.g., 'e3') to a 0-based board index.
    """
    file = ord(square[0]) - ord('a')
    rank = 8 - int(square[1])
    return rank * 8 + file


def game_state_from_fen(fen: str) -> GameState:
    """
    Convert a FEN string into a GameState object.
    """
    parts = fen.split()
    if len(parts) < 6:
        raise ValueError("Invalid FEN: not enough fields")

    board_part, active_color, castling, en_passant, halfmove, fullmove = parts[:6]

    # Build the board (a flat list of 64 ints).
    board = []
    ranks = board_part.split('/')
    if len(ranks) != 8:
        raise ValueError("Invalid FEN: board must have 8 ranks")
    for rank in ranks:
        for char in rank:
            if char.isdigit():
                board.extend([0] * int(char))
            elif char in fen_piece_to_int:
                board.append(fen_piece_to_int[char])
            else:
                raise ValueError(f"Invalid FEN character: {char}")
    if len(board) != 64:
        raise ValueError("Invalid FEN: board does not have 64 squares")

    # Set active color: white -> 1, black -> -1.
    color = 1 if active_color == 'w' else -1

    # Parse castling rights.
    white_king = 'K' in castling
    white_queen = 'Q' in castling
    black_king = 'k' in castling
    black_queen = 'q' in castling

    # Compute turn count based on the fullmove number.
    fullmove_num = int(fullmove)
    turn = (fullmove_num - 1) * 2 if color == 1 else (fullmove_num - 1) * 2 + 1

    # Handle en passant.
    # If the en passant field is not '-', simulate the last double pawn move.
    # According to FEN, the en passant target square is the square "behind" the pawn
    # that moved two squares. For white, a double move is from row 6 to 4 (target row 5),
    # and for black, from row 1 to 3 (target row 2).
    if en_passant != '-':
        ep_index = algebraic_to_index(en_passant)
        ep_row, ep_col = divmod(ep_index, 8)
        # Determine which pawn moved two squares.
        if active_color == 'b':
            # White just moved double from row 6 to 4.
            last_move = (6, ep_col, 4, ep_col)
        else:  # active_color == 'w'
            # Black just moved double from row 1 to 3.
            last_move = (1, ep_col, 3, ep_col)
    else:
        last_move = None

    return GameState(
        board=tuple(board),
        white_queen=white_queen,
        white_king=white_king,
        black_queen=black_queen,
        back_king=black_king,
        last_move=last_move,
        color=color,
        turn=turn,
    )


def game_state_from_line(line_number: int, filename: str = "positions.txt") -> GameState:
    """
    Read the specified (1-indexed) line from a file of FEN strings and
    return the corresponding GameState.
    """
    with open(filename, "r") as f:
        lines = f.readlines()
    if line_number < 1 or line_number > len(lines):
        raise ValueError("Line number out of range")
    fen = lines[line_number - 1].strip()
    return game_state_from_fen(fen)


if __name__ == '__main__':
    # Example: Create a GameState from line 1 of positions.txt and print its board.
    gs = game_state_from_line(1, "positions.txt")
    print(gs)