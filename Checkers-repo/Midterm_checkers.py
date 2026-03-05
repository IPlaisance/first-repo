import random
import time

EMPTY = "."
PLAYER = "P"
PLAYER_KING = "PK"
COMPUTER = "C"
COMPUTER_KING = "CK"
SIZE = 8

turn_clock = 0
start_time = time.time()
TURN_TIME_LIMIT = 30  # seconds per turn


player_special_move = False
computer_special_move = False

last_computer_move = None


# ---------------- BOARD ----------------

def create_board():
    board = [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

    for r in range(3):
        for c in range(SIZE):
            if (r + c) % 2 == 1:
                board[r][c] = COMPUTER

    for r in range(5, 8):
        for c in range(SIZE):
            if (r + c) % 2 == 1:
                board[r][c] = PLAYER

    return board


def print_board(board, selected_piece=None):
    elapsed = int(time.time() - start_time)

    print(f"\nTurn: {turn_clock} | Time: {elapsed}s")
    print("     a   b   c   d   e   f   g   h")

    for r in range(SIZE):
        row_str = f"{r} "
        for c in range(SIZE):
            cell = board[r][c]

            if last_computer_move == (r, c):
                cell = f"*{cell}"

            if selected_piece == (r, c):
                cell = f"[{cell}]"

            row_str += f"{cell:>4}"
        print(row_str)

    print("     a   b   c   d   e   f   g   h\n")


# ---------------- HELPERS ----------------

def in_bounds(r, c):
    return 0 <= r < SIZE and 0 <= c < SIZE


def coord_to_index(coord):
    col = ord(coord[0].lower()) - ord('a')
    row = int(coord[1])
    return row, col


def index_to_coord(r, c):
    return chr(ord('a') + c) + str(r)


def is_player_piece(p):
    return p in (PLAYER, PLAYER_KING)


def is_computer_piece(p):
    return p in (COMPUTER, COMPUTER_KING)


def is_king(p):
    return p in (PLAYER_KING, COMPUTER_KING)


# ---------------- MOVE GENERATION ----------------

def get_piece_moves(board, r, c):
    piece = board[r][c]
    if piece == EMPTY:
        return [], []

    moves = []
    jumps = []

    if piece in (PLAYER, PLAYER_KING):
        dirs = [(-1,-1),(-1,1)]
        if is_king(piece):
            dirs += [(1,-1),(1,1)]
        opponent_check = is_computer_piece
    else:
        dirs = [(1,-1),(1,1)]
        if is_king(piece):
            dirs += [(-1,-1),(-1,1)]
        opponent_check = is_player_piece

    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        jr, jc = r + 2*dr, c + 2*dc

        if in_bounds(nr, nc) and board[nr][nc] == EMPTY:
            moves.append((nr, nc))

        if (in_bounds(jr, jc) and
            in_bounds(nr, nc) and
            opponent_check(board[nr][nc]) and
            board[jr][jc] == EMPTY):
            jumps.append((jr, jc))

    return moves, jumps


def get_all_moves(board, piece_check):
    all_moves = []
    all_jumps = []

    for r in range(SIZE):
        for c in range(SIZE):
            if piece_check(board[r][c]):
                moves, jumps = get_piece_moves(board, r, c)
                for m in moves:
                    all_moves.append((r,c,m[0],m[1]))
                for j in jumps:
                    all_jumps.append((r,c,j[0],j[1]))

    return all_moves, all_jumps


# ---------------- MOVE EXECUTION ----------------

def make_move(board, r1, c1, r2, c2):
    piece = board[r1][c1]
    board[r2][c2] = piece
    board[r1][c1] = EMPTY

    if abs(r2 - r1) == 2:
        board[(r1+r2)//2][(c1+c2)//2] = EMPTY

    became_king = False

    if piece == PLAYER and r2 == 0:
        board[r2][c2] = PLAYER_KING
        became_king = True

    if piece == COMPUTER and r2 == SIZE - 1:
        board[r2][c2] = COMPUTER_KING
        became_king = True

    return became_king


# ---------------- KING POWER ----------------

def get_all_positions(board, check_func):
    return [(r,c) for r in range(SIZE) for c in range(SIZE) if check_func(board[r][c])]


def get_single_moves_any(board, r, c):
    out = []
    for dr,dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
        nr, nc = r+dr, c+dc
        if in_bounds(nr,nc) and board[nr][nc] == EMPTY:
            out.append((nr,nc))
    return out


def player_move_opponent_piece(board):
    print("⭐ KING POWER: Move opponent piece")
    opp = get_all_positions(board, is_computer_piece)

    while True:
        print("Opponent pieces:", [index_to_coord(r,c) for r,c in opp])
        sel = input("Select opponent piece → ")
        r,c = coord_to_index(sel)

        if (r,c) not in opp:
            print("Invalid.")
            continue

        moves = get_single_moves_any(board,r,c)
        if not moves:
            print("That piece can't move.")
            continue

        print("Destinations:", [index_to_coord(m[0],m[1]) for m in moves])
        dst = input("Move to → ")
        nr,nc = coord_to_index(dst)

        if (nr,nc) not in moves:
            print("Invalid.")
            continue

        board[nr][nc] = board[r][c]
        board[r][c] = EMPTY
        break


def computer_move_opponent_piece(board):
    opp = get_all_positions(board, is_player_piece)
    random.shuffle(opp)

    for r,c in opp:
        moves = get_single_moves_any(board,r,c)
        if moves:
            nr,nc = random.choice(moves)
            board[nr][nc] = board[r][c]
            board[r][c] = EMPTY
            print("Computer used KING POWER")
            return


# ---------------- TURN FUNCTIONS ----------------

def player_turn(board):
    global player_special_move

    if player_special_move:
        player_move_opponent_piece(board)
        player_special_move = False
        return

    moves, jumps = get_all_moves(board, is_player_piece)

    while True:
        piece = input("Select piece → ")
        try:
            r,c = coord_to_index(piece)
        except:
            print("Bad input.")
            continue

        if not in_bounds(r,c) or not is_player_piece(board[r][c]):
            print("Not your piece.")
            continue

        pmoves, pjumps = get_piece_moves(board,r,c)

        if jumps:
            if not pjumps:
                print("You must jump.")
                continue
            choices = pjumps
        else:
            choices = pmoves + pjumps

        print_board(board, selected_piece=(r,c))

        if not choices:
            print("No moves.")
            continue

        print("Moves:", [index_to_coord(m[0],m[1]) for m in choices])

        dest = input("Move to → ")
        try:
            r2,c2 = coord_to_index(dest)
        except:
            print("Bad input.")
            continue

        if (r2,c2) not in choices:
            print("Invalid.")
            continue

        became_king = make_move(board,r,c,r2,c2)
        if became_king:
            player_special_move = True
        break
import threading

turn_skipped = False

def skip_turn():
    global turn_skipped
    turn_skipped = True
    print("\nTIME'S UP! Your turn is skipped.")

def player_turn(board):
    global turn_skipped, turn_clock

    turn_skipped = False
    timer = threading.Timer(30, skip_turn)  # 30-second timer
    timer.start()

    _, forced_jumps = get_all_moves(board, is_player_piece)

    while True:
        if turn_skipped:
            timer.cancel()
            return

        piece = input("Select piece → ")
        if turn_skipped:
            timer.cancel()
            return

        try:
            r, c = coord_to_index(piece)
        except:
            print("Invalid input")
            continue

        if not is_player_piece(board[r][c]):
            print("Not your piece.")
            continue

        moves, jumps = get_piece_moves(board, r, c)
        choices = jumps if forced_jumps else moves + jumps

        if not choices:
            print("No valid moves")
            continue

        print("Available moves:", [index_to_coord(m[0], m[1]) for m in choices])

        dest = input("Move to → ")
        if turn_skipped:
            timer.cancel()
            return

        try:
            r2, c2 = coord_to_index(dest)
        except:
            print("Invalid input")
            continue

        if (r2, c2) not in choices:
            print("Invalid move")
            continue

        became_king = make_move(board, r, c, r2, c2)
        if became_king:
            player_special_move = True
        break

    timer.cancel()

    became_king = make_move(board, r, c, r2, c2)
    if became_king:
        player_special_move = True
    

def computer_turn(board):
    global computer_special_move, last_computer_move

    if computer_special_move:
        computer_move_opponent_piece(board)
        computer_special_move = False
        return

    moves, jumps = get_all_moves(board, is_computer_piece)

    if jumps:
        move = random.choice(jumps)
    elif moves:
        move = random.choice(moves)
    else:
        return

    became_king = make_move(board,*move)
    last_computer_move = (move[2], move[3])

    if became_king:
        computer_special_move = True

    print("Computer moved.")


# ---------------- GAME END ----------------

def has_piece(board, check):
    return any(check(cell) for row in board for cell in row)


def has_any_moves(board, check):
    moves, jumps = get_all_moves(board, check)
    return bool(moves or jumps)


# ---------------- MAIN ----------------

def main():
    global turn_clock
    board = create_board()

    while True:
        print_board(board)

        if not has_piece(board, is_player_piece):
            print("COMPUTER WINS — you have no pieces left.")
            break

        if not has_piece(board, is_computer_piece):
            print("YOU WIN — COMPUTER has no pieces left.")
            break

        if not has_any_moves(board, is_player_piece):
            print("COMPUTER WINS — you have no legal moves.")
            break

        if not has_any_moves(board, is_computer_piece):
            print("YOU WIN — COMPUTER has no legal moves.")
            break

        player_turn(board)
        turn_clock += 1

        computer_turn(board)
        turn_clock += 1


if __name__ == "__main__":
    main()