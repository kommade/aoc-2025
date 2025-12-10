from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from math import inf


def main():
    machines = parse_input("10/input.txt")
    total_indicator_presses = sum(min_indicator_presses(machine) for machine in machines)
    total_joltage_presses = sum(min_joltage_presses(machine) for machine in machines)
    print(total_indicator_presses)
    print(total_joltage_presses)


def parse_input(path):
    machines = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            lights = ""
            buttons = []
            joltages = []
            for section in line.split():
                if section.startswith('['):
                    lights = section[1:-1]
                elif section.startswith('('):
                    raw_targets = section[1:-1]
                    targets = [int(x) for x in raw_targets.split(',') if x]
                    buttons.append(Button(targets))
                elif section.startswith('{'):
                    joltages = [int(x) for x in section[1:-1].split(',') if x]
            machines.append(Machine(lights, buttons, joltages))
    return machines


def min_indicator_presses(machine):
    target_state = machine.target_light_mask
    if target_state == 0:
        return 0
    queue = deque([(0, 0)])
    visited = {0}
    while queue:
        state, presses = queue.popleft()
        if state == target_state:
            return presses
        for button in machine.buttons:
            new_state = state ^ button.bitmask
            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, presses + 1))
    raise ValueError("Indicator configuration unreachable")


def min_joltage_presses(machine):
    solver = JoltageSolver(machine)
    solution = solver.solve()
    return sum(solution)


class Machine:
    def __init__(self, light_pattern, buttons, required_joltages):
        self.num_lights = len(light_pattern)
        self.buttons = buttons
        self.required_joltages = required_joltages
        self.target_light_mask = 0
        for idx, char in enumerate(light_pattern):
            if char == '#':
                self.target_light_mask |= (1 << idx)


class Button:
    def __init__(self, toggles):
        self.toggles = toggles
        self.bitmask = 0
        for toggle in toggles:
            self.bitmask |= (1 << toggle)


@dataclass
class PivotExpression:
    pivot_col: int
    const: Fraction
    coeffs: list


@dataclass
class Constraint:
    base: Fraction
    coeffs: list


class JoltageSolver:
    def __init__(self, machine):
        self.target = machine.required_joltages
        self.buttons = machine.buttons
        self.num_counters = len(self.target)
        self.num_buttons = len(self.buttons)
        self.matrix = self._build_matrix()
        self.upper_bounds = self._compute_button_upper_bounds()

    def _build_matrix(self):
        matrix = [[0] * self.num_buttons for _ in range(self.num_counters)]
        for col, button in enumerate(self.buttons):
            for idx in button.toggles:
                if idx >= self.num_counters:
                    raise ValueError("Button references unknown counter")
                matrix[idx][col] = 1
        return matrix

    def _compute_button_upper_bounds(self):
        upper_bounds = []
        for button in self.buttons:
            if not button.toggles:
                upper_bounds.append(0)
                continue
            upper = min(self.target[idx] for idx in button.toggles)
            upper_bounds.append(upper)
        return upper_bounds

    def solve(self):
        system = LinearSystem(self.matrix, self.target, self.upper_bounds)
        return system.solve()


