def main():
    with open('1/input.txt', 'r') as file:
        lines = file.readlines()
        start = 50
        zeroes_a = 0
        zeroes_b = 0
        for line in lines:
            direction = line[0]
            value = int(line[1:])
            if direction == 'L':
                # count how many clicks during this left rotation hit 0
                if start == 0:
                    # when starting at 0, the first time we hit 0 while
                    # rotating left is after 100 clicks
                    zeroes_b += value // 100
                elif value >= start:
                    # first hit at `start` clicks, then every +100 clicks
                    zeroes_b += (value - start) // 100 + 1
                start = (start - value) % 100
            elif direction == 'R':
                if start + value >= 100:
                    # number of times we pass or land on 0 when moving right
                    zeroes_b += (start + value) // 100
                start = (start + value) % 100
            if start == 0:
                zeroes_a += 1
        print(zeroes_a)
        print(zeroes_b)

if __name__ == "__main__":
    main()