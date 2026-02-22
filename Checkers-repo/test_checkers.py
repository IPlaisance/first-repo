# test_checkers.py
import pytest
from checkers_midpoint_final import *

# ============================================================================
# BOARD CREATION TESTS
# ============================================================================

def test_create_board_dimensions():
    """Test that the board has correct dimensions."""
    board = create_board()
    assert len(board) == SIZE
    for row in board:
        assert len(row) == SIZE

def test_create_board_initial_positions():
    """Test that pieces start in correct positions."""
    board = create_board()
    
    # Top rows should have computer pieces on dark squares
    for r in range(3):
        for c in range(SIZE):
            if (r + c) % 2 == 1:
                assert board[r][c] == COMPUTER, f"Expected COMPUTER at ({r},{c})"
            else:
                assert board[r][c] == EMPTY, f"Expected EMPTY at ({r},{c})"
    
    # Bottom rows should have player pieces on dark squares
    for r in range(5, 8):
        for c in range(SIZE):
            if (r + c) % 2 == 1:
                assert board[r][c] == PLAYER, f"Expected PLAYER at ({r},{c})"
            else:
                assert board[r][c] == EMPTY, f"Expected EMPTY at ({r},{c})"
    
    # Middle rows empty
    for r in range(3, 5):
        for c in range(SIZE):
            assert board[r][c] == EMPTY, f"Expected EMPTY at ({r},{c})"

def test_create_board_piece_count():
    """Test that the correct number of pieces are created."""
    board = create_board()
    player_count = sum(1 for r in board for cell in r if is_player_piece(cell))
    computer_count = sum(1 for r in board for cell in r if is_computer_piece(cell))
    
    assert player_count == 12, f"Expected 12 player pieces, got {player_count}"
    assert computer_count == 12, f"Expected 12 computer pieces, got {computer_count}"

# ============================================================================
# COORDINATE CONVERSION TESTS
# ============================================================================

def test_coord_to_index_valid():
    """Test converting chess coordinates to indices."""
    assert coord_to_index('a0') == (0, 0)
    assert coord_to_index('a7') == (7, 0)
    assert coord_to_index('h0') == (0, 7)
    assert coord_to_index('h7') == (7, 7)
    assert coord_to_index('d4') == (4, 3)

def test_coord_to_index_case_insensitive():
    """Test that coordinate conversion is case-insensitive."""
    assert coord_to_index('A0') == (0, 0)
    assert coord_to_index('H7') == (7, 7)
    assert coord_to_index('D4') == (4, 3)

def test_index_to_coord_valid():
    """Test converting indices to chess coordinates."""
    assert index_to_coord(0, 0) == 'a0'
    assert index_to_coord(7, 0) == 'a7'
    assert index_to_coord(0, 7) == 'h0'
    assert index_to_coord(7, 7) == 'h7'
    assert index_to_coord(4, 3) == 'd4'

def test_coord_conversion_roundtrip():
    """Test that coordinate conversions are reversible."""
    for r in range(SIZE):
        for c in range(SIZE):
            coord = index_to_coord(r, c)
            r2, c2 = coord_to_index(coord)
            assert (r, c) == (r2, c2)

# ============================================================================
# BOUNDARY TESTS
# ============================================================================

def test_in_bounds_valid():
    """Test that valid coordinates are detected."""
    assert in_bounds(0, 0)
    assert in_bounds(7, 7)
    assert in_bounds(3, 3)
    assert in_bounds(0, 7)
    assert in_bounds(7, 0)

def test_in_bounds_invalid():
    """Test that invalid coordinates are detected."""
    assert not in_bounds(-1, 0)
    assert not in_bounds(0, -1)
    assert not in_bounds(-1, -1)
    assert not in_bounds(8, 0)
    assert not in_bounds(0, 8)
    assert not in_bounds(8, 8)
    assert not in_bounds(10, 10)

# ============================================================================
# PIECE IDENTIFICATION TESTS
# ============================================================================

