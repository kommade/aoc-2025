# i try not to use external libraries, but this is taking forever otherwise
from concurrent.futures import ProcessPoolExecutor

"""
NB: It seems like all the no-solution cases are trivial, which is exteremely
disappointing. I implemented the full algorithm X solver for nothing. This
entire file could have been replaced with a simple area check. WTF.
"""

def solve_area(args):
    area, all_shapes, shape_cells = args
    rows, columns, _ = area.build_matrix(all_shapes, shape_cells)
    if not rows or not columns:
        print(f"Area {area.x}x{area.y} with constraints {area.constraints} has NO solution (trivially).")
        return (area, False)
    return (area, algorithm_x(rows, columns))

# warning: this takes a minute to run
def main():
    with open("12/input.txt") as f:
        raw_input = []
        current = []
        for line in f.readlines():
            if not line.strip():
                if current:
                    raw_input.append(current)
                    current = []
                continue
            current.append(line.strip())
        if current:
            raw_input.append(current)

    areas = [Area(raw) for raw in raw_input[-1]]
    shapes_raw = raw_input[:-1]

    shapes = [
        [
            (r, c)
            for r, row in enumerate(shape)
            for c, ch in enumerate(row)
            if ch == "#"
        ]
        for shape in shapes_raw
    ]

    all_shapes = [get_shape_rotations_and_flips(shape) for shape in shapes]
    shape_cells = [len(shape) for shape in shapes]

    has_solution = 0
    jobs = [(area, all_shapes, shape_cells) for area in areas]
    with ProcessPoolExecutor() as executor:
        for area, solution in executor.map(solve_area, jobs):
            if solution:
                has_solution += 1
                print(f"Area {area.x}x{area.y} with constraints {area.constraints} has a solution.")
            elif solution is None:
                print(f"Area {area.x}x{area.y} with constraints {area.constraints} has NO solution.")
    print(f"Total areas with solutions: {has_solution} out of {len(areas)}")


def algorithm_x(rows, columns):
    if not rows:
        return [] if all(col.get("primary", True) is False or col["required"] == 0 for col in columns) else None

    column_rows = [set() for _ in columns]
    for row_idx, cols in enumerate(rows):
        for col in cols:
            column_rows[col].add(row_idx)

    remaining = [col["required"] for col in columns]
    primary_cols = {idx for idx, col in enumerate(columns) if col.get("primary", True) and remaining[idx] > 0}
    row_active = [True] * len(rows)
    solution = []

    def select_column():
        best_col = None
        best_candidates = None
        best_len = None
        for col in primary_cols:
            candidates = [r for r in column_rows[col] if row_active[r]]
            if not candidates:
                return None, None
            if best_len is None or len(candidates) < best_len:
                best_len = len(candidates)
                best_col = col
                best_candidates = candidates
        return best_col, best_candidates

    def apply_row(row_idx):
        actions = []
        if not row_active[row_idx]:
            return False, actions

        row_active[row_idx] = False
        actions.append(("row", row_idx))
        solution.append(row_idx)
        actions.append(("solution", row_idx))

        for col in rows[row_idx]:
            prev_val = remaining[col]
            actions.append(("remaining", col, prev_val))
            remaining[col] = prev_val - 1
            if remaining[col] < 0:
                return False, actions
            if columns[col].get("primary", True) and prev_val > 0 and remaining[col] == 0 and col in primary_cols:
                primary_cols.remove(col)
                actions.append(("primary_removed", col))
            if remaining[col] == 0:
                for other_row in column_rows[col]:
                    if row_active[other_row]:
                        row_active[other_row] = False
                        actions.append(("row", other_row))
        return True, actions

    def undo(actions):
        while actions:
            action = actions.pop()
            kind = action[0]
            if kind == "row":
                row_active[action[1]] = True
            elif kind == "solution":
                solution.pop()
            elif kind == "remaining":
                remaining[action[1]] = action[2]
            elif kind == "primary_removed":
                primary_cols.add(action[1])

    def search():
        if not primary_cols:
            return True
        col, candidates = select_column()
        if col is None or not candidates:
            return False
        for row_idx in candidates:
            success, actions = apply_row(row_idx)
            if not success:
                undo(actions)
                continue
            if search():
                return True
            undo(actions)
        return False

    return solution.copy() if search() else None


class Area:
    def __init__(self, raw: str):
        sizes, counts = raw.split(":")
        height, width = map(int, sizes.split("x"))
        self.y = height
        self.x = width
        self.constraints = [int(i) for i in counts.strip().split(" ")]

    def build_matrix(self, all_shapes, shape_areas):
        rows = []
        placements = []

        required_cells = sum(count * shape_areas[i] for i, count in enumerate(self.constraints))
        if required_cells > self.x * self.y:
            # if there are more required cells than available, no solution is possible
            # the solver will get stuck forever otherwise
            return [], [], []

        num_shape_cols = len(self.constraints)
        cell_col_offset = num_shape_cols

        for shape_index, variants in enumerate(all_shapes):
            need = self.constraints[shape_index]
            if need == 0:
                continue
            for variant in variants:
                h, w = shape_dimensions(variant)
                for top in range(self.y - h + 1):
                    for left in range(self.x - w + 1):
                        cell_cols = []
                        ok = True
                        for dr, dc in variant:
                            abs_r = top + dr
                            abs_c = left + dc
                            if not (0 <= abs_r < self.y and 0 <= abs_c < self.x):
                                ok = False
                                break
                            cell_cols.append(cell_col_offset + abs_r * self.x + abs_c)
                        if not ok:
                            continue
                        rows.append([shape_index] + cell_cols)
                        placements.append((shape_index, tuple(variant), (top, left)))

        columns = [
            {"name": f"P{idx}", "required": need, "primary": True}
            for idx, need in enumerate(self.constraints)
        ]
        columns.extend(
            {"name": f"C{r},{c}", "required": 1, "primary": False}
            for r in range(self.y)
            for c in range(self.x)
        )
        return rows, columns, placements


def get_shape_rotations_and_flips(shape):
    base = normalize(shape)
    seen = set()
    variants = []
    current = base
    for _ in range(4):
        for oriented in (current, flip_horizontal(current)):
            key = tuple(oriented)
            if key not in seen:
                seen.add(key)
                variants.append(oriented)
        current = rotate90(current)
    return variants


def normalize(shape):
    min_r = min(r for r, _ in shape)
    min_c = min(c for _, c in shape)
    return sorted((r - min_r, c - min_c) for r, c in shape)


def rotate90(shape):
    return normalize([(c, -r) for r, c in shape])


def flip_horizontal(shape):
    return normalize([(r, -c) for r, c in shape])


def shape_dimensions(shape):
    max_r = max(r for r, _ in shape)
    max_c = max(c for _, c in shape)
    return max_r + 1, max_c + 1


if __name__ == "__main__":
    main()