import math

def main():
    with open('8/input.txt') as file:
        lines = file.readlines()
        circuits = {}
        boxes = {}
        for i in range(0, len(lines)):
            line = lines[i]
            x, y, z = map(int, line.strip().split(','))
            box = Box(x, y, z, i)
            boxes[i] = box
            circuit = Circuit(i)
            circuit.add_box(i)
            circuits[i] = circuit

        pair_distances = []
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                pair_distances.append((distance(boxes[i], boxes[j]), i, j))

        pair_distances.sort(key=lambda entry: entry[0])
        max_connections = min(1000, len(pair_distances))

        part_a = False

        if part_a:
            for idx in range(max_connections):
                _, box_a_idx, box_b_idx = pair_distances[idx]
                merge_circuits(boxes[box_a_idx], boxes[box_b_idx], circuits, boxes)
            
            sorted_sizes = sorted([circuit.size() for circuit in circuits.values()], reverse=True)

            print(sorted_sizes[0] * sorted_sizes[1] * sorted_sizes[2])
        else:
            box_a = None
            box_b = None
            while len(circuits) > 1:
                idx = 0
                _, box_a_idx, box_b_idx = pair_distances[idx]
                box_a = boxes[box_a_idx]
                box_b = boxes[box_b_idx]
                # if this operation closes a loop, we can't merge the circuits
                if box_a.circuit_id != box_b.circuit_id:
                    merge_circuits(box_a, box_b, circuits, boxes)
                    idx += 1
                else:
                    # but add it back to the end of the list to try again later
                    pair_distances.append(pair_distances.pop(idx))
            if not box_a or not box_b:
                raise Exception("No boxes were merged")
            print(box_a.x * box_b.x)
            

def distance(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2 + (p1.z - p2.z) ** 2)

def merge_circuits(box_a, box_b, circuits, boxes):
    circuit_a = circuits[box_a.circuit_id]
    circuit_b = circuits[box_b.circuit_id]
    if circuit_a.id == circuit_b.id:
        return

    if circuit_a.size() < circuit_b.size():
        smaller_circuit = circuit_a
        larger_circuit = circuit_b
    else:
        smaller_circuit = circuit_b
        larger_circuit = circuit_a

    for bid in smaller_circuit.boxes:
        boxes[bid].circuit_id = larger_circuit.id
        larger_circuit.add_box(bid)
    del circuits[smaller_circuit.id]
        

class Box:
    def __init__(self, x, y, z, bid):
        self.x = x
        self.y = y
        self.z = z
        self.box_id = bid
        self.circuit_id = bid

class Circuit:
    def __init__(self, id):
        self.id = id
        self.boxes = []
    
    def add_box(self, *bids):
        for box in bids:
            self.boxes.append(box)

    def size(self):
        return len(self.boxes)

if __name__ == "__main__":
    main()