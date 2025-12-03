def main():
    with open('3/input.txt', 'r') as file:
        banks = file.readlines()
        output = 0
        for bank in banks:
            n = 12
            s = bank.strip()
            L = len(s)
            selected = []
            start = 0
            for k in range(n):
                max_d = -1
                max_idx = -1
                # last index we may choose for this digit (inclusive)
                last = L - (n - k)
                for idx in range(start, last + 1):
                    d = int(s[idx])
                    if d > max_d:
                        max_d = d
                        max_idx = idx
                        if max_d == 9:
                            break
                if max_idx == -1:
                    break
                selected.append(max_d)
                start = max_idx + 1

            for j, d in enumerate(selected):
                output += d * (10 ** (n - 1 - j))
        print(output)

if __name__ == "__main__":
    main()