class LinearSystem:
    def __init__(self, matrix, rhs, upper_bounds):
        self.matrix = matrix
        self.rhs = rhs
        self.upper_bounds = upper_bounds
        self.num_rows = len(matrix)
        self.num_cols = len(matrix[0]) if matrix else 0

    def solve(self):
        _, free_cols, free_uppers, expressions = self._gaussian_elimination()
        if not free_cols:
            values = [Fraction(0) for _ in range(self.num_cols)]
            for expr in expressions:
                values[expr.pivot_col] = expr.const
            ints = self._fractions_to_ints(values)
            if ints is None:
                raise ValueError("Unique solution is not integral")
            return ints
        constraints = self._build_constraints(expressions)
        best_solution = None
        best_cost = inf
        assignment = []
        free_upper_fracs = [Fraction(val) for val in free_uppers]

        def dfs(index, partial_cost):
            nonlocal best_solution, best_cost
            if partial_cost >= best_cost:
                return
            if index == len(free_cols):
                candidate = self._evaluate_solution(free_cols, assignment, expressions)
                if candidate is None:
                    return
                cost = sum(candidate)
                if cost < best_cost:
                    best_cost = cost
                    best_solution = candidate
                return
            ub = free_uppers[index]
            for value in range(ub + 1):
                assignment.append(value)
                if self._constraints_possible(constraints, assignment, free_upper_fracs):
                    dfs(index + 1, partial_cost + value)
                assignment.pop()

        dfs(0, 0)
        if best_solution is None:
            raise ValueError("No feasible integer solution for joltages")
        return best_solution

    def _gaussian_elimination(self):
        matrix = [[Fraction(val) for val in row] for row in self.matrix]
        rhs = [Fraction(val) for val in self.rhs]
        pivot_cols = []
        row = 0
        for col in range(self.num_cols):
            pivot = None
            for candidate in range(row, self.num_rows):
                if matrix[candidate][col] != 0:
                    pivot = candidate
                    break
            if pivot is None:
                continue
            matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
            rhs[row], rhs[pivot] = rhs[pivot], rhs[row]
            factor = matrix[row][col]
            for c in range(self.num_cols):
                matrix[row][c] /= factor
            rhs[row] /= factor
            for other in range(self.num_rows):
                if other == row:
                    continue
                scale = matrix[other][col]
                if scale == 0:
                    continue
                for c in range(self.num_cols):
                    matrix[other][c] -= scale * matrix[row][c]
                rhs[other] -= scale * rhs[row]
            pivot_cols.append(col)
            row += 1
            if row == self.num_rows:
                break
        for remaining in range(row, self.num_rows):
            if all(matrix[remaining][c] == 0 for c in range(self.num_cols)) and rhs[remaining] != 0:
                raise ValueError("Inconsistent system")
        free_cols = [c for c in range(self.num_cols) if c not in pivot_cols]
        free_info = sorted(((c, self.upper_bounds[c]) for c in free_cols), key=lambda item: item[1])
        free_cols = [info[0] for info in free_info]
        free_uppers = [info[1] for info in free_info]
        free_index = {col: idx for idx, col in enumerate(free_cols)}
        expressions = []
        for row_idx, pivot_col in enumerate(pivot_cols):
            const = rhs[row_idx]
            coeffs = [Fraction(0) for _ in range(len(free_cols))]
            for free_col in free_cols:
                coeff = -matrix[row_idx][free_col]
                if coeff != 0:
                    coeffs[free_index[free_col]] = coeff
            expressions.append(PivotExpression(pivot_col, const, coeffs))
        return pivot_cols, free_cols, free_uppers, expressions

    def _build_constraints(self, expressions):
        constraints = []
        for expr in expressions:
            constraints.append(Constraint(expr.const, expr.coeffs))
            upper = Fraction(self.upper_bounds[expr.pivot_col])
            coeffs = [(-coeff) for coeff in expr.coeffs]
            constraints.append(Constraint(upper - expr.const, coeffs))
        return constraints

    def _constraints_possible(self, constraints, assignment, upper_fracs):
        length = len(assignment)
        for constraint in constraints:
            total = constraint.base
            for idx in range(length):
                total += constraint.coeffs[idx] * Fraction(assignment[idx])
            for idx in range(length, len(constraint.coeffs)):
                coeff = constraint.coeffs[idx]
                if coeff > 0:
                    total += coeff * upper_fracs[idx]
            if total < 0:
                return False
        return True

    def _evaluate_solution(self, free_cols, free_values, expressions):
        values = [Fraction(0) for _ in range(self.num_cols)]
        for idx, col in enumerate(free_cols):
            values[col] = Fraction(free_values[idx])
        for expr in expressions:
            total = expr.const
            for coeff, assigned in zip(expr.coeffs, free_values):
                if coeff != 0:
                    total += coeff * Fraction(assigned)
            values[expr.pivot_col] = total
        return self._fractions_to_ints(values)

    def _fractions_to_ints(self, fractions):
        result = []
        for idx, value in enumerate(fractions):
            if value.denominator != 1:
                return None
            integer = value.numerator
            if integer < 0 or integer > self.upper_bounds[idx]:
                return None
            result.append(integer)
        return result


if __name__ == "__main__":
    main()