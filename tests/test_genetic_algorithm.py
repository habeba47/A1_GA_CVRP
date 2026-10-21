"""Tests the GA engine with TEMPORARY toy operators (not the real ones)."""
import random
from ga_toolbox.chromosomes import BinaryChromosome
from ga_toolbox.settings import GAConfig
from ga_toolbox.genetic_algorithm import GeneticAlgorithm
from ga_toolbox.base_classes import Selection, Crossover, Mutation, Replacement


class ToySelection(Selection):
    def select(self, population, n, maximize):
        chosen = []
        for _ in range(n):
            group = random.sample(population, 3)
            pick = max(group, key=lambda c: c.fitness) if maximize \
                else min(group, key=lambda c: c.fitness)
            chosen.append(pick.copy())
        return chosen


class ToyCrossover(Crossover):
    def crossover(self, p1, p2):
        point = random.randint(1, len(p1) - 1)
        c1, c2 = p1.copy(), p2.copy()
        c1.genes = p1.genes[:point] + p2.genes[point:]
        c2.genes = p2.genes[:point] + p1.genes[point:]
        return c1, c2


class ToyMutation(Mutation):
    def mutate(self, chromosome, rate):
        new = chromosome.copy()
        for i in range(len(new.genes)):
            if random.random() < rate:
                new.genes[i] = 1 - new.genes[i]
        return new


class ToyReplacement(Replacement):
    def replace(self, population, offspring, maximize):
        elites = sorted(population, key=lambda c: c.fitness, reverse=maximize)[:2]
        rest = sorted(offspring, key=lambda c: c.fitness, reverse=maximize)
        return elites + rest[:len(population) - 2]


def build(config, feasibility_fn):
    return GeneticAlgorithm(
        init_fn=lambda: BinaryChromosome.random(30),
        fitness_fn=lambda c: sum(c.genes),
        feasibility_fn=feasibility_fn,
        selection=ToySelection(), crossover=ToyCrossover(),
        mutation=ToyMutation(), replacement=ToyReplacement(), config=config)


# Test 1: OneMax (maximize the number of ones)
cfg = GAConfig(population_size=50, generations=60, mutation_rate=0.02,
               maximize=True, seed=1)
best, history = build(cfg, lambda c: True).run()
print("OneMax:", history[0], "->", best.fitness)

# Test 2: same seed gives the same result
best2, _ = build(cfg, lambda c: True).run()
assert best.genes == best2.genes

# Test 3: penalty strategy with a constraint (at most 20 ones)
cfg3 = GAConfig(population_size=50, generations=60, mutation_rate=0.02,
                maximize=True, seed=1, infeasible_penalty=1000)
best3, _ = build(cfg3, lambda c: sum(c.genes) <= 20).run()
print("Constrained:", best3.fitness, best3.feasible)
assert best3.feasible and best3.fitness <= 20
print("engine tests passed")
