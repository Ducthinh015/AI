from enum import IntEnum
from copy import deepcopy
from typing import List, Tuple, Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel



class Piece(IntEnum):
    """Board cell values to make the code self‑describing."""

    EMPTY = 0
    PLAYER_MAN = 1   
    PLAYER_KING = 2 
    AI_MAN = -1     
    AI_KING = -2     
    @property
    def is_player(self) -> bool:
        return self.value > 0

    @property
    def is_ai(self) -> bool:
        return self.value < 0

    @property
    def is_man(self) -> bool:
        return abs(self.value) == 1

    @property
    def is_king(self) -> bool:
        return abs(self.value) == 2


MoveSeq = List[Tuple[int, int]]  

class Move(BaseModel):
    board: List[List[int]]
    move: MoveSeq 



class GameState:
    """Holds the canonical board and implements all game mechanics."""

    BOARD_SIZE = 8
    PLAYER_DIR = -1 
    AI_DIR = 1       

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.board: List[List[int]] = self._init_board()
        self.turn: int = 1  
        self.history: List[List[List[int]]] = []

    @staticmethod
    def _init_board() -> List[List[int]]:
        board = [[Piece.EMPTY.value for _ in range(GameState.BOARD_SIZE)]
                 for _ in range(GameState.BOARD_SIZE)]
        # Place AI pieces (top)
        for r in range(3):
            for c in range(GameState.BOARD_SIZE):
                if (r + c) % 2 == 1:
                    board[r][c] = Piece.AI_MAN.value
        # Place player pieces (bottom)
        for r in range(5, 8):
            for c in range(GameState.BOARD_SIZE):
                if (r + c) % 2 == 1:
                    board[r][c] = Piece.PLAYER_MAN.value
        return board

    def _on_board(self, r: int, c: int) -> bool:
        return 0 <= r < self.BOARD_SIZE and 0 <= c < self.BOARD_SIZE

    def _piece_at(self, r: int, c: int) -> Piece:
        return Piece(self.board[r][c])

    def _directions_for(self, piece: Piece) -> List[Tuple[int, int]]:
        """Returns movement directions allowed for the piece."""
        if piece.is_king:
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        dir_ = self.PLAYER_DIR if piece.is_player else self.AI_DIR
        return [(dir_, -1), (dir_, 1)]

    def get_valid_moves(self, r: int, c: int) -> List[MoveSeq]:
        piece = self._piece_at(r, c)
        if piece == Piece.EMPTY or (self.turn == 1 and piece.is_ai) or (self.turn == -1 and piece.is_player):
            return []

        captures = self._capture_sequences_from(r, c, piece)
        if captures:
            return captures  
        return self._simple_moves_from(r, c, piece)

    def _simple_moves_from(self, r: int, c: int, piece: Piece) -> List[MoveSeq]:
        moves: List[MoveSeq] = []
        for dr, dc in self._directions_for(piece):
            nr, nc = r + dr, c + dc
            if self._on_board(nr, nc) and self._piece_at(nr, nc) == Piece.EMPTY:
                moves.append([(r, c), (nr, nc)])
        return moves

    def _capture_sequences_from(self, r: int, c: int, piece: Piece, visited: Optional[set] = None) -> List[MoveSeq]:
        if visited is None:
            visited = set()
        sequences: List[MoveSeq] = []
        for dr, dc in self._directions_for(piece):
            mid_r, mid_c = r + dr, c + dc
            end_r, end_c = r + 2 * dr, c + 2 * dc
            if not (self._on_board(end_r, end_c)):
                continue
            mid_piece = self._piece_at(mid_r, mid_c)
            if mid_piece == Piece.EMPTY or (mid_piece.is_player == piece.is_player):
                continue  
            if self._piece_at(end_r, end_c) != Piece.EMPTY:
                continue  

            board_copy = deepcopy(self.board)
            board_copy[end_r][end_c] = board_copy[r][c]
            board_copy[r][c] = Piece.EMPTY.value
            board_copy[mid_r][mid_c] = Piece.EMPTY.value

            nested_state = GameState()
            nested_state.board = board_copy
            nested_state.turn = self.turn  
            further_jumps = nested_state._capture_sequences_from(end_r, end_c, piece, visited | {(r, c)})

            if further_jumps:
                for seq in further_jumps:
                    sequences.append([(r, c)] + seq)
            else:
                sequences.append([(r, c), (end_r, end_c)])
        return sequences

    def apply_move_sequence(self, seq: MoveSeq) -> None:
        """Apply a simple move or multi‑jump sequence to the board."""
        self.history.append(deepcopy(self.board))
        for i in range(len(seq) - 1):
            r1, c1 = seq[i]
            r2, c2 = seq[i + 1]
            piece = self._piece_at(r1, c1)

            if abs(r2 - r1) == 2:
                mid_r, mid_c = (r1 + r2) // 2, (c1 + c2) // 2
                self.board[mid_r][mid_c] = Piece.EMPTY.value

            self.board[r1][c1] = Piece.EMPTY.value
            self.board[r2][c2] = piece.value

        final_r, final_c = seq[-1]
        final_piece = self._piece_at(final_r, final_c)
        if final_piece.is_man:
            if final_piece.is_player and final_r == 0:
                self.board[final_r][final_c] = Piece.PLAYER_KING.value
            elif final_piece.is_ai and final_r == self.BOARD_SIZE - 1:
                self.board[final_r][final_c] = Piece.AI_KING.value

        self.turn *= -1

    def undo(self) -> None:
        if self.history:
            self.board = self.history.pop()
            self.turn *= -1

   def status(self) -> str:
        player_pieces = sum(cell > 0 for row in self.board for cell in row)
        ai_pieces = sum(cell < 0 for row in self.board for cell in row)
        if player_pieces == 0:
            return "AI wins"
        if ai_pieces == 0:
            return "Player wins"
        return "In progress"

    def best_ai_move(self, depth: int = 4) -> MoveSeq:
        """Return the best move sequence for the AI using minimax + alpha‑beta pruning."""

        def evaluate(board: List[List[int]]) -> int:
            score = 0
            for row in board:
                for val in row:
                    piece = Piece(val)
                    if piece == Piece.EMPTY:
                        continue
                    factor = 1 if piece.is_ai else -1
                    base = 5 if piece.is_king else 3
                    score += factor * base
            return score

        def minimax(state: 'GameState', depth_left: int, alpha: int, beta: int) -> Tuple[int, Optional[MoveSeq]]:
            term = state.status()
            if depth_left == 0 or term != "In progress":
                return evaluate(state.board), None

            best_move_local: Optional[MoveSeq] = None

            if state.turn == -1:  
                max_eval = -float('inf')
                for move in state._all_moves_for_turn():
                    child = deepcopy(state)
                    child.apply_move_sequence(move)
                    eval_, _ = minimax(child, depth_left - 1, alpha, beta)
                    if eval_ > max_eval:
                        max_eval, best_move_local = eval_, move
                    alpha = max(alpha, eval_)
                    if beta <= alpha:
                        break
                return max_eval, best_move_local
            else:  
                min_eval = float('inf')
                for move in state._all_moves_for_turn():
                    child = deepcopy(state)
                    child.apply_move_sequence(move)
                    eval_, _ = minimax(child, depth_left - 1, alpha, beta)
                    if eval_ < min_eval:
                        min_eval = eval_
                    beta = min(beta, eval_)
                    if beta <= alpha:
                        break
                return min_eval, None

        _, best = minimax(self, depth, -float('inf'), float('inf'))
        if best is None:
            return []  
        return best

    def _all_moves_for_turn(self) -> List[MoveSeq]:
        moves: List[MoveSeq] = []
        captures_exist = False
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE):
                piece = self._piece_at(r, c)
                if piece == Piece.EMPTY:
                    continue
                if (self.turn == 1 and piece.is_player) or (self.turn == -1 and piece.is_ai):
                    cell_moves = self._capture_sequences_from(r, c, piece)
                    if cell_moves:
                        captures_exist = True
                        moves.extend(cell_moves)
        if captures_exist:
            return moves 
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE):
                piece = self._piece_at(r, c)
                if piece == Piece.EMPTY:
                    continue
                if (self.turn == 1 and piece.is_player) or (self.turn == -1 and piece.is_ai):
                    moves.extend(self._simple_moves_from(r, c, piece))
        return moves



