from copy import deepcopy

EMPTY, P1, P2, P1_KING, P2_KING = 0, 1, 2, 3, 4
DIAGS = {
    P1:      [(-1,-1),(-1,1)],
    P2:      [(1,-1),(1,1)],
    P1_KING: [(-1,-1),(-1,1),(1,-1),(1,1)],
    P2_KING: [(-1,-1),(-1,1),(1,-1),(1,1)],
}

class DraughtsGame:
    def __init__(self):
        self.board = []

    def init_board(self):
        b = [[EMPTY]*8 for _ in range(8)]
        for r in range(3):
            for c in range(8):
                if (r+c)%2==1: b[r][c] = P2
        for r in range(5,8):
            for c in range(8):
                if (r+c)%2==1: b[r][c] = P1
        self.board = b
        return deepcopy(self.board)

    def get_valid_moves(self, position):
        r0,c0 = map(int, position.split(','))
        piece = self.board[r0][c0]
        if piece not in DIAGS: 
            return {"simple":[], "jumps":[]}
        moves = {"simple":[], "jumps":[]}
        # Simple moves
        for dr,dc in DIAGS[piece]:
            r1,c1 = r0+dr, c0+dc
            if 0<=r1<8 and 0<=c1<8 and self.board[r1][c1]==EMPTY:
                moves["simple"].append((r1,c1))
        # Jumps (multi-jump recursion)
        def find_jumps(r,c,b,path,vis):
            found=False
            for dr,dc in DIAGS[piece]:
                rm,cm, r2,c2 = r+dr, c+dc, r+2*dr, c+2*dc
                if all(0<=x<8 for x in (rm,cm,r2,c2)) \
                  and b[rm][cm] not in (EMPTY,piece,piece+2) \
                  and b[r2][c2]==EMPTY and (rm,cm,r2,c2) not in vis:
                    nb = deepcopy(b)
                    nb[r][c],nb[rm][cm],nb[r2][c2] = EMPTY,EMPTY,piece
                    npth = path+[(r2,c2)]
                    nvis = vis|{(rm,cm,r2,c2)}
                    more = find_jumps(r2,c2,nb,npth,nvis)
                    if not more: moves["jumps"].append(npth)
                    found=True
            return found
        find_jumps(r0,c0,self.board,[],set())
        return moves

    
    def make_move(self, from_pos, to_pos):
        try:
            r0, c0 = map(int, from_pos.split(','))
            r1, c1 = map(int, to_pos.split(','))
        except (ValueError, AttributeError):
            return {"error": "Vị trí không hợp lệ. Định dạng đúng là 'row,col'."}

        if not all(0 <= x < 8 for x in (r0, c0, r1, c1)):
            return {"error": "Vị trí ngoài phạm vi bảng."}

        piece = self.board[r0][c0]
        if piece == EMPTY:
            return {"error": "Không có quân cờ tại vị trí xuất phát."}

        dr, dc = r1 - r0, c1 - c0
        # Capture?
        if abs(dr) == 2 and abs(dc) == 2:
            rm, cm = r0 + dr // 2, c0 + dc // 2
            self.board[rm][cm] = EMPTY
        # Move & crown
        self.board[r0][c0], self.board[r1][c1] = EMPTY, piece
        if piece == P1 and r1 == 0:
            self.board[r1][c1] = P1_KING
        if piece == P2 and r1 == 7:
            self.board[r1][c1] = P2_KING
        return {"board": deepcopy(self.board), "status": "ok"}
