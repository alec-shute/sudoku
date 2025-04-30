# Sudoku Solver

A Python-based Sudoku solver that can solve puzzles of different sizes (NxN grids), including traditional 9x9 puzzles. The solver uses advanced algorithms like constraint propagation and backtracking to find the solution. 

## Features

- Solves classic 9x9 Sudoku puzzles
- Supports customizable Sudoku grid sizes (NxN)
- Implements constraint propagation and backtracking algorithms
- Includes features for verbose output to debug the solving process
- Presents the solved grid in human-readable ASCII format
- Can be expanded for future features like solution counts, minimal Sudoku puzzles or 3D Sudoku

## Installation

To use the Sudoku solver, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/sudoku-solver.git
    cd sudoku-solver
    ```

2. Install dependencies:
    The project requires Python 3.6. If you don’t have it installed, please install it first.

    You can use `pip` to install any required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To use the Sudoku solver, run the following in your terminal:

```python
from sudoku_solver import SudokuSolver

solver = SudokuSolver(puzzle, k=3)
solver.solve()  # solves the puzzle

Required format for puzzle: for 4x4 and 9x9 puzzles, input a string of digits with dots (.) to represent blank cells.
for k**2 x k**2 sudokus for k>3, input a list of k**4 integers between 1 and k inclusive, and 0 for blank cells.
The input is read left to right, top to bottom to populate the grid.

## Algorithm Overview

1) The solver keeps track of a list of candidate digits for each cell
2) Naked Singles: Cells with only one possible candidate are immediately filled in.
3) Hidden Singles: When no naked singles are found, the solver searches for digits that can only go in one place in a row, column or box.
4) Updating Candidates: After each cell is solved, all neighboring cells (in same row, column or box) have that digit removed as a candidate.
5) Recursive backtracking: If no naked or hidden singles are found, the solver makes a guess using Minimal Value Recursion. It finds an unsolved cell with the minimum number of candidates, and makes a random guess among those candidates for this cell's value.
6) Contradiction check: The solver regularly checks for contradicitons. If a contradiction is found, it backtracks its latest guess and removes the incorrect guess from the list of candidates for that cell.
7) Termination: The algorithm recurses until a solution is found, a contradiction to the original puzzle is found, or the solver hits a user-defined maximum number of iterations.

## Example Usage

from sudoku import SudokuSolver

# Arto Inkala's famously difficult Sudoku
arto_inkala = "8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4.."

# A 16x16 Sudoku with multiple solutions
sudoku_16x16 = [
    0, 0, 0, 0,     0, 2, 0, 0,     12, 0, 0, 9,     0, 0, 0, 0,
    0, 0, 16, 0,    15, 0, 0, 0,     0, 0, 0, 0,     0, 8, 0, 0,
    1, 0, 0, 13,    0, 0, 0, 0,     0, 0, 0, 0,     0, 0, 0, 6,
    0, 0, 0, 0,     0, 14, 0, 0,     1, 0, 0, 0,     0, 0, 0, 0,
    # ...
    # Truncated for brevity — full example in the code
]

# Blank 9x9 Sudoku
blank_grid = "." * 81

# Blank 36x36 Sudoku
blank_grid_36x36 = [0] * (36 * 36)

# A grid with no possible solutions
no_solution = "339...4..2..7.9....87......75..6.23.6..9.4..8.28.5..41.......59...1.6..7..6...1.4"

# Solve puzzles
solver1 = SudokuSolver(arto_inkala)
solution1 = solver1.solve()

solver2 = SudokuSolver(sudoku_16x16, box_size=4)
solution2 = solver2.solve()

solver3 = SudokuSolver(blank_grid)
solution3 = solver3.solve()

solver4 = SudokuSolver(blank_grid_36x36, box_size=6)
solution4 = solver4.solve(max_steps=5000)  # Increase steps for very large puzzles

solver5 = SudokuSolver(no_solution)
solution5 = solver5.solve()  # Returns None





