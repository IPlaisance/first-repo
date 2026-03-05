import sys
import os
import unittest
import random

# ----------------- HANDLE MODULE IMPORT -----------------
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    import Midterm_checkers as mc
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "Cannot find 'Midterm_checkers.py'. Make sure it's in the same folder as this test file."
    )

# ----------------- FULL TEST SUITE -----------------

class TestMidtermCheckers(unittest.TestCase):

    def setUp(self):
        self.board = mc.create_board()

    # ----- Board setup -----
    def test_initial_board_setup(self):
        player_pieces = sum(row.count(mc.PLAYER) for row in self.board)
        computer_pieces = sum(row.count(mc.COMPUTER) for row in self.board)
        self.assertEqual(player_pieces, 12)
        self.assertEqual(computer_pieces, 12)

    # ----- Boundaries and coordinates -----
    def test_in_bounds(self):
        self.assertTrue(mc.in_bounds(0, 0))
        self.assertTrue(mc.in_bounds(7, 7))
        self.assertFalse(mc.in_bounds(-1, 0))
        self.assertFalse(mc.in_bounds(0, 8))

    def test_coord_conversion(self):
        r, c = mc.coord_to_index('a0')
        self.assertEqual((r, c), (0, 0))
        coord = mc.index_to_coord(r, c)
        self.assertEqual(coord, 'a0')

        r, c = mc.coord_to_index('h7')
        self.assertEqual((r, c), (7, 7))
        coord = mc.index_to_coord(r, c)
        self.assertEqual(coord, 'h7')

    # ----- Piece checks -----
    def test_piece_type_checks(self):
        self.assertTrue(mc.is_player_piece(mc.PLAYER))
        self.assertTrue(mc.is_computer_piece(mc.COMPUTER))
        self.assertFalse(mc.is_king(mc.PLAYER))
        self.assertTrue(mc.is_king(mc.PLAYER_KING))
        self.assertTrue(mc.is_king(mc.COMPUTER_KING))

    # ----- Move generation -----
    def test_get_piece_moves_basic(self):
        moves, jumps = mc.get_piece_moves(self.board, 5, 0)
        self.assertTrue(len(moves) > 0)
        self.assertEqual(len(jumps), 0)

    def test_get_all_moves(self):
        moves, jumps = mc.get_all_moves(self.board, mc.is_player_piece)
        self.assertTrue(len(moves) > 0)
        self.assertEqual(len(jumps), 0)

    # ----- Move execution and king promotion -----
    def test_make_move_regular_and_king(self):
        # Regular move
        mc.make_move(self.board, 5, 0, 4, 1)
        self.assertEqual(self.board[4][1], mc.PLAYER)
        self.assertEqual(self.board[5][0], mc.EMPTY)

        # King promotion
        self.board[1][1] = mc.PLAYER
        became_king = mc.make_move(self.board, 1, 1, 0, 0)
        self.assertTrue(became_king)
        self.assertEqual(self.board[0][0], mc.PLAYER_KING)

    # ----- Forced jumps -----
    def test_forced_jump(self):
        # Setup: player piece must jump over computer piece
        self.board[5][1] = mc.PLAYER
        self.board[4][2] = mc.COMPUTER
        self.board[3][3] = mc.EMPTY

        moves, jumps = mc.get_piece_moves(self.board, 5, 1)
        self.assertEqual(len(jumps), 1)
        self.assertEqual(jumps[0], (3, 3))

    # ----- Multi-jump scenario -----
    def test_multi_jump(self):
        # Player can chain two jumps
        self.board[5][1] = mc.PLAYER
        self.board[4][2] = mc.COMPUTER
        self.board[2][4] = mc.COMPUTER
        self.board[3][3] = mc.EMPTY
        self.board[1][5] = mc.EMPTY

        _, jumps = mc.get_piece_moves(self.board, 5, 1)
        self.assertIn((3,3), jumps)
        # Note: multi-jump logic continues in the game loop; single jump detected here

    # ----- King power -----
    def test_player_king_power(self):
        self.board[0][1] = mc.COMPUTER
        mc.player_special_move = True
        # simulate moving opponent piece
        opp = mc.get_all_positions(self.board, mc.is_computer_piece)
        r, c = opp[0]
        moves = mc.get_single_moves_any(self.board, r, c)
        if moves:
            nr, nc = moves[0]
            self.board[nr][nc] = self.board[r][c]
            self.board[r][c] = mc.EMPTY
        self.assertIn(mc.COMPUTER, sum(self.board, []))

    def test_computer_king_power(self):
        self.board[7][1] = mc.PLAYER
        mc.computer_special_move = True
        mc.computer_move_opponent_piece(self.board)
        self.assertTrue(any(mc.is_player_piece(cell) for row in self.board for cell in row))

    # ----- Game end detection -----
    def test_has_piece_and_moves(self):
        self.assertTrue(mc.has_piece(self.board, mc.is_player_piece))
        self.assertTrue(mc.has_piece(self.board, mc.is_computer_piece))
        self.assertTrue(mc.has_any_moves(self.board, mc.is_player_piece))
        self.assertTrue(mc.has_any_moves(self.board, mc.is_computer_piece))

        empty_board = [[mc.EMPTY]*mc.SIZE for _ in range(mc.SIZE)]
        self.assertFalse(mc.has_piece(empty_board, mc.is_player_piece))
        self.assertFalse(mc.has_any_moves(empty_board, mc.is_computer_piece))

    # ----- Speed checker simulation -----
    def test_speed_turn_skipped(self):
        mc.turn_skipped = False
        mc.skip_turn()
        self.assertTrue(mc.turn_skipped)


if __name__ == '__main__':
    unittest.main()