app = FastAPI()

game = GameState()


class BoardOnly(BaseModel):
    board: List[List[int]]


@app.get("/init")
def init_game():
    game.reset()
    return {"board": game.board, "turn": game.turn}


@app.post("/move")
def make_move(data: Move):
    game.board = data.board
    game.apply_move_sequence(data.move)
    return {
        "board": game.board,
        "player_move": data.move,
        "turn": game.turn,
    }


@app.post("/ai-move")
def ai_move(data: BoardOnly, depth: int = Query(4, ge=1, le=8)):
    """Compute and apply the best AI move, returning the updated board and move sequence."""
    game.board = data.board
    game.turn = -1  
    best_seq = game.best_ai_move(depth)
    if best_seq:
        game.apply_move_sequence(best_seq)
    return {
        "board": game.board,
        "ai_move": best_seq,
        "turn": game.turn,
    }


@app.post("/reset")
def reset_game():
    game.reset()
    return {"message": "Game reset", "board": game.board, "turn": game.turn}


@app.get("/valid-moves")
def get_valid_moves(row: int = Query(...), col: int = Query(...)):
    return {"valid_moves": game.get_valid_moves(row, col)}


@app.get("/status")
def get_status():
    return {"status": game.status()}


@app.post("/undo")
def undo_move():
    game.undo()
    return {"board": game.board, "turn": game.turn}
