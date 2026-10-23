def format_solution(problem, chromosome):
    if not problem.is_feasible(chromosome):
        raise ValueError("Error: Cannot print an infeasible CVRP chromosome.")

    routes = problem.decode(chromosome)

    total_distance = 0
    total_load = 0
    output_lines = []

    for vehicle_id in range(len(routes)):
        route = routes[vehicle_id]
        route_distance = 0
        route_load = 0
        route_steps = []

        output_lines.append(f"Route for vehicle {vehicle_id}:")

        for index in range(len(route)):
            node = route[index]

            route_load += problem.demands[node]
            route_steps.append(f" {node} Load({route_load})")

            if index < len(route) - 1:
                next_node = route[index + 1]
                route_distance += problem.distance_matrix[node][next_node]

        output_lines.append(" ->".join(route_steps))
        output_lines.append(f"Distance of the route: {route_distance}m")
        output_lines.append(f"Load of the route: {route_load}")
        output_lines.append("")

        total_distance += route_distance
        total_load += route_load

    output_lines.insert(0, f"Objective: {total_distance}")

    output_lines.append(f"Total Distance of all routes: {total_distance}m")
    output_lines.append(f"Total Load of all routes: {total_load}")

    return "\n".join(output_lines)


def print_solution(problem, chromosome):
    print(format_solution(problem, chromosome))