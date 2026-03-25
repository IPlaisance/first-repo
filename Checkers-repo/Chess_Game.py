import tkinter as tk
import copy
import random

TILE_SIZE = 70

# ♟️ Emoji pieces instead of labels to make it visually easier 
PIECES = {
    "wK": "♔", "wQ": "♕", "wR": "♖", "wB": "♗", "wN": "♘", "wP": "♙",
    "bK": "♚", "bQ": "♛", "bR": "♜", "bB": "♝", "bN": "♞", "bP": "♟"
}

# ---------------- GAME LOGIC ----------------
class ChessGame:
    def __init__(self):
        self.board = self.create_board()
        self.turn = "w"
        self.selected = None
        self.en_passant = None
        self.castling = {"wK": True, "wQ": True, "bK": True, "bQ": True}

    def create_board(self):
        return [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bP"]*8,
            ["."]*8,
            ["."]*8,
            ["."]*8,
            ["."]*8,
            ["wP"]*8,
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
        ]

    def in_bounds(self,r,c):
        return 0<=r<8 and 0<=c<8

    # ---------- MOVE GENERATION ---------- 
    # player can just select their piece and move it when their turn, 
    # each piece is labeled and has their own rules and will suggest what moves are available once selected 
    def get_all_moves(self,color):
        moves=[]
        for r in range(8):
            for c in range(8):
                if self.board[r][c].startswith(color):
                    for m in self.get_moves(r,c):
                        moves.append((r,c,*m))
        return moves

    def get_moves(self,r,c):
        piece=self.board[r][c]
        if piece==".":
            return []
        color=piece[0]
        p=piece[1]

        if p=="P": return self.pawn(r,c,color)
        if p=="R": return self.slide(r,c,color,[(1,0),(-1,0),(0,1),(0,-1)])
        if p=="B": return self.slide(r,c,color,[(1,1),(1,-1),(-1,1),(-1,-1)])
        if p=="Q": return self.slide(r,c,color,[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)])
        if p=="N": return self.knight(r,c,color)
        if p=="K": return self.king(r,c,color)

    def pawn(self,r,c,color):
        moves=[]
        d=-1 if color=="w" else 1
        start=6 if color=="w" else 1

        if self.board[r+d][c]==".":
            moves.append((r+d,c))
            if r==start and self.board[r+2*d][c]==".":
                moves.append((r+2*d,c))

        for dc in [-1,1]:
            nr,nc=r+d,c+dc
            if self.in_bounds(nr,nc):
                if self.board[nr][nc]!="." and self.board[nr][nc][0]!=color:
                    moves.append((nr,nc))

        if self.en_passant:
            if (r+d,c-1)==self.en_passant or (r+d,c+1)==self.en_passant:
                moves.append(self.en_passant)

        return moves

    def knight(self,r,c,color):
        moves=[]
        for dr,dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            nr,nc=r+dr,c+dc
            if self.in_bounds(nr,nc):
                if self.board[nr][nc]=="." or self.board[nr][nc][0]!=color:
                    moves.append((nr,nc))
        return moves

    def king(self,r,c,color):
        moves=[]
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr==0 and dc==0: continue
                nr,nc=r+dr,c+dc
                if self.in_bounds(nr,nc):
                    if self.board[nr][nc]=="." or self.board[nr][nc][0]!=color:
                        moves.append((nr,nc))

        # castling
        if color=="w" and r==7:
            if self.castling["wK"] and self.board[7][5]=="." and self.board[7][6]==".":
                moves.append((7,6))
            if self.castling["wQ"] and self.board[7][1]=="." and self.board[7][2]=="." and self.board[7][3]==".":
                moves.append((7,2))
        if color=="b" and r==0:
            if self.castling["bK"] and self.board[0][5]=="." and self.board[0][6]==".":
                moves.append((0,6))
            if self.castling["bQ"] and self.board[0][1]=="." and self.board[0][2]=="." and self.board[0][3]==".":
                moves.append((0,2))

        return moves

    def slide(self,r,c,color,dirs):
        moves=[]
        for dr,dc in dirs:
            nr,nc=r+dr,c+dc
            while self.in_bounds(nr,nc):
                if self.board[nr][nc]==".":
                    moves.append((nr,nc))
                else:
                    if self.board[nr][nc][0]!=color:
                        moves.append((nr,nc))
                    break
                nr+=dr; nc+=dc
        return moves

    # ---------- CHECK ----------
    def is_in_check(self,color):
        king=None
        for r in range(8):
            for c in range(8):
                if self.board[r][c]==color+"K":
                    king=(r,c)

        enemy="b" if color=="w" else "w"
        for r in range(8):
            for c in range(8):
                if self.board[r][c].startswith(enemy):
                    if king in self.get_moves(r,c):
                        return True
        return False

    def is_checkmate(self,color):
        return self.is_in_check(color) and len(self.legal_moves(color))==0

    def is_stalemate(self,color):
        return not self.is_in_check(color) and len(self.legal_moves(color))==0

    def legal_moves(self,color):
        moves=[]
        for m in self.get_all_moves(color):
            new=copy.deepcopy(self)
            new.make_move(*m)
            if not new.is_in_check(color):
                moves.append(m)
        return moves

    # ---------- MOVE ----------
    def make_move(self,r1,c1,r2,c2):
        piece=self.board[r1][c1]

        # en passant
        if piece[1]=="P" and (r2,c2)==self.en_passant:
            if piece[0]=="w": self.board[r2+1][c2]="."
            else: self.board[r2-1][c2]="."

        self.en_passant=None
        if piece[1]=="P" and abs(r2-r1)==2:
            self.en_passant=((r1+r2)//2,c1)

        # castling
        if piece[1]=="K":
            if piece[0]=="w":
                self.castling["wK"]=False
                self.castling["wQ"]=False
            else:
                self.castling["bK"]=False
                self.castling["bQ"]=False

            if abs(c2-c1)==2:
                if c2==6:
                    self.board[r2][5]=self.board[r2][7]
                    self.board[r2][7]="."
                else:
                    self.board[r2][3]=self.board[r2][0]
                    self.board[r2][0]="."

        # promotion
        if piece=="wP" and r2==0: piece="wQ"
        if piece=="bP" and r2==7: piece="bQ"

        self.board[r2][c2]=piece
        self.board[r1][c1]="."
        self.turn="b" if self.turn=="w" else "w"

# ---------- AI ----------this is random and not at set diffculty (bc i barely play chess and don't want it to be super hard or a long game)
def ai_move(game):
    moves = game.legal_moves("b")
    return random.choice(moves) if moves else None

# ---------------- GUI ----------------to make the board and game more visually easy  
class ChessGUI:
    def __init__(self, root):
        self.game = ChessGame()
        self.root = root
        self.canvas = tk.Canvas(root, width=560, height=600)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.click)
        self.status = "White to move"
        self.draw()

    def draw(self):
        self.canvas.delete("all")

        for r in range(8):
            for c in range(8):

                color = "#f0d9b5" if (r+c)%2==0 else "#b58863"

                # highlight selected square
                if self.game.selected == (r,c):
                    color = "#f7ec59"

                # highlight king if in check
                piece = self.game.board[r][c]
                if piece.endswith("K"):
                    if self.game.is_in_check(piece[0]):
                        color = "#ff4d4d"

                self.canvas.create_rectangle(
                    c*70, r*70, (c+1)*70, (r+1)*70,
                    fill=color
                )

                if piece != ".":
                    self.canvas.create_text(
                        c*70+35, r*70+35,
                        text=PIECES[piece],
                        font=("Arial", 32)
                    )

        # show legal moves
        if self.game.selected:
            r,c = self.game.selected
            for move in self.game.legal_moves("w"):
                if move[0]==r and move[1]==c:
                    _,_,mr,mc = move
                    self.canvas.create_oval(
                        mc*70+25, mr*70+25,
                        mc*70+45, mr*70+45,
                        fill="black"
                    )

        # status text
        self.canvas.create_text(
            280, 580,
            text=self.status,
            font=("Arial", 16)
        )

    def click(self, event):
        r = event.y // 70
        c = event.x // 70

        if self.game.turn != "w":
            return

        if self.game.selected:
            r1,c1 = self.game.selected

            if (r1,c1,r,c) in self.game.legal_moves("w"):
                self.game.make_move(r1,c1,r,c)

                # after player move
                if self.game.is_checkmate("b"):
                    self.status = "Checkmate! You win!"
                    self.draw()
                    return
                elif self.game.is_stalemate("b"):
                    self.status = "Stalemate!"
                    self.draw()
                    return
                elif self.game.is_in_check("b"):
                    self.status = "Black is in Check!"
                else:
                    self.status = "Black to move"

                self.draw()

                # AI move
                if self.game.turn == "b":
                    move = ai_move(self.game)
                    if move:
                        self.game.make_move(*move)

                        if self.game.is_checkmate("w"):
                            self.status = "Checkmate! Computer wins!"
                            self.draw()
                            return
                        elif self.game.is_stalemate("w"):
                            self.status = "Stalemate!"
                            self.draw()
                            return
                        elif self.game.is_in_check("w"):
                            self.status = "White is in Check!"
                        else:
                            self.status = "White to move"

            self.game.selected = None
        else:
            if self.game.board[r][c].startswith("w"):
                self.game.selected = (r,c)

        self.draw()

# ---------- RUN ----------
root = tk.Tk()
root.title("Chess ♟️")
ChessGUI(root)
root.mainloop()
