from abc import ABC, abstractmethod


class Selection(ABC):
    """Chooses parents from the population."""

    @abstractmethod
    def select(self, population, n, maximize):
        """Return a list of n chromosomes chosen from the population.

        Use the fitness values and respect `maximize` (False = lower is better).
        Return copies; never modify the population.
        """


class Crossover(ABC):
    """Combines two parents into two children."""

    @abstractmethod
    def crossover(self, parent1, parent2):
        """Return a tuple (child1, child2) of NEW chromosomes.

        Never modify the parents (use copy()).
        """


class Mutation(ABC):
    """Randomly changes a chromosome."""

    @abstractmethod
    def mutate(self, chromosome, rate):
        """Return a NEW mutated chromosome. Never modify the input (use copy())."""


class Replacement(ABC):
    """Builds the next population from the current one and the offspring."""

    @abstractmethod
    def replace(self, population, offspring, maximize):
        """Return the next population as a list with the same size as `population`.

        Respect `maximize` (False = lower fitness is better).
        """
