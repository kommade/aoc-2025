def main():
    with open('4/input.txt', 'r') as file:
        lines = file.readlines()

        def is_empty(x, y):
            if x < 0 or y < 0 or y >= len(lines) or x >= len(lines[0].strip()):
                return True
            elif lines[y][x] == ".":
                return True
            return False
        
        part_b = True  # Change to True for part B logic
        removed = 0
        accessible = -1
        while accessible != 0:
            accessible = 0
            for y in range(len(lines)):
                for x in range(len(lines[y].strip())):
                    if not is_empty(x, y):
                        count = 0
                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                if dy == 0 and dx == 0:
                                    continue
                                if not is_empty(x + dx, y + dy):
                                    count += 1
                        if count < 4:
                            accessible += 1
                            if part_b:
                                lines[y] = lines[y][:x] + "." + lines[y][x+1:]
            if not part_b:
                print(accessible)
                break
            removed += accessible

    if part_b:
        print(removed)

if __name__ == "__main__":
    main()