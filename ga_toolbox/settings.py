import math
from dataclasses import dataclass


@dataclass
class GAConfig:
    """Configuration options for the genetic algorithm."""

    population_size: int = 100
    generations: int = 300
    crossover_rate: float = 0.9
    mutation_rate: float = 0.1
    elitism_count: int = 2
    tournament_size: int = 3
    maximize: bool = False
    seed: int = None
    infeasible_penalty: float = 100000.0

    def __post_init__(self):
        if type(self.population_size) is not int or self.population_size < 2:
            raise ValueError("population_size must be an integer of at least 2")
        if type(self.generations) is not int or self.generations < 0:
            raise ValueError("generations must be a non-negative integer")
        if type(self.elitism_count) is not int or not 0 <= self.elitism_count < self.population_size:
            raise ValueError("elitism_count must be between 0 and population_size - 1")
        if type(self.tournament_size) is not int or not 1 <= self.tournament_size <= self.population_size:
            raise ValueError("tournament_size must be between 1 and population_size")
        if type(self.maximize) is not bool:
            raise ValueError("maximize must be a boolean")
        if self.seed is not None and type(self.seed) is not int:
            raise ValueError("seed must be an integer or None")

        for name in ("crossover_rate", "mutation_rate"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be a number")
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")

        penalty = self.infeasible_penalty
        if isinstance(penalty, bool) or not isinstance(penalty, (int, float)):
            raise ValueError("infeasible_penalty must be a number")
        if not math.isfinite(penalty) or penalty < 0:
            raise ValueError("infeasible_penalty must be finite and non-negative")
