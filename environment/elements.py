from enum import Enum


class CellType(Enum):
    EMPTY       = "."
    WALL        = "#"
    TRAP        = "T"
    TREASURE    = "$"
    HIDDEN_PATH = "H"
    START       = "S"
    EXIT        = "E"
    AGENT       = "A"


class Trap:
    """Trap element in the grid."""

    def __init__(self, x: int, y: int, damage: int = 20, is_active: bool = True):
        self.x = x
        self.y = y
        self.damage = damage
        self.is_active = is_active
        self.timer = 0

    def tick(self):
        """Update trap state each step."""
        self.timer += 1
        if self.timer % 3 == 0:
            self.is_active = not self.is_active

    def __repr__(self):
        status = "ACTIVE" if self.is_active else "INACTIVE"
        return f"Trap({self.x},{self.y}) [{status}] DMG={self.damage}"


class Treasure:
    """Treasure element in the grid."""

    def __init__(self, x: int, y: int, value: int = 10):
        self.x = x
        self.y = y
        self.value = value
        self.collected = False

    def collect(self) -> int:
        if not self.collected:
            self.collected = True
            return self.value
        return 0

    def __repr__(self):
        status = "COLLECTED" if self.collected else f"VALUE={self.value}"
        return f"Treasure({self.x},{self.y}) [{status}]"