def test_is_player_piece():
    """Test player piece identification."""
    assert is_player_piece(PLAYER)
    assert is_player_piece(PLAYER_KING)
    assert not is_player_piece(COMPUTER)
    assert not is_player_piece(COMPUTER_KING)
    assert not is_player_piece(EMPTY)

def test_is_computer_piece():
    """Test computer piece identification."""
    assert is_computer_piece(COMPUTER)
    assert is_computer_piece(COMPUTER_KING)
    assert not is_computer_piece(PLAYER)
    assert not is_computer_piece(PLAYER_KING)
    assert not is_computer_piece(EMPTY)

def test_is_king():
    """Test king piece identification."""
    assert is_king(PLAYER_KING)
    assert is_king(COMPUTER_KING)
    assert not is_king(PLAYER)
    assert not is_king(COMPUTER)
    assert not is_king(EMPTY)

# ============================================================================
# MOVE GENERATION TESTS
# ============================================================================

def test_get_piece_moves_empty_square():
    """Test that empty squares have no moves."""
    board = create_board()
    moves, jumps = get_piece_moves(board, 3, 3)
    assert moves == []
    assert jumps == []

def test_get_piece_moves_player_regular():
    """Test player piece movement (should move up)."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[5][3] = PLAYER
    
    moves, jumps = get_piece_moves(board, 5, 3)
    
    # Player pieces should move diagonally up
    expected_moves = [(4, 2), (4, 4)]
    assert set(moves) == set(expected_moves)
    assert jumps == []

def test_get_piece_moves_player_king():
    """Test player king movement (should move both up and down)."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[4][3] = PLAYER_KING
    
    moves, jumps = get_piece_moves(board, 4, 3)
    
    # King should be able to move in all diagonals if not blocked
    expected_moves = [(3, 2), (3, 4), (5, 2), (5, 4)]
    assert set(moves) == set(expected_moves)

def test_get_piece_moves_computer_regular():
    """Test computer piece movement (should move down)."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[2][3] = COMPUTER
    
    moves, jumps = get_piece_moves(board, 2, 3)
    
    # Computer pieces should move diagonally down
    expected_moves = [(3, 2), (3, 4)]
    assert set(moves) == set(expected_moves)

def test_get_piece_moves_computer_king():
    """Test computer king movement (should move both directions)."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[3][3] = COMPUTER_KING
    
    moves, jumps = get_piece_moves(board, 3, 3)
    
    expected_moves = [(2, 2), (2, 4), (4, 2), (4, 4)]
    assert set(moves) == set(expected_moves)

def test_get_piece_moves_jump_player():
    """Test player piece jump move detection."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[4][3] = PLAYER
    board[3][2] = COMPUTER  # Opponent to jump over
    
    moves, jumps = get_piece_moves(board, 4, 3)
    
    assert (2, 1) in jumps
    assert (2, 1) not in moves

def test_get_piece_moves_jump_computer():
    """Test computer piece jump move detection."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[3][3] = COMPUTER
    board[4][2] = PLAYER  # Opponent to jump over
    
    moves, jumps = get_piece_moves(board, 3, 3)
    
    assert (5, 1) in jumps
    assert (5, 1) not in moves

def test_get_piece_moves_corner():
    """Test move generation at board corners."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    # Player pieces at bottom move UP (negative row), so put at bottom corner
    board[7][0] = PLAYER
    
    moves, jumps = get_piece_moves(board, 7, 0)
    
    # Can only move one direction from corner (up-right only)
    expected_moves = [(6, 1)]
    assert set(moves) == set(expected_moves)

def test_get_piece_moves_edge():
    """Test move generation at board edges."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[4][0] = PLAYER
    
    moves, jumps = get_piece_moves(board, 4, 0)
    
    expected_moves = [(3, 1)]  # Can't go left (would be out of bounds)
    assert set(moves) == set(expected_moves)

# ============================================================================
# GET ALL MOVES TESTS
# ============================================================================

