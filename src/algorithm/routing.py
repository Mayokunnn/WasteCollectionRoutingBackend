import functools

import networkx as nx
from networkx import NetworkXNoPath

def find_best_route(graph: nx.Graph, threshold: float = 0.7):
    """
    Builds an initial greedy route covering all full bins,
    then improves the route using 2-opt while ensuring all full bins remain in the route.
    """
    full_bins = [n for n, d in graph.nodes(data=True) if d["fill_level"] >= threshold]
    if len(full_bins) < 2:
        return [], 0, 0

    # 1. Start with greedy route (Dijkstra-based)
    route = [full_bins[0]]
    visited = {route[0]}
    total_dist = 0
    current = route[0]

    while len(visited) < len(full_bins):
        nearest = None
        min_dist = float('inf')
        for target in full_bins:
            if target not in visited:
                try:
                    dist = nx.dijkstra_path_length(graph, current, target, weight="weight")
                    if dist < min_dist:
                        nearest = target
                        min_dist = dist
                except nx.NetworkXNoPath:
                    continue

        if not nearest:
            break

        path = nx.dijkstra_path(graph, current, nearest, weight="weight")
        for node in path[1:]:
            if node not in route:
                route.append(node)
                visited.add(node)
        total_dist += min_dist
        current = nearest

    # 2. 2-opt optimization
    @functools.lru_cache(None)
    def dist(i, j):
        return nx.dijkstra_path_length(graph, route[i], route[j], weight="weight")

    improved = True
    MAX_ITERATIONS = 100000
    iteration = 0
    while improved and iteration < MAX_ITERATIONS:
        improved = False
        iteration += 1
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route) - 1):
                before = dist(i - 1, i) + dist(j, j + 1)
                after = dist(i - 1, j) + dist(i, j + 1)
                if after + 1e-6 < before:
                    route[i:j + 1] = list(reversed(route[i:j + 1]))
                    improved = True
        if improved:
            total_dist = sum(dist(k, k + 1) for k in range(len(route) - 1))

    # 3. Ensure all full bins are still present in route
    for full_bin in full_bins:
        if full_bin not in route:
            try:
                nearest_node = min(
                    route,
                    key=lambda n: nx.dijkstra_path_length(graph, full_bin, n, weight="weight")
                )
                path = nx.dijkstra_path(graph, full_bin, nearest_node, weight="weight")
                insert_idx = route.index(nearest_node)
                for node in reversed(path[:-1]):
                    if node not in route:
                        route.insert(insert_idx, node)
            except NetworkXNoPath:
                print(f"No path from {full_bin} to any node in route. Skipping.")
                continue

    return route, total_dist, len(route)

def find_best_route_using_djikstra(graph: nx.Graph, threshold=0.7):
    full_bins = [node for node, attr in graph.nodes(data=True) if attr['fill_level'] >= threshold]
    if len(full_bins) < 2:
        return [], 0, 0

    route = [full_bins[0]]
    visited = {full_bins[0]}
    current = full_bins[0]
    total_distance = 0
 
    while len(visited) < len(full_bins):
        nearest = None
        min_dist = float('inf')
        for target in full_bins:
            if target not in visited:
                try:
                    dist = nx.dijkstra_path_length(graph, current, target, weight='weight')
                    if dist < min_dist:
                        nearest = target
                        min_dist = dist
                except nx.NetworkXNoPath:
                    continue

        if nearest is None:
            break

        path = nx.dijkstra_path(graph, current, nearest, weight='weight')
        route += [node for node in path[1:] if node not in route]
        total_distance += min_dist
        visited.add(nearest)
        current = nearest

    # Ensure all full bins are in the route
    for full_bin in full_bins:
        if full_bin not in route:
            try:
                # Connect missing bin to nearest in route
                nearest = min(route, key=lambda n: nx.dijkstra_path_length(graph, full_bin, n, weight='weight'))
                path = nx.dijkstra_path(graph, full_bin, nearest, weight='weight')
                insert_idx = route.index(nearest)
                for node in reversed(path[:-1]):
                    if node not in route:
                        route.insert(insert_idx, node)
                # Update distance
                total_distance = sum(
                    nx.dijkstra_path_length(graph, route[i], route[i + 1], weight='weight')
                    for i in range(len(route) - 1)
                )
            except nx.NetworkXNoPath:
                continue

    return route, total_distance, len(route)

def find_best_route_using_astar(graph: nx.Graph, threshold=0.7):
    full_bins = [node for node, attr in graph.nodes(data=True) if attr['fill_level'] >= threshold]
    if len(full_bins) < 2:
        return [], 0, 0

    def heuristic(u, v):
        x1, y1 = graph.nodes[u]["pos"]
        x2, y2 = graph.nodes[v]["pos"]
        return ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5

    route = [full_bins[0]]
    visited = {full_bins[0]}
    current = full_bins[0]
    total_distance = 0

    while len(visited) < len(full_bins):
        nearest = None
        min_dist = float('inf')
        for target in full_bins:
            if target not in visited:
                try:
                    dist = nx.astar_path_length(graph, current, target, heuristic=heuristic, weight='weight')
                    if dist < min_dist:
                        nearest = target
                        min_dist = dist
                except nx.NetworkXNoPath:
                    continue

        if nearest is None:
            break

        path = nx.astar_path(graph, current, nearest, heuristic=heuristic, weight='weight')
        route += [node for node in path[1:] if node not in route]
        total_distance += min_dist
        visited.add(nearest)
        current = nearest

    # Ensure all full bins are in the route
    for full_bin in full_bins:
        if full_bin not in route:
            try:
                nearest = min(route, key=lambda n: nx.astar_path_length(graph, full_bin, n, heuristic=heuristic, weight='weight'))
                path = nx.astar_path(graph, full_bin, nearest, heuristic=heuristic, weight='weight')
                insert_idx = route.index(nearest)
                for node in reversed(path[:-1]):
                    if node not in route:
                        route.insert(insert_idx, node)
                total_distance = sum(
                    nx.astar_path_length(graph, route[i], route[i + 1], heuristic=heuristic, weight='weight')
                    for i in range(len(route) - 1)
                )
            except nx.NetworkXNoPath:
                continue

    return route, total_distance, len(route)


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

