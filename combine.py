#!/usr/bin/env python3

# Takes in a file containing disjoint k-moves and combines them into possible gainful k-moves.
# Note that the newly combined moves may break the tour into multiple cycles.

import json

def read_instance(path):
    """Reads a TSPLIB-formatted TSP instance (not tour) file. """
    coordinates = []
    with open(path, "r") as f:
        for line in f:
            if "NODE_COORD_SECTION" in line:
                break
        for line in f:
            line = line.strip()
            if "EOF" in line or not line:
                break
            fields = line.strip().split()
            coordinates.append((float(fields[1]), float(fields[2])))
    return coordinates

def read_moves(path):
    """Reads a JSON file containing a list of two sets of edges, each representing disjoint k-moves. """
    return json.load(open(path, 'r'))

def distance(instance, i, j):
    # i and j are index + 1.
    i -= 1
    j -= 1
    assert(i >= 0 and j >= 0)
    dx = instance[i][0] - instance[j][0]
    dy = instance[i][1] - instance[j][1]
    return round((dx ** 2 + dy ** 2) ** 0.5)
def edge_cost(instance, edge):
    return distance(instance, edge[0], edge[1])
def edge_cost_sum(instance, edges):
    total = 0
    for e in edges:
        total += edge_cost(instance, e)
    return total

def compute_costs(moves):
    new_moves = []
    for m in moves:
        cost = edge_cost_sum(instance, m[0]) - edge_cost_sum(instance, m[1])
        new_moves.append((cost, m))
    new_moves.sort(reverse = True)
    return new_moves

calls = 0

def discover_moves(kmin, base_moves, current_move, new_moves, i):
    if i >= len(base_moves):
        return
    if base_moves[i][0] + current_move[0] <= 0:
        return

    global calls
    calls += 1

    current_move[0] += base_moves[i][0]
    current_move[1] += len(base_moves[i][1][0])
    current_move[2].append(i)
    if current_move[1] >= kmin:
        new_moves.append([current_move[0], current_move[1], current_move[2][:]])
    discover_moves(kmin, base_moves, current_move, new_moves, i + 1)
    current_move[0] -= base_moves[i][0]
    current_move[1] -= len(base_moves[i][1][0])
    current_move[2].pop()

    discover_moves(kmin, base_moves, current_move, new_moves, i + 1)

import sys

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("arguments: instance_file moves_file minimum_k output_file")
        sys.exit()

    instance = read_instance(sys.argv[1])
    moves = compute_costs(read_moves(sys.argv[2]))
    kmin = int(sys.argv[3])
    output_file = sys.argv[4]

    current_move = [0, 0, []]
    new_moves = []
    discover_moves(kmin, moves, current_move, new_moves, 0)
    print(f'got {len(new_moves)} move combinations.')
    print(f'function calls: {calls}')

    converts = []
    for m in new_moves:
        convert = [[], []]
        for i in m[2]:
            convert[0] += moves[i][1][0]
            convert[1] += moves[i][1][1]
        assert(len(convert[0]) == len(convert[1]))
        converts.append(convert)
    assert(len(converts) == len(new_moves))

    json.dump(converts, open(output_file, 'w'))
