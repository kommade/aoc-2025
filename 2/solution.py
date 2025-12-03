def main():
    with open('2/input.txt', 'r') as file:
        ranges = file.readlines()[0].strip().split(',')
        counter_a = 0
        counter_b = 0
        for r in ranges:
            low, high = map(int, r.split('-'))
            for n in range(low, high + 1):
                n_str = str(n)
                if len(n_str) == 1:
                    continue
                if check_n(n_str, True):
                    counter_a += n
                if check_n(n_str, False):
                    counter_b += n
        print(counter_a)
        print(counter_b)

def check_n(n_str, only_two):
    L = len(n_str)
    if only_two:
        if L % 2 != 0:
            return False
        half = L // 2
        return n_str[:half] * 2 == n_str

    for i in range(1, L // 2 + 1):
        if L % i != 0:
            continue
        chunk = n_str[:i]
        if chunk * (L // i) == n_str:
            return True
    return False

if __name__ == "__main__":
    main()