class CVRPProblem:
    def __init__(self, distance_matrix, demands, vehicle_capacities, depot=0):
        self.distance_matrix = distance_matrix
        self.demands = demands
        self.vehicle_capacities = vehicle_capacities
        self.depot = depot
        self.num_vehicles = len(vehicle_capacities)

        self.customers = []
        for node in range(len(demands)):
            if node != depot:
                self.customers.append(node)

        if any(demand < 0 for demand in demands):
            raise ValueError("Error: Demands cannot be negative.")

        if any(demand > max(vehicle_capacities) for demand in demands):
            raise ValueError("Error: A customer's demand is larger than our biggest vehicle.")

    def _get_genes_list(self, chromosome):
        if hasattr(chromosome, "genes"):
            return list(chromosome.genes)
        return list(chromosome)

    def get_capacity(self, route_number):
        if route_number < self.num_vehicles:
            return self.vehicle_capacities[route_number]
        return self.vehicle_capacities[-1]

    def decode(self, chromosome):
        genes = self._get_genes_list(chromosome)

        route_customers = []  
        route_loads = []    

        for customer in genes:
            demand = self.demands[customer]
            placed = False

            for route_number in range(len(route_customers)):
                if route_loads[route_number] + demand <= self.get_capacity(route_number):
                    route_customers[route_number].append(customer)
                    route_loads[route_number] += demand
                    placed = True
                    break

            if not placed:
                route_customers.append([customer])
                route_loads.append(demand)

        routes = []
        for customers in route_customers:
            routes.append([self.depot] + customers + [self.depot])
        return routes

    def get_route_load(self, route):
        total_load = 0
        for node in route:
            if node != self.depot:
                total_load += self.demands[node]
        return total_load

    def violations_from_routes(self, routes):
        violations = {"extra_vehicles": 0, "capacity_excess": 0}

        if len(routes) > self.num_vehicles:
            violations["extra_vehicles"] = len(routes) - self.num_vehicles

        for route_number in range(len(routes)):
            load = self.get_route_load(routes[route_number])
            capacity = self.get_capacity(route_number)
            if load > capacity:
                violations["capacity_excess"] += load - capacity

        return violations

    def constraint_violations(self, chromosome):
        genes = self._get_genes_list(chromosome)
        expected_customers = set(self.customers)
        actual_customers = set(genes)

        violations = {
            "missing_customers": len(expected_customers - actual_customers),
            "duplicate_customers": len(genes) - len(actual_customers),
            "unknown_customers": len(actual_customers - expected_customers),
            "capacity_excess": 0,
            "extra_vehicles": 0,
        }

        if (violations["missing_customers"] > 0
                or violations["duplicate_customers"] > 0
                or violations["unknown_customers"] > 0):
            return violations

        routes = self.decode(genes)
        route_violations = self.violations_from_routes(routes)
        violations["extra_vehicles"] = route_violations["extra_vehicles"]
        violations["capacity_excess"] = route_violations["capacity_excess"]

        return violations

    def is_feasible(self, chromosome):
        try:
            violations = self.constraint_violations(chromosome)
        except Exception:
            return False

        for value in violations.values():
            if value > 0:
                return False

        return True