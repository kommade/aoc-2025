from functools import reduce

def main():
    with open('6/input.txt', 'r') as file:
        lines = file.readlines()

        def lookahead_not_empty(index):
            for i in range(0, len(lines) - 1):
                if lines[i][index].strip() != '':
                    return True
            return False
        
        total = 0
        total_b = 0
        index = 0
        while index < len(lines[0]):
            number_arr = [0 for _ in range(len(lines) - 1)]
            number_arr_b = []
            operation = lines[-1][index]
            for i in range(0, len(lines) - 1):
                j = 0
                while True:
                    if lookahead_not_empty(index + j):
                        if j == len(number_arr_b):
                            number_arr_b.append(0)
                        if lines[i][index + j].strip() != '':
                            number_arr[i] = number_arr[i] * 10 + int(lines[i][index + j])
                            number_arr_b[j] = number_arr_b[j] * 10 + int(lines[i][index + j])
                    else:
                        break
                    j += 1
            if operation == '+':
                result = sum(number_arr)
                result_b = sum(number_arr_b)
            elif operation == '*':
                result = reduce(lambda x, y: x * y, number_arr, 1)
                result_b = reduce(lambda x, y: x * y, number_arr_b, 1)
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            total += result
            total_b += result_b
            index += j + 1
        print(total)
        print(total_b)

if __name__ == "__main__":
    main()
