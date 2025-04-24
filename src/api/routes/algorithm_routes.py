import base64
import io

import networkx as nx
from random import sample
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from matplotlib import pyplot as plt

from src.models.response_models import RouteOptimizationResponse
from src.algorithm.data_generator import generate_synthetic_data
from src.algorithm.routing import find_best_route_using_djikstra
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal

from src.database.models import Bin, Route
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/optimize-route", response_model=RouteOptimizationResponse)
def optimize_route(bins: int = 10, threshold: float = 0.7, db: Session = Depends(get_db)):
    # Generate data
    graph = generate_synthetic_data(num_bins=bins)
    route, total_dist, bins_covered = find_best_route_using_djikstra(graph, threshold=threshold)

    # Convert graph node data to serializable form
    graph_data = {
        node: {
            "pos": list(attr["pos"]),
            "fill_level": attr["fill_level"]
        } for node, attr in graph.nodes(data=True)
    }

    # Save Bins
    for bin_id, data in graph_data.items():
        bin_entry = Bin(id=bin_id, position=data["pos"], fill_level=data["fill_level"])
        db.merge(bin_entry)

    db.commit()  # Save Bins to DB

    # Save Route
    route_entry = Route(
        optimized_route=route,
        total_distance=total_dist,
        bins_covered=bins_covered
    )
    db.add(route_entry)
    db.commit()

    # Return result
    return RouteOptimizationResponse(
        optimized_route=route,
        total_distance=round(total_dist, 2),
        bins_covered=bins_covered
    )


@router.get("/evaluate-route")
def evaluate_route(bins: int = 10, threshold: float = 0.7):
    graph = generate_synthetic_data(num_bins=bins)

    # Run optimized route (Dijkstra-style greedy)
    optimized_route, optimized_distance, bins_covered = find_best_route_using_djikstra(graph, threshold=threshold)

    # Simulate a random route (same full bins, shuffled)
    full_bins = [n for n, d in graph.nodes(data=True) if d["fill_level"] >= threshold]

    if len(full_bins) < 2:
        return {
            "error": "Not enough full bins to compare routes."
        }

    # Shuffle route
    random_route = sample(full_bins, len(full_bins))

    # Calculate distance for random route
    random_distance = 0
    for i in range(len(random_route) - 1):
        try:
            path = nx.shortest_path(graph, source=random_route[i], target=random_route[i+1], weight="weight")
            path_distance = sum(graph[u][v]["weight"] for u, v in zip(path[:-1], path[1:]))
            random_distance += path_distance
        except nx.NetworkXNoPath:
            continue  # Skip if disconnected

    # Calculate performance gain
    improvement = ((random_distance - optimized_distance) / random_distance) * 100 if random_distance > 0 else 0

    return {
        "optimized_route": optimized_route,
        "optimized_distance": round(optimized_distance, 2),
        "random_route": random_route,
        "random_distance": round(random_distance, 2),
        "improvement_percent": round(improvement, 2),
        "bins_compared": len(full_bins)
    }



@router.get("/view-last-route", response_class=HTMLResponse)
def view_last_route(db: Session = Depends(get_db)):
    # Get last saved route
    last_route = db.query(Route).order_by(Route.id.desc()).first()
    if not last_route:
        return HTMLResponse("<h2>No route data found.</h2>")

    # Get bin data for the route
    bin_data = db.query(Bin).filter(Bin.id.in_(last_route.optimized_route)).all()

    # Prepare for visualization
    bins_positions = {bin.id: bin.position for bin in bin_data}
    route_nodes = last_route.optimized_route

    # Visualize the graph (you can reuse the `visualize_graph` function)
    img_html = visualize_graph_from_data(bins_positions, route_nodes)

    return HTMLResponse(f"""
    <html>
    <body>
    <h2>Optimized Route Visualization</h2>
    {img_html}
    </body>
    </html>
    """)


def visualize_graph_from_data(bins_positions, route_nodes):
    import networkx as nx
    import matplotlib.pyplot as plt
    import io
    import base64

    G = nx.Graph()

    # Rebuild the graph from bin positions
    for bin_id, position in bins_positions.items():
        G.add_node(bin_id, pos=tuple(position))  # Ensure position is a tuple not list

    # Add route edges
    route_edges = [(route_nodes[i], route_nodes[i + 1]) for i in range(len(route_nodes) - 1)]
    G.add_edges_from(route_edges)

    # Extract positions
    pos = nx.get_node_attributes(G, 'pos')

    # Draw
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=600, node_color='skyblue', font_weight='bold')
    nx.draw_networkx_edges(G, pos, edgelist=route_edges, edge_color='green', width=3)

    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)

    # Encode image as base64
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    return f'<img src="data:image/png;base64,{image_base64}" />'
