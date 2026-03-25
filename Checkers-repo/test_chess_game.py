import unittest
from chess_game import ChessGame

class TestChessGame(unittest.TestCase):
    def setUp(self):
        self.game = ChessGame()

    def test_initial_board(self):
        self.assertEqual(self.game.board[0][0], "bR")
        self.assertEqual(self.game.board[7][4], "wK")
        self.assertEqual(self.game.board[1][0], "bP")
        self.assertEqual(self.game.board[6][7], "wP")

    def test_pawn_moves(self):
        moves = self.game.get_moves(6,0)  # white pawn a2
        self.assertIn((5,0), moves)
        self.assertIn((4,0), moves)

    def test_knight_moves(self):
        moves = self.game.get_moves(7,1)  # white knight b1
        self.assertIn((5,0), moves)
        self.assertIn((5,2), moves)

    def test_bishop_moves_blocked(self):
        moves = self.game.get_moves(7,2)  # white bishop c1
        self.assertEqual(moves, [])  # initially blocked

    def test_rook_moves_blocked(self):
        moves = self.game.get_moves(7,0)  # white rook a1
        self.assertEqual(moves, [])  # initially blocked

    def test_king_moves_initial(self):
        moves = self.game.get_moves(7,4)  # white king e1
        self.assertEqual(moves, [])  # blocked by pawns

    def test_make_move_and_turn(self):
        self.game.make_move(6,0,4,0)  # move pawn a2->a4
        self.assertEqual(self.game.board[4][0], "wP")
        self.assertEqual(self.game.board[6][0], ".")
        self.assertEqual(self.game.turn, "b")

    def test_is_in_check(self):
        self.game.board = [["."]*8 for _ in range(8)]
        self.game.board[0][4] = "bK"
        self.game.board[7][4] = "wQ"
        self.assertTrue(self.game.is_in_check("b"))
        self.assertFalse(self.game.is_in_check("w"))

    def test_legal_moves_no_check(self):
        moves = self.game.legal_moves("w")
        self.assertTrue(len(moves) > 0)

    def test_checkmate(self):
        self.game.board = [["."]*8 for _ in range(8)]
        self.game.board[0][0] = "bK"
        self.game.board[1][1] = "wQ"
        self.game.board[2][2] = "wR"
        self.assertTrue(self.game.is_checkmate("b"))
        self.assertFalse(self.game.is_checkmate("w"))

    def test_stalemate(self):
        self.game.board = [["."]*8 for _ in range(8)]
        self.game.board[0][0] = "bK"
        self.game.board[7][7] = "wK"
        self.game.board[1][1] = "wQ"
        self.game.board[1][0] = "wR"
        self.assertTrue(self.game.is_stalemate("b"))

if __name__ == "__main__":
    unittest.main()
