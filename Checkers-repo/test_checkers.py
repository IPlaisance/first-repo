# test_checkers.py
import unittest
from unittest.mock import patch
import random
import sys
import os

# Dynamically import the module regardless of location
sys.path.insert(0, os.path.dirname(__file__))
import checkers_midpoint_final as ck

class TestCheckers(unittest.TestCase):

    def setUp(self):
        self.board = ck.create_board()

    # ---------------- BOARD CREATION ----------------
    def test_create_board_initial(self):
        board = self.board
        # Check board size
        self.assertEqual(len(board), ck.SIZE)
        self.assertEqual(len(board[0]), ck.SIZE)
        # Check initial number of player and computer pieces
        player_count = sum(1 for r in board for c in r if ck.is_player_piece(c))
        computer_count = sum(1 for r in board for c in r if ck.is_computer_piece(c))
        self.assertEqual(player_count, 12)
        self.assertEqual(computer_count, 12)
        # Check empty squares
        empty_count = sum(1 for r in board for c in r if c == ck.EMPTY)
        self.assertEqual(empty_count, ck.SIZE*ck.SIZE - 24)

    # ---------------- HELPER FUNCTIONS ----------------
    def test_in_bounds(self):
        self.assertTrue(ck.in_bounds(0,0))
        self.assertTrue(ck.in_bounds(7,7))
        self.assertFalse(ck.in_bounds(-1,0))
        self.assertFalse(ck.in_bounds(0,8))

    def test_coord_conversion(self):
        r, c = ck.coord_to_index("a0")
        self.assertEqual((r,c), (0,0))
        coord = ck.index_to_coord(7,7)
        self.assertEqual(coord, "h7")

    # ---------------- MOVE EXECUTION ----------------
    def test_make_move_normal_and_jump(self):
        # Move a player piece forward
        became_king = ck.make_move(self.board, 5, 0, 4, 1)
        self.assertFalse(became_king)
        self.assertEqual(self.board[4][1], ck.PLAYER)
        self.assertEqual(self.board[5][0], ck.EMPTY)

        # Set up jump
        self.board[3][2] = ck.COMPUTER
        became_king = ck.make_move(self.board, 4, 1, 2, 3)
        self.assertFalse(became_king)
        # Check captured piece removed
        self.assertEqual(self.board[3][2], ck.EMPTY)
        # Check new piece position
        self.assertEqual(self.board[2][3], ck.PLAYER)

    # ---------------- MULTI-JUMP LOGIC ----------------
    def test_get_jump_paths(self):
        board = [[ck.EMPTY]*ck.SIZE for _ in range(ck.SIZE)]
        board[5][0] = ck.PLAYER
        board[4][1] = ck.COMPUTER
        board[2][3] = ck.COMPUTER
        board[3][2] = ck.EMPTY
        paths = ck.get_jump_paths(board, 5, 0, ck.PLAYER)
        # Should return a path with two jumps
        self.assertTrue(any(len(p) >= 2 for p in paths))

    # ---------------- GET ALL MOVES ----------------
    def test_get_all_moves(self):
        moves, jumps = ck.get_all_moves(self.board, ck.is_player_piece)
        # Player has some normal moves
        self.assertTrue(len(moves) > 0)

    # ---------------- PLAYER AND COMPUTER PIECES ----------------
    def test_has_piece_and_has_any_moves(self):
        self.assertTrue(ck.has_piece(self.board, ck.is_player_piece))
        self.assertTrue(ck.has_piece(self.board, ck.is_computer_piece))
        self.assertTrue(ck.has_any_moves(self.board, ck.is_player_piece))
        self.assertTrue(ck.has_any_moves(self.board, ck.is_computer_piece))

    # ---------------- COMPUTER TURN WITH MOCK ----------------
    @patch('random.choice')
    def test_computer_turn_executes_move(self, mock_choice):
        # Force deterministic move
        moves, jumps = ck.get_all_moves(self.board, ck.is_computer_piece)
        mock_choice.return_value = moves[0]  # pick first move
        ck.computer_turn(self.board)
        self.assertNotEqual(self.board[moves[0][0]][moves[0][1]], ck.COMPUTER)  # old spot empty
        self.assertEqual(self.board[moves[0][2]][moves[0][3]], ck.COMPUTER)  # new spot filled

    # ---------------- PLAYER TURN MOCK INPUT ----------------
    @patch('builtins.input', side_effect=['f5','e4'])
    def test_player_turn_executes_move(self, mock_input):
        # Select a piece at f5 (5,5) and move to e4 (4,4)
        self.board[5][5] = ck.PLAYER
        self.board[4][4] = ck.EMPTY
        ck.player_turn(self.board)
        self.assertEqual(self.board[4][4], ck.PLAYER)
        self.assertEqual(self.board[5][5], ck.EMPTY)

if __name__ == "__main__":
    unittest.main()