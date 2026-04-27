from typing import Tuple, List
from environment.grid import Grid
from agent.actuators import Actuators


class PyramidAgent:
    """Main Pyramid Explorer agent."""

    def __init__(self, grid: Grid):
        self.grid = grid
        self.actuators = Actuators()

        self.position: Tuple[int, int] = grid.start_pos
        self.health: int = 100
        self.score: int = 0
        self.steps: int = 0
        self.alive:    bool = True
        self.exited:   bool = False

        self.path_taken: List[Tuple[int, int]] = [self.position]

        print(f"[Agent] Starting at {self.position}")

    def act(self, next_pos: Tuple[int, int]) -> str:
        """Move agent to next_pos and resolve cell effects."""
        if not self.alive:
            return "Agent is dead."

        success, msg = self.actuators.move(self.grid, self.position, next_pos)
        if not success:
            return msg

        self.position = next_pos
        self.steps += 1
        self.path_taken.append(self.position)

        self.grid.tick_dynamic_elements()

        val, t_msg = self.actuators.collect_treasure(self.grid, *self.position)
        self.score += val

        trap = self.grid.get_trap_at(*self.position)
        if trap:
            self.health -= trap.damage
            msg += f" | HIT TRAP! -{trap.damage} HP"
            if self.health <= 0:
                self.alive = False
                return msg + " | Agent DEAD"

        if self.position == self.grid.exit_pos:
            self.exited = True
            return msg + " | REACHED EXIT!"

        if val > 0:
            msg += f" | {t_msg}"

        return msg

    def status(self):
        print(f"\n{'─'*40}")
        print(f"  Position : {self.position}")
        print(f"  Health   : {self.health} HP")
        print(f"  Score    : {self.score}")
        print(f"  Steps    : {self.steps}")
        print(f"  Alive    : {self.alive}")
        print(f"  Exited   : {self.exited}")
        print(f"{'─'*40}\n")

    def is_done(self) -> bool:
        return not self.alive or self.exited
