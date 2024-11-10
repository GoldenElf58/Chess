from enum import Flag, auto


class Piece(Flag):
    PAWN = auto()
    KNIGHT = auto()
    BISHOP = auto()
    ROOK = auto()
    QUEEN = auto()
    KING = auto()

    WHITE = auto()
    BLACK = auto()

    NONE = auto()


PAWN = Piece.PAWN
KNIGHT = Piece.KNIGHT
BISHOP = Piece.BISHOP
ROOK = Piece.ROOK
QUEEN = Piece.QUEEN
KING = Piece.KING

WHITE = Piece.WHITE
BLACK = Piece.BLACK

NONE = Piece.NONE
