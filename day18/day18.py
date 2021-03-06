from itertools import product
import networkx as nx


def gen_tunnels(input):
    tunnels = nx.Graph()
    starts = []
    for x, y in product(range(1, len(input[0]) - 1), range(1, len(input) - 1)):
        val = input[y][x]
        if val != '#':
            if 'A' <= val <= 'Z':
                tunnels.add_node((x, y), door=chr(ord(val) + 32))
            elif 'a' <= val <= 'z':
                tunnels.add_node((x, y), key=val)
            else:
                tunnels.add_node((x, y))
            if val == '@':
                starts.append((x, y))
            if input[y-1][x] != '#':
                tunnels.add_edge((x, y), (x,y-1))
            if input[y][x-1] != '#':
                tunnels.add_edge((x, y), (x-1,y))
    return tunnels, starts


def shortest_path(nodes, keys_to_get, my_keys, steps, cache):
    cache_val = cache.get((nodes, my_keys))
    if cache_val and cache_val <= steps:
        return float('inf')
    cache[(nodes, my_keys)] = steps
    if not keys_to_get:
        return steps
    min_steps = float('inf')
    for i, k in enumerate(keys_to_get):
        key, key_node, others, vault = k
        path = others[nodes[vault]]
        if not path[1] - my_keys:
            sp = shortest_path(nodes[:vault] + (key_node,) + nodes[vault+1:], keys_to_get[:i] + keys_to_get[i+1:], my_keys | {key}, steps + path[0], cache)
            min_steps = sp if sp < min_steps else min_steps
    return min_steps


def p1(inp):
    tunnels, start = gen_tunnels(inp)
    start = start.pop()
    keys_to_get = [(tunnels.nodes[t]['key'], t) for t in tunnels.nodes if tunnels.nodes[t].get('key')]
    keys_to_get2 = []
    for k1 in keys_to_get:
        others = {}
        for key, path in [(k2[1], nx.shortest_path(tunnels, k1[1], k2[1])) for k2 in keys_to_get + [('@', start)] if k1[0] != k2[0]]:
            others[key] = (len(path) - 1, {tunnels.nodes[p]['door'] for p in path if tunnels.nodes[p].get('door')})
        keys_to_get2.append((k1[0], k1[1], others, 0))
    return shortest_path((start,), keys_to_get2, frozenset(), 0, {})


def find_start(grid):
    for y, line in enumerate(grid):
        x = line.find('@')
        if x >= 0:
            return x, y


def get_vault(node, vaults):
    for i, v in enumerate(vaults):
        if node in v:
            return i


def p2(inp):
    start = find_start(inp)
    inp = [list(i) for i in inp]
    for x, y in [(0,0), (-1,0), (0,-1), (1,0), (0,1)]:
        inp[start[1]+y][start[0]+x] = '#'
    for x, y in [(-1,-1), (-1,1), (1,-1), (1,1)]:
        inp[start[1]+y][start[0]+x] = '@'
    tunnels, starts = gen_tunnels(inp)
    keys_to_get = [(tunnels.nodes[t]['key'], t) for t in tunnels.nodes if tunnels.nodes[t].get('key')]
    vaults = [tunnels.subgraph(nodes).copy() for nodes in [nx.node_connected_component(tunnels,s) for s in starts]]
    keys_to_get2 = []
    for k1 in keys_to_get:
        vault = get_vault(k1[1], vaults)
        others = {}
        for key, path in [(k2[1], nx.shortest_path(vaults[vault], k1[1], k2[1])) for k2 in keys_to_get + [('@', starts[vault])] if k2[1] in vaults[vault] and k1[0] != k2[0]]:
            others[key] = (len(path) - 1, {vaults[vault].nodes[p]['door'] for p in path if vaults[vault].nodes[p].get('door')})
        keys_to_get2.append((k1[0], k1[1], others, vault))
    return shortest_path(tuple(starts), keys_to_get2, frozenset(), 0, {})


if __name__ == "__main__":
    with open('input.txt', "r") as f:
        inp = f.readlines()
        print(f"Part 1: {p1(inp.copy())}")
        print(f"Part 2: {p2(inp.copy())}")
