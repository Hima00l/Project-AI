import random
from typing import Optional

from environment.grid import Grid
from environment.elements import CellType, Trap, Treasure


def build_random_pyramid(
    rows: int = 8,
    cols: int = 8,
    wall_ratio: float = 0.18,
    trap_ratio: float = 0.10,
    treasure_count: int = 4,
    rng: Optional[random.Random] = None,
) -> Grid:
    """Build a random, solvable pyramid grid."""
    rand = rng or random.Random()
    while True:
        grid = Grid(rows, cols)
        start = (0, 0)
        goal = (rows - 1, cols - 1)
        grid.set_start(*start)
        grid.set_exit(*goal)

        blocked = {start, goal}
        for r in range(rows):
            for c in range(cols):
                if (r, c) in blocked:
                    continue
                roll = rand.random()
                if roll < wall_ratio:
                    grid.set_cell(r, c, CellType.WALL)
                else:
                    grid.set_cell(r, c, CellType.EMPTY)

        # Carve a guaranteed path to keep the map solvable.
        r = 0
        c = 0
        while r < rows - 1 or c < cols - 1:
            grid.set_cell(r, c, CellType.EMPTY)
            if r == rows - 1:
                c += 1
            elif c == cols - 1:
                r += 1
            elif rand.random() < 0.5:
                c += 1
            else:
                r += 1
        grid.set_cell(rows - 1, cols - 1, CellType.EMPTY)
        grid.set_start(*start)
        grid.set_exit(*goal)

        # Place traps.
        trap_count = int(rows * cols * trap_ratio)
        free_cells = [
            (rr, cc)
            for rr in range(rows)
            for cc in range(cols)
            if grid.cells[rr][cc] == CellType.EMPTY
        ]
        rand.shuffle(free_cells)
        for rr, cc in free_cells[:trap_count]:
            grid.add_trap(Trap(rr, cc, damage=rand.choice([10, 15, 20, 25])))

        # Place treasures.
        free_for_treasure = [
            (rr, cc)
            for rr in range(rows)
            for cc in range(cols)
            if grid.cells[rr][cc] == CellType.EMPTY
        ]
        rand.shuffle(free_for_treasure)
        for rr, cc in free_for_treasure[:treasure_count]:
            grid.add_treasure(Treasure(rr, cc, value=rand.choice([10, 20, 30, 40, 50])))

        return grid
