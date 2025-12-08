def main():
    with open('7/input.txt') as file:
        lines = file.readlines()
        beam_indices = set()
        paths = { k:0 for k in range(len(lines[0].strip())) }
        start = lines[0].find('S')
        if start == -1:
            raise ValueError("Start position 'S' not found in the input.")
        beam_indices.add(start)
        paths[start] = 1
        num_splits = 0
        for line in lines[1:]:
            for i in range(len(line)):
                char = line[i]
                if char == '^' and i in beam_indices:
                    beam_indices.remove(i)
                    beam_indices.add(i - 1)
                    beam_indices.add(i + 1)
                    paths[i - 1] += paths[i]
                    paths[i + 1] += paths[i]
                    paths[i] = 0
                    num_splits += 1
                    
        print(num_splits)
        print(sum(paths.values()))
        

if __name__ == "__main__":
    main()