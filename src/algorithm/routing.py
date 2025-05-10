import networkx as nx
from copy import deepcopy

def find_best_route_2opt(graph: nx.Graph, threshold: float = 0.7):
    """
    1) Build an initial route with the same greedy Dijkstra approach.
    2) Then repeatedly apply 2-opt swaps to remove crossing edges and shorten the tour.
    """
    # 1) Seed with greedy Dijkstra
    full_bins = [n for n, d in graph.nodes(data=True) if d["fill_level"] >= threshold]
    if len(full_bins) < 2:
        return [], 0, 0

    # greedy start
    route = [full_bins[0]]
    visited = {route[0]}
    total_dist = 0
    current = route[0]

    # build initial greedy route
    while len(visited) < len(full_bins):
        best, best_d = None, float("inf")
        for tgt in full_bins:
            if tgt in visited:
                continue
            try:
                d = nx.dijkstra_path_length(graph, current, tgt, weight="weight")
                if d < best_d:
                    best, best_d = tgt, d
            except nx.NetworkXNoPath:
                pass
        if not best:
            break
        path = nx.dijkstra_path(graph, current, best, weight="weight")
        # append intermediate nodes only if they’re new
        for n in path[1:]:
            if n not in visited:
                route.append(n)
                visited.add(n)
        total_dist += best_d
        current = best

    # 2) Precompute distance matrix between route nodes
    import functools
    @functools.lru_cache(None)
    def dist(i, j):
        return nx.dijkstra_path_length(graph, route[i], route[j], weight="weight")

    # 3) 2-opt improvement
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route) - 1):
                # cost before swap: edges (i−1→i) + (j→j+1)
                before = dist(i - 1, i) + dist(j, j + 1)
                # cost after swap: (i−1→j) + (i→j+1)
                after = dist(i - 1, j) + dist(i, j + 1)
                if after + 1e-6 < before:
                    # perform 2-opt: reverse segment [i..j]
                    route[i : j + 1] = reversed(route[i : j + 1])
                    improved = True
        if improved:
            # recompute total_dist
            total_dist = sum(dist(k, k + 1) for k in range(len(route) - 1))

    return route, total_dist, len(route)


def find_best_route_using_djikstra(graph: nx.Graph, threshold=0.7):
    """
    Finds the shortest route that connects all bins above a certain fill level using Dijkstra’s algorithm.
    This is a simplification and not a full TSP solution.
    """
    # Filter full bins
    full_bins = [node for node, attr in graph.nodes(data=True) if attr['fill_level'] >= threshold]

    if len(full_bins) < 2:
        return [], 0, 0  # Not enough bins to optimize

    total_distance = 0
    route = []

    # Greedy path: Start from the first full bin and keep going to the nearest next full bin
    current = full_bins[0]
    visited = {current}
    route.append(current)

    while len(visited) < len(full_bins):
        # Find the nearest unvisited full bin
        nearest = None
        min_dist = float('inf')

        for target in full_bins:
            if target not in visited:
                try:
                    dist = nx.dijkstra_path_length(graph, current, target, weight='weight')
                    if dist < min_dist:
                        min_dist = dist
                        nearest = target
                except nx.NetworkXNoPath:
                    continue

        if nearest is None:
            break  # No reachable bin found

        path = nx.dijkstra_path(graph, current, nearest, weight='weight')
        # Add path but avoid duplicates
        route += [node for node in path[1:] if node not in visited]
        total_distance += min_dist
        visited.add(nearest)
        current = nearest

    return route, total_distance, len(visited)

def find_best_route_using_astar(graph: nx.Graph, threshold=0.7):
    full_bins = [node for node, attr in graph.nodes(data=True) if attr['fill_level'] >= threshold]

    if len(full_bins) < 2:
        return [], 0, 0

    def heuristic(u, v):
        x1, y1 = graph.nodes[u]["pos"]
        x2, y2 = graph.nodes[v]["pos"]
        return ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5

    total_distance = 0
    route = []
    visited = set()
    current = full_bins[0]
    visited.add(current)
    route.append(current)

    while len(visited) < len(full_bins):
        nearest = None
        min_dist = float('inf')

        for target in full_bins:
            if target not in visited:
                try:
                    dist = nx.astar_path_length(graph, current, target, heuristic=heuristic, weight='weight')
                    if dist < min_dist:
                        min_dist = dist
                        nearest = target
                except nx.NetworkXNoPath:
                    continue

        if nearest is None:
            break

        path = nx.astar_path(graph, current, nearest, heuristic=heuristic, weight='weight')
        route += [node for node in path[1:] if node not in visited]
        total_distance += min_dist
        visited.add(nearest)
        current = nearest

    return route, total_distance, len(visited)


def find_naive_route(graph: nx.Graph, threshold=0.7):
    full_bins = [node for node, attr in graph.nodes(data=True) if attr['fill_level'] >= threshold]

    if len(full_bins) < 2:
        return [], 0, 0

    total_distance = 0
    route = [full_bins[0]]

    for i in range(len(full_bins) - 1):
        try:
            path = nx.shortest_path(graph, full_bins[i], full_bins[i + 1], weight='weight')
            route += [node for node in path[1:] if node not in route]
            total_distance += sum(graph[u][v]["weight"] for u, v in zip(path[:-1], path[1:]))
        except nx.NetworkXNoPath:
            continue

    return route, total_distance, len(full_bins)

