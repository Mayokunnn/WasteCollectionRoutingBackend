import random
import networkx as nx
import matplotlib.pyplot as plt

# Constants
DEFAULT_NUM_BINS = 20

# Generate fixed positions for bins once
FIXED_POSITIONS = {
    f"bin_{i}": (random.uniform(0, 100), random.uniform(0, 100))
    for i in range(DEFAULT_NUM_BINS)
}

# Generate fixed edges once
FIXED_EDGES = []
for i in range(DEFAULT_NUM_BINS):
    for j in range(i + 1, DEFAULT_NUM_BINS):
        if random.random() < 0.3:  # 30% chance of connection
            FIXED_EDGES.append((f"bin_{i}", f"bin_{j}"))

def distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def generate_synthetic_data(num_bins=20):
    fixed_random = random.Random(42)  # for consistent positions and edges
    dynamic_random = random.Random()  # no seed = random every time

    G = nx.Graph()

    for i in range(num_bins):
        x = fixed_random.uniform(0, 100)
        y = fixed_random.uniform(0, 100)
        fill_level = dynamic_random.uniform(0, 1)  # this now changes every call
        G.add_node(f"bin_{i}", pos=(x, y), fill_level=fill_level)

    for i in range(num_bins):
        for j in range(i + 1, num_bins):
            if fixed_random.random() < 0.3:  # connection still deterministic
                pos_i = G.nodes[f"bin_{i}"]["pos"]
                pos_j = G.nodes[f"bin_{j}"]["pos"]
                dist = ((pos_i[0] - pos_j[0])**2 + (pos_i[1] - pos_j[1])**2)**0.5
                G.add_edge(f"bin_{i}", f"bin_{j}", weight=dist)

    return G

def visualize_graph(G, route=None):
    pos = nx.get_node_attributes(G, 'pos')
    edge_labels = nx.get_edge_attributes(G, 'weight')

    node_colors = [
        "red" if G.nodes[node].get("fill_level", 0) >= 0.7 else "skyblue"
        for node in G.nodes()
    ]

    plt.figure(figsize=(10, 8))
    nx.draw(
        G, pos,
        with_labels=True,
        node_color=node_colors,
        node_size=600,
        font_weight='bold'
    )
    nx.draw_networkx_edge_labels(G, pos, edge_labels={k: f"{v:.1f}" for k, v in edge_labels.items()})
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.5)

    if route and len(route) > 1:
        route_edges = [(route[i], route[i + 1]) for i in range(len(route) - 1)]
        nx.draw_networkx_edges(G, pos, edgelist=route_edges, edge_color='green', width=3)

    plt.title("Waste Collection Network")
    plt.axis("off")
    plt.tight_layout()
    plt.show()
