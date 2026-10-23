from abc import ABC, abstractmethod
from typing import Any, Sequence
from .settings import GAConfig


class Selection(ABC):
    @abstractmethod
    def select(
        self, population: Sequence[Any], n: int, maximize: bool
    ) -> list[Any]:
        """Return n chromosomes (copies) chosen from the population."""


class Crossover(ABC):
    @abstractmethod
    def crossover(self, parent1, parent2):
        """Return (child1, child2) as new chromosomes; never modify the parents."""


class Mutation(ABC):
    @abstractmethod
    def mutate(self, chromosome, rate):
        """Return a new mutated chromosome; never modify the input."""


class Replacement(ABC):
    @abstractmethod
    def replace(self, population, offspring, config: GAConfig):
        """
        Return the next population, same size as `population`.
        Assumption: the offsprings and the population are already mutated and evaluated.
        """