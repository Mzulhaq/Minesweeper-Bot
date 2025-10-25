import pygame
from board import MinesweeperBoard



class MinesweeperUI:
	def __init__(self, width=9, height=9, num_mines=10, cell_size=36, header_height=48):
		self.board = MinesweeperBoard(width=width, height=height, num_mines=num_mines)
		self.cell_size = cell_size
		self.header_height = header_height

		# colors
		self.COLORS = {
			'bg': (240, 240, 240),
			'grid': (200, 200, 200),
			'border': (50, 50, 50),
			'hidden': (160, 160, 160),
			'mine': (220, 20, 60),
			'flag': (30, 144, 255),
			'text': (10, 10, 10),
			'header_bg': (225, 225, 225),
			'header_text': (20, 20, 20),
		}
		self.NUM_COLORS = {
			1: (25, 118, 210),
			2: (56, 142, 60),
			3: (211, 47, 47),
			4: (123, 31, 162),
			5: (191, 54, 12),
			6: (0, 151, 167),
			7: (97, 97, 97),
			8: (66, 66, 66),
		}

		pygame.init()
		# Cell number font; header uses dynamic fit per available width
		self.font = pygame.font.SysFont(None, 22)
		self.screen = pygame.display.set_mode((
			self.board.width * self.cell_size,
			self.header_height + self.board.height * self.cell_size
		))
		pygame.display.set_caption("Minesweeper")
		self.clock = pygame.time.Clock()

	def _fit_text(self, text: str, color, max_width: int, base_ratio: float = 0.6, min_size: int = 12):
		"""Render text scaled down to fit within max_width based on header height."""
		size = max(min_size, int(self.header_height * base_ratio))
		while size >= min_size:
			font = pygame.font.SysFont(None, size)
			surf = font.render(text, True, color)
			if surf.get_width() <= max_width:
				return font, surf
			size -= 1
		# fallback to minimum size
		font = pygame.font.SysFont(None, min_size)
		surf = font.render(text, True, color)
		return font, surf

	def mouse_to_cell(self, pos):
		x, y = pos
		# account for header bar
		y -= self.header_height
		if y < 0:
			return None
		c = x // self.cell_size
		r = y // self.cell_size
		if 0 <= r < self.board.height and 0 <= c < self.board.width:
			return r, c
		return None

	def draw(self):
		s = self.screen
		cs = self.cell_size
		s.fill(self.COLORS['bg'])

		# header bar
		pygame.draw.rect(s, self.COLORS['header_bg'], (0, 0, s.get_width(), self.header_height))
		pygame.draw.line(s, self.COLORS['border'], (0, self.header_height), (s.get_width(), self.header_height), 1)

		for r in range(self.board.height):
			for c in range(self.board.width):
				x, y = c * cs, self.header_height + r * cs
				pygame.draw.rect(s, self.COLORS['border'], (x, y, cs, cs), 1)

				if self.board.revealed[r, c]:
					pygame.draw.rect(s, self.COLORS['bg'], (x+1, y+1, cs-2, cs-2))
					val = self.board.board[r, c]
					if val == -1:
						pygame.draw.circle(s, self.COLORS['mine'], (x + cs//2, y + cs//2), cs//4)
					elif val > 0:
						color = self.NUM_COLORS.get(val, self.COLORS['text'])
						text = self.font.render(str(val), True, color)
						s.blit(text, text.get_rect(center=(x + cs//2, y + cs//2)))
				else:
					pygame.draw.rect(s, self.COLORS['hidden'], (x+1, y+1, cs-2, cs-2))
					if self.board.flagged[r, c]:
						tip = (x + cs//2, y + cs//4)
						left = (x + cs//4, y + cs//2)
						right = (x + 3*cs//4, y + cs//2)
						pygame.draw.polygon(s, self.COLORS['flag'], [tip, left, right])

		# bombs remaining in header (right) — render first to know occupied width
		bombs_left = self.board.bombs_remaining()
		bombs_str = f"Mines: {bombs_left}"
		_, bomb_surf = self._fit_text(bombs_str, self.COLORS['header_text'], max_width=max(80, s.get_width() // 3))
		bx = s.get_width() - bomb_surf.get_width() - 10
		by = (self.header_height - bomb_surf.get_height()) // 2
		s.blit(bomb_surf, (bx, by))

		# status banner in header (left) — fit into remaining width
		if self.board.game_over:
			msg = "You Win! (R to restart)" if self.board.won else "Game Over (R to restart)"
		else:
			msg = "Left: reveal | Right: flag | R: restart"
		left_max = max(60, s.get_width() - bomb_surf.get_width() - 30)
		_, status_surf = self._fit_text(msg, self.COLORS['header_text'], max_width=left_max)
		s.blit(status_surf, (10, (self.header_height - status_surf.get_height()) // 2))

		pygame.display.flip()


def run_game():
	ui = MinesweeperUI(width=9, height=9, num_mines=10, cell_size=36)
	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
				ui.board.reset()
			elif event.type == pygame.MOUSEBUTTONDOWN and not ui.board.game_over:
				cell = ui.mouse_to_cell(event.pos)
				if cell is not None:
					r, c = cell
					if event.button == 1:
						ui.board.reveal(r, c)
					elif event.button == 3:
						ui.board.toggle_flag(r, c)

		ui.draw()
		ui.clock.tick(60)

	pygame.quit()


if __name__ == "__main__":
	run_game()

