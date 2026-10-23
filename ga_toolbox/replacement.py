from .base_classes import Replacement
from .settings import GAConfig

def _rank_key(chromosome, maximize):
    """feasible first, then by fitness."""
    fitness = -chromosome.fitness if maximize else chromosome.fitness
    return (not chromosome.feasible, fitness)


class GenerationalReplacement(Replacement):
    def replace(self, population, offspring, config: GAConfig):
        size = len(population)
        maximize = config.maximize
        if size == 0:
            raise ValueError("population cannot be empty")

        if len(offspring) >= size:
            if len(offspring) == size:
                chosen = list(offspring)
            else:
                chosen = sorted(offspring, key=lambda c: _rank_key(c, maximize))[:size]
        else:
            survivors = sorted(population, key=lambda c: _rank_key(c, maximize))
            chosen = list(offspring) + survivors[:size - len(offspring)]

        return [c.copy() for c in chosen]

class SteadyStateReplacement(Replacement):
    def replace(self, population, offspring, config: GAConfig):
        size = len(population)
        if size == 0:
            raise ValueError("population cannot be empty")

        k = min(config.steady_state_replacement_count , size, len(offspring))
        maximize = config.maximize

        best_offspring = sorted(offspring, key=lambda c: _rank_key(c, maximize))[:k]

        # population indices ordered best -> worst; the last k are the victims
        ranked = sorted(range(size), key=lambda i: _rank_key(population[i], maximize))
        victims = ranked[size - k:]

        next_population = [c.copy() for c in population]

        for index, child in zip(victims, best_offspring):
            next_population[index] = child.copy()
        
        return next_population
