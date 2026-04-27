import heapq
from typing import List, Tuple, Optional, Union
from environment.grid import Grid
from environment.problem import Problem


def _ensure_problem(
    source: Union[Grid, Problem],
    start: Tuple[int, int],
    goal: Tuple[int, int],
    avoid_traps: bool,
) -> Problem:
    if isinstance(source, Problem):
        return source
    return Problem(source, start, goal, avoid_traps=avoid_traps)


def astar(grid: Union[Grid, Problem],
          start: Tuple[int, int],
          goal:  Tuple[int, int],
          avoid_traps: bool = True) -> Optional[List[Tuple[int, int]]]:
    """
    A* Search
    ━━━━━━━━━
    Balances path cost and heuristic estimate to the goal.

    - avoid_traps=True: penalize active traps.
    - avoid_traps=False: treat all walkable cells equally.

    Returns a list of positions from start to goal, or None.
    """
    problem = _ensure_problem(grid, start, goal, avoid_traps=avoid_traps)

    # (f_score, g_score, position, path)
    open_heap = []
    heapq.heappush(open_heap, (0, 0, problem.initial_state, [problem.initial_state]))

    visited: dict = {}   # position → best g_score

    while open_heap:
        f, g, (x, y), path = heapq.heappop(open_heap)

        if problem.is_goal((x, y)):
            return path

        if (x, y) in visited and visited[(x, y)] <= g:
            continue
        visited[(x, y)] = g

        for (nx, ny) in problem.neighbors((x, y)):
            new_g = g + problem.step_cost((nx, ny))
            new_h = problem.heuristic((nx, ny))
            new_f = new_g + new_h
            new_path = path + [(nx, ny)]
            heapq.heappush(open_heap, (new_f, new_g, (nx, ny), new_path))

    return None
