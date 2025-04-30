from collections import defaultdict, Counter
import copy
import random
import sys
from itertools import product

sys.setrecursionlimit(100000)

class SudokuSolver:

    """
    A class to solve Sudoku puzzles of any size, using naked singles, 
    hidden singles, and backtracking (guessing) with Minimum Value Recursion when necessary.
    
    Attributes:
        str (str): The puzzle to solve.
        Required format: for 4x4 and 9x9 puzzles, input a string of digits with dots (.) to represent blank cells.
        for k**2 x k**2 sudokus for k>3, input a list of k**4 integers between 1 and k inclusive, and 0 for blank cells.
        The input is read left to right, top to bottom to populate the grid.
        
        k (int): The size of the smaller subgrid in the Sudoku puzzle (3 for a standard 9x9 Sudoku).
        verbose (bool): Whether to print detailed debugging information during the solving process.
    """
    
    def __init__(self, str, k=3, verbose=False):
        self.str = str
        self.verbose = verbose
        self.attempt = 1
        self.k = k
        self.n = k ** 2
        
        if k <= 3:
            format = "dots"
        else:
            format = "not dots"
        
        if format == "dots":
            digits = {"1", "2", "3", "4", "5", "6", "7", "8", "9"}
            if k > 3 and any(digit in self.str for digit in digits):
                print("Warning! Dots format is only unambiguous for 4x4, 9x9 and blank sudokus!")
            arr = []
            l = list(self.str)
            brackets = {"[", "]", "(", ")", "{", "}"}
            if l[0] in brackets:
                l = l[1:]
            if l[-1] in brackets:
                l.pop()
            puzzle_str = "." + "".join(l)
            for i in range(1, len(puzzle_str)):
                punctuation = {"0", ",", "."}
                if (puzzle_str[i - 1] in punctuation and
                        puzzle_str[i] in punctuation) or puzzle_str[i] == ".":
                    arr.append(0)
                else:
                    if puzzle_str[i] not in punctuation:
                        arr.append(int(puzzle_str[i]))
    
            if not len(arr) == k ** 4:
                print(f"Disaster! The input does not specify {k}^4 numbers including blanks!")
    
            self.arr = arr
        else: 
            self.arr = self.str
            

        self.reset()
        cand_dict = self.cand_dict

        # nbh_dict records cells in the same row, column, or box as each cell
        nbh_dict = defaultdict(set)
        for cell1 in cand_dict:
            for cell2 in cand_dict:
                if cell2 != cell1:
                    if (cell2[0] == cell1[0] or cell1[1] == cell2[1] or
                        ((cell1[0] - 1) // k == (cell2[0] - 1) // k and
                         (cell1[1] - 1) // k == (cell2[1] - 1) // k)):
                        nbh_dict[cell1].add(cell2)
        self.nbh_dict = nbh_dict

        self.bc = {
            x: [((x - 1) // k) * k + 1, ((x - 1) % k) * k + 1]
            for x in range(1, self.n + 1)
        }

        if self.verbose:
            print("Initial setup complete! Here are the data structures I have produced:\n")
            self.print_data()

    def print_data(self):
        """Prints the current values of the data for debugging."""
        if self.verbose:
            print(f"cand_dict: {self.cand_dict} \n")
            print(f"row_counter: {self.row_counter}\n")
            print(f"col_counter: {self.col_counter}\n")
            print(f"box_counter: {self.box_counter}\n")

    def print_sudoku(self, arr):
        """
        Prints the Sudoku grid in a human-readable ASCII format.
        
        Args:
            arr (list): A list of integers representing the Sudoku puzzle.
        """

        def format_val(val):
            if self.k <= 3:
                return str(val) if val != 0 else '.'
            else:
                return (str(val) if val != 0 else '.') + ' ' * (2 - len(str(val)))

        def horizontal_border():
            dash_widths = {2: 5, 3: 7, 4: 13, 5: 16, 6: 19}
            cell_width = dash_widths.get(self.k, 3 * self.k + 1)
            return " " + "".join("+" + "-" * cell_width for _ in range(self.k)) + "+"

        print(horizontal_border())
        for i in range(self.n):
            row = arr[i * self.n:(i + 1) * self.n]
            row_str = ""
            for section in range(self.k):
                section_vals = row[self.k * section:self.k * (section + 1)]
                formatted = " ".join(format_val(val) for val in section_vals)
                row_str += " | " + formatted
            row_str += " |"
            print(row_str)
            if (i + 1) % self.k == 0:
                print(horizontal_border())
    
    def reset(self):
        """
        Resets the internal state of the solver, clearing counters, solved cells, and other temporary data.
        """
        self.row_counter = [Counter()] + [
            Counter({i: self.n for i in range(1, self.n + 1)})
            for _ in range(1, self.n + 1)
        ]
        self.col_counter = [Counter()] + [
            Counter({i: self.n for i in range(1, self.n + 1)})
            for _ in range(1, self.n + 1)
        ]
        self.box_counter = [Counter()] + [
            Counter({i: self.n for i in range(1, self.n + 1)})
            for _ in range(1, self.n + 1)
        ]

        self.progress = True
        self.steps = 0
        self.solved_cells = set()
        self.guess_path = []
        self.guesses = []
        self.finished = False
        self.soln = []
        self.start = True

        self.cand_dict = {
            (row, col): set(range(1, self.k ** 2 + 1))
            for row in range(1, self.k ** 2 + 1)
            for col in range(1, self.k ** 2 + 1)
        }
    def input(self, arr, k):
        """
        Updates the candidate dictionary and counters with given puzzle values, initializing the solving process.
        
        Args:
            arr (list): The list of numbers representing the puzzle (0 for empty cells).
            k (int): The size of the smaller subgrid (e.g., 3 for a 9x9 puzzle).
        """
        row, col = 1, 1
        for i in range(len(arr)):
            if col > self.n:
                row += 1
                col = 1
            if arr[i] > 0:
                self.solve_update(self.cand_dict, (row, col), arr[i])
            col += 1
        return

    def cell_to_box(self, cell):
        k = self.k
        return k * ((cell[0] - 1) // k) + (cell[1] - 1) // k + 1

    def result(self, cand_dict):
        """Ends the solving procedure and outputs the solution or report the failure."""
        if self.soln:
            return self.soln
        if self.has_contradiction(cand_dict):
            print("Bad luck! There is no valid solution. Check your input or try a different sudoku")
        elif all([len(val) == 1 for val in cand_dict.values()]):
            print(f"Yay! Solution found! It took me {self.steps} steps and {self.attempt} attempts.")
            self.soln = [list(cand_dict[(i, j)])[0]
            for i in range(1, self.n + 1) for j in range(1, self.n + 1)]
            self.print_sudoku(self.soln)
            return list(self.soln)
        else:
            print(f"Blast, I've got stuck! I couldn't find a unique solution after taking {self.steps} steps")

    def cand_update(self, cand_dict, cell, d):
        """Updates all dicts with the removal of a candidate from a cell."""
        if self.row_counter[cell[0]][d] > 0:
            self.row_counter[cell[0]][d] -= 1
        if self.col_counter[cell[1]][d] > 0:
            self.col_counter[cell[1]][d] -= 1
        if self.box_counter[self.cell_to_box(cell)][d] > 0:
            self.box_counter[self.cell_to_box(cell)][d] -= 1

    def solve_update(self, cand_dict, cell, value):
        """
        Updates the candidate dictionary by placing a given value in a cell and eliminating it from neighbors.
        
        Args:
            cand_dict (dict): The dictionary holding candidates for each cell.
            cell (tuple): The coordinates of the cell to update (row, col).
            value (int): The value to place in the specified cell.
        """
        if self.verbose:
            print(f"running solve update on cell {cell} and digit {value}...")

        self.solved_cells.add(cell)

        self.row_counter[cell[0]][value] = 0
        self.col_counter[cell[1]][value] = 0
        self.box_counter[self.cell_to_box(cell)][value] = 0

        for d in cand_dict[cell]:
            if d != value:
                self.cand_update(cand_dict, cell, d)

        self.cand_dict[cell] = {value}
        for nbh in self.nbh_dict[cell]:
            if value in cand_dict[nbh]:
                cand_dict[nbh].discard(value)
                self.cand_update(cand_dict, nbh, value)

    def cell_solve(self, cand_dict):
        """Checks for naked singles and updates dicts accordingly."""
        if self.verbose:
            print("running cell_solve...")

        cand_dict = self.cand_dict
        for cell, cands in cand_dict.items():
            if cell not in self.solved_cells and len(cands) == 1:
                self.progress = True
                s = list(cand_dict[cell])[0]
                if self.verbose:
                    print(f"naked single {s} found in cell {cell}!")
                self.solve_update(cand_dict, cell, s)
        return cand_dict
    def single_solve(self, cand_dict):
        """Checks for hidden singles (digits that can only go in one place in a row, column, or box)."""
        if all([len(val) == 1 for val in cand_dict.values()]):
            return cand_dict

        k = self.k

        if self.verbose:
            print("running single_solve...")

        if self.has_contradiction(self.cand_dict):
            if self.guess_path:
                return self.guess(cand_dict)
            else:
                return "Contradiction found! There are no valid solutions!"

        for row in range(1, self.n + 1):
            for digit in range(1, self.n + 1):
                if self.row_counter[row][digit] == 1:
                    for col in range(1, self.n + 1):
                        if digit in cand_dict[(row, col)]:
                            cell = (row, col)
                            if self.verbose:
                                print(f"hidden single {digit} found in row {row}!")
                            self.solve_update(cand_dict, cell, digit)
                            self.progress = True
                            return cand_dict

        for col in range(1, self.n + 1):
            for digit in range(1, self.n + 1):
                if self.col_counter[col][digit] == 1:
                    for row in range(1, self.n + 1):
                        if digit in cand_dict[(row, col)]:
                            cell = (row, col)
                            if self.verbose:
                                print(f"hidden single {digit} found in col {col}!")
                            self.solve_update(cand_dict, cell, digit)
                            self.progress = True
                            return cand_dict

        for box in range(1, self.n + 1):
            for digit in range(1, self.n + 1):
                if self.box_counter[box][digit] == 1:
                    for row in range(self.bc[box][0], self.bc[box][0] + k):
                        for col in range(self.bc[box][1], self.bc[box][1] + k):
                            if digit in cand_dict[(row, col)]:
                                cell = (row, col)
                                if self.verbose:
                                    print(f"hidden single {digit} found in box {box}!")
                                self.solve_update(cand_dict, cell, digit)
                                self.progress = True
                                return cand_dict

        if self.verbose:
            print("no hidden singles found.")

    def has_contradiction(self, cand_dict):
        """Returns True if there is any contradiction in the puzzle."""
        if self.verbose:
            print("running contradiction check")
        return not all([len(val) > 0 for val in cand_dict.values()])
    def guess(self, cand_dict):
        """Makes a random guess in an unsolved cell, or backtracks if contradiction is found."""
        k = self.k
        
        if self.verbose:
            print("I couldn't find any naked or hidden singles so I'm making a guess")

        self.steps += 1
        if self.verbose:
            print(f"step {self.steps}")

        if not self.has_contradiction(self.cand_dict):
            if self.verbose:
                print("No contradiction found. Proceeding with solve...")

            if self.finished:
                return self.result(cand_dict)

            # Minimum Remaining Values (MRV) heuristic
            min_remaining_values = float('inf')
            selected_cell = None
            for cell, candidates in cand_dict.items():
                if cell not in self.solved_cells:
                    remaining_values = len(candidates)
                    if remaining_values == 2:
                        selected_cell = cell
                        break
                    if remaining_values < min_remaining_values:
                        min_remaining_values = remaining_values
                        selected_cell = cell

            if selected_cell is None:
                self.finished = True
                return self.solve(
                    max_steps=self.max_steps,
                    max_attempts=self.max_attempts
                )

            cell = selected_cell
            guess = random.choice(list(cand_dict[cell]))
            self.guesses.append((cell, guess))

            if self.verbose:
                print(f"Making guess {guess} in cell {cell}...")
                print(f"The current guess depth is {len(self.guesses)}")
                print(f"The current guesses are {self.guesses}")

            self.progress = True
            data_old = (
                copy.deepcopy(self.cand_dict),
                copy.deepcopy(self.row_counter),
                copy.deepcopy(self.col_counter),
                copy.deepcopy(self.box_counter),
                copy.deepcopy(self.solved_cells)
            )
            self.guess_path.append(data_old)
            self.solve_update(cand_dict, cell, guess)

            return self.solve(
                max_steps=self.max_steps,
                max_attempts=self.max_attempts
            )

        elif self.guess_path:
            if self.verbose:
                print("Contradiction found! Undoing latest guess...")
                print(f"Guesses are now {self.guesses}")

            self.progress = True
            data_old = self.guess_path.pop()
            wrong_guess = self.guesses.pop()
            (
                self.cand_dict,
                self.row_counter,
                self.col_counter,
                self.box_counter,
                self.solved_cells
            ) = data_old

            self.cand_update(self.cand_dict, wrong_guess[0], wrong_guess[1])
            self.cand_dict[wrong_guess[0]].discard(wrong_guess[1])

            return self.solve(
                max_steps=self.max_steps,
                max_attempts=self.max_attempts
            )

        else:
            if self.verbose:
                print("Contradiction found with no guess to undo!")
                print(f"Final cand_dict is {cand_dict}")
            self.finished = True
            return self.result(self.cand_dict)
    def solve(self, max_steps=2000, max_attempts=10):
        """
        Solves the Sudoku puzzle using naked singles, hidden singles and backtracking.
        
        Args:
            max_steps (int): The maximum number of steps to take before giving up and starting a fresh attempt (default is 2000).
            max_attempts (int): The maximum number of attempts to make if the solver gets stuck (default is 10).
        
        Returns:
            list: The solved Sudoku puzzle as a list of integers, or a message indicating failure.
        """
        self.max_steps = max_steps
        self.max_attempts = max_attempts

        if self.verbose:
            print("Running sudoku solver. Let's begin!")

        cand_dict = self.cand_dict
        if self.finished or self.soln:
            return self.result(cand_dict)
        if self.attempt > self.max_attempts:
            print("Blast! I tried really hard but I couldn't do it. Try increasing max_steps or max_attempts.")
            self.finished = True

        k = self.k
        if self.start:
            self.input(self.arr, k)
            if self.verbose:
                print("I'm giving it a go!")
            self.start = False

        while self.progress and self.steps < self.max_steps:
            self.progress = False
            self.steps += 1

            if self.verbose:
                print(f"\nAttempt {self.attempt}, step {self.steps}")
                print(f"Solved cells: {len(self.solved_cells)}")

            self.cell_solve(cand_dict)
            if not self.progress:
                self.single_solve(cand_dict)
            if not self.progress:
                return self.guess(cand_dict)

        self.attempt += 1  # If we get stuck, try a complete reset

        if self.verbose:
            print(f"I solved {len(self.solved_cells)} but then got in a pickle so I'm trying again from scratch")

        self.reset()
        return self.solve(self.max_steps, self.max_attempts)

"""Example Usage:"""

#Arto Inkala, a one of the hardest classical sudokus.
arto_inkala = "8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4.."

#A 16x16 sudoku (multiple solutions)
sudoku_16x16 = [
    0, 0,  0,  0,    0,  2,  0,  0,     12, 0,  0,  9,     0,  0,  0,  0,
    0, 0,  16, 0,    15, 0,  0,  0,     0,  0,  0,  0,     0,  8,  0,  0,
    1, 0,  0,  13,   0,  0,  0,  0,     0,  0,  0,  0,     0,  0,  0,  6,
    0, 0,  0,  0,    0,  14, 0,  0,     1,  0,  0,  0,     0,  0,  0,  0,

    0, 0,  7,  0,    0,  0,  0,  4,     0,  0,  0,  0,     0,  15, 0,  0,
    0, 0,  0,  15,   0,  0,  13, 0,     0,  0,  0,  0,     0,  0,  0,  0,
    0, 0,  0,  0,    0,  16, 0,  0,     14, 0,  0,  0,     0,  0,  0,  3,
    0, 5,  0,  0,    0,  0,  0,  0,     0,  0,  0,  0,     0,  0,  0,  0,

    0, 0,  0,  0,    0,  0,  0,  0,     0,  0,  4,  0,     2,  0,  0,  0,
    0, 0,  0,  0,    0,  0,  0,  0,     0,  13, 0,  16,    0,  0,  0,  0,
    5, 0,  0,  0,    0,  0,  0,  0,     0,  0,  0,  14,    0,  0,  9,  0,
    0, 0,  0,  0,    0,  0,  12, 0,     0,  0,  0,  0,     0,  0,  13, 0,

    0, 0,  0,  0,    0,  0,  0,  0,     0,  0,  0,  0,     11, 0,  0,  1,
    0, 3,  0,  0,    0,  0,  0,  0,     0,  2,  0,  0,     0,  0,  0,  0,
    0, 0,  2,  0,    0,  0,  0,  0,     0,  0,  0,  0,     16, 0,  0,  0,
    0, 0,  0,  14,   6,  0,  0,  0,     0,  0,  10, 0,     0,  0,  0,  0,
]

#A blank 9x9 grid
blank_grid = "".join(["." for _ in range(3 ** 4)])

#A blank 36x36 grid
blank_grid_36x36 = [0] * (6 ** 4)

#A sudoku with no solutions
no_soln = "339...4..2..7.9....87......75..6.23.6..9.4..8.28.5..41.......59...1.6..7..6...1.4"

test_1 = SudokuSolver(arto_inkala)
test_2 = SudokuSolver(sudoku_16x16, 4)
test_3 = SudokuSolver(blank_grid)
test_4 = SudokuSolver(blank_grid_36x36, 6)
test_5 = SudokuSolver(no_soln)

soln = test_1.solve()
soln = test_2.solve()
soln = test_3.solve()
soln = test_4.solve(max_steps = 5000) #max_steps should be increased for very large sudokus
soln = test_5.solve()