from typing import List

def route_cost(route: List[int], dist: List[List[float]], depot=0):
    """
    Returns the distance covered by a vehicle
    Inputs: 
        the route (route: List[int])
        Note: A route must exclude the depot, which means the first value is the first destination
        the destination Matrix (dist: List[list[float]] size= M x M)
        depot: int
    """
    if not route or len(route) == 0: # unused vehicle costs nothing
        return 0
    
    total = dist[depot][route[0]] # first distination
    for a, b in zip(route, route[1:]):
        total += dist[a][b]
    
    return total + dist[route[-1]][depot] # return to depot distance

def total_distance(routes: List[List[int]], dist: List[List[float]], depot=0):
    """
    Returns the total distance Covered by all Vehicles using their routes
    Inputs:
        a list of their routes, each being a list of points the vehicle passes through (routes: List[List[int]])
        Note: A route must exclude the depot, which means the first value is the first destination
        the destination Matrix (dist: List[list[float]] size = M x M)
        depot: int
    """
    return sum(route_cost(route, dist, depot) for route in routes)