"""
🏺 Pyramid Explorer AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Project entry point.

Run: python main.py
"""

from environment.pyramid import build_random_pyramid
from agent.agent import PyramidAgent
from algorithms.bfs import bfs
from algorithms.dfs import dfs
from algorithms.astar import astar


def configure_console_encoding():
    """
    Force UTF-8 output on Windows terminals.
    """
    import os
    import sys

    os.environ.setdefault("PYTHONUTF8", "1")
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass


def run_text_mode(algo: str = "astar"):
    """Run project in terminal mode without pygame."""
    print("\nPyramid Explorer AI - Text Mode")
    print("=" * 45)

    grid  = build_random_pyramid(rows=10, cols=10)
    agent = PyramidAgent(grid)

    grid.display(agent.position)

    if algo == "bfs":
        path = bfs(grid, grid.start_pos, grid.exit_pos)
    elif algo == "dfs":
        path = dfs(grid, grid.start_pos, grid.exit_pos)
    else:
        path = astar(grid, grid.start_pos, grid.exit_pos, avoid_traps=True)

    if not path:
        print("❌ No path found!")
        return

    print(f"\nPath found ({algo.upper()}) - {len(path)} steps:")
    print(" → ".join(str(p) for p in path))
    print()

    for next_pos in path[1:]:
        result = agent.act(next_pos)
        print(f"  Step {agent.steps:02d}: {result}")
        grid.display(agent.position)

        if agent.is_done():
            break

    agent.status()


def run_visual_mode(algo: str = "astar"):
    """Run project in pygame visual mode."""
    try:
        from game.visualizer import PyramidVisualizer
    except ImportError as e:
        print(f"❌ {e}")
        return

    grid  = build_random_pyramid(rows=10, cols=16)
    agent = PyramidAgent(grid)

    path = []
    print("Interactive mode: choose BFS/DFS/A* and click RUN/RESTART.")
    viz = PyramidVisualizer(grid, agent, initial_algo=algo)
    viz.run(path, step_delay=0.5)


if __name__ == "__main__":
    import sys
    configure_console_encoding()

    # Usage: python main.py [text|visual] [bfs|dfs|astar]
    mode = sys.argv[1] if len(sys.argv) > 1 else "visual"
    algo = sys.argv[2] if len(sys.argv) > 2 else "astar"

    if mode == "text":
        run_text_mode(algo)
    else:
        run_visual_mode(algo)
