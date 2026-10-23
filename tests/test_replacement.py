import math
import random

from ga_toolbox import GAConfig, GeneticAlgorithm, IntegerChromosome, Mutation, OrderCrossover, Replacement, TournamentSelection
from ga_toolbox import GenerationalReplacement, SteadyStateReplacement

random.seed(1)
config=GAConfig(population_size=20, generations=30, mutation_rate=0.5, seed=1)

def make(fitness, feasible=True, gene=0):
    """A tiny evaluated chromosome; `gene` just makes each one identifiable."""
    chromosome = IntegerChromosome([gene], low=0, high=1000)
    chromosome.fitness = fitness
    chromosome.feasible = feasible
    return chromosome


def make_list(values, feasibles=None):
    feasibles = feasibles if feasibles is not None else [True] * len(values)
    return [make(value, ok, gene=i) for i, (value, ok) in enumerate(zip(values, feasibles))]


def fits(chromosomes):
    return [c.fitness for c in chromosomes]


def snapshot(chromosomes):
    return [(c.genes.copy(), c.fitness, c.feasible) for c in chromosomes]


def no_shared_objects(result, *inputs):
    originals = [c for group in inputs for c in group]
    return all(r is not c for r in result for c in originals)


# ---------------------------------------------------------------- Generational
generational = GenerationalReplacement()
assert isinstance(generational, Replacement)

# Equal sizes: the offspring become the next population (as copies).
population = make_list([4, 2, 3, 1])
offspring = make_list([8, 6, 7, 5])
before_pop, before_off = snapshot(population), snapshot(offspring)
result = generational.replace(population, offspring, config)
assert fits(result) == [8, 6, 7, 5]
assert len(result) == len(population)
assert no_shared_objects(result, population, offspring)
assert all(r.fitness is not None for r in result)          # copies keep their fitness
assert snapshot(population) == before_pop and snapshot(offspring) == before_off
print("generational: equal size tests passed")

# More offspring than the population: keep the best `size` (minimising).
population = make_list([9, 9, 9])
offspring = make_list([5, 1, 4, 2, 3])
result = generational.replace(population, offspring, config)
assert len(result) == 3 and sorted(fits(result)) == [1, 2, 3]
assert no_shared_objects(result, population, offspring)

# ...and maximising keeps the highest ones.
config.maximize = True
result = generational.replace(population, offspring, config)
assert len(result) == 3 and sorted(fits(result)) == [3, 4, 5]
print("generational: too many offspring tests passed")

# Fewer offspring than the population: the best old individuals fill the gap.
population = make_list([4, 2, 3, 1])
offspring = make_list([9])
before_pop = snapshot(population)
config.maximize = False
result = generational.replace(population, offspring, config)
assert len(result) == 4 and sorted(fits(result)) == [1, 2, 3, 9]
assert no_shared_objects(result, population, offspring)
assert snapshot(population) == before_pop

config.maximize = True
result = generational.replace(population, offspring, config)   # maximising: best old are 4, 3, 2
assert len(result) == 4 and sorted(fits(result)) == [2, 3, 4, 9]
print("generational: too few offspring tests passed")

# Feasible beats infeasible even when its fitness number is worse; inf ranks last.
population = make_list([5])
offspring = make_list([10, 1], feasibles=[True, False])

config.maximize = False
assert fits(generational.replace(population, offspring, config)) == [10]
offspring = make_list([math.inf, 3, 4], feasibles=[False, True, True])
result = generational.replace(make_list([0, 0]), offspring, config)
assert sorted(fits(result)) == [3, 4]
print("generational: feasibility and inf tests passed")

# Errors.
try:
    generational.replace([], make_list([1]), config)
    raise SystemExit("empty population should raise")
except ValueError:
    pass
print("generational: error tests passed")

# --------------------------------------------------------------- Steady-state
assert isinstance(SteadyStateReplacement(), Replacement)

# The best k offspring replace the k worst; everyone else is unchanged.
steady = SteadyStateReplacement()
population = make_list([1, 5, 3, 9, 7])
offspring = make_list([2, 8, 0, 6, 4])
before_pop, before_off = snapshot(population), snapshot(offspring)
result = steady.replace(population, offspring, config)
assert len(result) == 5
assert fits(result[:3]) == [1, 5, 3]                       # untouched positions
assert sorted(fits(result[3:])) == [0, 2]                  # 9 and 7 replaced by 0 and 2
assert no_shared_objects(result, population, offspring)
assert snapshot(population) == before_pop and snapshot(offspring) == before_off
print("steady-state: basic tests passed")

# Maximising: best offspring is the highest, worst individual is the lowest.
config.steady_state_replacement_count = 1
config.maximize = True
result = SteadyStateReplacement().replace(make_list([1, 5, 3]), make_list([10, 0, 4]), config)
assert sorted(fits(result)) == [3, 5, 10]

# k larger than the population or the offspring list is clamped.
config.steady_state_replacement_count = 10
result = SteadyStateReplacement().replace(make_list([1, 2, 3]), make_list([7, 8, 9]), config)
assert sorted(fits(result)) == [7, 8, 9]

config.steady_state_replacement_count = 5
config.maximize = False
result = SteadyStateReplacement().replace(make_list([1, 5, 3, 9]), make_list([2, 0]), config)
assert len(result) == 4 and sorted(fits(result)) == [0, 1, 2, 3]
print("steady-state: clamping tests passed")

# No offspring: the population is returned unchanged (as copies).
population = make_list([3, 1, 2])
result = steady.replace(population, [], config)
assert fits(result) == [3, 1, 2] and no_shared_objects(result, population)

# Feasible beats infeasible, so the infeasible one is the worst even with a low number.
population = make_list([1, 5, 3], feasibles=[False, True, True])
offspring = make_list([4, 0], feasibles=[True, False])

config.steady_state_replacement_count = 1
result = SteadyStateReplacement().replace(population, offspring, config)
assert sorted(fits(result)) == [3, 4, 5]
print("steady-state: edge case tests passed")

# Errors.

try:
    steady.replace([], make_list([1]), config)
    raise SystemExit("empty population should raise")
except ValueError:
    pass
print("steady-state: error tests passed")


# ------------------------------------------------- Inside the real GA engine
class SwapTwo(Mutation):
    """Minimal swap mutation so this test does not depend on mutation.py."""

    def mutate(self, chromosome, rate):
        child = chromosome.copy()
        child.fitness = None
        child.feasible = True
        if random.random() < rate:
            i, j = random.sample(range(len(child.genes)), 2)
            child.genes[i], child.genes[j] = child.genes[j], child.genes[i]
        return child


def misplaced(chromosome):
    return sum(1 for position, gene in enumerate(chromosome.genes) if gene != position + 1)


for replacement in (GenerationalReplacement(), SteadyStateReplacement()):
    ga = GeneticAlgorithm(
        init_fn=lambda: IntegerChromosome.random(8, low=1, permutation=True),
        fitness_fn=misplaced,
        feasibility_fn=lambda chromosome: True,
        selection=TournamentSelection(3),
        crossover=OrderCrossover(),
        mutation=SwapTwo(),
        replacement=replacement,
        config=GAConfig(population_size=20, generations=30, mutation_rate=0.5, seed=1),
    )
    best, history = ga.run()
    assert best.is_valid() and best.feasible
    assert len(history) == 31
    assert all(later <= earlier for earlier, later in zip(history, history[1:]))
    assert history[-1] <= history[0]
print("engine integration tests passed")

print("all replacement tests passed")