def test_get_all_moves_initial_board():
    """Test that all moves are found in initial board state."""
    board = create_board()
    
    all_moves, all_jumps = get_all_moves(board, is_player_piece)
    assert isinstance(all_moves, list)
    assert isinstance(all_jumps, list)
    assert len(all_moves) > 0
    assert len(all_jumps) == 0  # No jumps possible initially
    
    all_moves_c, all_jumps_c = get_all_moves(board, is_computer_piece)
    assert isinstance(all_moves_c, list)
    assert isinstance(all_jumps_c, list)
    assert len(all_moves_c) > 0
    assert len(all_jumps_c) == 0

def test_get_all_moves_empty_board():
    """Test that no moves are found on empty board."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    
    all_moves, all_jumps = get_all_moves(board, is_player_piece)
    assert all_moves == []
    assert all_jumps == []

def test_get_all_moves_forced_jump():
    """Test that jumps are detected when available."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[4][3] = PLAYER
    board[3][2] = COMPUTER
    
    all_moves, all_jumps = get_all_moves(board, is_player_piece)
    assert len(all_jumps) > 0

# ============================================================================
# MOVE EXECUTION TESTS
# ============================================================================

def test_make_move_simple_player():
    """Test simple player move execution."""
    board = create_board()
    # Find a player piece at the bottom (darker squares have odd r+c)
    r1, c1 = 5, 0  # (5+0) = 5, odd → player piece
    r2, c2 = 4, 1  # target square
    
    became_king = make_move(board, r1, c1, r2, c2)
    
    assert board[r2][c2] == PLAYER
    assert board[r1][c1] == EMPTY
    assert became_king == False

def test_make_move_simple_computer():
    """Test simple computer move execution."""
    board = create_board()
    r1, c1 = 2, 1
    r2, c2 = 3, 0
    
    became_king = make_move(board, r1, c1, r2, c2)
    
    assert board[r2][c2] == COMPUTER
    assert board[r1][c1] == EMPTY
    assert became_king == False

def test_make_move_player_king_backward():
    """Test that player king can move backward."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[3][3] = PLAYER_KING
    
    became_king = make_move(board, 3, 3, 4, 4)
    
    assert board[4][4] == PLAYER_KING
    assert board[3][3] == EMPTY
    assert became_king == False

def test_make_move_player_becomes_king():
    """Test player piece becoming king."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[1][0] = PLAYER
    
    became_king = make_move(board, 1, 0, 0, 1)
    
    assert board[0][1] == PLAYER_KING
    assert board[1][0] == EMPTY
    assert became_king == True

def test_make_move_computer_becomes_king():
    """Test computer piece becoming king."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[6][0] = COMPUTER
    
    became_king = make_move(board, 6, 0, 7, 1)
    
    assert board[7][1] == COMPUTER_KING
    assert board[6][0] == EMPTY
    assert became_king == True

def test_make_move_jump_capture():
    """Test jump move captures opponent piece."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[3][2] = PLAYER
    board[2][3] = COMPUTER
    board[1][4] = EMPTY
    
    became_king = make_move(board, 3, 2, 1, 4)
    
    assert board[1][4] == PLAYER
    assert board[3][2] == EMPTY
    assert board[2][3] == EMPTY  # Captured piece removed
    assert became_king == False

def test_make_move_jump_to_king_row():
    """Test jumping to king row."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[2][1] = COMPUTER
    board[3][2] = PLAYER
    
    # Move from (3,2) to (1,0) - capturing (2,1)
    # But player gets crowned at row 0, so we need to reach row 0
    # Let's move closer to row 0
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[1][1] = COMPUTER
    board[2][2] = PLAYER
    
    became_king = make_move(board, 2, 2, 0, 0)
    
    assert board[0][0] == PLAYER_KING
    assert board[1][1] == EMPTY  # Captured piece
    assert became_king == True

def test_make_move_preserves_other_pieces():
    """Test that making a move doesn't affect other pieces."""
    board = create_board()
    original_board = [row[:] for row in board]
    
    r1, c1 = 5, 1
    r2, c2 = 4, 0
    make_move(board, r1, c1, r2, c2)
    
    # Check that all other pieces are unchanged
    for r in range(SIZE):
        for c in range(SIZE):
            if not ((r == r1 and c == c1) or (r == r2 and c == c2)):
                assert board[r][c] == original_board[r][c]

