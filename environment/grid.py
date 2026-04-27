from typing import List, Tuple, Optional
from environment.elements import CellType, Trap, Treasure


class Grid:
    """Grid model for the pyramid world."""

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols

        self.cells: List[List[CellType]] = [
            [CellType.EMPTY for _ in range(cols)]
            for _ in range(rows)
        ]

        self.traps: List[Trap] = []
        self.treasures: List[Treasure] = []

        self.start_pos: Tuple[int, int] = (0, 0)
        self.exit_pos: Tuple[int, int] = (rows - 1, cols - 1)

    def set_cell(self, x: int, y: int, cell_type: CellType):
        if self.in_bounds(x, y):
            self.cells[x][y] = cell_type

    def add_trap(self, trap: Trap):
        self.traps.append(trap)
        self.set_cell(trap.x, trap.y, CellType.TRAP)

    def add_treasure(self, treasure: Treasure):
        self.treasures.append(treasure)
        self.set_cell(treasure.x, treasure.y, CellType.TREASURE)

    def set_start(self, x: int, y: int):
        self.start_pos = (x, y)
        self.set_cell(x, y, CellType.START)

    def set_exit(self, x: int, y: int):
        self.exit_pos = (x, y)
        self.set_cell(x, y, CellType.EXIT)

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.rows and 0 <= y < self.cols

    def is_walkable(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return False
        return self.cells[x][y] not in (CellType.WALL,)

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Return walkable orthogonal neighbors."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                neighbors.append((nx, ny))
        return neighbors

    def get_trap_at(self, x: int, y: int) -> Optional[Trap]:
        for trap in self.traps:
            if trap.x == x and trap.y == y and trap.is_active:
                return trap
        return None

    def get_treasure_at(self, x: int, y: int) -> Optional[Treasure]:
        for t in self.treasures:
            if t.x == x and t.y == y and not t.collected:
                return t
        return None

    def tick_dynamic_elements(self):
        """Update dynamic elements on each step."""
        for trap in self.traps:
            trap.tick()

    def display(self, agent_pos: Optional[Tuple[int, int]] = None):
        """Print the grid in terminal."""
        print("\n" + "═" * (self.cols * 2 + 2))
        for r in range(self.rows):
            row_str = "║ "
            for c in range(self.cols):
                if agent_pos and (r, c) == agent_pos:
                    row_str += "A "
                else:
                    row_str += self.cells[r][c].value + " "
            row_str += "║"
            print(row_str)
        print("═" * (self.cols * 2 + 2))
