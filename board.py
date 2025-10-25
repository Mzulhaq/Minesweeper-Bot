import random
from typing import List, Tuple, Optional

import numpy as np


class MinesweeperBoard:
    """
    Pure logic Minesweeper board (no pygame).

    Attributes
    - board: int32 (H,W), -1 for mine else 0..8
    - revealed: bool (H,W)
    - flagged: bool (H,W)
    - game_over: bool
    - won: bool

    API
    - reset()
    - reveal(r,c): reveal cell, handles first-click-safe and flood fill
    - toggle_flag(r,c)
    - neighbors(r,c) -> List[(nr,nc)]
    - counts around cell: flagged_count, unrevealed_unflagged
    """

    def __init__(self, width: int = 9, height: int = 9, num_mines: int = 10) -> None:
        self.width = width
        self.height = height
        self.num_mines = num_mines

        self.board: np.ndarray
        self.revealed: np.ndarray
        self.flagged: np.ndarray
        self.first_click_done: bool
        self.game_over: bool
        self.won: bool

        self.reset()

    # ---------------- core ----------------
    def reset(self) -> None:
        self.board = np.zeros((self.height, self.width), dtype=np.int32)
        self.revealed = np.zeros((self.height, self.width), dtype=bool)
        self.flagged = np.zeros((self.height, self.width), dtype=bool)
        self.first_click_done = False
        self.game_over = False
        self.won = False

    def neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        nbrs = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    nbrs.append((nr, nc))
        return nbrs

    def _place_mines_safe(self, sr: int, sc: int) -> None:
        cells = [(r, c) for r in range(self.height) for c in range(self.width) if (r, c) != (sr, sc)]
        mines = random.sample(cells, k=min(self.num_mines, len(cells)))
        for r, c in mines:
            self.board[r, c] = -1

        # fill numbers
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r, c] == -1:
                    continue
                cnt = 0
                for nr, nc in self.neighbors(r, c):
                    if self.board[nr, nc] == -1:
                        cnt += 1
                self.board[r, c] = cnt

    def _flood_reveal(self, r: int, c: int) -> None:
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if self.revealed[cr, cc] or self.flagged[cr, cc]:
                continue
            self.revealed[cr, cc] = True
            if self.board[cr, cc] == 0:
                for nr, nc in self.neighbors(cr, cc):
                    if not self.revealed[nr, nc] and not self.flagged[nr, nc]:
                        stack.append((nr, nc))

    def _all_safe_revealed(self) -> bool:
        mask_safe = self.board != -1
        return bool(np.all(self.revealed[mask_safe]))

    def reveal(self, r: int, c: int) -> None:
        if self.game_over or self.flagged[r, c] or self.revealed[r, c]:
            return

        if not self.first_click_done:
            self._place_mines_safe(r, c)
            self.first_click_done = True

        if self.board[r, c] == -1:
            self.revealed[r, c] = True
            self.game_over = True
            self.won = False
            # show all mines for clarity
            self.revealed[self.board == -1] = True
            return

        self._flood_reveal(r, c)
        if self._all_safe_revealed():
            self.game_over = True
            self.won = True

    def toggle_flag(self, r: int, c: int) -> None:
        if self.game_over or self.revealed[r, c]:
            return
        self.flagged[r, c] = not self.flagged[r, c]

    # --------------- helpers for rules ---------------
    def adjacent_counts(self, r: int, c: int) -> Tuple[int, int]:
        """Return (n_flagged, n_unrevealed_unflagged) around (r,c)."""
        nbrs = self.neighbors(r, c)
        n_flagged = sum(1 for nr, nc in nbrs if self.flagged[nr, nc])
        n_unrev_unflag = sum(1 for nr, nc in nbrs if (not self.revealed[nr, nc] and not self.flagged[nr, nc]))
        return n_flagged, n_unrev_unflag

    def observation(self) -> np.ndarray:
        """(H,W,3) int32: [revealed(0/1), value(-1..8, masked to 0 if hidden), flagged(0/1)]."""
        obs = np.zeros((self.height, self.width, 3), dtype=np.int32)
        obs[:, :, 0] = self.revealed.astype(np.int32)
        obs[:, :, 1] = np.where(self.revealed, self.board, 0).astype(np.int32)
        obs[:, :, 2] = self.flagged.astype(np.int32)
        return obs

    def bombs_remaining(self) -> int:
        """Return how many mines are left to find based on flags placed."""
        return int(self.num_mines - int(self.flagged.sum()))
