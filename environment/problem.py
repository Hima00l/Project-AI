from typing import Iterable, Tuple

from environment.grid import Grid


Position = Tuple[int, int]


class Problem:
    """Search problem wrapper for grid navigation."""

    def __init__(
        self,
        grid: Grid,
        start: Position,
        goal: Position,
        avoid_traps: bool = False,
    ):
        self.grid = grid
        self.initial_state = start
        self.goal_state = goal
        self.avoid_traps = avoid_traps

    def is_goal(self, state: Position) -> bool:
        return state == self.goal_state

    def neighbors(self, state: Position) -> Iterable[Position]:
        x, y = state
        return self.grid.get_neighbors(x, y)

    def step_cost(self, state: Position) -> int:
        if self.avoid_traps:
            trap = self.grid.get_trap_at(state[0], state[1])
            if trap:
                return 100
        return 1

    def heuristic(self, state: Position) -> int:
        return abs(state[0] - self.goal_state[0]) + abs(state[1] - self.goal_state[1])
