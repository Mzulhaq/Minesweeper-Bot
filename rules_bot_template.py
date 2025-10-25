"""
Visual rules-engine demo (no Gym, no RL).

What it does
- Displays the Minesweeper grid using the same UI as the manual game
- Applies deterministic rules step-by-step and draws after each action
- When stuck, makes a simple random guess (replace with your probability logic)

Run:
  python rules_bot_template.py

Controls during demo:
- R: restart a new game
- Window close: exit
"""

import time
import random
import pygame

from board import MinesweeperBoard
from minesweeper import MinesweeperUI


# ---------------------- deterministic rules helpers ----------------------
def get_frontier_cells(board: MinesweeperBoard):
    """All revealed number cells (value > 0)."""
    return [
        (r, c)
        for r in range(board.height)
        for c in range(board.width)
        if board.revealed[r, c] and board.board[r, c] > 0
    ]


def find_one_flag_move(board: MinesweeperBoard):
    """Find one cell that must be a mine, return (r,c) to flag or None."""
    for r, c in get_frontier_cells(board):
        N = board.board[r, c]
        n_flagged, n_unrev_unflag = board.adjacent_counts(r, c)
        if n_unrev_unflag > 0 and (N - n_flagged) == n_unrev_unflag:
            # All unrevealed neighbors are mines -> flag one of them
            for nr, nc in board.neighbors(r, c):
                if not board.revealed[nr, nc] and not board.flagged[nr, nc]:
                    return (nr, nc)
    return None


def find_one_safe_move(board: MinesweeperBoard):
    """Find one cell that is safe to reveal, return (r,c) or None."""
    for r, c in get_frontier_cells(board):
        N = board.board[r, c]
        n_flagged, n_unrev_unflag = board.adjacent_counts(r, c)
        if n_unrev_unflag > 0 and n_flagged == N:
            # All remaining unrevealed neighbors are safe -> reveal one
            for nr, nc in board.neighbors(r, c):
                if not board.revealed[nr, nc] and not board.flagged[nr, nc]:
                    return (nr, nc)
    return None


def pick_guess(board: MinesweeperBoard):
    """Fallback guess when no deterministic move exists (replace with smarter logic)."""
    choices = [
        (r, c)
        for r in range(board.height)
        for c in range(board.width)
        if not board.revealed[r, c] and not board.flagged[r, c]
    ]
    return random.choice(choices) if choices else None


# ---------------------- visual runner ----------------------
def run_visual_bot(width=16, height=16, num_mines=40, step_delay=0.08):
    # Build UI and share its internal board for rendering
    ui = MinesweeperUI(width=width, height=height, num_mines=num_mines, cell_size=32, header_height=48)
    board = ui.board

    started = False
    running = True
    last_action_time = 0.0

    while running:
        # Handle window events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                board.reset()
                started = False

        # Bot logic with throttled steps to keep it visible
        now = time.time()
        if now - last_action_time >= step_delay and not board.game_over:
            if not started:
                # Initial safe reveal (center)
                board.reveal(board.height // 2, board.width // 2)
                last_action_time = now
            else:
                move = find_one_flag_move(board)
                if move:
                    r, c = move
                    board.toggle_flag(r, c)
                    last_action_time = now
                else:
                    move = find_one_safe_move(board)
                    if move:
                        r, c = move
                        board.reveal(r, c)
                        last_action_time = now
                    else:
                        guess = pick_guess(board)
                        if guess:
                            r, c = guess
                            board.reveal(r, c)
                            last_action_time = now
            started = True

        ui.draw()
        ui.clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    run_visual_bot(width=16, height=16, num_mines=40, step_delay=0.06)