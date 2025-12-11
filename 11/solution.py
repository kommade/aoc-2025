from functools import lru_cache

def main():
    with open("11/input.txt") as f:
        lines = f.readlines()
        connections = {}
        for line in lines:
            data = line.strip().split(": ")
            key = data[0]
            values = set(data[1].split(" "))
            connections[key] = values

        start = 'you'
        end = 'out'
        visited_paths = count_paths(connections, start, end)
        print(visited_paths)

        paths_1a = count_paths(connections, 'svr', 'dac')
        paths_1b = count_paths(connections, 'dac', 'fft')
        paths_1c = count_paths(connections, 'fft', 'out')
        paths_2a = count_paths(connections, 'svr', 'fft')
        paths_2b = count_paths(connections, 'fft', 'dac')
        paths_2c = count_paths(connections, 'dac', 'out')

        total_paths = (paths_1a * paths_1b * paths_1c +
                       paths_2a * paths_2b * paths_2c)
        print(total_paths)
        

# assumes there are no cycles, or the function will loop infinitely
def count_paths(connections, start, end):
    @lru_cache(None)
    def dfs(node):
        if node == end:
            return 1
        total = 0
        for nxt in connections.get(node, ()):
            total += dfs(nxt)
        return total
    return dfs(start)     

if __name__ == "__main__":
    main()