# ============================================================================
# GAME STATE TESTS
# ============================================================================

def test_has_piece_player():
    """Test piece detection for player."""
    board = create_board()
    assert has_piece(board, is_player_piece)
    
    # Remove all player pieces
    for r in range(SIZE):
        for c in range(SIZE):
            if is_player_piece(board[r][c]):
                board[r][c] = EMPTY
    
    assert not has_piece(board, is_player_piece)

def test_has_piece_computer():
    """Test piece detection for computer."""
    board = create_board()
    assert has_piece(board, is_computer_piece)
    
    # Remove all computer pieces
    for r in range(SIZE):
        for c in range(SIZE):
            if is_computer_piece(board[r][c]):
                board[r][c] = EMPTY
    
    assert not has_piece(board, is_computer_piece)

def test_has_any_moves_initial():
    """Test that both sides have moves in initial state."""
    board = create_board()
    assert has_any_moves(board, is_player_piece)
    assert has_any_moves(board, is_computer_piece)

def test_has_any_moves_no_pieces():
    """Test that side with no pieces has no moves."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    assert not has_any_moves(board, is_player_piece)
    assert not has_any_moves(board, is_computer_piece)

def test_has_any_moves_piece_boxed_in():
    """Test detection of side with pieces but no valid moves."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    # Place a single player piece in the corner surrounded by computer pieces
    board[1][1] = PLAYER
    board[0][0] = COMPUTER
    board[0][2] = COMPUTER
    board[2][0] = COMPUTER
    board[2][2] = COMPUTER
    
    # This piece should have no valid moves
    assert not has_any_moves(board, is_player_piece)

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_game_flow_player_move_then_computer():
    """Test a sequence of player and computer moves."""
    board = create_board()
    
    # Make a player move
    player_moves, _ = get_all_moves(board, is_player_piece)
    if player_moves:
        r1, c1, r2, c2 = player_moves[0]
        make_move(board, r1, c1, r2, c2)
        
        # Verify computer can still move
        computer_moves, _ = get_all_moves(board, is_computer_piece)
        assert len(computer_moves) > 0

def test_multiple_moves_sequence():
    """Test multiple moves in sequence."""
    board = create_board()
    initial_player_count = sum(1 for r in board for cell in r if is_player_piece(cell))
    
    # Make several moves
    for _ in range(5):
        player_moves, _ = get_all_moves(board, is_player_piece)
        if player_moves:
            r1, c1, r2, c2 = player_moves[0]
            make_move(board, r1, c1, r2, c2)
        
        computer_moves, _ = get_all_moves(board, is_computer_piece)
        if computer_moves:
            r1, c1, r2, c2 = computer_moves[0]
            make_move(board, r1, c1, r2, c2)
    
    # Still should have pieces
    final_player_count = sum(1 for r in board for cell in r if is_player_piece(cell))
    assert final_player_count <= initial_player_count

def test_win_condition_no_opponent_pieces():
    """Test win condition when opponent has no pieces."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[4][3] = PLAYER
    
    # Computer has no pieces
    assert not has_piece(board, is_computer_piece)

def test_win_condition_no_opponent_moves():
    """Test win condition when opponent has no legal moves."""
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    # Computer piece boxed in - it can only move down and can't jump
    # Place computer piece with no empty squares below it
    board[6][3] = COMPUTER
    board[7][2] = PLAYER  # Block down-left
    board[7][4] = PLAYER  # Block down-right
    # Row 7 is the king row, and there are no squares at row 8
    
    assert has_piece(board, is_computer_piece)
    # Computer at (6,3) would try to move to (7,2) or (7,4) but both are blocked
    moves, jumps = get_all_moves(board, is_computer_piece)
    assert len(moves) == 0 and len(jumps) == 0
