from piece import *


class Board:
    def __init__(self):
        self.board = self.start_board()
        self.turn = WHITE
        self.possible_moves = FILL IN

    def find_moves(self) -> None:

        for row in self.board:
            for piece in row:


    @staticmethod
    def start_board() -> list[list[Piece]]:
        board = Board.empty_board()

        board[0][0] = ROOK | WHITE
        board[0][1] = KNIGHT | WHITE
        board[0][2] = BISHOP | WHITE
        board[0][3] = QUEEN | WHITE
        board[0][4] = KING | WHITE
        board[0][5] = BISHOP | WHITE
        board[0][6] = KNIGHT | WHITE
        board[0][7] = ROOK | WHITE

        board[7][0] = ROOK | BLACK
        board[7][1] = KNIGHT | BLACK
        board[7][2] = BISHOP | BLACK
        board[7][3] = QUEEN | BLACK
        board[7][4] = KING | BLACK
        board[7][5] = BISHOP | BLACK
        board[7][6] = KNIGHT | BLACK
        board[7][7] = ROOK | BLACK

        for i in range(8):
            board[1][i] = PAWN | WHITE
            board[6][i] = PAWN | BLACK

        return board

    @staticmethod
    def empty_board() -> list[list[Piece]]:
        return [[Piece.NONE for _ in range(8)] for _ in range(8)]
