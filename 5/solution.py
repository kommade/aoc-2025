def main():
    with open('5/input.txt', 'r') as file:
        lines = file.readlines()
        ranges = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line == '':
                break
            start, end = map(int, line.split('-'))
            ranges.append(Range(start, end))
            i += 1
        fresh = 0
        for line in lines[i+1:]:
            value = int(line.strip())
            if any(r.contains(value) for r in ranges):
                fresh += 1
        print(fresh)

        sorted_ranges = sorted(ranges, key=lambda r: r.start)
        total = 0
        prev_end = 0
        for range in sorted_ranges:
            if range.start > prev_end:
                total += range.end - range.start + 1
                prev_end = range.end
            elif range.end > prev_end:
                total += range.end - prev_end
                prev_end = range.end
        print(total)

class Range:
        def __init__(self, start, end):
            self.start = start
            self.end = end
        
        def contains(self, value):
            return self.start <= value <= self.end
        
        
if __name__ == "__main__":
    main()