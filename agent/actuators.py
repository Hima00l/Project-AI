from typing import Tuple
from environment.grid import Grid


class Actuators:
    """Actions that the agent can execute."""

    def move(self, grid: Grid, current: Tuple[int, int],
             target: Tuple[int, int]) -> Tuple[bool, str]:
        """Try moving from current to target."""
        if grid.is_walkable(target[0], target[1]):
            return True, f"Moved to {target}"
        return False, f"Cannot move to {target} — blocked"

    def collect_treasure(self, grid: Grid,
                         x: int, y: int) -> Tuple[int, str]:
        """Collect treasure at the current position if available."""
        treasure = grid.get_treasure_at(x, y)
        if treasure:
            val = treasure.collect()
            return val, f"Collected treasure worth {val} at ({x},{y})!"
        return 0, "No treasure here."
