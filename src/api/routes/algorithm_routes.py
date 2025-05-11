import networkx as nx
import matplotlib
matplotlib.use('Agg')
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
import matplotlib.pyplot as plt
import io
import base64
import uuid

from src.models.response_models import RouteOptimizationResponse
from src.algorithm.data_generator import generate_synthetic_data
from src.algorithm.routing import find_best_route_using_djikstra, find_best_route, find_best_route_using_astar, \
    find_naive_route
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal

from src.database.models import Bin, Route

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/optimize-route", response_model=RouteOptimizationResponse)
def optimize_route(bins: int = 20, threshold: float = 0.7, db: Session = Depends(get_db)):
    graph = generate_synthetic_data(num_bins=bins)
    route, total_dist, bins_covered = find_best_route(graph, threshold=threshold)

    # Convert graph node data to serializable form
    graph_data = {
        node: {
            "pos": list(attr["pos"]),
            "fill_level": attr["fill_level"]
        } for node, attr in graph.nodes(data=True)
    }
    batch_id = str(uuid.uuid4())

    for bin_id, data in graph_data.items():
        bin_entry = Bin(id=bin_id, position=data["pos"], fill_level=data["fill_level"], batch_id=batch_id)
        db.merge(bin_entry)

    db.commit()  # Save Bins to DB

    edges_data = []
    for u, v, data in graph.edges(data=True):
        edges_data.append({
            "from": u,
            "to": v,
            "weight": data["weight"]
        })

    # Save Route with edges
    route_entry = Route(
        optimized_route=route,
        total_distance=total_dist,
        bins_covered=bins_covered,
        batch_id=batch_id,
        edges=edges_data
    )

    db.add(route_entry)
    db.commit()

    # Return result
    return RouteOptimizationResponse(
        optimized_route=route,
        total_distance=round(total_dist, 2),
        bins_covered=bins_covered
    )

@router.get("/view-last-route", response_class=HTMLResponse)
def view_last_route(db: Session = Depends(get_db)):
    # Get last saved route
    last_route = db.query(Route).order_by(Route.id.desc()).first()
    if not last_route:
        return HTMLResponse("<h2>No route data found.</h2>")

    last_route = db.query(Route).order_by(Route.id.desc()).first()
    bin_data = db.query(Bin).filter(Bin.batch_id == last_route.batch_id).all()

    bins_positions = {b.id: b.position for b in bin_data}
    route_nodes = last_route.optimized_route

    img_html = visualize_graph_from_data(
        bins_positions,
        route_nodes,
        edges=last_route.edges,
        fill_level_data={b.id: b.fill_level for b in bin_data}
    )

    return HTMLResponse(f"""
    <html>
    <body>
    <h2>Optimized Route Visualization</h2>
    {img_html}
    </body>
    </html>
    """)


def visualize_graph_from_data(bins_positions, route_nodes, edges, fill_level_data=None, threshold=0.7):
    G = nx.Graph()

    for bin_id, pos in bins_positions.items():
        G.add_node(bin_id, pos=tuple(pos))

    # Add original edges
    for edge in edges:
        G.add_edge(edge["from"], edge["to"], weight=edge["weight"])

    # Coloring nodes based on fill level
    node_colors = []
    for node in G.nodes():
        fill = fill_level_data.get(node, 0) if fill_level_data else 0
        node_colors.append("red" if fill >= threshold else "skyblue")

    # Route edges (highlighted)
    route_edges = [(route_nodes[i], route_nodes[i + 1]) for i in range(len(route_nodes) - 1)]

    pos = nx.get_node_attributes(G, 'pos')
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=600, node_color=node_colors, font_weight='bold')
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.3)  # All original edges
    nx.draw_networkx_edges(G, pos, edgelist=route_edges, edge_color='green', width=3)  # Optimized route

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)

    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    return f'<img src="data:image/png;base64,{image_base64}" />'


@router.get("/compare-algorithms")
def compare_algorithms(threshold: float = 0.7, db: Session = Depends(get_db)):
    # Get the most recent batch ID from the routes table
    last_route = db.query(Route).order_by(Route.id.desc()).first()
    if not last_route:
        return {"error": "No optimized route found yet."}

    # Get all bins from the same batch
    bin_data = db.query(Bin).filter(Bin.batch_id == last_route.batch_id).all()
    if not bin_data:
        return {"error": "No bin data found for the latest batch."}

    # Rebuild the graph
    G = nx.Graph()
    for bin in bin_data:
        G.add_node(bin.id, pos=tuple(bin.position), fill_level=bin.fill_level)

    # Add the saved edges from the route
    for edge in last_route.edges:
        G.add_edge(edge["from"], edge["to"], weight=edge["weight"])

    # Run all four algorithms on the same graph
    o_route, o_dist, o_cov = find_best_route(G, threshold)
    d_route, d_dist, d_cov = find_best_route_using_djikstra(G, threshold)
    a_route, a_dist, a_cov = find_best_route_using_astar(G, threshold)
    n_route, n_dist, n_cov = find_naive_route(G, threshold)

    return {
        "dijkstra": {"distance": round(d_dist, 2), "bins": d_cov, "route": d_route},
        "astar":    {"distance": round(a_dist, 2), "bins": a_cov, "route": a_route},
        "naive":    {"distance": round(n_dist, 2), "bins": n_cov, "route": n_route},
        "Main":     {"distance": round(o_dist, 2), "bins": o_cov, "route": o_route},
    }
