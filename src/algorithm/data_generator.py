import random
import networkx as nx
import matplotlib.pyplot as plt

def generate_synthetic_data(num_bins=10):
    """
    Generate a random graph of bins with fill levels and distances between them.
    """
    # Create a graph
    G = nx.Graph()

    bins = []

    for i in range(num_bins):
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        fill_level = random.uniform(0, 1)  # 0 = empty, 1 = full
        bin_info = {
            "id": f"bin_{i}",
            "pos": (x, y),
            "fill_level": fill_level
        }
        bins.append(bin_info)
        G.add_node(f"bin_{i}", pos=(x, y), fill_level=fill_level)

    # Randomly connect the bins with roads (edges)
    for i in range(num_bins):
        for j in range(i+1, num_bins):
            if random.random() < 0.3:  # 30% chance of connection
                dist = distance(bins[i]["pos"], bins[j]["pos"])
                G.add_edge(bins[i]["id"], bins[j]["id"], weight=dist)

    return G

def distance(p1, p2):
    """Calculate Euclidean distance between 2D points."""
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

def visualize_graph(G, route=None):
    """
    Visualize the bin network.
    - route: Optional list of bin IDs that form the optimized path
    """
    pos = nx.get_node_attributes(G, 'pos')
    labels = nx.get_edge_attributes(G, 'weight')

    # Node colors: red for full bins, blue otherwise
    node_colors = []
    for node in G.nodes():
        fill = G.nodes[node].get("fill_level", 0)
        if fill >= 0.7:
            node_colors.append("red")
        else:
            node_colors.append("skyblue")

    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=600, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels={k: f"{v:.1f}" for k, v in labels.items()})

    # Highlight optimized route with green edges
    if route and len(route) > 1:
        route_edges = [(route[i], route[i+1]) for i in range(len(route)-1)]
        nx.draw_networkx_edges(G, pos, edgelist=route_edges, edge_color='green', width=3)

    plt.title("Waste Collection Graph with Optimized Route")
    plt.show()

