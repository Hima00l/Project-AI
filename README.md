# Pyramid Explorer AI

A modular AI pathfinding project where an agent navigates a dynamic pyramid grid using classical search algorithms: **BFS**, **DFS**, and **A\***.

The system supports:
- **Visual mode** with an interactive `pygame` interface
- **Text mode** for terminal-based execution and debugging
- **Random but solvable maps** with walls, traps, and treasures

---

## Why this project is interesting

This project demonstrates core AI concepts in a clean, educational way:
- State-space search
- Heuristic planning
- Cost-aware navigation in risky environments
- Separation between environment, algorithms, agent logic, and rendering

It is ideal for AI coursework, demos, and algorithm comparison experiments.

---

## Features

- Multiple search strategies:
  - `BFS` (shortest path in steps)
  - `DFS` (depth-first exploration)
  - `A*` (heuristic + trap-aware cost)
- Dynamic traps that toggle state over time
- Treasure collection and health tracking
- Interactive controls in visual mode:
  - Select algorithm
  - Run / Restart
  - Generate new map

---

## Project Architecture

```text
.
├── main.py
├── requirements.txt
├── algorithms/
│   ├── bfs.py
│   ├── dfs.py
│   └── astar.py
├── environment/
│   ├── elements.py
│   ├── grid.py
│   ├── problem.py
│   └── pyramid.py
├── agent/
│   ├── actuators.py
│   └── agent.py
└── game/
    └── visualizer.py
```

### Module responsibilities

- `algorithms/`: search implementations and path planning logic
- `environment/`: world model, map generation, costs, and transitions
- `agent/`: action execution, health/score state, and run-time effects
- `game/`: rendering, UI controls, and animation loop
- `main.py`: startup, mode selection, and orchestration

---

## Installation

### 1) Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
```

**Windows (PowerShell)**
```bash
.venv\Scripts\Activate.ps1
```

**Linux / macOS**
```bash
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run the project

### Visual mode (default)

```bash
python main.py
```

Or explicitly:

```bash
python main.py visual astar
```

### Text mode

```bash
python main.py text astar
```

You can replace `astar` with `bfs` or `dfs`.

---

## Controls (Visual Mode)

- Click `BFS`, `DFS`, or `A*` to choose algorithm
- Click `RUN / RESTART` to compute and animate a path
- Click `NEW MAP` to generate a new random pyramid
- Close window to exit

---

## Algorithm Notes

### BFS
- Complete and optimal in unweighted step count
- Can be memory-heavy on larger maps

### DFS
- Fast to implement and may find a path quickly
- Does **not** guarantee shortest path

### A*
- Uses Manhattan heuristic and path cost
- In this project, it can penalize active traps, often producing safer routes
- Usually the best practical choice here

---

## Current Design Scope

This is a simplified educational version:
- The agent follows a computed path (planner-driven execution)
- Planning is done before movement starts (not continuous replanning)
- Environment is random at generation time, then evolves with trap toggling

---

## Suggested Next Steps

- Add real-time replanning while the agent moves
- Add reproducible map seeds for benchmarking
- Add unit tests for map generation and algorithm correctness
- Add experiment scripts for BFS/DFS/A* performance comparison

---

## Requirements

- Python 3.10+ (tested with newer versions)
- `pygame`
- `numpy`
- `colorama`

See exact package constraints in `requirements.txt`.

---

## License

This project is intended for educational use.  
