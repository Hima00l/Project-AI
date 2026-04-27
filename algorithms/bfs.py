from collections import deque
from typing import List, Tuple, Optional, Union
from environment.grid import Grid
from environment.problem import Problem


def _ensure_problem(
    source: Union[Grid, Problem],
    start: Tuple[int, int],
    goal: Tuple[int, int],
) -> Problem:
    if isinstance(source, Problem):
        return source
    return Problem(source, start, goal)


def bfs(grid: Union[Grid, Problem],
        start: Tuple[int, int],
        goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
    """
    Breadth-First Search
    ━━━━━━━━━━━━━━━━━━━
    Finds the shortest path in number of steps.

    Returns a list of positions from start to goal, or None.
    """
    problem = _ensure_problem(grid, start, goal)
    queue   = deque([(problem.initial_state, [problem.initial_state])])
    visited = {problem.initial_state}

    while queue:
        (x, y), path = queue.popleft()

        if problem.is_goal((x, y)):
            return path

        for neighbor in problem.neighbors((x, y)):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None
