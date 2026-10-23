from cvrp.cost import total_distance

class CVRPFitness:
    def __init__(self, problem, penalty_weight=10000):
        self.problem = problem
        self.penalty_weight = penalty_weight

    def fitness(self, chromosome):
        violations = self.problem.constraint_violations(chromosome)

        broken = (violations["missing_customers"]
                  + violations["duplicate_customers"]
                  + violations["unknown_customers"])
        if broken > 0:
            return broken * self.penalty_weight * 100

        routes = self.problem.decode(chromosome)
        distance = total_distance(routes, self.problem.distance_matrix, self.problem.depot)

        penalty = (violations["extra_vehicles"] + violations["capacity_excess"]) * self.penalty_weight

        return distance + penalty