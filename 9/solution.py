from collections import deque

def main():
    with open('9/input.txt') as f:
        lines = f.readlines()
        points = []
        for line in lines:
            x, y = map(int, line.strip().split(','))
            points.append((x, y))

    outside_prefix, x_lookup, y_lookup = build_outside_prefix(points)

    greatest_area = 0
    greatest_area_b = 0

    for i in range(len(points)):
        x1, y1 = points[i]
        for j in range(i + 1, len(points)):
            x2, y2 = points[j]
            area = abs(x1 - x2) + 1
            area *= abs(y1 - y2) + 1
            if area > greatest_area:
                greatest_area = area

            if abs(j - i) > 1:
                x_lo_idx = x_lookup[min(x1, x2)]
                x_hi_idx = x_lookup[max(x1, x2)]
                y_lo_idx = y_lookup[min(y1, y2)]
                y_hi_idx = y_lookup[max(y1, y2)]
                if not rectangle_has_outside(outside_prefix, x_lo_idx, x_hi_idx, y_lo_idx, y_hi_idx):
                    if area > greatest_area_b:
                        greatest_area_b = area

    print(greatest_area)
    print(greatest_area_b)

def rectangle_has_outside(prefix, x_start, x_end, y_start, y_end):
    if x_start == x_end or y_start == y_end:
        return False
    total = prefix[y_end][x_end] - prefix[y_start][x_end] - prefix[y_end][x_start] + prefix[y_start][x_start]
    return total > 0


def build_outside_prefix(points):
    xs = sorted({p[0] for p in points} | {p[0] - 1 for p in points} | {p[0] + 1 for p in points})
    ys = sorted({p[1] for p in points} | {p[1] - 1 for p in points} | {p[1] + 1 for p in points})

    x_lookup = {value: idx for idx, value in enumerate(xs)}
    y_lookup = {value: idx for idx, value in enumerate(ys)}

    width = len(xs) - 1
    height = len(ys) - 1

    block_vertical = [[False] * (width + 1) for _ in range(height)]
    block_horizontal = [[False] * width for _ in range(height + 1)]

    for idx in range(len(points)):
        x1, y1 = points[idx]
        x2, y2 = points[(idx + 1) % len(points)]
        if x1 == x2:
            x_line_idx = x_lookup[x1]
            y_lo = min(y1, y2)
            y_hi = max(y1, y2)
            y_start = y_lookup[y_lo]
            y_end = y_lookup[y_hi]
            for y in range(y_start, y_end):
                block_vertical[y][x_line_idx] = True
        else:
            y_line_idx = y_lookup[y1]
            x_lo = min(x1, x2)
            x_hi = max(x1, x2)
            x_start = x_lookup[x_lo]
            x_end = x_lookup[x_hi]
            for x in range(x_start, x_end):
                block_horizontal[y_line_idx][x] = True

    outside = [[False] * width for _ in range(height)]
    q = deque()
    start = (0, 0)
    q.append(start)
    outside[start[1]][start[0]] = True

    while q:
        cx, cy = q.popleft()

        # move left
        if cx > 0 and not block_vertical[cy][cx]:
            nx, ny = cx - 1, cy
            if not outside[ny][nx]:
                outside[ny][nx] = True
                q.append((nx, ny))

        # move right
        if cx < width - 1 and not block_vertical[cy][cx + 1]:
            nx, ny = cx + 1, cy
            if not outside[ny][nx]:
                outside[ny][nx] = True
                q.append((nx, ny))

        # move up
        if cy > 0 and not block_horizontal[cy][cx]:
            nx, ny = cx, cy - 1
            if not outside[ny][nx]:
                outside[ny][nx] = True
                q.append((nx, ny))

        # move down
        if cy < height - 1 and not block_horizontal[cy + 1][cx]:
            nx, ny = cx, cy + 1
            if not outside[ny][nx]:
                outside[ny][nx] = True
                q.append((nx, ny))

    outside_grid = [[1 if outside[row][col] else 0 for col in range(width)] for row in range(height)]
    prefix = [[0] * (width + 1) for _ in range(height + 1)]
    for y in range(height):
        row_total = 0
        for x in range(width):
            row_total += outside_grid[y][x]
            prefix[y + 1][x + 1] = prefix[y][x + 1] + row_total

    return prefix, x_lookup, y_lookup


if __name__ == "__main__":
    main()