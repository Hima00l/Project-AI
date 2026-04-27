import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from environment.grid import Grid
from environment.elements import CellType
from agent.agent import PyramidAgent
from environment.pyramid import build_random_pyramid
from algorithms.bfs import bfs
from algorithms.dfs import dfs
from algorithms.astar import astar


# ─────────── Colors ───────────
COLORS = {
    "bg":           (28, 21, 13),
    "empty":        (85, 67, 43),
    "wall":         (58, 45, 30),
    "trap":         (165, 45, 36),
    "trap_off":     (95, 50, 42),
    "treasure":     (214, 175, 75),
    "start":        (76, 128, 84),
    "exit":         (70, 155, 120),
    "agent":        (225, 210, 156),
    "path":         (120, 98, 62),
    "grid_line":    (112, 88, 52),
    "text":         (242, 223, 178),
    "hud_bg":       (37, 28, 18),
    "btn":          (87, 65, 38),
    "btn_hover":    (117, 86, 47),
    "btn_active":   (166, 125, 56),
}

HUD_HEIGHT  = 190
FONT_SIZE   = 18


class PyramidVisualizer:
    """
    Pygame visualizer for Pyramid Explorer.
    """

    def __init__(self, grid: Grid, agent: PyramidAgent, initial_algo: str = "astar"):
        if not PYGAME_AVAILABLE:
            raise ImportError("pygame is not installed. Run: pip install pygame")

        self.grid  = grid
        self.agent = agent
        self.rows = grid.rows
        self.cols = grid.cols

        pygame.init()
        self.cell = 64
        self.screen = None
        self._fit_to_screen()

        pygame.display.set_caption("Pyramid Explorer AI")

        self.font       = pygame.font.SysFont("arial", FONT_SIZE, bold=True)
        self.font_small = pygame.font.SysFont("arial", FONT_SIZE - 4)
        self.clock      = pygame.time.Clock()
        self.selected_algo = initial_algo if initial_algo in {"bfs", "dfs", "astar"} else "astar"
        self.latest_path: List[Tuple[int, int]] = []
        self.step_idx = 1
        self.last_step_at = 0.0
        self.step_delay = 0.45
        self.running_path = False
        self.status_text = "Choose an algorithm, then press RUN"
        self.buttons = self._build_buttons()
        self.icons = self._load_icons()

    def _fit_to_screen(self):
        info = pygame.display.Info()
        max_w = max(760, int(info.current_w * 0.92))
        max_h = max(680, int(info.current_h * 0.90))
        cell_w = max_w // self.cols
        self.cell = min(cell_w, 96)
        self.cell = max(24, self.cell)
        while (self.cols * self.cell) > max_w and self.cell > 16:
            self.cell -= 1
        while (self.rows * self.cell + HUD_HEIGHT) > max_h and self.cell > 24:
            self.cell -= 1
        w = self.cols * self.cell
        h = self.rows * self.cell + HUD_HEIGHT
        self.screen = pygame.display.set_mode((w, h))

    def _build_buttons(self):
        hud_y = self.grid.rows * self.cell
        top = hud_y + 16
        run_top = hud_y + 84
        return {
            "bfs": pygame.Rect(20, top, 110, 38),
            "dfs": pygame.Rect(142, top, 110, 38),
            "astar": pygame.Rect(264, top, 110, 38),
            "run": pygame.Rect(20, run_top, 185, 48),
            "new_map": pygame.Rect(220, run_top, 154, 48),
        }

    def _load_icons(self):
        """Load icons from assets by case-insensitive filename."""
        icons = {}
        root = Path(__file__).resolve().parents[1]
        assets_dir = root / "assets"
        if not assets_dir.exists():
            return icons

        expected_names: Dict[str, str] = {
            "agent": "agent",
            "exit": "exit",
            "start": "start",
            "trap": "trap",
            "wall": "wall",
            "treasure": "treasure",
            "pyramid": "pyramid",
        }

        assets_by_stem = {p.stem.lower(): p for p in assets_dir.iterdir() if p.is_file()}
        for key, stem in expected_names.items():
            p = assets_by_stem.get(stem)
            if not p:
                continue
            try:
                icons[key] = pygame.image.load(str(p)).convert_alpha()
            except pygame.error:
                continue
        return icons

    def _draw_pyramid_background(self):
        """Draw pyramid image background with a fallback shape."""
        grid_h = self.rows * self.cell
        w = self.screen.get_width()
        pyramid_img = self.icons.get("pyramid")
        if pyramid_img:
            scaled = pygame.transform.smoothscale(pyramid_img, (w, grid_h))
            layer = pygame.Surface((w, grid_h), pygame.SRCALPHA)
            layer.blit(scaled, (0, 0))
            layer.fill((0, 0, 0, 70), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(layer, (0, 0))
            return

        h = grid_h
        layer = pygame.Surface((w, h), pygame.SRCALPHA)
        base_y = int(h * 0.95)
        apex = (w // 2, int(h * 0.10))
        left = (int(w * 0.08), base_y)
        right = (int(w * 0.92), base_y)

        pygame.draw.polygon(layer, (160, 125, 70, 48), [left, apex, right])
        pygame.draw.line(layer, (205, 170, 110, 75), apex, left, 2)
        pygame.draw.line(layer, (205, 170, 110, 75), apex, right, 2)
        for i in range(1, 9):
            t = i / 9
            y = int(apex[1] + (base_y - apex[1]) * t)
            half_w = int((right[0] - apex[0]) * t)
            pygame.draw.line(
                layer,
                (220, 190, 130, 30),
                (apex[0] - half_w, y),
                (apex[0] + half_w, y),
                1,
            )
        self.screen.blit(layer, (0, 0))

    def _draw_icon(self, key: str, rect: pygame.Rect):
        icon = self.icons.get(key)
        if not icon:
            return False
        target = int(self.cell * 0.74)
        scaled = pygame.transform.smoothscale(icon, (target, target))
        shadow = pygame.Surface((target, target), pygame.SRCALPHA)
        shadow.blit(scaled, (0, 0))
        shadow.fill((0, 0, 0, 70), special_flags=pygame.BLEND_RGBA_MULT)
        self.screen.blit(
            shadow,
            (rect.x + (rect.width - target) // 2 + 2, rect.y + (rect.height - target) // 2 + 2),
        )
        self.screen.blit(
            scaled,
            (rect.x + (rect.width - target) // 2, rect.y + (rect.height - target) // 2),
        )
        return True

    def _draw_button(self, rect: pygame.Rect, text: str, active: bool = False):
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)
        color = COLORS["btn_active"] if active else (COLORS["btn_hover"] if hovered else COLORS["btn"])
        pygame.draw.rect(self.screen, color, rect, border_radius=6)
        pygame.draw.rect(self.screen, COLORS["grid_line"], rect, 2, border_radius=6)
        txt = self.font.render(text, True, COLORS["text"])
        self.screen.blit(txt, (rect.x + (rect.width - txt.get_width()) // 2, rect.y + 7))

    def _compute_path(self):
        if self.selected_algo == "bfs":
            return bfs(self.grid, self.grid.start_pos, self.grid.exit_pos)
        if self.selected_algo == "dfs":
            return dfs(self.grid, self.grid.start_pos, self.grid.exit_pos)
        return astar(self.grid, self.grid.start_pos, self.grid.exit_pos, avoid_traps=True)

    def _reset_with_new_world(self):
        self.grid = build_random_pyramid(rows=self.rows, cols=self.cols)
        self.agent = PyramidAgent(self.grid)
        self.latest_path = []
        self.step_idx = 1
        self.running_path = False
        self.status_text = "New map generated - press RUN"

    def _restart_current_map(self):
        self.agent = PyramidAgent(self.grid)
        self.latest_path = self._compute_path() or []
        self.step_idx = 1
        self.last_step_at = time.time()
        self.running_path = bool(self.latest_path)
        if self.running_path:
            self.status_text = f"Running {self.selected_algo.upper()}..."
        else:
            self.status_text = f"No path found with {self.selected_algo.upper()}"

    def draw_grid(self):
        for r in range(self.grid.rows):
            for c in range(self.grid.cols):
                x = c * self.cell
                y = r * self.cell
                rect = pygame.Rect(x, y, self.cell, self.cell)
                cell = self.grid.cells[r][c]

                if   cell == CellType.WALL:    color = COLORS["wall"]
                elif cell == CellType.TREASURE: color = COLORS["treasure"]
                elif cell == CellType.START:    color = COLORS["start"]
                elif cell == CellType.EXIT:     color = COLORS["exit"]
                elif cell == CellType.TRAP:
                    trap = self.grid.get_trap_at(r, c)
                    color = COLORS["trap"] if trap else COLORS["trap_off"]
                else:
                    color = COLORS["empty"]

                tile = pygame.Surface((self.cell, self.cell), pygame.SRCALPHA)
                tile.fill((color[0], color[1], color[2], 212))
                self.screen.blit(tile, (x, y))
                pygame.draw.rect(self.screen, COLORS["grid_line"], rect, 1)

                cx = x + self.cell // 2
                cy = y + self.cell // 2

                if cell == CellType.WALL:
                    if not self._draw_icon("wall", rect):
                        for i in range(0, self.cell * 2, 10):
                            pygame.draw.line(self.screen, (35, 28, 20),
                                             (x + i, y), (x + i - self.cell, y + self.cell), 2)

                elif cell == CellType.TRAP:
                    trap = self.grid.get_trap_at(r, c)
                    col  = (255, 80, 80) if trap else (100, 40, 40)
                    if not self._draw_icon("trap", rect):
                        pts = [(cx, cy - 18), (cx - 16, cy + 12), (cx + 16, cy + 12)]
                        pygame.draw.polygon(self.screen, col, pts)
                        pygame.draw.polygon(self.screen, (255, 200, 0), pts, 2)

                elif cell == CellType.TREASURE:
                    if not self._draw_icon("treasure", rect):
                        pts = [(cx, cy - 18), (cx + 14, cy), (cx, cy + 18), (cx - 14, cy)]
                        pygame.draw.polygon(self.screen, (212, 175, 55), pts)
                        pygame.draw.polygon(self.screen, (255, 230, 100), pts, 2)

                elif cell == CellType.START:
                    if not self._draw_icon("start", rect):
                        pygame.draw.circle(self.screen, (60, 160, 60), (cx, cy), 18)
                        pygame.draw.circle(self.screen, (100, 255, 100), (cx, cy), 18, 2)

                elif cell == CellType.EXIT:
                    if not self._draw_icon("exit", rect):
                        er = pygame.Rect(x + 10, y + 10, self.cell - 20, self.cell - 20)
                        pygame.draw.rect(self.screen, (60, 200, 120), er, border_radius=6)
                        pygame.draw.rect(self.screen, (100, 255, 180), er, 2, border_radius=6)

                elif cell == CellType.HIDDEN_PATH:
                    t = self.font.render("?", True, (150, 130, 100))
                    self.screen.blit(t, (cx - t.get_width()//2, cy - t.get_height()//2))

    def draw_path(self):
        for pos in self.agent.path_taken[:-1]:
            r, c = pos
            x = c * self.cell + self.cell // 2
            y = r * self.cell + self.cell // 2
            pygame.draw.circle(self.screen, COLORS["path"], (x, y), 6)

    def draw_agent(self):
        r, c = self.agent.position
        x = c * self.cell
        y = r * self.cell
        cx = x + self.cell // 2
        cy = y + self.cell // 2
        rect = pygame.Rect(x, y, self.cell, self.cell)
        if not self._draw_icon("agent", rect):
            pygame.draw.circle(self.screen, COLORS["agent"], (cx, cy), self.cell // 3)
            txt = self.font.render("assets/agent.ico", True, (10, 10, 20))
            self.screen.blit(txt, (cx - txt.get_width()//2, cy - txt.get_height()//2))

    def _draw_hud_hieroglyph_pattern(self, hud_rect: pygame.Rect):
        layer = pygame.Surface((hud_rect.width, hud_rect.height), pygame.SRCALPHA)
        glyph_color = (190, 155, 88, 42)
        row_y = 10
        step = 48
        for x in range(8, hud_rect.width - 20, step):
            pygame.draw.rect(layer, glyph_color, pygame.Rect(x, row_y + 4, 16, 14), 1)
            pygame.draw.line(layer, glyph_color, (x + 8, row_y + 4), (x + 8, row_y + 18), 1)
            pygame.draw.circle(layer, glyph_color, (x + 8, row_y + 28), 6, 1)
            pygame.draw.line(layer, glyph_color, (x, row_y + 40), (x + 16, row_y + 40), 1)
        for x in range(20, hud_rect.width - 16, step):
            y2 = hud_rect.height - 44
            pygame.draw.polygon(layer, glyph_color, [(x, y2 + 14), (x + 8, y2), (x + 16, y2 + 14)], 1)
            pygame.draw.line(layer, glyph_color, (x + 8, y2 + 16), (x + 8, y2 + 30), 1)
        self.screen.blit(layer, (hud_rect.x, hud_rect.y))

    def draw_hud(self):
        hud_y = self.grid.rows * self.cell
        hud_rect = pygame.Rect(0, hud_y, self.screen.get_width(), HUD_HEIGHT)
        pygame.draw.rect(self.screen, COLORS["hud_bg"], hud_rect)
        self._draw_hud_hieroglyph_pattern(hud_rect)

        info = (
            f"  POS: {self.agent.position}   "
            f"HP: {self.agent.health}   "
            f"SCORE: {self.agent.score}   "
            f"STEPS: {self.agent.steps}"
        )
        txt = self.font.render(info, True, COLORS["text"])
        self.screen.blit(txt, (400, hud_y + 22))

        if self.agent.exited:
            status = "[ EXITED! ]"
            scol   = (100, 255, 150)
        elif not self.agent.alive:
            status = "[ DEAD ]"
            scol   = (255, 80, 80)
        else:
            status = "[ Exploring... ]"
            scol   = COLORS["treasure"]
        s_txt = self.font.render(status, True, scol)
        self.screen.blit(s_txt, (400, hud_y + 52))

        self._draw_button(self.buttons["bfs"], "BFS", active=self.selected_algo == "bfs")
        self._draw_button(self.buttons["dfs"], "DFS", active=self.selected_algo == "dfs")
        self._draw_button(self.buttons["astar"], "A*", active=self.selected_algo == "astar")
        self._draw_button(self.buttons["run"], "RUN / RESTART", active=False)
        self._draw_button(self.buttons["new_map"], "NEW MAP", active=False)

        hint = self.font_small.render(self.status_text, True, COLORS["text"])
        self.screen.blit(hint, (20, hud_y + 150))

    def render(self):
        self.screen.fill(COLORS["bg"])
        self._draw_pyramid_background()
        self.draw_grid()
        self.draw_path()
        self.draw_agent()
        self.draw_hud()
        pygame.display.flip()

    def run(self, path: List[Tuple[int, int]], step_delay: float = 0.4):
        """Run visualizer loop and animate agent movement."""
        self.latest_path = path
        self.step_delay = step_delay
        self.step_idx = 1
        self.running_path = False
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    if self.buttons["bfs"].collidepoint(pos):
                        self.selected_algo = "bfs"
                        self.running_path = False
                        self.status_text = "Selected BFS - press RUN"
                    elif self.buttons["dfs"].collidepoint(pos):
                        self.selected_algo = "dfs"
                        self.running_path = False
                        self.status_text = "Selected DFS - press RUN"
                    elif self.buttons["astar"].collidepoint(pos):
                        self.selected_algo = "astar"
                        self.running_path = False
                        self.status_text = "Selected A* - press RUN"
                    elif self.buttons["run"].collidepoint(pos):
                        self._restart_current_map()
                    elif self.buttons["new_map"].collidepoint(pos):
                        self._reset_with_new_world()

            self.render()

            if self.running_path and self.step_idx < len(self.latest_path) and not self.agent.is_done():
                now = time.time()
                if now - self.last_step_at >= self.step_delay:
                    result = self.agent.act(self.latest_path[self.step_idx])
                    print(f"Step {self.agent.steps}: {result}")
                    self.step_idx += 1
                    self.last_step_at = now
            elif self.running_path and (self.agent.is_done() or self.step_idx >= len(self.latest_path)):
                self.running_path = False
                self.status_text = f"Finished {self.selected_algo.upper()} - press RUN to generate a new pyramid"

            self.clock.tick(30)

        pygame.quit()
