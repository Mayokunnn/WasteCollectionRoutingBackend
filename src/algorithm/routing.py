import networkx as nx

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
