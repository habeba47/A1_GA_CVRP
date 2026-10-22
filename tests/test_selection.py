import math
import random
from collections import Counter

from ga_toolbox.chromosomes import BinaryChromosome
from ga_toolbox.settings import GAConfig
from ga_toolbox.genetic_algorithm import GeneticAlgorithm
from ga_toolbox.selection import TournamentSelection, RouletteSelection
from tests.test_genetic_algorithm import ToyCrossover, ToyMutation, ToyReplacement


class TaggedChromosome(BinaryChromosome):
    tag: int = 0


def make_population(fitnesses, feasible=None):
    population = []
    for i, fitness in enumerate(fitnesses):
        chromosome = TaggedChromosome([i % 2])
        chromosome.fitness = fitness
        chromosome.feasible = True if feasible is None else feasible[i]
        chromosome.tag = i
        population.append(chromosome)
    return population


def tag_counts(chosen):
    return Counter(c.tag for c in chosen)  # type: ignore[attr-defined]


random.seed(0)

for selection in (TournamentSelection(3), RouletteSelection()):
    name = type(selection).__name__
    population = make_population([5.0, 3.0, 9.0, 1.0, 7.0])

    # returns n new objects, population untouched
    chosen = selection.select(population, 8, False)
    assert len(chosen) == 8
    assert all(c is not p for c in chosen for p in population), name
    assert [c.fitness for c in population] == [5.0, 3.0, 9.0, 1.0, 7.0]

    # n = 0 and n > population size both work
    assert selection.select(population, 0, False) == []
    assert len(selection.select(population, 50, True)) == 50

    # bad input
    for bad_population, bad_n in (([], 2), (population, -1), (population, 1.5)):
        try:
            selection.select(bad_population, bad_n, False)  # type: ignore
            raise AssertionError(f"{name} accepted bad input")
        except ValueError:
            pass

    # better chromosomes are picked more often (minimize, then maximize)
    counts = tag_counts(selection.select(population, 20000, False))
    assert counts[3] > counts[1] > counts[0] > counts[4] > counts[2] - 1, (name, counts)
    counts = tag_counts(selection.select(population, 20000, True))
    assert counts[2] > counts[4] > counts[0] > counts[1] > counts[3] - 1, (name, counts)
    print(name, "ordering ok (minimize and maximize)")

# Tournament: size 1 is uniform, big size almost always returns the best
uniform = tag_counts(TournamentSelection(1).select(make_population([5, 3, 9, 1, 7]), 20000, False))
assert all(3000 < v < 5000 for v in uniform.values()), uniform
strong = tag_counts(TournamentSelection(5).select(make_population([5, 3, 9, 1, 7]), 200, False))
assert set(strong) == {3}, strong  # tournament_size == population size: always the best
# tournament larger than the population is capped, not an error
assert len(TournamentSelection(50).select(make_population([1, 2, 3]), 4, False)) == 4
for bad in (0, -1, 2.5, True):
    try:
        TournamentSelection(bad)  # type: ignore
        raise AssertionError("accepted bad tournament_size")
    except ValueError:
        pass

# Feasible beats infeasible even when penalty is 0 (same fitness)
mixed = make_population([1.0, 1.0], feasible=[False, True])
assert set(tag_counts(TournamentSelection(2).select(mixed, 100, False))) == {1}
print("TournamentSelection feasibility + size ok")

# Roulette: equal fitness -> uniform; invalid (inf) never picked; all invalid -> still works
roulette = RouletteSelection()
equal = tag_counts(roulette.select(make_population([4.0] * 4), 20000, False))
assert all(4000 < v < 6000 for v in equal.values()), equal
with_invalid = make_population([4.0, math.inf, 6.0])
assert 1 not in tag_counts(roulette.select(with_invalid, 2000, False))
all_invalid = make_population([math.inf, math.inf])
assert len(roulette.select(all_invalid, 10, False)) == 10

# Roulette: the engine's huge penalty must not flatten the feasible chromosomes
penalised = make_population([400.0, 500.0, 100400.0, 100500.0],
                            feasible=[True, True, False, False])
counts = tag_counts(roulette.select(penalised, 20000, False))
assert counts[0] > counts[1] * 1.5, counts      # still prefers the shorter route
assert counts[0] + counts[1] > 0.85 * 20000      # feasible ones dominate
assert counts[2] + counts[3] > 0                 # but infeasible can still be picked
print("RouletteSelection edge cases ok")

# Plugs into the real engine and improves OneMax
for selection in (TournamentSelection(3), RouletteSelection()):
    config = GAConfig(population_size=50, generations=60, mutation_rate=0.02,
                      maximize=True, seed=1)
    ga = GeneticAlgorithm(lambda: BinaryChromosome.random(30), lambda c: sum(c.genes),
                          lambda c: True, selection, ToyCrossover(), ToyMutation(),
                          ToyReplacement(), config=config)
    best, history = ga.run()
    again, _ = GeneticAlgorithm(lambda: BinaryChromosome.random(30), lambda c: sum(c.genes),
                                lambda c: True, selection, ToyCrossover(), ToyMutation(),
                                ToyReplacement(), config=config).run()
    assert best.genes == again.genes  # same seed, same result
    assert best.fitness > history[0] or history[0] == 30
    print(type(selection).__name__, "OneMax:", history[0], "->", best.fitness)

print("selection tests passed")