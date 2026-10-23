from data.example import create_data_model
from cvrp.problem import CVRPProblem
from cvrp.fitness import CVRPFitness
from cvrp.output import print_solution

from ga_toolbox import GAConfig, GeneticAlgorithm, IntegerChromosome, OrderCrossover, TournamentSelection
from ga_toolbox.mutation import SwapMutation
from ga_toolbox.replacement import GenerationalReplacement


def main():
    print("Starting the Genetic Algorithm for CVRP...")

    data = create_data_model()
    DISTANCE_MATRIX = data["distance_matrix"]
    DEMANDS = data["demands"]
    VEHICLE_CAPACITIES = data["vehicle_capacities"]
    DEPOT = data["depot"]

    problem = CVRPProblem(DISTANCE_MATRIX, DEMANDS, VEHICLE_CAPACITIES, depot=DEPOT)
    evaluator = CVRPFitness(problem, penalty_weight=10_000)

    def create_random_chromosome():
        return IntegerChromosome.random(
            length=len(problem.customers),
            low=1,
            high=len(DEMANDS) - 1,
            permutation=True
        )

    config = GAConfig(
        population_size=180,
        generations=1200,
        crossover_rate=0.95,
        mutation_rate=0.15,
        elitism_count=3,
        tournament_size=4,
        maximize=False,          
        seed=42,
        infeasible_penalty=100_000
    )

    ga = GeneticAlgorithm(
        init_fn=create_random_chromosome,
        fitness_fn=evaluator.fitness,
        feasibility_fn=problem.is_feasible,
        selection=TournamentSelection(tournament_size=config.tournament_size),
        crossover=OrderCrossover(),
        mutation=SwapMutation(),
        replacement=GenerationalReplacement(),
        config=config
    )

    print(f"Running {config.generations} generations... Please wait.")
    best_chromosome, history = ga.run()

    print("\n--- Algorithm Finished ---")
    print(f"Generations recorded: {len(history)}")
    print(f"Best fitness score: {best_chromosome.fitness}")
    print(f"Is the solution feasible (valid)? {best_chromosome.feasible}\n")

    if best_chromosome.feasible:
        print("=== Best Route Found ===")
        print_solution(problem, best_chromosome)
    else:
        print("No valid route found. Try running again or changing the settings.")


if __name__ == "__main__":
    main()