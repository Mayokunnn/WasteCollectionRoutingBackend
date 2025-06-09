from src.algorithm.data_generator import generate_synthetic_data, visualize_graph
from src.algorithm.routing import find_best_route, find_best_route_using_djikstra

G = generate_synthetic_data(num_bins=20)
route, total_dist, num_bins = find_best_route(G, threshold=0.7)

print("Optimized Route:", route)
print("Total Distance:", round(total_dist, 2))
print("Bins Covered:", num_bins)

visualize_graph(G, route, threshold=0.7)
