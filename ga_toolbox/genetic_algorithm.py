import math
import random
from functools import cmp_to_key

from ga_toolbox.settings import GAConfig


class GeneticAlgorithm:
    """Run a configurable genetic algorithm using user-supplied operators."""

    def __init__(self, init_fn, fitness_fn, feasibility_fn,
                 selection, crossover, mutation, replacement, config=None):
        for name, function in (
            ("init_fn", init_fn),
            ("fitness_fn", fitness_fn),
            ("feasibility_fn", feasibility_fn),
        ):
            if not callable(function):
                raise TypeError(f"{name} must be callable")

        for name, operator, method in (
            ("selection", selection, "select"),
            ("crossover", crossover, "crossover"),
            ("mutation", mutation, "mutate"),
            ("replacement", replacement, "replace"),
        ):
            if not callable(getattr(operator, method, None)):
                raise TypeError(f"{name} must provide {method}()")

        if config is not None and not isinstance(config, GAConfig):
            raise TypeError("config must be a GAConfig or None")

        self.init_fn = init_fn
        self.fitness_fn = fitness_fn
        self.feasibility_fn = feasibility_fn
        self.selection = selection
        self.crossover = crossover
        self.mutation = mutation
        self.replacement = replacement
        self.config = config or GAConfig()

    def run(self):
        config = self.config
        if config.seed is not None:
            random.seed(config.seed)

        population = [self._evaluate(self.init_fn()) for _ in range(config.population_size)]
        best = self._best_of(population).copy()
        history = [best.fitness]

        for _ in range(config.generations):
            offspring = self._make_offspring(population)
            new_population = self.replacement.replace(population, offspring, config.maximize)
            if not isinstance(new_population, (list, tuple)):
                raise TypeError("replacement must return a list or tuple")
            if len(new_population) != config.population_size:
                raise ValueError("replacement must keep the configured population size")

            new_population = self._apply_elitism(population, list(new_population))
            population = new_population
            generation_best = self._best_of(population)
            if self._is_better(generation_best, best):
                best = generation_best.copy()
            history.append(best.fitness)

        return best, history

    def _make_offspring(self, population):
        config = self.config
        offspring = []

        while len(offspring) < config.population_size:
            parents = self.selection.select(population, 2, config.maximize)
            if not isinstance(parents, (list, tuple)) or len(parents) != 2:
                raise ValueError("selection must return two parents")

            parent1, parent2 = parents
            if random.random() < config.crossover_rate:
                children = self.crossover.crossover(parent1, parent2)
                if not isinstance(children, (list, tuple)) or len(children) != 2:
                    raise ValueError("crossover must return two children")
                child1, child2 = children
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            for child in (child1, child2):
                offspring.append(self._evaluate(self.mutation.mutate(child, config.mutation_rate)))
                if len(offspring) == config.population_size:
                    break

        return offspring

    def _apply_elitism(self, old_population, new_population):
        """Put the best `elitism_count` old chromosomes back in place of the worst new ones."""
        count = self.config.elitism_count
        if count == 0:
            return new_population

        def compare(first, second):
            if self._is_better(first, second):
                return -1
            if self._is_better(second, first):
                return 1
            return 0

        elites = sorted(old_population, key=cmp_to_key(compare))[:count]
        worst_indices = sorted(
            range(len(new_population)),
            key=cmp_to_key(lambda i, j: compare(new_population[i], new_population[j])),
        )[-count:]
        for index, elite in zip(worst_indices, elites):
            new_population[index] = elite.copy()
        return new_population

    def _evaluate(self, chromosome):
        """Set feasibility and fitness of a chromosome (penalty if infeasible)."""
        if not callable(getattr(chromosome, "is_valid", None)) or not callable(
            getattr(chromosome, "copy", None)
        ):
            raise TypeError("chromosomes must provide is_valid() and copy()")

        if not chromosome.is_valid():
            chromosome.feasible = False
            chromosome.fitness = -math.inf if self.config.maximize else math.inf
            return chromosome

        feasible = bool(self.feasibility_fn(chromosome))
        fitness = self.fitness_fn(chromosome)
        if isinstance(fitness, bool) or not isinstance(fitness, (int, float)):
            raise TypeError("fitness_fn must return a number")
        if not math.isfinite(fitness):
            raise ValueError("fitness_fn must return a finite number")

        chromosome.feasible = feasible
        chromosome.fitness = float(fitness)
        if not feasible:
            if self.config.maximize:
                chromosome.fitness -= self.config.infeasible_penalty
            else:
                chromosome.fitness += self.config.infeasible_penalty
        return chromosome

    def _is_better(self, first, second):
        if bool(first.feasible) != bool(second.feasible):
            return bool(first.feasible)
        if self.config.maximize:
            return first.fitness > second.fitness
        return first.fitness < second.fitness

    def _best_of(self, population):
        if not population:
            raise ValueError("population cannot be empty")
        best = population[0]
        for chromosome in population[1:]:
            if self._is_better(chromosome, best):
                best = chromosome
        return best
