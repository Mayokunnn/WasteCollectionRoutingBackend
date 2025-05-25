from pydantic import BaseModel
from typing import List

class RouteOptimizationResponse(BaseModel):
    optimized_route: List[str]
    total_distance: float
    bins_covered: int
    threshold: float
